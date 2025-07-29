"""
Enhanced Tool Executor
结合动态解析和预定义执行的优势
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path

from ..tools.base import BaseTool, ToolResult
from ..tools.plugin_manager import plugin_manager


@dataclass
class ToolCall:
    """工具调用请求"""
    tool_name: str
    method: str = "execute"
    parameters: Dict[str, Any] = None
    reason: str = ""
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class EnhancedToolExecutor:
    """
    增强的工具执行器
    结合动态解析和预定义执行的优势
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.mcp_tools: Dict[str, Any] = {}  # MCP工具
        self.unknown_tool = None
        self._initialize_tools()
    
    def _initialize_tools(self):
        """初始化工具"""
        # 从插件管理器加载工具
        plugin_manager.discover_tools()
        self.tools = plugin_manager.loaded_tools.copy()
        
        # 初始化Unknown工具
        self._init_unknown_tool()
    
    def _init_unknown_tool(self):
        """初始化Unknown工具作为fallback"""
        class UnknownTool(BaseTool):
            def __init__(self):
                super().__init__("unknown", "未知工具")
            
            async def execute(self, **kwargs) -> ToolResult:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Unknown tool: {kwargs.get('tool_name', 'unknown')}"
                )
        
        self.unknown_tool = UnknownTool()
    
    def process_tools(self, llm_response: str) -> List[ToolCall]:
        """
        从LLM响应中解析工具调用
        
        Args:
            llm_response: LLM的响应文本
            
        Returns:
            List[ToolCall]: 解析出的工具调用列表
        """
        tool_calls = []
        
        # 方法1: 解析JSON格式的工具调用
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'\{[^{}]*"tool"[^{}]*\}',
            r'\[[^\[\]]*\{[^{}]*"tool"[^{}]*\}[^\[\]]*\]'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, llm_response, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and "tool" in data:
                        tool_calls.append(self._parse_tool_call(data))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "tool" in item:
                                tool_calls.append(self._parse_tool_call(item))
                except json.JSONDecodeError:
                    continue
        
        # 方法2: 解析 tool:method 格式
        tool_method_pattern = r'(\w+):(\w+)\s*\(([^)]*)\)'
        matches = re.findall(tool_method_pattern, llm_response)
        for tool_name, method, params_str in matches:
            try:
                params = json.loads(f"{{{params_str}}}") if params_str.strip() else {}
                tool_calls.append(ToolCall(
                    tool_name=tool_name,
                    method=method,
                    parameters=params
                ))
            except json.JSONDecodeError:
                # 简单参数解析
                params = {}
                if params_str.strip():
                    for param in params_str.split(','):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            params[key.strip()] = value.strip().strip('"\'')
                
                tool_calls.append(ToolCall(
                    tool_name=tool_name,
                    method=method,
                    parameters=params
                ))
        
        return tool_calls
    
    def _parse_tool_call(self, data: Dict) -> ToolCall:
        """解析单个工具调用"""
        return ToolCall(
            tool_name=data.get("tool", ""),
            method=data.get("method", "execute"),
            parameters=data.get("parameters", {}),
            reason=data.get("reason", "")
        )
    
    def get_tool(self, tool_name: str) -> BaseTool:
        """
        动态获取工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            BaseTool: 工具实例
        """
        # 1. 从本地工具中查找
        if tool_name in self.tools:
            return self.tools[tool_name]
        
        # 2. 从MCP工具中查找
        if tool_name in self.mcp_tools:
            return self.mcp_tools[tool_name]
        
        # 3. 尝试动态加载
        tool = self._load_tool_dynamically(tool_name)
        if tool:
            return tool
        
        # 4. Fallback到Unknown工具
        logging.warning(f"Tool not found: {tool_name}, using unknown tool")
        return self.unknown_tool
    
    def _load_tool_dynamically(self, tool_name: str) -> Optional[BaseTool]:
        """动态加载工具"""
        try:
            # 构建工具文件路径
            tools_dir = Path("python/tools")
            tool_file = tools_dir / f"{tool_name}.py"
            
            if not tool_file.exists():
                return None
            
            # 动态导入工具类
            import importlib.util
            spec = importlib.util.spec_from_file_location(tool_name, tool_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找工具类
            for name, obj in module.__dict__.items():
                if (hasattr(obj, '__bases__') and 
                    any('BaseTool' in str(base) for base in obj.__bases__) and
                    obj.__name__.endswith('Tool')):
                    # 创建工具实例
                    tool_instance = obj()
                    self.tools[tool_name] = tool_instance
                    return tool_instance
            
            return None
            
        except Exception as e:
            logging.error(f"Failed to load tool {tool_name}: {e}")
            return None
    
    async def execute_tool_call(self, tool_call: ToolCall) -> ToolResult:
        """
        执行单个工具调用
        
        Args:
            tool_call: 工具调用请求
            
        Returns:
            ToolResult: 执行结果
        """
        try:
            # 获取工具实例
            tool = self.get_tool(tool_call.tool_name)
            
            # 检查工具是否支持该方法
            if not hasattr(tool, tool_call.method):
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Method {tool_call.method} not found in tool {tool_call.tool_name}"
                )
            
            # 执行工具方法
            method = getattr(tool, tool_call.method)
            
            if tool_call.method == "execute":
                # 标准execute方法
                result = await method(**tool_call.parameters)
                # 确保返回的是ToolResult
                if not isinstance(result, ToolResult):
                    result = ToolResult(
                        success=True,
                        data=result,
                        metadata={"method": tool_call.method}
                    )
            else:
                # 其他方法
                if asyncio.iscoroutinefunction(method):
                    result = await method(**tool_call.parameters)
                else:
                    result = method(**tool_call.parameters)
                
                # 包装结果
                result = ToolResult(
                    success=True,
                    data=result,
                    metadata={"method": tool_call.method}
                )
            
            return result
            
        except Exception as e:
            logging.error(f"Tool execution error: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def execute_tool_calls(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """
        执行多个工具调用
        
        Args:
            tool_calls: 工具调用列表
            
        Returns:
            List[ToolResult]: 执行结果列表
        """
        results = []
        
        for tool_call in tool_calls:
            print(f"🔧 执行工具: {tool_call.tool_name}:{tool_call.method}")
            
            result = await self.execute_tool_call(tool_call)
            results.append(result)
            
            if result.success:
                print(f"✅ {tool_call.tool_name} 执行成功")
            else:
                print(f"❌ {tool_call.tool_name} 执行失败: {result.error}")
            
            # 检查是否需要终止执行
            if hasattr(result, 'terminate_loop') and result.terminate_loop:
                print("🛑 工具请求终止执行")
                break
        
        return results
    
    def add_mcp_tool(self, tool_name: str, tool_instance: Any):
        """添加MCP工具"""
        self.mcp_tools[tool_name] = tool_instance
        logging.info(f"Added MCP tool: {tool_name}")
    
    def get_available_tools(self) -> Dict[str, str]:
        """获取可用工具列表"""
        tools = {}
        
        # 本地工具
        for name, tool in self.tools.items():
            tools[name] = f"Local: {tool.description}"
        
        # MCP工具
        for name, tool in self.mcp_tools.items():
            tools[name] = f"MCP: {getattr(tool, 'description', 'Unknown')}"
        
        return tools


# 全局实例
enhanced_tool_executor = EnhancedToolExecutor() 