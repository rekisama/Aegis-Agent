"""
Base Tool System for Agent Zero
Provides the foundation for creating and using custom tools.
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """
    Base class for all tools in the Agent Zero framework.
    
    All tools should inherit from this class and implement the required methods.
    """
    
    def __init__(self, name: str = None, description: str = None):
        self.name = name or self.__class__.__name__
        self.description = description or "A tool for Agent Zero"
        self.created_at = datetime.now()
        self.usage_count = 0
        self.success_count = 0
        self.last_used = None
        
        logging.info(f"Initialized tool: {self.name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult: The result of the tool execution
        """
        pass
    
    def get_info(self) -> Dict:
        """Get information about the tool."""
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "success_rate": self.success_count / max(self.usage_count, 1),
            "last_used": self.last_used.isoformat() if self.last_used else None
        }
    
    def _update_usage_stats(self, success: bool):
        """Update usage statistics."""
        self.usage_count += 1
        if success:
            self.success_count += 1
        self.last_used = datetime.now()


class ToolRegistry:
    """
    Registry for managing tools in the Agent Zero framework.
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.tool_factories: Dict[str, Callable] = {}
    
    def register_tool(self, tool: BaseTool):
        """Register a tool instance."""
        self.tools[tool.name] = tool
        logging.info(f"Registered tool: {tool.name}")
    
    def register_tool_factory(self, name: str, factory: Callable):
        """Register a tool factory function."""
        self.tool_factories[name] = factory
        logging.info(f"Registered tool factory: {name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def create_tool(self, name: str, **kwargs) -> Optional[BaseTool]:
        """Create a tool using a factory."""
        factory = self.tool_factories.get(name)
        if factory:
            return factory(**kwargs)
        return None
    
    def list_tools(self) -> List[Dict]:
        """List all available tools."""
        return [tool.get_info() for tool in self.tools.values()]
    
    def remove_tool(self, name: str):
        """Remove a tool from the registry."""
        if name in self.tools:
            del self.tools[name]
            logging.info(f"Removed tool: {name}")


class CustomTool(BaseTool):
    """
    A customizable tool that can be created dynamically.
    """
    
    def __init__(self, name: str, description: str, func: Callable):
        super().__init__(name, description)
        self.func = func
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the custom function."""
        start_time = datetime.now()
        
        try:
            # Check if the function is async
            if asyncio.iscoroutinefunction(self.func):
                result = await self.func(**kwargs)
            else:
                result = self.func(**kwargs)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_usage_stats(True)
            
            return ToolResult(
                success=True,
                data=result,
                execution_time=execution_time,
                metadata={"tool_type": "custom"}
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_usage_stats(False)
            
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time=execution_time,
                metadata={"tool_type": "custom"}
            )


class ToolBuilder:
    """
    Builder for creating custom tools.
    """
    
    def __init__(self):
        self.registry = ToolRegistry()
    
    def create_tool(self, name: str, description: str, func: Callable) -> CustomTool:
        """Create a custom tool."""
        tool = CustomTool(name, description, func)
        self.registry.register_tool(tool)
        return tool
    
    def create_code_tool(self, name: str, description: str, code: str) -> CustomTool:
        """Create a tool from code string."""
        # This would compile and execute the code
        # For now, we'll create a simple wrapper
        def code_wrapper(**kwargs):
            # In a real implementation, this would safely execute the code
            return f"Executed code for {name}: {code}"
        
        return self.create_tool(name, description, code_wrapper)
    
    def create_http_tool(self, name: str, description: str, url: str, method: str = "GET") -> CustomTool:
        """Create a tool for HTTP requests."""
        import requests
        
        async def http_wrapper(**kwargs):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, params=kwargs)
                elif method.upper() == "POST":
                    response = requests.post(url, json=kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                return {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.text
                }
            except Exception as e:
                raise Exception(f"HTTP request failed: {e}")
        
        return self.create_tool(name, description, http_wrapper)
    
    def get_registry(self) -> ToolRegistry:
        """Get the tool registry."""
        return self.registry 