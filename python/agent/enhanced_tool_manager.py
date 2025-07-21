"""
Enhanced Tool Manager for Aegis Agent
参考 Agent Zero 的设计，提供更强大的工具管理功能
"""

from typing import Dict, List, Optional, Any, Type, Callable
from .tool_manager import ToolManager
from ..tools.base import BaseTool, ToolResult
import asyncio
import json
import logging


class Instrument:
    """自定义函数工具，参考 Agent Zero 的 Instruments"""
    
    def __init__(self, name: str, func: Callable, description: str = ""):
        self.name = name
        self.func = func
        self.description = description
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行自定义函数"""
        try:
            if asyncio.iscoroutinefunction(self.func):
                result = await self.func(**kwargs)
            else:
                result = self.func(**kwargs)
            
            return ToolResult(
                success=True,
                data={"result": result},
                error=None
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=str(e)
            )


class EnhancedToolManager(ToolManager):
    """
    增强的工具管理器
    参考 Agent Zero 的设计，提供更多功能
    """
    
    def __init__(self):
        super().__init__()
        self.instruments: Dict[str, Instrument] = {}
        self.tool_chains: Dict[str, List[str]] = {}
        self.execution_history: List[Dict] = []
    
    def register_instrument(self, name: str, func: Callable, description: str = ""):
        """注册自定义函数作为工具"""
        instrument = Instrument(name, func, description)
        self.instruments[name] = instrument
        
        # 同时注册到工具实例中
        self.tool_instances[name] = instrument
    
    def unregister_instrument(self, name: str):
        """卸载自定义函数工具"""
        if name in self.instruments:
            del self.instruments[name]
        
        if name in self.tool_instances:
            del self.tool_instances[name]
    
    def create_tool_chain(self, name: str, tools: List[str]):
        """创建工具链"""
        self.tool_chains[name] = tools
    
    async def execute_tool_chain(self, chain_name: str, initial_params: Dict = None) -> List[ToolResult]:
        """执行工具链"""
        if chain_name not in self.tool_chains:
            raise ValueError(f"Tool chain '{chain_name}' not found")
        
        results = []
        params = initial_params or {}
        
        for tool_name in self.tool_chains[chain_name]:
            tool = self.get_tool_instance(tool_name)
            if tool:
                result = await tool.execute(**params)
                results.append(result)
                
                # 将结果作为下一个工具的输入
                if result.success and result.data:
                    params.update(result.data)
        
        return results
    
    async def execute_with_fallback(self, tool_name: str, params: Dict, fallback_tools: List[str] = None):
        """带回退机制的工具执行"""
        # 尝试主要工具
        tool = self.get_tool_instance(tool_name)
        if tool:
            result = await tool.execute(**params)
            if result.success:
                return result
        
        # 尝试回退工具
        if fallback_tools:
            for fallback_tool in fallback_tools:
                tool = self.get_tool_instance(fallback_tool)
                if tool:
                    result = await tool.execute(**params)
                    if result.success:
                        return result
        
        return ToolResult(
            success=False,
            data={},
            error=f"All tools failed: {tool_name} and fallbacks"
        )
    
    def get_execution_history(self) -> List[Dict]:
        """获取执行历史"""
        return self.execution_history.copy()
    
    def clear_execution_history(self):
        """清空执行历史"""
        self.execution_history.clear()
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """获取工具使用统计"""
        stats = {
            "total_tools": len(self.tool_instances),
            "total_instruments": len(self.instruments),
            "total_chains": len(self.tool_chains),
            "tool_categories": {},
            "most_used_tools": []
        }
        
        # 按类别统计
        for tool_name, tool in self.tool_instances.items():
            desc = self.get_tool_description(tool_name)
            if desc:
                category = desc.category.value
                if category not in stats["tool_categories"]:
                    stats["tool_categories"][category] = 0
                stats["tool_categories"][category] += 1
        
        return stats
    
    def export_tool_config(self) -> Dict[str, Any]:
        """导出工具配置"""
        config = {
            "tools": {},
            "instruments": {},
            "chains": self.tool_chains.copy()
        }
        
        # 导出工具描述
        for tool_name, desc in self.get_all_descriptions().items():
            config["tools"][tool_name] = {
                "name": desc.name,
                "category": desc.category.value,
                "description": desc.description,
                "capabilities": desc.capabilities,
                "use_cases": desc.use_cases,
                "parameters": desc.parameters,
                "examples": desc.examples,
                "limitations": desc.limitations
            }
        
        # 导出自定义函数
        for name, instrument in self.instruments.items():
            config["instruments"][name] = {
                "name": instrument.name,
                "description": instrument.description
            }
        
        return config
    
    def import_tool_config(self, config: Dict[str, Any]):
        """导入工具配置"""
        # 导入工具链
        if "chains" in config:
            self.tool_chains.update(config["chains"])
        
        # 导入自定义函数描述
        if "instruments" in config:
            for name, instrument_config in config["instruments"].items():
                # 这里可以重新创建自定义函数
                # 重新创建动态工具的自定义函数
                try:
                    from .dynamic_tool_creator import dynamic_tool_creator
                    
                    # 获取所有动态工具
                    dynamic_tools = dynamic_tool_creator.list_dynamic_tools()
                    
                    for tool_name in dynamic_tools:
                        # 重新创建工具的自定义函数
                        tool_info = dynamic_tool_creator.get_tool_info(tool_name)
                        if tool_info:
                            # 创建新的自定义函数
                            custom_function = self._create_custom_function_from_tool(tool_info)
                            if custom_function:
                                self.custom_functions[tool_name] = custom_function
                                logging.info(f"Recreated custom function for tool: {tool_name}")
                
                except Exception as e:
                    logging.error(f"Failed to recreate custom functions: {e}")
    
    def _create_custom_function_from_tool(self, tool_info) -> Optional[Callable]:
        """从工具信息创建自定义函数"""
        try:
            # 创建动态函数
            def custom_function(**kwargs):
                # 这里可以调用动态工具的执行逻辑
                # 简化实现，返回工具信息
                return {
                    "tool_name": tool_info.name,
                    "description": tool_info.description,
                    "parameters": kwargs,
                    "status": "executed"
                }
            
            return custom_function
            
        except Exception as e:
            logging.error(f"Failed to create custom function: {e}")
            return None
    
    def get_available_tools_summary(self) -> str:
        """获取可用工具摘要"""
        summary = "🛡️ Aegis Agent - Available Tools Summary\n"
        summary += "=" * 50 + "\n\n"
        
        # 工具统计
        stats = self.get_tool_statistics()
        summary += f"📊 Statistics:\n"
        summary += f"   Total Tools: {stats['total_tools']}\n"
        summary += f"   Custom Instruments: {stats['total_instruments']}\n"
        summary += f"   Tool Chains: {stats['total_chains']}\n\n"
        
        # 按类别显示工具
        for category, count in stats["tool_categories"].items():
            summary += f"📂 {category.upper()} ({count} tools):\n"
            for tool_name, tool in self.tool_instances.items():
                desc = self.get_tool_description(tool_name)
                if desc and desc.category.value == category:
                    summary += f"   📦 {tool_name}: {desc.description}\n"
            summary += "\n"
        
        # 显示工具链
        if self.tool_chains:
            summary += "🔗 Tool Chains:\n"
            for chain_name, tools in self.tool_chains.items():
                summary += f"   ⛓️ {chain_name}: {' -> '.join(tools)}\n"
            summary += "\n"
        
        return summary


# 全局增强工具管理器实例
enhanced_tool_manager = EnhancedToolManager() 