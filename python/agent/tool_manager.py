"""
Tool Manager for Aegis Agent
Provides dynamic tool registration and management capabilities.
"""

from typing import Dict, List, Optional, Any, Type
from .tool_registry import ToolRegistry, ToolDescription, ToolCategory
from .tool_descriptions import TOOL_DESCRIPTIONS
from ..tools.base import BaseTool


class ToolManager:
    """
    Dynamic tool manager for Aegis Agent.
    
    Features:
    - Dynamic tool registration
    - Tool description management
    - Tool instance management
    - Category-based organization
    """
    
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.tool_instances: Dict[str, BaseTool] = {}
        self.tool_classes: Dict[str, Type[BaseTool]] = {}
    
    def register_tool(self, tool_name: str, tool_class: Type[BaseTool], 
                     description_config: Dict[str, Any] = None):
        """
        Register a new tool with its description.
        
        Args:
            tool_name: Name of the tool
            tool_class: Tool class to instantiate
            description_config: Tool description configuration
        """
        # Register tool class
        self.tool_classes[tool_name] = tool_class
        
        # Create tool instance
        self.tool_instances[tool_name] = tool_class()
        
        # Register tool description if provided
        if description_config:
            self.tool_registry.add_tool_description(tool_name, description_config)
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool."""
        if tool_name in self.tool_instances:
            del self.tool_instances[tool_name]
        
        if tool_name in self.tool_classes:
            del self.tool_classes[tool_name]
        
        self.tool_registry.remove_tool_description(tool_name)
    
    def get_tool_instance(self, tool_name: str) -> Optional[BaseTool]:
        """Get tool instance by name."""
        return self.tool_instances.get(tool_name)
    
    def get_tool_description(self, tool_name: str) -> Optional[ToolDescription]:
        """Get tool description by name."""
        return self.tool_registry.get_tool_description(tool_name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tool instances."""
        return self.tool_instances.copy()
    
    def get_all_descriptions(self) -> Dict[str, ToolDescription]:
        """Get all tool descriptions."""
        return self.tool_registry.get_all_tools()
    
    def get_tools_by_category(self, category: ToolCategory) -> Dict[str, BaseTool]:
        """Get tools filtered by category."""
        category_tools = self.tool_registry.get_tools_by_category(category)
        return {name: self.tool_instances[name] 
                for name in category_tools.keys() 
                if name in self.tool_instances}
    
    def generate_tool_summary_for_llm(self) -> str:
        """Generate tool summary for LLM."""
        return self.tool_registry.generate_tool_summary_for_llm()
    
    def find_best_tools_for_task(self, task_description: str) -> List[str]:
        """Find best tools for a task."""
        return self.tool_registry.find_best_tools_for_task(task_description)
    
    def list_available_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tool_instances.keys())
    
    def get_tool_categories(self) -> Dict[ToolCategory, List[str]]:
        """Get tools organized by category."""
        categories = {}
        for category in ToolCategory:
            category_tools = self.tool_registry.get_tools_by_category(category)
            categories[category] = list(category_tools.keys())
        return categories
    
    def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fill default parameters for a tool.
        
        Args:
            tool_name: Name of the tool
            parameters: Provided parameters
            
        Returns:
            Validated parameters with defaults
        """
        tool_desc = self.get_tool_description(tool_name)
        if not tool_desc:
            return parameters
        
        validated_params = parameters.copy()
        
        # Fill default values
        for param_name, param_config in tool_desc.parameters.items():
            if param_name not in validated_params and "default" in param_config:
                validated_params[param_name] = param_config["default"]
        
        return validated_params
    
    def get_tool_help(self, tool_name: str) -> str:
        """Get detailed help information for a tool."""
        tool_desc = self.get_tool_description(tool_name)
        if not tool_desc:
            return f"Tool '{tool_name}' not found."
        
        help_text = f"📦 {tool_name} ({tool_desc.category.value})\n"
        help_text += f"📝 Description: {tool_desc.description}\n\n"
        
        help_text += "🔧 Capabilities:\n"
        for capability in tool_desc.capabilities:
            help_text += f"   • {capability}\n"
        
        help_text += "\n💡 Use Cases:\n"
        for use_case in tool_desc.use_cases:
            help_text += f"   • {use_case}\n"
        
        help_text += "\n⚙️ Parameters:\n"
        for param_name, param_config in tool_desc.parameters.items():
            help_text += f"   • {param_name}: {param_config['description']}\n"
            if "examples" in param_config:
                help_text += f"     Examples: {param_config['examples']}\n"
            if "default" in param_config:
                help_text += f"     Default: {param_config['default']}\n"
        
        help_text += "\n📋 Examples:\n"
        for example in tool_desc.examples:
            help_text += f"   • Task: {example['task']}\n"
            help_text += f"     Parameters: {example['parameters']}\n"
            help_text += f"     Reason: {example['reason']}\n"
        
        help_text += "\n⚠️ Limitations:\n"
        for limitation in tool_desc.limitations:
            help_text += f"   • {limitation}\n"
        
        return help_text
    
    def get_system_summary(self) -> str:
        """Get a summary of all available tools for system prompts."""
        summary = "🛡️ Aegis Agent - Available Tools\n"
        summary += "=" * 50 + "\n\n"
        
        categories = self.get_tool_categories()
        for category, tools in categories.items():
            if tools:
                summary += f"📂 {category.value.upper()} Tools:\n"
                for tool_name in tools:
                    tool_desc = self.get_tool_description(tool_name)
                    if tool_desc:
                        summary += f"   📦 {tool_name}: {tool_desc.description}\n"
                summary += "\n"
        
        return summary


# Global tool manager instance
tool_manager = ToolManager() 