"""
Enhanced Communication System for Aegis Agent
参考 Agent Zero 的设计，提供实时流式通信功能
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json


class CommunicationEvent:
    """通信事件"""
    
    def __init__(self, event_type: str, data: Any, timestamp: datetime = None):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class StreamHandler:
    """流式处理器"""
    
    def __init__(self):
        self.callbacks: List[Callable] = []
        self.buffer: List[CommunicationEvent] = []
    
    def add_callback(self, callback: Callable):
        """添加回调函数"""
        self.callbacks.append(callback)
    
    async def emit(self, event: CommunicationEvent):
        """发送事件"""
        self.buffer.append(event)
        
        # 异步调用所有回调
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def get_buffer(self) -> List[CommunicationEvent]:
        """获取缓冲区内容"""
        return self.buffer.copy()
    
    def clear_buffer(self):
        """清空缓冲区"""
        self.buffer.clear()


class EnhancedCommunication:
    """
    增强的通信系统
    参考 Agent Zero 的设计，提供实时流式通信
    """
    
    def __init__(self):
        self.superior = None
        self.subordinates: List['EnhancedCommunication'] = []
        self.stream_handler = StreamHandler()
        self.chat_history: List[Dict] = []
        self.settings = {
            "auto_report": True,
            "stream_enabled": True,
            "max_history": 1000
        }
    
    def set_superior(self, superior: 'EnhancedCommunication'):
        """设置上级"""
        self.superior = superior
        if superior:
            superior.subordinates.append(self)
    
    def add_subordinate(self, subordinate: 'EnhancedCommunication'):
        """添加下级"""
        subordinate.set_superior(self)
    
    async def report_to_superior(self, message: str, data: Any = None):
        """向上级报告"""
        if self.superior:
            event = CommunicationEvent("report", {
                "message": message,
                "data": data,
                "from": "subordinate"
            })
            await self.superior.receive_report(event)
    
    async def receive_report(self, event: CommunicationEvent):
        """接收报告"""
        # 记录到历史
        self.chat_history.append({
            "type": "report",
            "content": event.data,
            "timestamp": event.timestamp.isoformat()
        })
        
        # 流式输出
        if self.settings["stream_enabled"]:
            await self.stream_handler.emit(event)
        
        # 限制历史记录数量
        if len(self.chat_history) > self.settings["max_history"]:
            self.chat_history = self.chat_history[-self.settings["max_history"]:]
    
    async def broadcast_to_subordinates(self, message: str, data: Any = None):
        """向下级广播"""
        event = CommunicationEvent("broadcast", {
            "message": message,
            "data": data,
            "from": "superior"
        })
        
        for subordinate in self.subordinates:
            await subordinate.receive_broadcast(event)
    
    async def receive_broadcast(self, event: CommunicationEvent):
        """接收广播"""
        # 记录到历史
        self.chat_history.append({
            "type": "broadcast",
            "content": event.data,
            "timestamp": event.timestamp.isoformat()
        })
        
        # 流式输出
        if self.settings["stream_enabled"]:
            await self.stream_handler.emit(event)
    
    async def stream_message(self, message: str, message_type: str = "info"):
        """流式发送消息"""
        event = CommunicationEvent("stream", {
            "message": message,
            "type": message_type
        })
        
        await self.stream_handler.emit(event)
        
        # 记录到历史
        self.chat_history.append({
            "type": "stream",
            "content": {"message": message, "type": message_type},
            "timestamp": event.timestamp.isoformat()
        })
    
    async def stream_progress(self, task: str, progress: float, details: str = ""):
        """流式发送进度"""
        event = CommunicationEvent("progress", {
            "task": task,
            "progress": progress,
            "details": details
        })
        
        await self.stream_handler.emit(event)
    
    async def stream_tool_execution(self, tool_name: str, params: Dict, result: Any):
        """流式发送工具执行结果"""
        event = CommunicationEvent("tool_execution", {
            "tool": tool_name,
            "parameters": params,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        await self.stream_handler.emit(event)
    
    def add_stream_callback(self, callback: Callable):
        """添加流式回调"""
        self.stream_handler.add_callback(callback)
    
    def get_chat_history(self) -> List[Dict]:
        """获取聊天历史"""
        return self.chat_history.copy()
    
    def clear_chat_history(self):
        """清空聊天历史"""
        self.chat_history.clear()
    
    def update_settings(self, settings: Dict[str, Any]):
        """更新设置"""
        self.settings.update(settings)
    
    def get_communication_summary(self) -> Dict[str, Any]:
        """获取通信摘要"""
        return {
            "superior": self.superior is not None,
            "subordinates_count": len(self.subordinates),
            "chat_history_count": len(self.chat_history),
            "settings": self.settings.copy(),
            "stream_callbacks_count": len(self.stream_handler.callbacks)
        }
    
    async def export_communication_data(self) -> Dict[str, Any]:
        """导出通信数据"""
        return {
            "chat_history": self.chat_history,
            "settings": self.settings,
            "summary": self.get_communication_summary()
        }
    
    async def import_communication_data(self, data: Dict[str, Any]):
        """导入通信数据"""
        if "chat_history" in data:
            self.chat_history = data["chat_history"]
        
        if "settings" in data:
            self.settings.update(data["settings"])


# 全局增强通信实例
enhanced_communication = EnhancedCommunication() 