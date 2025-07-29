"""
Advanced Plugin Manager for Aegis Agent
实现类似 agent-zero 的插件化工具管理系统
"""

import asyncio
import importlib
import inspect
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .base import BaseTool, ToolResult


class PluginStatus(Enum):
    """插件状态枚举"""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class ToolMetadata:
    """工具元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"
    category: str = "general"
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    status: PluginStatus = PluginStatus.DISCOVERED
    error_message: Optional[str] = None
    last_modified: datetime = field(default_factory=datetime.now)
    enabled: bool = True
    auto_load: bool = True


# 向后兼容性：保持ToolPlugin类
class ToolPlugin:
    """
    Base class for tool plugins.
    All tool plugins should inherit from this class.
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.plugin_info: Optional[ToolMetadata] = None
        self.config: Dict[str, Any] = {}
        
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the plugin with configuration."""
        if config:
            self.config = config
        return True
    
    def cleanup(self):
        """Cleanup plugin resources."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "description": self.description,
            "config": self.config,
            "plugin_info": self.plugin_info.__dict__ if self.plugin_info else None
        }


# 向后兼容性：保持PluginInfo别名
PluginInfo = ToolMetadata


class PluginManager:
    """
    高级插件管理器
    实现自动发现、热插拔、统一接口调用等功能
    """
    
    def __init__(self, tools_dir: str = "python/tools"):
        self.tools_dir = Path(tools_dir)
        self.loaded_tools: Dict[str, BaseTool] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.tool_classes: Dict[str, Type[BaseTool]] = {}
        
        # 工具别名映射
        self.tool_aliases: Dict[str, str] = {
            "codeexecution": "code",
            "code_execution": "code",
            "python_code": "code",
            "terminal_command": "terminal",
            "shell": "terminal",
            "web_search": "search",
            "tavily_search": "search"
        }
        
        # 回调函数
        self.on_tool_loaded: List[Callable[[str, BaseTool], None]] = []
        self.on_tool_unloaded: List[Callable[[str], None]] = []
        self.on_tool_error: List[Callable[[str, str], None]] = []
        
        # 文件监控
        self.file_watchers: Dict[str, float] = {}
        self.watch_enabled = False
        
        logging.info(f"PluginManager initialized with tools directory: {self.tools_dir}")
    
    def discover_tools(self) -> List[ToolMetadata]:
        """自动发现所有可用工具"""
        discovered_tools = []
        
        # 扫描工具目录
        for tool_file in self.tools_dir.rglob("*.py"):
            if tool_file.name.startswith("__"):
                continue
            
            try:
                metadata = self._extract_tool_metadata(tool_file)
                if metadata:
                    discovered_tools.append(metadata)
                    self.tool_metadata[metadata.name] = metadata
                    
            except Exception as e:
                logging.warning(f"Failed to extract metadata from {tool_file}: {e}")
        
        logging.info(f"Discovered {len(discovered_tools)} tools")
        return discovered_tools
    
    # 向后兼容性方法
    def discover_plugins(self) -> List[PluginInfo]:
        """向后兼容：发现插件"""
        return self.discover_tools()
    
    def _extract_tool_metadata(self, tool_file: Path) -> Optional[ToolMetadata]:
        """从工具文件中提取元数据"""
        try:
            # 添加项目根目录到Python路径
            project_root = tool_file.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # 加载模块 - 使用更简单的方法避免importlib作用域问题
            module = None
            
            # 使用更安全的方法提取元数据，避免相对导入问题
            try:
                # 直接解析文件内容，不执行代码
                with open(tool_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 使用AST解析，避免执行代码
                import ast
                
                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    # 如果语法错误，跳过这个文件
                    return None
                
                # 查找类定义
                tool_classes = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # 检查类名是否包含"Tool"
                        if 'Tool' in node.name and node.name != 'BaseTool':
                            # 检查是否有基类
                            if node.bases:
                                tool_classes.append(node.name)
                
                if not tool_classes:
                    return None
                
                # 使用第一个工具类
                tool_class_name = tool_classes[0]
                
                # 使用文件名作为工具名称（去掉.py扩展名）
                tool_name = tool_file.stem
                
                # 提取文档字符串
                description = ""
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == tool_class_name:
                        if node.body and isinstance(node.body[0], ast.Expr):
                            if isinstance(node.body[0].value, ast.Str):
                                description = node.body[0].value.s
                            elif isinstance(node.body[0].value, ast.Constant):
                                description = str(node.body[0].value.value)
                        break
                
                if not description:
                    description = tool_class_name
                
                # 创建元数据
                metadata = ToolMetadata(
                    name=tool_name,
                    description=description,
                    version="1.0.0",
                    author="Unknown",
                    category=self._determine_category(tool_file),
                    last_modified=datetime.fromtimestamp(tool_file.stat().st_mtime)
                )
                
                return metadata
                
            except Exception as e:
                logging.warning(f"Failed to extract metadata from {tool_file}: {e}")
                return None
            
        except Exception as e:
            logging.error(f"Failed to extract metadata from {tool_file}: {e}")
            return None
    
    # 向后兼容性方法
    def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> Optional[ToolPlugin]:
        """向后兼容：加载插件"""
        tool_instance = self.load_tool(plugin_name, config)
        if tool_instance:
            # 创建ToolPlugin适配器
            plugin = ToolPlugin(plugin_name, self.tool_metadata[plugin_name].description)
            plugin.plugin_info = self.tool_metadata[plugin_name]
            plugin.config = config or {}
            return plugin
        return None
    
    def _determine_category(self, tool_file: Path) -> str:
        """确定工具类别"""
        if "dynamic" in tool_file.parts:
            return "dynamic"
        elif tool_file.name in ["terminal.py", "search.py", "code.py", "tavily_search.py"]:
            return "builtin"
        else:
            return "custom"
    
    def load_tool(self, tool_name: str, config: Dict[str, Any] = None) -> Optional[BaseTool]:
        """加载指定工具"""
        try:
            # 检查是否已加载
            if tool_name in self.loaded_tools:
                return self.loaded_tools[tool_name]
            
            # 获取元数据
            metadata = self.tool_metadata.get(tool_name)
            if not metadata:
                # 尝试重新发现
                self.discover_tools()
                metadata = self.tool_metadata.get(tool_name)
            
            if not metadata:
                logging.error(f"Tool '{tool_name}' not found")
                return None
            
            if not metadata.enabled:
                logging.warning(f"Tool '{tool_name}' is disabled")
                return None
            
            # 动态导入工具类
            tool_class = self._import_tool_class(tool_name)
            if not tool_class:
                logging.error(f"Failed to import tool class for '{tool_name}'")
                return None
            
            # 创建工具实例
            tool_instance = tool_class(**(config or {}))
            
            # 注册工具
            self.loaded_tools[tool_name] = tool_instance
            metadata.status = PluginStatus.LOADED
            
            # 通知回调
            for callback in self.on_tool_loaded:
                try:
                    callback(tool_name, tool_instance)
                except Exception as e:
                    logging.error(f"Tool loaded callback error: {e}")
            
            logging.info(f"Loaded tool: {tool_name}")
            return tool_instance
            
        except Exception as e:
            error_msg = f"Failed to load tool '{tool_name}': {e}"
            logging.error(error_msg)
            
            # 更新元数据状态
            if tool_name in self.tool_metadata:
                self.tool_metadata[tool_name].status = PluginStatus.ERROR
                self.tool_metadata[tool_name].error_message = str(e)
            
            # 通知错误回调
            for callback in self.on_tool_error:
                try:
                    callback(tool_name, str(e))
                except Exception as callback_e:
                    logging.error(f"Tool error callback error: {callback_e}")
            
            return None
    
    def _import_tool_class(self, tool_name: str) -> Optional[Type[BaseTool]]:
        """动态导入工具类"""
        try:
            # 根据工具名找到对应的文件
            tool_file = None
            for file_path in self.tools_dir.rglob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                
                # 检查文件名是否匹配工具名
                if tool_name in file_path.stem.lower():
                    tool_file = file_path
                    break
            
            if not tool_file:
                logging.error(f"Tool file not found for '{tool_name}'")
                return None
            
            # 构建模块路径
            relative_path = tool_file.relative_to(self.tools_dir.parent)
            module_path = str(relative_path).replace(os.sep, '.').replace('.py', '')
            
            # 添加项目根目录到Python路径
            project_root = self.tools_dir.parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            # 导入模块
            module = importlib.import_module(module_path)
            
            # 查找工具类
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, '__bases__') and
                    any('BaseTool' in str(base) for base in obj.__bases__) and 
                    obj.__name__ != 'BaseTool' and
                    tool_name in obj.__name__.lower()):
                    return obj
            
            logging.error(f"Tool class not found in module {module_path}")
            return None
            
        except Exception as e:
            logging.error(f"Failed to import tool class for '{tool_name}': {e}")
            return None
    
    def unload_tool(self, tool_name: str) -> bool:
        """卸载指定工具"""
        try:
            if tool_name in self.loaded_tools:
                tool = self.loaded_tools[tool_name]
                
                # 调用清理方法
                if hasattr(tool, 'cleanup'):
                    tool.cleanup()
                
                # 移除工具
                del self.loaded_tools[tool_name]
                
                # 更新元数据
                if tool_name in self.tool_metadata:
                    self.tool_metadata[tool_name].status = PluginStatus.DISCOVERED
                
                # 通知回调
                for callback in self.on_tool_unloaded:
                    try:
                        callback(tool_name)
                    except Exception as e:
                        logging.error(f"Tool unloaded callback error: {e}")
                
                logging.info(f"Unloaded tool: {tool_name}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to unload tool '{tool_name}': {e}")
            return False
    
    def reload_tool(self, tool_name: str) -> Optional[BaseTool]:
        """重新加载工具（热更新）"""
        try:
            # 先卸载
            self.unload_tool(tool_name)
            
            # 重新发现
            self.discover_tools()
            
            # 重新加载
            return self.load_tool(tool_name)
            
        except Exception as e:
            logging.error(f"Failed to reload tool '{tool_name}': {e}")
            return None
    
    def load_all_tools(self, config: Dict[str, Any] = None) -> Dict[str, BaseTool]:
        """加载所有可用工具"""
        # 先发现工具
        self.discover_tools()
        
        # 加载启用的工具
        loaded_tools = {}
        for metadata in self.tool_metadata.values():
            if metadata.enabled and metadata.auto_load:
                tool_config = config.get(metadata.name, {}) if config else {}
                tool = self.load_tool(metadata.name, tool_config)
                if tool:
                    loaded_tools[metadata.name] = tool
        
        # 更新内部状态
        self.loaded_tools.update(loaded_tools)
        
        return loaded_tools
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """获取工具实例，支持别名"""
        # 检查别名
        actual_name = self.tool_aliases.get(tool_name, tool_name)
        return self.loaded_tools.get(actual_name)
    
    def list_available_tools(self) -> List[str]:
        """列出所有可用工具"""
        return list(self.tool_metadata.keys())
    
    def list_loaded_tools(self) -> List[str]:
        """列出已加载的工具"""
        return list(self.loaded_tools.keys())
    
    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """获取工具元数据"""
        return self.tool_metadata.get(tool_name)
    
    # 向后兼容性方法
    def list_available_plugins(self) -> List[str]:
        """向后兼容：列出可用插件"""
        return self.list_available_tools()
    
    def list_plugins(self) -> List[str]:
        """向后兼容：列出插件"""
        return self.list_loaded_tools()
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """向后兼容：获取插件信息"""
        return self.get_tool_metadata(plugin_name)
    
    def get_plugin_status(self, plugin_name: str) -> Optional[PluginStatus]:
        """向后兼容：获取插件状态"""
        metadata = self.get_tool_metadata(plugin_name)
        return metadata.status if metadata else None
    
    def enable_tool(self, tool_name: str) -> bool:
        """启用工具"""
        if tool_name in self.tool_metadata:
            self.tool_metadata[tool_name].enabled = True
            self.tool_metadata[tool_name].status = PluginStatus.DISCOVERED
            logging.info(f"Enabled tool: {tool_name}")
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """禁用工具"""
        if tool_name in self.tool_metadata:
            self.tool_metadata[tool_name].enabled = False
            self.tool_metadata[tool_name].status = PluginStatus.DISABLED
            # 如果已加载，则卸载
            if tool_name in self.loaded_tools:
                self.unload_tool(tool_name)
            logging.info(f"Disabled tool: {tool_name}")
            return True
        return False
    
    # 向后兼容性方法
    def enable_plugin(self, plugin_name: str) -> bool:
        """向后兼容：启用插件"""
        return self.enable_tool(plugin_name)
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """向后兼容：禁用插件"""
        return self.disable_tool(plugin_name)
    
    def add_tool_loaded_callback(self, callback: Callable[[str, BaseTool], None]):
        """添加工具加载回调"""
        self.on_tool_loaded.append(callback)
    
    def add_tool_unloaded_callback(self, callback: Callable[[str], None]):
        """添加工具卸载回调"""
        self.on_tool_unloaded.append(callback)
    
    def add_tool_error_callback(self, callback: Callable[[str, str], None]):
        """添加工具错误回调"""
        self.on_tool_error.append(callback)
    
    # 向后兼容性方法
    def add_plugin_loaded_callback(self, callback: Callable[[str, ToolPlugin], None]):
        """向后兼容：添加插件加载回调"""
        # 转换为工具加载回调
        def tool_callback(tool_name: str, tool: BaseTool):
            plugin = ToolPlugin(tool_name, self.tool_metadata[tool_name].description)
            plugin.plugin_info = self.tool_metadata[tool_name]
            callback(tool_name, plugin)
        self.on_tool_loaded.append(tool_callback)
    
    def add_plugin_unloaded_callback(self, callback: Callable[[str], None]):
        """向后兼容：添加插件卸载回调"""
        self.on_tool_unloaded.append(callback)
    
    # 向后兼容性方法
    def add_tool_registered_callback(self, callback: Callable[[str, BaseTool], None]):
        """向后兼容：添加工具注册回调"""
        # 这个回调在工具加载时触发
        def tool_loaded_callback(tool_name: str, tool: BaseTool):
            callback(tool_name, tool)
        self.on_tool_loaded.append(tool_loaded_callback)
    
    def start_file_watching(self):
        """开始文件监控（热更新）"""
        self.watch_enabled = True
        logging.info("Started file watching for hot reload")
    
    def stop_file_watching(self):
        """停止文件监控"""
        self.watch_enabled = False
        logging.info("Stopped file watching")
    
    def cleanup(self):
        """清理资源"""
        # 卸载所有工具
        for tool_name in list(self.loaded_tools.keys()):
            self.unload_tool(tool_name)
        
        # 停止文件监控
        self.stop_file_watching()
        
        logging.info("PluginManager cleaned up")


# 全局插件管理器实例
plugin_manager = PluginManager()


# 便捷函数
def register_tool(tool_name: str, tool: BaseTool):
    """注册工具实例"""
    plugin_manager.loaded_tools[tool_name] = tool
    logging.info(f"Registered tool: {tool_name}")


def get_tool(tool_name: str) -> Optional[BaseTool]:
    """获取工具实例"""
    return plugin_manager.get_tool(tool_name)


def list_available_tools() -> List[str]:
    """列出所有可用工具"""
    return plugin_manager.list_available_tools()


def list_loaded_tools() -> List[str]:
    """列出已加载的工具"""
    return plugin_manager.list_loaded_tools()


def load_all_tools() -> Dict[str, BaseTool]:
    """加载所有工具"""
    return plugin_manager.load_all_tools()


def reload_tool(tool_name: str) -> Optional[BaseTool]:
    """重新加载工具"""
    return plugin_manager.reload_tool(tool_name) 