"""
Hot Swap Manager for Aegis Agent
Provides runtime tool management and hot-plugging capabilities.
"""

import asyncio
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import threading
import queue

from .base import BaseTool, ToolResult
from .plugin_manager import PluginManager, plugin_manager, ToolPlugin
from .tool_adapter import ToolRegistryAdapter, tool_registry_adapter


@dataclass
class HotSwapEvent:
    """Event for tool hot-swapping."""
    event_type: str  # "loaded", "unloaded", "updated", "error"
    tool_name: str
    timestamp: datetime
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class HotSwapManager:
    """
    Hot swap manager for runtime tool management.
    Provides monitoring, automatic reloading, and event handling.
    """
    
    def __init__(self, watch_directories: List[str] = None):
        self.watch_directories = watch_directories or ["python/tools/dynamic"]
        self.event_queue = queue.Queue()
        self.event_handlers: List[Callable[[HotSwapEvent], None]] = []
        self.monitoring = False
        self.monitor_thread = None
        self.file_timestamps: Dict[str, float] = {}
        
        # Initialize monitoring
        self._initialize_file_monitoring()
        
        logging.info(f"HotSwapManager initialized with watch directories: {self.watch_directories}")
    
    def _initialize_file_monitoring(self):
        """Initialize file monitoring for hot-swapping."""
        for directory in self.watch_directories:
            dir_path = Path(directory)
            if dir_path.exists():
                for file_path in dir_path.rglob("*.py"):
                    if file_path.name.startswith("__"):
                        continue
                    self.file_timestamps[str(file_path)] = file_path.stat().st_mtime
    
    def start_monitoring(self):
        """Start monitoring for file changes."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logging.info("Hot swap monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring for file changes."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logging.info("Hot swap monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self._check_for_changes()
                time.sleep(1)  # Check every second
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _check_for_changes(self):
        """Check for file changes in monitored directories."""
        for directory in self.watch_directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.rglob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                
                file_str = str(file_path)
                current_mtime = file_path.stat().st_mtime
                last_mtime = self.file_timestamps.get(file_str, 0)
                
                if current_mtime > last_mtime:
                    self.file_timestamps[file_str] = current_mtime
                    self._handle_file_change(file_path)
    
    def _handle_file_change(self, file_path: Path):
        """Handle a file change event."""
        try:
            tool_name = file_path.stem.replace("dynamic_", "")
            
            # Try to reload the tool
            success = self.hot_reload_tool(tool_name)
            
            event = HotSwapEvent(
                event_type="updated" if success else "error",
                tool_name=tool_name,
                timestamp=datetime.now(),
                details={
                    "file_path": str(file_path),
                    "success": success
                }
            )
            
            self._emit_event(event)
            
        except Exception as e:
            logging.error(f"Error handling file change for {file_path}: {e}")
            
            event = HotSwapEvent(
                event_type="error",
                tool_name=file_path.stem,
                timestamp=datetime.now(),
                details={
                    "file_path": str(file_path),
                    "error": str(e)
                }
            )
            
            self._emit_event(event)
    
    def hot_reload_tool(self, tool_name: str) -> bool:
        """
        Hot reload a specific tool.
        
        Args:
            tool_name: Name of the tool to reload
            
        Returns:
            True if reload successful
        """
        try:
            # Unload the tool first
            self.hot_unload_tool(tool_name)
            
            # Reload the tool
            success = tool_registry_adapter.register_tool_class(tool_name, None, "dynamic")
            
            if success:
                logging.info(f"Hot reloaded tool: {tool_name}")
                return True
            else:
                logging.error(f"Failed to hot reload tool: {tool_name}")
                return False
                
        except Exception as e:
            logging.error(f"Error hot reloading tool {tool_name}: {e}")
            return False
    
    def hot_unload_tool(self, tool_name: str) -> bool:
        """
        Hot unload a specific tool.
        
        Args:
            tool_name: Name of the tool to unload
            
        Returns:
            True if unload successful
        """
        try:
            success = tool_registry_adapter.unregister_tool_class(tool_name)
            
            if success:
                logging.info(f"Hot unloaded tool: {tool_name}")
                return True
            else:
                logging.warning(f"Tool {tool_name} was not loaded")
                return False
                
        except Exception as e:
            logging.error(f"Error hot unloading tool {tool_name}: {e}")
            return False
    
    def hot_load_tool(self, tool_name: str, tool_class: Any) -> bool:
        """
        Hot load a new tool.
        
        Args:
            tool_name: Name of the tool
            tool_class: Tool class to load
            
        Returns:
            True if load successful
        """
        try:
            success = tool_registry_adapter.register_tool_class(tool_name, tool_class, "dynamic")
            
            if success:
                logging.info(f"Hot loaded tool: {tool_name}")
                return True
            else:
                logging.error(f"Failed to hot load tool: {tool_name}")
                return False
                
        except Exception as e:
            logging.error(f"Error hot loading tool {tool_name}: {e}")
            return False
    
    def get_tool_status(self, tool_name: str) -> Dict[str, Any]:
        """
        Get status information for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Status information dictionary
        """
        tool_instance = plugin_manager.loaded_tools.get(tool_name)
        plugin_info = plugin_manager.get_plugin_info(tool_name)
        
        status = {
            "name": tool_name,
            "loaded": tool_instance is not None,
            "plugin_info": plugin_info.__dict__ if plugin_info else None,
            "last_modified": None
        }
        
        # Get file modification time if available
        for directory in self.watch_directories:
            dir_path = Path(directory)
            if dir_path.exists():
                file_path = dir_path / f"dynamic_{tool_name}.py"
                if file_path.exists():
                    status["last_modified"] = datetime.fromtimestamp(file_path.stat().st_mtime)
                    break
        
        return status
    
    def list_tool_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status for all tools.
        
        Returns:
            Dictionary mapping tool names to status information
        """
        status = {}
        
        # Get all available tools
        all_tools = plugin_manager.list_available_plugins()
        
        for tool_name in all_tools:
            status[tool_name] = self.get_tool_status(tool_name)
        
        return status
    
    def add_event_handler(self, handler: Callable[[HotSwapEvent], None]):
        """
        Add an event handler for hot swap events.
        
        Args:
            handler: Function to call when events occur
        """
        self.event_handlers.append(handler)
    
    def remove_event_handler(self, handler: Callable[[HotSwapEvent], None]):
        """
        Remove an event handler.
        
        Args:
            handler: Handler to remove
        """
        if handler in self.event_handlers:
            self.event_handlers.remove(handler)
    
    def _emit_event(self, event: HotSwapEvent):
        """Emit an event to all handlers."""
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                logging.error(f"Error in event handler: {e}")
    
    def get_event_queue(self) -> queue.Queue:
        """Get the event queue for manual processing."""
        return self.event_queue
    
    def cleanup(self):
        """Cleanup the hot swap manager."""
        self.stop_monitoring()
        self.event_handlers.clear()


class ToolHotSwapPlugin(ToolPlugin):
    """
    Plugin for managing hot-swappable tools.
    """
    
    def __init__(self):
        super().__init__("hot_swap", "Hot swap tool management")
        self.hot_swap_manager = HotSwapManager()
    
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the hot swap plugin."""
        try:
            # Start monitoring
            self.hot_swap_manager.start_monitoring()
            
            # Register event handlers
            self.hot_swap_manager.add_event_handler(self._on_tool_event)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize hot swap plugin: {e}")
            return False
    
    def cleanup(self):
        """Cleanup the hot swap plugin."""
        self.hot_swap_manager.cleanup()
    
    def _on_tool_event(self, event: HotSwapEvent):
        """Handle tool events."""
        logging.info(f"Tool event: {event.event_type} - {event.tool_name}")
        
        # Update agent's tool list if needed
        # This would typically notify the agent to refresh its tool list
        pass
    
    def get_hot_swap_manager(self) -> HotSwapManager:
        """Get the hot swap manager instance."""
        return self.hot_swap_manager


# Global hot swap manager instance
hot_swap_manager = HotSwapManager() 