"""
Dynamic Tool Creator for Self-Evolving Agent
允许 Agent 在运行时创建自定义工具和函数
"""

import os
import json
import logging
import tempfile
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

from .tool_descriptions import ToolCategory


@dataclass
class DynamicTool:
    """动态创建的工具定义"""
    name: str
    description: str
    code: str
    parameters: Dict[str, Any]
    category: ToolCategory
    created_at: str
    usage_count: int = 0
    success_rate: float = 0.0


class DynamicToolCreator:
    """
    动态工具创建器
    允许 Agent 在运行时创建自定义工具和函数
    """
    
    def __init__(self, tools_dir: str = "python/tools/dynamic"):
        self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        self.dynamic_tools: Dict[str, DynamicTool] = {}
        self.load_existing_tools()
    
    def load_existing_tools(self):
        """加载已存在的动态工具"""
        for tool_file in self.tools_dir.glob("*.py"):
            if tool_file.name.startswith("dynamic_"):
                try:
                    tool_name = tool_file.stem.replace("dynamic_", "")
                    tool_data = self._load_tool_metadata(tool_name)
                    if tool_data:
                        self.dynamic_tools[tool_name] = DynamicTool(**tool_data)
                except Exception as e:
                    logging.warning(f"Failed to load dynamic tool {tool_file.name}: {e}")
    
    def create_tool(self, name: str, description: str, code: str, 
                   parameters: Dict[str, Any], category: ToolCategory = ToolCategory.UTILITY) -> bool:
        """
        创建新的动态工具
        
        Args:
            name: 工具名称
            description: 工具描述
            code: Python 代码
            parameters: 参数定义
            category: 工具类别
            
        Returns:
            bool: 创建是否成功
        """
        try:
            # 验证代码安全性
            if not self._validate_code_safety(code):
                logging.error(f"Code validation failed for tool {name}")
                return False
            
            # 创建工具文件
            tool_file = self.tools_dir / f"dynamic_{name}.py"
            
            # 生成工具代码模板
            tool_code = self._generate_tool_template(name, code, parameters)
            
            # 写入文件
            with open(tool_file, 'w', encoding='utf-8') as f:
                f.write(tool_code)
            
            # 保存元数据
            tool_metadata = DynamicTool(
                name=name,
                description=description,
                code=code,
                parameters=parameters,
                category=category if isinstance(category, ToolCategory) else ToolCategory.UTILITY,
                created_at=self._get_timestamp()
            )
            
            self.dynamic_tools[name] = tool_metadata
            self._save_tool_metadata(name, tool_metadata)
            
            logging.info(f"Created dynamic tool: {name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create tool {name}: {e}")
            return False
    
    async def create_tool_from_spec(self, tool_spec: Dict[str, Any]):
        """
        从规范创建动态工具
        
        Args:
            tool_spec: 工具规范字典
            
        Returns:
            BaseTool: 创建的工具实例或None
        """
        try:
            name = tool_spec.get("name")
            description = tool_spec.get("description", "")
            code = tool_spec.get("code", "")
            parameters = tool_spec.get("parameters", {})
            
            if not name or not code:
                logging.error("Invalid tool spec: missing name or code")
                return None
            
            # 创建工具
            success = self.create_tool(name, description, code, parameters)
            
            if success:
                # 尝试导入并返回工具实例
                try:
                    import importlib.util
                    tool_file = self.tools_dir / f"dynamic_{name}.py"
                    
                    if tool_file.exists():
                        spec = importlib.util.spec_from_file_location(f"dynamic_{name}", tool_file)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # 查找工具类
                        tool_class_name = f"Dynamic{name.capitalize()}Tool"
                        if hasattr(module, tool_class_name):
                            tool_class = getattr(module, tool_class_name)
                            return tool_class()
                        
                        logging.error(f"Tool class {tool_class_name} not found in module")
                        return None
                    else:
                        logging.error(f"Tool file {tool_file} does not exist")
                        return None
                        
                except Exception as e:
                    logging.error(f"Failed to import created tool {name}: {e}")
                    return None
            
            return None
            
        except Exception as e:
            logging.error(f"Failed to create tool from spec: {e}")
            return None
    
    def _generate_tool_template(self, name: str, code: str, parameters: Dict[str, Any]) -> str:
        """生成工具代码模板"""
        template = '''"""
Dynamic Tool: {name}
Auto-generated by Agent
"""

import json
import logging
from typing import Dict, Any
from ...tools.base import BaseTool, ToolResult


class Dynamic{name_capitalized}Tool(BaseTool):
    """Dynamic tool: {name}"""
    
    def __init__(self):
        super().__init__()
        self.name = "{name}"
        self.description = "Dynamic tool created by agent"
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the dynamic tool"""
        try:
            # 参数验证
            validated_params = self._validate_parameters(kwargs)
            
            # 执行动态代码
            result = self._execute_dynamic_code(validated_params)
            
            return ToolResult(
                success=True,
                data={{"result": result}},
                error=None
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data={{}},
                error=str(e)
            )
    
    def _validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证参数"""
        try:
            validated_params = {{}}
            
            for key, value in params.items():
                # 基本类型检查
                if not isinstance(key, str):
                    logging.warning(f"Invalid parameter key type: {{type(key)}}")
                    continue
                
                # 值验证
                if value is None:
                    logging.warning(f"Parameter '{{key}}' is None")
                    continue
                
                # 字符串长度限制
                if isinstance(value, str) and len(value) > 10000:
                    logging.warning(f"Parameter '{{key}}' string too long: {{len(value)}} characters")
                    value = value[:10000] + "..."
                
                # 列表长度限制
                if isinstance(value, list) and len(value) > 1000:
                    logging.warning(f"Parameter '{{key}}' list too long: {{len(value)}} items")
                    value = value[:1000]
                
                # 字典深度限制
                if isinstance(value, dict):
                    value = self._validate_dict_depth(value, max_depth=5)
                
                validated_params[key] = value
            
            return validated_params
            
        except Exception as e:
            logging.error(f"Parameter validation failed: {{e}}")
            return params
    
    def _validate_dict_depth(self, data: Dict[str, Any], max_depth: int = 5, current_depth: int = 0) -> Dict[str, Any]:
        """验证字典深度，防止过深的嵌套"""
        if current_depth >= max_depth:
            logging.warning(f"Dictionary depth limit reached: {{current_depth}}")
            return {{"error": "Dictionary too deep"}}
        
        validated = {{}}
        for key, value in data.items():
            if isinstance(value, dict):
                validated[key] = self._validate_dict_depth(value, max_depth, current_depth + 1)
            else:
                validated[key] = value
        
        return validated
    
    def _execute_dynamic_code(self, params: Dict[str, Any]) -> Any:
        """执行动态代码"""
        # 创建局部变量环境
        local_vars = {{}}
        local_vars.update(params)
        
        # 执行代码
        exec(self.code, {{}}, local_vars)
        
        # 返回结果（假设代码中定义了 result 变量）
        return local_vars.get('result', None)
'''
        return template.format(name=name, name_capitalized=name.capitalize())
    
    def _validate_code_safety(self, code: str) -> bool:
        """验证代码安全性"""
        dangerous_keywords = [
            'import os', 'import sys', 'import subprocess',
            'eval(', 'exec(', '__import__', 'open(',
            'delete', 'remove', 'format', 'shutdown'
        ]
        
        code_lower = code.lower()
        for keyword in dangerous_keywords:
            if keyword in code_lower:
                logging.warning(f"Dangerous keyword found in code: {keyword}")
                return False
        
        return True
    
    def _save_tool_metadata(self, name: str, tool: DynamicTool):
        """保存工具元数据"""
        metadata_file = self.tools_dir / f"{name}_metadata.json"
        metadata = {
            "name": tool.name,
            "description": tool.description,
            "code": tool.code,
            "parameters": tool.parameters,
            "category": tool.category.value,
            "created_at": tool.created_at,
            "usage_count": tool.usage_count,
            "success_rate": tool.success_rate
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _load_tool_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """加载工具元数据"""
        metadata_file = self.tools_dir / f"{name}_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data["category"] = ToolCategory(data["category"])
                return data
        return None
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def list_dynamic_tools(self) -> List[str]:
        """列出所有动态工具"""
        return list(self.dynamic_tools.keys())
    
    def get_tool_info(self, name: str) -> Optional[DynamicTool]:
        """获取工具信息"""
        return self.dynamic_tools.get(name)
    
    def update_tool_usage(self, name: str, success: bool):
        """更新工具使用统计"""
        if name in self.dynamic_tools:
            tool = self.dynamic_tools[name]
            tool.usage_count += 1
            
            # 更新成功率
            if tool.usage_count == 1:
                tool.success_rate = 1.0 if success else 0.0
            else:
                # 简单的移动平均
                current_rate = 1.0 if success else 0.0
                tool.success_rate = (tool.success_rate * (tool.usage_count - 1) + current_rate) / tool.usage_count
            
            self._save_tool_metadata(name, tool)
    
    def delete_tool(self, name: str) -> bool:
        """删除动态工具"""
        try:
            # 删除文件
            tool_file = self.tools_dir / f"dynamic_{name}.py"
            metadata_file = self.tools_dir / f"{name}_metadata.json"
            
            if tool_file.exists():
                tool_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            # 从内存中移除
            if name in self.dynamic_tools:
                del self.dynamic_tools[name]
            
            logging.info(f"Deleted dynamic tool: {name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete dynamic tool {name}: {e}")
            return False
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        total_tools = len(self.dynamic_tools)
        total_usage = sum(tool.usage_count for tool in self.dynamic_tools.values())
        avg_success_rate = sum(tool.success_rate for tool in self.dynamic_tools.values()) / total_tools if total_tools > 0 else 0
        
        return {
            "total_dynamic_tools": total_tools,
            "total_usage": total_usage,
            "average_success_rate": avg_success_rate,
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "usage_count": tool.usage_count,
                    "success_rate": tool.success_rate,
                    "created_at": tool.created_at
                }
                for tool in self.dynamic_tools.values()
            ]
        }


# 全局动态工具创建器实例
dynamic_tool_creator = DynamicToolCreator() 