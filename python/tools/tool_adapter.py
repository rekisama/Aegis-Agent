"""
Tool Adapter System for Aegis Agent
Converts existing tools to plugin architecture and provides compatibility layer.
"""

import logging
import sys
from typing import Dict, List, Optional, Any, Type
from pathlib import Path

from .base import BaseTool, ToolResult
from .plugin_manager import ToolPlugin, PluginManager, plugin_manager


class ToolAdapter(ToolPlugin):
    """
    Adapter for converting existing BaseTool classes to plugin architecture.
    """
    
    def __init__(self, tool_class: Type[BaseTool], name: str = None, description: str = None):
        self.tool_class = tool_class
        self.tool_instance: Optional[BaseTool] = None
        
        # Use provided name/description or extract from tool class
        if name is None:
            name = tool_class.__name__.lower().replace('tool', '')
        if description is None:
            description = getattr(tool_class, '__doc__', '') or tool_class.__name__
        
        super().__init__(name, description)
    
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the tool adapter."""
        try:
            # Create tool instance
            self.tool_instance = self.tool_class(**config or {})
            
            # Register the tool with plugin manager
            plugin_manager.register_tool(self.name, self.tool_instance)
            
            logging.info(f"Tool adapter initialized: {self.name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize tool adapter {self.name}: {e}")
            return False
    
    def cleanup(self):
        """Cleanup the tool adapter."""
        if self.tool_instance:
            # Unregister the tool
            plugin_manager.unregister_tool(self.name)
            
            # Call cleanup if available
            if hasattr(self.tool_instance, 'cleanup'):
                self.tool_instance.cleanup()
            
            self.tool_instance = None
    
    def get_tool_instance(self) -> Optional[BaseTool]:
        """Get the underlying tool instance."""
        return self.tool_instance


class BuiltinToolAdapter(ToolAdapter):
    """
    Adapter for built-in tools.
    """
    
    def __init__(self, tool_class: Type[BaseTool]):
        super().__init__(tool_class)
        self.category = "builtin"


class DynamicToolAdapter(ToolAdapter):
    """
    Adapter for dynamic tools.
    """
    
    def __init__(self, tool_class: Type[BaseTool]):
        super().__init__(tool_class)
        self.category = "dynamic"


class ToolAdapterFactory:
    """
    Factory for creating tool adapters.
    """
    
    @staticmethod
    def create_adapter(tool_class: Type[BaseTool], adapter_type: str = "builtin") -> ToolAdapter:
        """
        Create a tool adapter.
        
        Args:
            tool_class: The tool class to adapt
            adapter_type: Type of adapter ("builtin", "dynamic", "custom")
            
        Returns:
            ToolAdapter instance
        """
        if adapter_type == "builtin":
            return BuiltinToolAdapter(tool_class)
        elif adapter_type == "dynamic":
            return DynamicToolAdapter(tool_class)
        else:
            return ToolAdapter(tool_class)


class ToolRegistryAdapter:
    """
    Adapter for the existing tool registry to work with the new plugin system.
    """
    
    def __init__(self):
        self.adapters: Dict[str, ToolAdapter] = {}
        self.tool_classes: Dict[str, Type[BaseTool]] = {}
        
        # Register callbacks
        plugin_manager.add_tool_registered_callback(self._on_tool_registered)
        plugin_manager.add_plugin_loaded_callback(self._on_plugin_loaded)
    
    def register_tool_class(self, tool_name: str, tool_class: Type[BaseTool], 
                          adapter_type: str = "builtin") -> bool:
        """
        Register a tool class with the adapter system.
        
        Args:
            tool_name: Name of the tool
            tool_class: Tool class to register
            adapter_type: Type of adapter to use
            
        Returns:
            True if registration successful
        """
        try:
            # Create adapter
            adapter = ToolAdapterFactory.create_adapter(tool_class, adapter_type)
            
            # Store references
            self.adapters[tool_name] = adapter
            self.tool_classes[tool_name] = tool_class
            
            # Load the plugin
            plugin_manager.load_plugin(tool_name, {})
            
            logging.info(f"Registered tool class: {tool_name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to register tool class {tool_name}: {e}")
            return False
    
    def unregister_tool_class(self, tool_name: str) -> bool:
        """
        Unregister a tool class.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            True if unregistration successful
        """
        try:
            if tool_name in self.adapters:
                adapter = self.adapters[tool_name]
                adapter.cleanup()
                
                del self.adapters[tool_name]
                del self.tool_classes[tool_name]
                
                logging.info(f"Unregistered tool class: {tool_name}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to unregister tool class {tool_name}: {e}")
            return False
    
    def get_tool_instance(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool instance by name."""
        return plugin_manager.loaded_tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tool instances."""
        return plugin_manager.loaded_tools.copy()
    
    def list_available_tools(self) -> List[str]:
        """List all available tool names."""
        return list(plugin_manager.loaded_tools.keys())
    
    def _on_tool_registered(self, tool_name: str, tool: BaseTool):
        """Callback when a tool is registered."""
        logging.info(f"Tool registered via adapter: {tool_name}")
    
    def _on_plugin_loaded(self, plugin_name: str, plugin: ToolPlugin):
        """Callback when a plugin is loaded."""
        logging.info(f"Plugin loaded via adapter: {plugin_name}")


# Global tool registry adapter instance
tool_registry_adapter = ToolRegistryAdapter()


def register_builtin_tools():
    """Register all built-in tools with the adapter system."""
    from .terminal import TerminalTool
    from .search import SearchTool
    from .code import CodeExecutionTool
    from .tavily_search import TavilySearchTool
    
    # Register built-in tools
    tools_to_register = [
        ("terminal", TerminalTool, "builtin"),
        ("search", SearchTool, "builtin"),
        ("code", CodeExecutionTool, "builtin"),
        ("tavily_search", TavilySearchTool, "builtin"),
    ]
    
    for tool_name, tool_class, adapter_type in tools_to_register:
        tool_registry_adapter.register_tool_class(tool_name, tool_class, adapter_type)
    
    logging.info("Built-in tools registered with adapter system")


def register_dynamic_tools():
    """Register dynamic tools with the adapter system."""
    dynamic_tools_dir = Path("python/tools/dynamic")
    
    if not dynamic_tools_dir.exists():
        return
    
    for tool_file in dynamic_tools_dir.glob("*.py"):
        if tool_file.name.startswith("__"):
            continue
        
        try:
            # Add the project root to sys.path for imports
            project_root = tool_file.parent.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # Import the dynamic tool
            import importlib.util
            spec = importlib.util.spec_from_file_location(tool_file.stem, tool_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find tool classes
            for name, obj in module.__dict__.items():
                if (isinstance(obj, type) and 
                    hasattr(obj, '__bases__') and
                    any('BaseTool' in str(base) for base in obj.__bases__) and 
                    obj.__name__ != 'BaseTool'):
                    
                    # Convert class name to tool name (e.g., HelloWorldTool -> hello_world)
                    tool_name = name.lower().replace('tool', '')
                    if tool_name == 'helloworld':
                        tool_name = 'hello_world'
                    elif tool_name == 'mock':
                        tool_name = 'mock_tool'
                    
                    tool_registry_adapter.register_tool_class(tool_name, obj, "dynamic")
                    break
                    
        except Exception as e:
            logging.warning(f"Failed to register dynamic tool {tool_file.name}: {e}")
    
    logging.info("Dynamic tools registered with adapter system") 