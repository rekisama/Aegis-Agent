"""
JSON-based Tool Manager
实现基于JSON配置文件的工具热插拔系统
"""

import json
import logging
import importlib
import inspect
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading

from .base import BaseTool, ToolResult


class ToolStatus(Enum):
    """工具状态枚举"""
    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"
    UNLOADED = "unloaded"


@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    description: str
    class_name: str
    module_path: str
    aliases: List[str] = field(default_factory=list)
    category: str = "general"
    enabled: bool = True
    auto_load: bool = True
    version: str = "1.0.0"
    author: str = "Unknown"
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ToolStatus = ToolStatus.DISCOVERED
    error_message: Optional[str] = None
    last_modified: datetime = field(default_factory=datetime.now)
    instance: Optional[BaseTool] = None


class JSONToolManager:
    """
    基于JSON的工具管理器
    支持热插拔和动态配置
    """
    
    def __init__(self, registry_file: str = "python/tools/tools_registry.json"):
        # 尝试多个可能的路径
        possible_paths = [
            Path(registry_file),  # 当前目录
            Path(__file__).parent / "tools_registry.json",  # 相对于当前文件
            Path(__file__).parent.parent.parent / "python/tools/tools_registry.json",  # 项目根目录
            Path.cwd() / registry_file,  # 当前工作目录
        ]
        
        self.registry_file = None
        for path in possible_paths:
            if path.exists():
                self.registry_file = path
                break
        
        if not self.registry_file:
            # 如果找不到文件，使用第一个路径作为默认值
            self.registry_file = Path(__file__).parent / "tools_registry.json"
            print(f"⚠️ 工具注册文件未找到，使用默认路径: {self.registry_file}")
        
        self.tools: Dict[str, ToolInfo] = {}
        self.loaded_tools: Dict[str, BaseTool] = {}
        self.categories: Dict[str, Dict] = {}
        self.settings: Dict[str, Any] = {}
        
        # 回调函数
        self.on_tool_loaded: List[Callable[[str, BaseTool], None]] = []
        self.on_tool_unloaded: List[Callable[[str], None]] = []
        self.on_tool_error: List[Callable[[str, str], None]] = []
        self.on_registry_updated: List[Callable[[], None]] = []
        
        # 文件监控
        self.watch_enabled = False
        self.watch_thread = None
        self.last_modified = 0
        
        # 初始化
        self._load_registry()
        
        # 启动文件监控
        if self.settings.get("hot_reload", True):
            self.start_file_watching()
    
    def _load_registry(self):
        """加载工具注册表"""
        try:
            if not self.registry_file.exists():
                logging.warning(f"Registry file not found: {self.registry_file}")
                return
            
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载设置
            self.settings = data.get("settings", {})
            self.categories = data.get("categories", {})
            
            # 加载工具信息
            tools_data = data.get("tools", {})
            
            for tool_name, tool_info in tools_data.items():
                try:
                    # 创建ToolInfo对象
                    tool_info_obj = ToolInfo(
                        name=tool_info.get("name", tool_name),
                        description=tool_info.get("description", ""),
                        class_name=tool_info.get("class", ""),
                        module_path=tool_info.get("module", ""),
                        aliases=tool_info.get("aliases", []),
                        category=tool_info.get("category", "general"),
                        enabled=tool_info.get("enabled", True),
                        auto_load=tool_info.get("auto_load", True),
                        version=tool_info.get("version", "1.0.0"),
                        author=tool_info.get("author", "Unknown"),
                        dependencies=tool_info.get("dependencies", []),
                        config_schema=tool_info.get("config_schema", {}),
                        metadata=tool_info.get("metadata", {})
                    )
                    
                    self.tools[tool_name] = tool_info_obj
                    
                except Exception as e:
                    logging.error(f"Failed to load tool {tool_name}: {e}")
                    continue
            
            logging.info(f"Loaded {len(self.tools)} tools from registry")
            
        except Exception as e:
            logging.error(f"Failed to load registry: {e}")
            import traceback
            traceback.print_exc()
    
    def _save_registry(self):
        """保存工具注册表"""
        try:
            data = {
                "tools": {},
                "categories": self.categories,
                "settings": self.settings
            }
            
            for tool_name, tool_info in self.tools.items():
                data["tools"][tool_name] = {
                    "name": tool_info.name,
                    "description": tool_info.description,
                    "class": tool_info.class_name,
                    "module": tool_info.module_path,
                    "aliases": tool_info.aliases,
                    "category": tool_info.category,
                    "enabled": tool_info.enabled,
                    "auto_load": tool_info.auto_load,
                    "version": tool_info.version,
                    "author": tool_info.author,
                    "dependencies": tool_info.dependencies,
                    "config_schema": tool_info.config_schema,
                    "metadata": tool_info.metadata
                }
            
            # 确保目录存在
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Saved registry to {self.registry_file}")
            
        except Exception as e:
            logging.error(f"Failed to save registry: {e}")
    
    def load_tool(self, tool_name: str, config: Dict[str, Any] = None) -> Optional[BaseTool]:
        """加载指定工具"""
        try:
            # 检查是否已加载
            if tool_name in self.loaded_tools:
                return self.loaded_tools[tool_name]
            
            # 获取工具信息
            tool_info = self.tools.get(tool_name)
            if not tool_info:
                logging.error(f"Tool '{tool_name}' not found in registry")
                return None
            
            if not tool_info.enabled:
                logging.warning(f"Tool '{tool_name}' is disabled")
                return None
            
            # 检查依赖
            if not self._check_dependencies(tool_info):
                return None
            
            # 动态导入工具类
            tool_class = self._import_tool_class(tool_info)
            if not tool_class:
                tool_info.status = ToolStatus.ERROR
                tool_info.error_message = f"Failed to import tool class: {tool_info.class_name}"
                return None
            
            # 创建工具实例
            try:
                tool_instance = tool_class(**(config or {}))
                tool_info.instance = tool_instance
                tool_info.status = ToolStatus.LOADED
                
                # 注册工具
                self.loaded_tools[tool_name] = tool_instance
                
                # 通知回调
                for callback in self.on_tool_loaded:
                    try:
                        callback(tool_name, tool_instance)
                    except Exception as e:
                        logging.error(f"Tool loaded callback error: {e}")
                
                logging.info(f"Loaded tool: {tool_name}")
                return tool_instance
                
            except Exception as e:
                tool_info.status = ToolStatus.ERROR
                tool_info.error_message = str(e)
                logging.error(f"Failed to create tool instance '{tool_name}': {e}")
                return None
            
        except Exception as e:
            logging.error(f"Failed to load tool '{tool_name}': {e}")
            return None
    
    def _import_tool_class(self, tool_info: ToolInfo) -> Optional[Type[BaseTool]]:
        """动态导入工具类"""
        try:
            # 导入模块
            module = importlib.import_module(tool_info.module_path)
            
            # 查找工具类
            tool_class = getattr(module, tool_info.class_name, None)
            if not tool_class:
                logging.error(f"Class '{tool_info.class_name}' not found in module '{tool_info.module_path}'")
                return None
            
            # 检查是否是BaseTool的子类
            if not (inspect.isclass(tool_class) and 
                   hasattr(tool_class, '__bases__') and
                   any('BaseTool' in str(base) for base in tool_class.__bases__)):
                logging.error(f"Class '{tool_info.class_name}' is not a BaseTool subclass")
                return None
            
            return tool_class
            
        except Exception as e:
            logging.error(f"Failed to import tool class '{tool_info.class_name}': {e}")
            return None
    
    def _check_dependencies(self, tool_info: ToolInfo) -> bool:
        """检查工具依赖"""
        for dep in tool_info.dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                logging.error(f"Missing dependency '{dep}' for tool '{tool_info.name}'")
                tool_info.status = ToolStatus.ERROR
                tool_info.error_message = f"Missing dependency: {dep}"
                return False
        return True
    
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
                
                # 更新状态
                if tool_name in self.tools:
                    self.tools[tool_name].status = ToolStatus.UNLOADED
                    self.tools[tool_name].instance = None
                
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
        """重新加载工具"""
        try:
            # 先卸载
            self.unload_tool(tool_name)
            
            # 重新加载
            return self.load_tool(tool_name)
            
        except Exception as e:
            logging.error(f"Failed to reload tool '{tool_name}': {e}")
            return None
    
    def load_all_tools(self, config: Dict[str, Any] = None) -> Dict[str, BaseTool]:
        """加载所有启用的工具"""
        loaded_tools = {}
        
        for tool_name, tool_info in self.tools.items():
            if tool_info.enabled and tool_info.auto_load:
                tool = self.load_tool(tool_name, config.get(tool_name, {}) if config else {})
                if tool:
                    loaded_tools[tool_name] = tool
        
        return loaded_tools
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """获取工具实例，支持别名"""
        # 检查别名
        for name, tool_info in self.tools.items():
            if tool_name == name or tool_name in tool_info.aliases:
                return self.loaded_tools.get(name)
        
        return None
    
    def list_available_tools(self) -> List[str]:
        """列出所有可用工具"""
        return list(self.tools.keys())
    
    def list_loaded_tools(self) -> List[str]:
        """列出已加载的工具"""
        return list(self.loaded_tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[ToolInfo]:
        """获取工具信息"""
        return self.tools.get(tool_name)
    
    def enable_tool(self, tool_name: str) -> bool:
        """启用工具"""
        if tool_name in self.tools:
            self.tools[tool_name].enabled = True
            self.tools[tool_name].status = ToolStatus.DISCOVERED
            logging.info(f"Enabled tool: {tool_name}")
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """禁用工具"""
        if tool_name in self.tools:
            self.tools[tool_name].enabled = False
            self.tools[tool_name].status = ToolStatus.DISABLED
            # 如果已加载，则卸载
            if tool_name in self.loaded_tools:
                self.unload_tool(tool_name)
            logging.info(f"Disabled tool: {tool_name}")
            return True
        return False
    
    def add_tool(self, tool_info: ToolInfo) -> bool:
        """添加新工具"""
        try:
            self.tools[tool_info.name] = tool_info
            logging.info(f"Added tool: {tool_info.name}")
            return True
        except Exception as e:
            logging.error(f"Failed to add tool '{tool_info.name}': {e}")
            return False
    
    def remove_tool(self, tool_name: str) -> bool:
        """移除工具"""
        try:
            if tool_name in self.tools:
                # 先卸载
                if tool_name in self.loaded_tools:
                    self.unload_tool(tool_name)
                
                # 移除工具信息
                del self.tools[tool_name]
                logging.info(f"Removed tool: {tool_name}")
                return True
            return False
        except Exception as e:
            logging.error(f"Failed to remove tool '{tool_name}': {e}")
            return False
    
    def start_file_watching(self):
        """开始文件监控"""
        if self.watch_enabled:
            return
        
        self.watch_enabled = True
        self.watch_thread = threading.Thread(target=self._watch_file, daemon=True)
        self.watch_thread.start()
        logging.info("Started file watching for hot reload")
    
    def stop_file_watching(self):
        """停止文件监控"""
        self.watch_enabled = False
        if self.watch_thread:
            self.watch_thread.join(timeout=1)
        logging.info("Stopped file watching")
    
    def _watch_file(self):
        """文件监控线程"""
        while self.watch_enabled:
            try:
                if self.registry_file.exists():
                    current_mtime = self.registry_file.stat().st_mtime
                    if current_mtime > self.last_modified:
                        self.last_modified = current_mtime
                        logging.info("Registry file changed, reloading...")
                        self._load_registry()
                        
                        # 通知回调
                        for callback in self.on_registry_updated:
                            try:
                                callback()
                            except Exception as e:
                                logging.error(f"Registry updated callback error: {e}")
                
                time.sleep(1)  # 检查间隔
                
            except Exception as e:
                logging.error(f"File watching error: {e}")
                time.sleep(5)  # 错误时等待更长时间
    
    def add_tool_loaded_callback(self, callback: Callable[[str, BaseTool], None]):
        """添加工具加载回调"""
        self.on_tool_loaded.append(callback)
    
    def add_tool_unloaded_callback(self, callback: Callable[[str], None]):
        """添加工具卸载回调"""
        self.on_tool_unloaded.append(callback)
    
    def add_tool_error_callback(self, callback: Callable[[str, str], None]):
        """添加工具错误回调"""
        self.on_tool_error.append(callback)
    
    def add_registry_updated_callback(self, callback: Callable[[], None]):
        """添加注册表更新回调"""
        self.on_registry_updated.append(callback)
    
    def cleanup(self):
        """清理资源"""
        # 停止文件监控
        self.stop_file_watching()
        
        # 卸载所有工具
        for tool_name in list(self.loaded_tools.keys()):
            self.unload_tool(tool_name)
        
        logging.info("JSONToolManager cleaned up")


# 全局实例
json_tool_manager = JSONToolManager() 