"""
Tool Registry for Aegis Agent
Provides a comprehensive tool registration system with detailed descriptions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from .tool_descriptions import TOOL_DESCRIPTIONS, get_tool_description, get_all_tool_descriptions, ToolCategory


# ToolCategory 已移动到 tool_descriptions.py


@dataclass
class ToolDescription:
    """Detailed tool description for LLM understanding."""
    name: str
    category: ToolCategory
    description: str
    capabilities: List[str]
    use_cases: List[str]
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]]
    limitations: List[str]


class ToolRegistry:
    """
    Comprehensive tool registry with detailed descriptions.
    
    Features:
    - Detailed tool descriptions
    - Capability matching
    - Use case examples
    - Parameter specifications
    - Category organization
    """
    
    def __init__(self):
        self.tools: Dict[str, ToolDescription] = {}
        self._load_tool_descriptions()
    
    def _load_tool_descriptions(self):
        """Load tool descriptions from configuration."""
        for tool_name, tool_config in TOOL_DESCRIPTIONS.items():
            self.tools[tool_name] = ToolDescription(
                name=tool_config["name"],
                category=tool_config["category"],
                description=tool_config["description"],
                capabilities=tool_config["capabilities"],
                use_cases=tool_config["use_cases"],
                parameters=tool_config["parameters"],
                examples=tool_config["examples"],
                limitations=tool_config["limitations"]
            )
    
    def get_tool_description(self, tool_name: str) -> Optional[ToolDescription]:
        """Get detailed description of a tool."""
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, ToolDescription]:
        """Get all registered tools."""
        return self.tools.copy()
    
    def get_tools_by_category(self, category: ToolCategory) -> Dict[str, ToolDescription]:
        """Get tools filtered by category."""
        return {name: tool for name, tool in self.tools.items() if tool.category == category}
    
    def generate_tool_summary_for_llm(self) -> str:
        """Generate a comprehensive tool summary for LLM."""
        summary = "Available Tools:\n\n"
        
        for name, tool in self.tools.items():
            summary += f"📦 {name} ({tool.category.value})\n"
            summary += f"   Description: {tool.description}\n"
            summary += f"   Capabilities: {', '.join(tool.capabilities)}\n"
            summary += f"   Use Cases: {', '.join(tool.use_cases)}\n"
            summary += f"   Parameters: {tool.parameters}\n"
            summary += f"   Examples:\n"
            for example in tool.examples:
                summary += f"     - Task: {example['task']}\n"
                summary += f"       Parameters: {example['parameters']}\n"
                summary += f"       Reason: {example['reason']}\n"
            summary += f"   Limitations: {', '.join(tool.limitations)}\n\n"
        
        return summary
    
    def find_best_tools_for_task(self, task_description: str) -> List[str]:
        """Find the best tools for a given task based on capabilities."""
        # This is a simple keyword-based matching
        # In practice, this would be done by LLM
        task_lower = task_description.lower()
        matching_tools = []
        
        for name, tool in self.tools.items():
            # Check if task matches any capability or use case
            for capability in tool.capabilities:
                if any(keyword in task_lower for keyword in capability.lower().split()):
                    matching_tools.append(name)
                    break
            
            for use_case in tool.use_cases:
                if any(keyword in task_lower for keyword in use_case.lower().split()):
                    matching_tools.append(name)
                    break
        
        return matching_tools
    
    def add_tool_description(self, tool_name: str, tool_config: Dict[str, Any]):
        """Add a new tool description to the registry."""
        self.tools[tool_name] = ToolDescription(
            name=tool_config["name"],
            category=tool_config["category"],
            description=tool_config["description"],
            capabilities=tool_config["capabilities"],
            use_cases=tool_config["use_cases"],
            parameters=tool_config["parameters"],
            examples=tool_config["examples"],
            limitations=tool_config["limitations"]
        )
    
    def remove_tool_description(self, tool_name: str):
        """Remove a tool description from the registry."""
        if tool_name in self.tools:
            del self.tools[tool_name]


# Global tool registry instance
tool_registry = ToolRegistry() 