"""
Agent Core Module
Provides the core Agent class and task execution logic.
"""

import asyncio
import logging
import uuid
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
        try:
            task_description = self.current_task["description"]
            
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