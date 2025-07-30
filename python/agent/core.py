"""
Agent Core Module
Provides the core Agent class and task execution logic.
"""

import asyncio
import logging
import uuid
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..utils.config_types import AgentConfig
from ..memory.memory_manager import MemoryManager
from ..communication.communication import CommunicationManager
from ..tools.base import BaseTool

class Agent:
    """
    Core Agent class for task execution and tool management.
    
    Features:
    - Task analysis and execution
    - Tool management and execution
    - Memory management
    - Communication with other agents
    """
    
    def __init__(self, config: AgentConfig = None):
        # Load configuration from environment if not provided
        if config is None:
            from ..utils.config import load_config
            config = load_config()
        
        self.config = config
        self.id = str(uuid.uuid4())
        self.current_task = None
        self.tools: Dict[str, BaseTool] = {}
        self.superior = None
        self.subordinates: List['Agent'] = []
        
        # Initialize components
        self.memory = MemoryManager(self.config)
        self.communication = CommunicationManager(self)
        
        # Initialize tools first
        self._initialize_default_tools()
        
        # Initialize dynamic tool creator
        self._initialize_dynamic_tool_creator()
        
        # Load system prompt after tools are initialized
        self.system_prompt = self._load_system_prompt()
        
        logging.info(f"Agent {self.config.name} (ID: {self.id}) initialized")
    
    def _initialize_default_tools(self):
        """Initialize default tools from the tool registry."""
        try:
            from ..tools.json_tool_manager import json_tool_manager
            
            # Load all tools from JSON registry
            loaded_tools = json_tool_manager.load_all_tools()
            self.tools = loaded_tools.copy()
            
            logging.info(f"Initialized {len(self.tools)} tools from JSON registry: {list(self.tools.keys())}")
        except Exception as e:
            logging.error(f"Failed to initialize tools: {e}")
            self.tools = {}
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file or use default."""
        try:
            from pathlib import Path
            prompt_file = Path("prompts/default/agent.system.md")
            if prompt_file.exists():
                return prompt_file.read_text(encoding='utf-8')
        except Exception as e:
            logging.warning(f"Failed to load system prompt: {e}")
        
        return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt with dynamic tool list."""
        # 动态生成工具列表
        tool_list = self._generate_tool_summary_for_llm()
        
        return f"""你是一个智能AI助手，能够执行各种任务。

你可以使用以下工具来完成任务：
{tool_list}

请根据用户的任务需求，选择合适的工具并执行。"""
    
    async def execute_task(self, task_description: str) -> Dict:
        """执行任务"""
        try:
            self.current_task = {"description": task_description}
            logging.info(f"Agent {self.config.name} starting task: {task_description}")
            logging.info(f"Agent {self.config.name} 开始执行任务: {task_description}")
            
            # 分析任务
            logging.info(f"开始分析任务...")
            context = {"task_description": task_description, "agent_id": self.id}
            task_analysis = await self._analyze_task(task_description, context)
            logging.info(f"任务分析完成: {task_analysis.get('task_type', '未知')}")
            
            # 执行任务
            logging.info(f"开始执行任务...")
            result = await self._execute_task_internal(task_analysis)
            
            # 存储结果到内存
            if self.memory:
                await self.memory.store_task_result(task_description, result)
            
            logging.info(f"任务执行完成")
            return result
            
        except Exception as e:
            logging.error(f"Task execution failed: {e}")
            logging.error(f"任务执行失败: {e}")
            return {
                "status": "failed",
                "result": f"任务执行失败: {str(e)}",
                "metadata": {}
            }
    
    async def _analyze_task(self, task_description: str, context: Dict) -> Dict:
        """Analyze task to determine execution strategy."""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            system_prompt = """你是一个任务分析专家，负责分析用户任务并确定最佳执行策略。

请分析任务并返回JSON格式的分析结果：
{
    "description": "任务描述",
    "complexity": "simple|medium|complex",
    "required_tools": ["tool1", "tool2"],
    "execution_plan": "执行计划描述"
}"""
            
            prompt = f"任务：{task_description}\n\n上下文：{context}\n\n请分析此任务："
            
            async with DeepSeekClient() as llm_client:
                response = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3
                )
                
                if response["success"]:
                    # Parse JSON response
                    import json
                    import re
                    
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
                    if json_match:
                        try:
                            analysis = json.loads(json_match.group())
                            return analysis
                        except json.JSONDecodeError:
                            pass
                    
                    # Fallback to simple analysis
                    return {
                        "description": task_description,
                        "complexity": "simple",
                        "required_tools": ["code"],
                        "execution_plan": "直接执行任务"
                    }
                else:
                    return {
                        "description": task_description,
                        "complexity": "simple",
                        "required_tools": ["code"],
                        "execution_plan": "直接执行任务"
                    }
                    
        except Exception as e:
            logging.error(f"Task analysis failed: {e}")
            return {
                "description": task_description,
                "complexity": "simple",
                "required_tools": ["code"],
                "execution_plan": "直接执行任务"
            }
    
    async def _execute_task_internal(self, task_analysis: Dict) -> Dict:
        """内部任务执行逻辑"""
        try:
            task_description = task_analysis.get("task_description", "")
            context = task_analysis.get("context", {})
            
            # 检查是否需要创建新工具
            tool_creation_spec = await self._analyze_tool_creation_need(task_description)
            
            if tool_creation_spec:
                logging.info(f"检测到需要创建新工具: {tool_creation_spec.get('name')}")
                
                # 创建新工具
                creation_result = await self.create_new_tool(tool_creation_spec)
                
                if creation_result["success"]:
                    logging.info(f"新工具创建成功: {creation_result['tool_name']}")
                    # 重新分析任务，使用新创建的工具
                    task_analysis = await self._analyze_task(task_description, context)
                else:
                    logging.warning(f"工具创建失败: {creation_result['error']}")
            
            # Select tools using LLM
            logging.info(f"LLM分析任务: {task_description}")
            await self._send_log_to_frontend(f"LLM分析任务: {task_description}")
            tool_plan = await self._select_tools_with_llm(task_description, task_analysis)
            logging.info(f"执行计划: {tool_plan.get('description', '无描述')}")
            await self._send_log_to_frontend(f"执行计划: {tool_plan.get('description', '无描述')}")
            
            # Execute tools
            results = []
            for i, step in enumerate(tool_plan.get("steps", []), 1):
                tool_name = step.get("tool", "")
                tool_params = step.get("parameters", {})
                reason = step.get("reason", "无原因")
                
                logging.info(f"步骤 {i}: 执行工具 {tool_name}")
                await self._send_log_to_frontend(f"步骤 {i}: 执行工具 {tool_name}")
                logging.info(f"   原因: {reason}")
                await self._send_log_to_frontend(f"   原因: {reason}")
                logging.info(f"   参数: {tool_params}")
                await self._send_log_to_frontend(f"   参数: {tool_params}")
                
                tool = self.get_tool(tool_name)
                if tool:
                    try:
                        logging.info(f"   开始执行...")
                        await self._send_log_to_frontend(f"   开始执行...")
                        tool_result = await tool.execute(**tool_params)
                        
                        # 显示工具输出
                        if tool_result.success:
                            if hasattr(tool_result.data, 'get') and tool_result.data.get('stdout'):
                                output = tool_result.data['stdout']
                                logging.info(f"   执行成功")
                                await self._send_log_to_frontend(f"   执行成功")
                                logging.info(f"   输出: {output[:200]}{'...' if len(output) > 200 else ''}")
                                await self._send_log_to_frontend(f"   输出: {output[:200]}{'...' if len(output) > 200 else ''}")
                            else:
                                logging.info(f"   执行成功")
                                await self._send_log_to_frontend(f"   执行成功")
                        else:
                            logging.info(f"   执行失败: {tool_result.error}")
                            await self._send_log_to_frontend(f"   执行失败: {tool_result.error}")
                        
                        results.append({
                            "tool": tool_name,
                            "result": {
                                "success": tool_result.success,
                                "data": tool_result.data,
                                "error": tool_result.error,
                                "execution_time": tool_result.execution_time
                            },
                            "success": tool_result.success
                        })
                    except Exception as e:
                        error_msg = f"工具 {tool_name} 执行失败: {str(e)}"
                        logging.error(f"   执行异常: {e}")
                        await self._send_log_to_frontend(f"   执行异常: {e}")
                        results.append({
                            "tool": tool_name,
                            "result": {"error": error_msg},
                            "success": False
                        })
                else:
                    error_msg = f"工具 {tool_name} 未找到"
                    logging.error(f"   工具未找到")
                    await self._send_log_to_frontend(f"   工具未找到")
                    results.append({
                        "tool": tool_name,
                        "result": {"error": error_msg},
                        "success": False
                    })
            
            # Generate final result using LLM
            logging.info(f"生成最终结果...")
            await self._send_log_to_frontend(f"生成最终结果...")
            final_result = await self._generate_final_result(task_description, results, tool_plan)
            logging.info(f"最终结果: {final_result[:200]}{'...' if len(final_result) > 200 else ''}")
            await self._send_log_to_frontend(f"最终结果: {final_result[:200]}{'...' if len(final_result) > 200 else ''}")
            
            return {
                "status": "completed",
                "result": final_result,
                "metadata": {
                    "execution_method": "direct",
                    "tool_results": results,
                    "task_analysis": task_analysis
                }
            }
            
        except Exception as e:
            logging.error(f"Task execution failed: {e}")
            logging.error(f"任务执行失败: {e}")
            await self._send_log_to_frontend(f"任务执行失败: {e}")
            return {
                "status": "failed",
                "result": f"任务执行失败: {str(e)}",
                "metadata": task_analysis
            }
    
    async def _select_tools_with_llm(self, task_description: str, task_analysis: Dict) -> Dict:
        """Use LLM to intelligently select tools for task execution."""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            # Get comprehensive tool information from JSON tool manager
            tool_summary = self._generate_tool_summary_for_llm()
            logging.info(f"可用工具: {list(self.tools.keys())}")
            
            system_prompt = f"""你是一个智能任务规划专家，专门为AI智能体服务。

你的工作是分析用户的任务，并从可用的工具注册表中选择最合适的工具。

{tool_summary}

对于每个任务，请仔细分析：
1. 用户想要完成什么
2. 哪些工具有能力帮助
3. 每个选定工具的最佳参数
4. 工具执行的顺序

重要：只回复有效的JSON，不要添加其他文本。只能使用上面列出的工具。

JSON格式：
{{
    "description": "执行计划的简要描述",
    "steps": [
        {{
            "tool": "工具名称",
            "parameters": {{
                "参数名": "参数值"
            }},
            "reason": "选择此工具的原因"
        }}
    ]
}}

可用工具：
{tool_summary}

任务：{task_description}

请分析任务并创建执行计划："""
            
            prompt = f"任务：{task_description}\n\n任务分析：{task_analysis}\n\n创建执行计划："
            
            logging.info(f"调用LLM选择工具...")
            async with DeepSeekClient() as llm_client:
                response = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3
                )
                
                if response["success"]:
                    logging.info(f"LLM响应: {response['content'][:200]}...")
                    # Parse JSON response
                    import json
                    import re
                    
                    # Extract JSON from response
                    json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
                    if json_match:
                        try:
                            tool_plan = json.loads(json_match.group())
                            logging.info(f"成功解析工具计划")
                            return tool_plan
                        except json.JSONDecodeError:
                            logging.info(f"JSON解析失败")
                            pass
                    
                    # Fallback to simple plan
                    logging.warning(f"使用默认工具计划")
                    return {
                        "description": "直接执行任务",
                        "steps": [
                            {
                                "tool": "code",
                                "parameters": {"code": f"# {task_description}\n# 请实现这个任务"},
                                "reason": "使用代码执行工具"
                            }
                        ]
                    }
                else:
                    logging.error(f"LLM调用失败: {response.get('error', '未知错误')}")
                    return {
                        "description": "直接执行任务",
                        "steps": [
                            {
                                "tool": "code",
                                "parameters": {"code": f"# {task_description}\n# 请实现这个任务"},
                                "reason": "使用代码执行工具"
                            }
                        ]
                    }
                    
        except Exception as e:
            logging.error(f"Tool selection failed: {e}")
            logging.error(f"工具选择失败: {e}")
            return {
                "description": "直接执行任务",
                "steps": [
                    {
                        "tool": "code",
                        "parameters": {"code": f"# {task_description}\n# 请实现这个任务"},
                        "reason": "使用代码执行工具"
                    }
                ]
            }
    
    async def _generate_final_result(self, task_description: str, tool_results: List[Dict], tool_plan: Dict) -> str:
        """Generate a final result from tool execution results."""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            system_prompt = """你是一个AI助手，负责将多个工具的结果综合成一个连贯的响应。

你的工作是将工具执行的结果整合成一个清晰、有用的回答。

指导原则：
1. 保持回答简洁明了
2. 突出最重要的信息
3. 如果工具执行失败，解释原因并提供替代方案
4. 使用中文回答
5. 保持专业和友好的语调

请根据工具执行结果生成最终回答。"""
            
            # 构建工具结果摘要
            results_summary = []
            for result in tool_results:
                tool_name = result.get("tool", "未知工具")
                success = result.get("success", False)
                
                if success:
                    tool_result = result.get("result", {})
                    # 处理不同工具的输出格式
                    if isinstance(tool_result, dict):
                        if 'stdout' in tool_result:
                            # code工具的输出
                            output = tool_result['stdout']
                        elif 'data' in tool_result and isinstance(tool_result['data'], dict) and 'stdout' in tool_result['data']:
                            # 嵌套的ToolResult格式
                            output = tool_result['data']['stdout']
                        elif 'output' in tool_result:
                            # 其他工具的输出
                            output = tool_result['output']
                        else:
                            output = str(tool_result)
                    else:
                        output = str(tool_result)
                    
                    results_summary.append(f"- {tool_name}: 成功 - {output}")
                else:
                    error = result.get("result", {}).get("error", "未知错误")
                    results_summary.append(f"- {tool_name}: 失败 - {error}")
            
            prompt = f"""原始任务：{task_description}

工具执行计划：{tool_plan.get('description', '无描述')}

工具执行结果：
{chr(10).join(results_summary)}

请根据以上信息生成最终回答："""
            
            async with DeepSeekClient() as llm_client:
                response = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.7
                )
                
                if response["success"]:
                    return response["content"]
                else:
                    return f"任务执行完成，但生成最终结果时出现错误：{response.get('error', '未知错误')}"
                    
        except Exception as e:
            return f"任务执行完成，但生成最终结果时出现异常：{str(e)}"
    
    def add_tool(self, name: str, tool: BaseTool):
        """Add a custom tool to the agent."""
        self.tools[name] = tool
        logging.info(f"Added tool: {name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name, supporting aliases."""
        # 检查别名
        tool_aliases = {
            "codeexecution": "code",
            "code_execution": "code",
            "python_code": "code",
            "terminal_command": "terminal",
            "shell": "terminal",
            "web_search": "search",
            "tavily_search": "search"
        }
        actual_name = tool_aliases.get(name, name)
        return self.tools.get(actual_name)
    
    def get_status(self) -> Dict:
        """Get agent status."""
        return {
            "id": self.id,
            "name": self.config.name,
            "status": "active",
            "tools_count": len(self.tools),
            "current_task": self.current_task,
            "memory_enabled": self.config.memory_enabled,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_tool_summary_for_llm(self) -> str:
        """Generate a summary of available tools for LLM."""
        tool_descriptions = []
        for name, tool in self.tools.items():
            tool_descriptions.append(f"- {name}: {tool.description}")
        
        return "\n".join(tool_descriptions) 

    async def _send_log_to_frontend(self, message: str, level: str = "info"):
        """向前端发送日志消息"""
        try:
            # 这里需要导入websocket_manager
            from web.main import websocket_manager
            await websocket_manager.broadcast_log(message, level)
        except Exception as e:
            logging.error(f"Failed to send log to frontend: {e}")
    
    def _initialize_dynamic_tool_creator(self):
        """初始化动态工具创建器"""
        try:
            from .dynamic_tool_creator import dynamic_tool_creator
            self.dynamic_tool_creator = dynamic_tool_creator
            
            # 加载已存在的动态工具
            self._load_dynamic_tools()
            
            logging.info("Dynamic tool creator initialized")
        except Exception as e:
            logging.error(f"Failed to initialize dynamic tool creator: {e}")
    
    def _load_dynamic_tools(self):
        """加载动态工具"""
        try:
            dynamic_tools = self.dynamic_tool_creator.list_dynamic_tools()
            for tool_name in dynamic_tools:
                dynamic_tool = self._import_dynamic_tool(tool_name)
                if dynamic_tool:
                    self.add_tool(tool_name, dynamic_tool)
                    logging.info(f"Loaded dynamic tool: {tool_name}")
        except Exception as e:
            logging.error(f"Failed to load dynamic tools: {e}")
    
    def _import_dynamic_tool(self, tool_name: str) -> Optional[BaseTool]:
        """导入动态工具"""
        try:
            import importlib.util
            from pathlib import Path
            
            tool_file = Path("python/tools/dynamic") / f"dynamic_{tool_name}.py"
            if tool_file.exists():
                spec = importlib.util.spec_from_file_location(f"dynamic_{tool_name}", tool_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找工具类
                tool_class_name = f"Dynamic{tool_name.capitalize()}Tool"
                if hasattr(module, tool_class_name):
                    tool_class = getattr(module, tool_class_name)
                    return tool_class()
                
                # 如果没有找到特定类名，查找任何继承自BaseTool的类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseTool) and 
                        attr != BaseTool):
                        return attr()
            
            return None
        except Exception as e:
            logging.error(f"Failed to import dynamic tool {tool_name}: {e}")
            return None
    
    async def _analyze_tool_creation_need(self, task_description: str) -> Optional[Dict[str, Any]]:
        """分析是否需要创建新工具"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            llm_client = DeepSeekClient()
            
            analysis_prompt = f"""
分析以下任务是否需要创建新工具：

任务描述：{task_description}

当前可用工具：
{self._generate_tool_summary_for_llm()}

请判断：
1. 现有工具是否能完成此任务？
2. 是否需要创建新工具？
3. 如果需要，请提供工具规范

返回JSON格式：
{{
    "need_new_tool": true/false,
    "reason": "原因",
    "tool_spec": {{
        "name": "工具名称",
        "description": "工具描述",
        "code": "Python代码",
        "parameters": {{"param1": "类型描述"}}
    }}
}}
"""
            
            response = await llm_client.chat_completion(analysis_prompt)
            
            try:
                analysis_result = json.loads(response)
                
                if analysis_result.get("need_new_tool", False):
                    return analysis_result.get("tool_spec")
                else:
                    return None
                    
            except json.JSONDecodeError:
                logging.error("工具创建需求分析响应格式错误")
                return None
                
        except Exception as e:
            logging.error(f"分析工具创建需求失败: {e}")
            return None
    
    async def create_new_tool(self, tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Agent创建新工具的方法"""
        try:
            logging.info(f"Agent {self.config.name} 开始创建新工具: {tool_spec.get('name', 'unknown')}")
            
            # 使用LLM验证工具规范
            validated_spec = await self._validate_tool_spec_with_llm(tool_spec)
            
            if not validated_spec:
                return {
                    "success": False,
                    "error": "工具规范验证失败"
                }
            
            # 创建工具
            new_tool = await self.dynamic_tool_creator.create_tool_from_spec(validated_spec)
            
            if new_tool:
                # 注册到工具管理器
                self.add_tool(validated_spec["name"], new_tool)
                
                # 重新加载系统提示词以包含新工具
                self.system_prompt = self._load_system_prompt()
                
                logging.info(f"成功创建工具: {validated_spec['name']}")
                return {
                    "success": True,
                    "tool_name": validated_spec["name"],
                    "message": f"工具 {validated_spec['name']} 创建成功"
                }
            else:
                return {
                    "success": False,
                    "error": "工具创建失败"
                }
                
        except Exception as e:
            logging.error(f"创建工具时发生错误: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_tool_spec_with_llm(self, tool_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用LLM验证工具规范"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            llm_client = DeepSeekClient()
            
            validation_prompt = f"""
请验证以下工具规范是否安全、完整和有效：

工具规范：
{json.dumps(tool_spec, ensure_ascii=False, indent=2)}

请检查：
1. 代码安全性（是否包含危险操作）
2. 参数完整性（是否定义了必要的参数）
3. 功能合理性（工具功能是否明确）
4. 命名规范性（工具名称是否合适）

请返回JSON格式的验证结果：
{{
    "is_valid": true/false,
    "validated_spec": {{...}},
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"]
}}
"""
            
            response = await llm_client.chat_completion(validation_prompt)
            
            try:
                validation_result = json.loads(response)
                
                if validation_result.get("is_valid", False):
                    return validation_result.get("validated_spec", tool_spec)
                else:
                    logging.warning(f"工具规范验证失败: {validation_result.get('issues', [])}")
                    return None
                    
            except json.JSONDecodeError:
                logging.error("LLM验证响应格式错误")
                return None
                
        except Exception as e:
            logging.error(f"LLM验证工具规范失败: {e}")
            return None 