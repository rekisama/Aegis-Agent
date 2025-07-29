"""
Improved Tool System
结合 agent-zero 和我们的 BaseTool 的优点
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ToolStatus(Enum):
    """工具状态枚举"""
    IDLE = "idle"
    EXECUTING = "executing"
    SUCCESS = "success"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class Response:
    """工具执行响应"""
    message: str
    break_loop: bool = False
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class Tool(ABC):
    """
    改进版工具基类
    结合 agent-zero Tool 和我们的 BaseTool 的优点
    """
    
    def __init__(self, 
                 agent: Any = None,
                 name: str = None, 
                 method: str = None,
                 args: Dict[str, str] = None,
                 message: str = "",
                 description: str = None,
                 **kwargs):
        self.agent = agent
        self.name = name or self.__class__.__name__
        self.method = method
        self.args = args or {}
        self.message = message
        self.description = description or "An improved tool"
        
        # 统计信息
        self.created_at = datetime.now()
        self.usage_count = 0
        self.success_count = 0
        self.last_used = None
        self.status = ToolStatus.IDLE
        
        # 日志对象
        self.log = None
        
        logging.info(f"Initialized tool: {self.name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Response:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            Response: 执行结果
        """
        pass
    
    async def before_execution(self, **kwargs):
        """执行前的准备工作"""
        self.status = ToolStatus.EXECUTING
        self.usage_count += 1
        
        # 创建日志对象
        self.log = self._get_log_object()
        
        # 打印执行信息
        if self.agent:
            self._print_execution_info()
        
        logging.info(f"Tool '{self.name}' execution started")
    
    async def after_execution(self, response: Response, **kwargs):
        """执行后的清理工作"""
        self.status = ToolStatus.SUCCESS if response.success else ToolStatus.ERROR
        self.last_used = datetime.now()
        
        if response.success:
            self.success_count += 1
        
        # 更新日志
        if self.log:
            self.log.update(content=response.message)
        
        # 添加到历史记录
        if self.agent and hasattr(self.agent, 'hist_add_tool_result'):
            self.agent.hist_add_tool_result(self.name, response.message)
        
        # 打印响应信息
        if self.agent:
            self._print_response_info(response)
        
        logging.info(f"Tool '{self.name}' execution completed")
    
    def _get_log_object(self):
        """获取日志对象"""
        if not self.agent or not hasattr(self.agent, 'context'):
            return None
        
        heading = f"icon://construction {self.agent.agent_name}: Using tool '{self.name}'"
        if self.method:
            heading += f":{self.method}"
        
        return self.agent.context.log.log(
            type="tool", 
            heading=heading, 
            content="", 
            kvps=self.args
        )
    
    def _print_execution_info(self):
        """打印执行信息"""
        if not self.agent:
            return
        
        print(f"🔧 {self.agent.agent_name}: Using tool '{self.name}'")
        
        if self.args:
            for key, value in self.args.items():
                print(f"   {self._nice_key(key)}: {value}")
    
    def _print_response_info(self, response: Response):
        """打印响应信息"""
        if not self.agent:
            return
        
        print(f"📤 {self.agent.agent_name}: Response from tool '{self.name}'")
        print(f"   {response.message}")
    
    def _nice_key(self, key: str) -> str:
        """美化键名显示"""
        words = key.split('_')
        words = [words[0].capitalize()] + [word.lower() for word in words[1:]]
        return ' '.join(words)
    
    def get_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        return {
            "name": self.name,
            "description": self.description,
            "method": self.method,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "success_rate": self.success_count / max(self.usage_count, 1),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "args": self.args
        }
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        return self.success_count / max(self.usage_count, 1)
    
    def is_available(self) -> bool:
        """检查工具是否可用"""
        return self.status != ToolStatus.DISABLED
    
    def disable(self):
        """禁用工具"""
        self.status = ToolStatus.DISABLED
        logging.info(f"Tool '{self.name}' disabled")
    
    def enable(self):
        """启用工具"""
        self.status = ToolStatus.IDLE
        logging.info(f"Tool '{self.name}' enabled")


# 便捷的包装器函数
async def execute_tool_with_wrapper(tool: Tool, **kwargs) -> Response:
    """使用包装器执行工具"""
    try:
        await tool.before_execution(**kwargs)
        response = await tool.execute(**kwargs)
        await tool.after_execution(response, **kwargs)
        return response
    except Exception as e:
        error_response = Response(
            message=f"Tool execution failed: {str(e)}",
            success=False,
            error=str(e)
        )
        await tool.after_execution(error_response, **kwargs)
        return error_response


# 示例工具实现
class ExampleTool(Tool):
    """示例工具"""
    
    def __init__(self, agent: Any = None):
        super().__init__(
            agent=agent,
            name="example_tool",
            method="demo",
            args={"demo_param": "example_value"},
            message="This is an example tool",
            description="An example tool for demonstration"
        )
    
    async def execute(self, **kwargs) -> Response:
        """执行示例工具"""
        # 模拟执行时间
        await asyncio.sleep(0.1)
        
        return Response(
            message="Example tool executed successfully!",
            data={"result": "success", "timestamp": datetime.now().isoformat()},
            execution_time=0.1
        )


# 兼容性工具（继承自BaseTool的工具可以转换为Tool）
class ToolAdapter(Tool):
    """工具适配器，将BaseTool转换为Tool"""
    
    def __init__(self, base_tool, agent: Any = None):
        self.base_tool = base_tool
        super().__init__(
            agent=agent,
            name=base_tool.name,
            description=base_tool.description
        )
    
    async def execute(self, **kwargs) -> Response:
        """执行基础工具并转换为Response"""
        try:
            result = await self.base_tool.execute(**kwargs)
            
            # 转换ToolResult为Response
            return Response(
                message=str(result.data) if result.data else "Tool executed successfully",
                success=result.success,
                data=result.data,
                error=result.error,
                execution_time=result.execution_time,
                metadata=result.metadata or {}
            )
        except Exception as e:
            return Response(
                message=f"Tool execution failed: {str(e)}",
                success=False,
                error=str(e)
            ) 