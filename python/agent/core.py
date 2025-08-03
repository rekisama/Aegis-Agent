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
    "execution_plan": "执行计划描述",
    "need_new_tool": true/false,
    "tool_creation_spec": {
        "name": "工具名称",
        "description": "工具描述", 
        "code": "纯函数定义代码，不包含交互式输入输出",
        "parameters": {"param1": "类型描述"}
    }
}

重要判断标准：
1. 如果任务明确要求"创建"、"制作"、"开发"、"实现"新工具/功能，则need_new_tool应为true
2. 如果任务需要访问网页URL但现有工具无法处理，则need_new_tool应为true
3. 如果任务需要特定功能但现有工具不包含，则need_new_tool应为true
4. 如果任务只是使用现有工具执行计算或操作，则need_new_tool应为false
5. 如果需要创建新工具，请提供完整的tool_creation_spec
6. 代码应该只包含函数定义，不包含input()、print()等交互式代码
7. 如果不需要创建新工具，tool_creation_spec可以为null

任务类型识别指南：
- 网页访问任务：包含URL、网址、网页、网站等关键词，或直接提供http/https链接
- 搜索任务：包含"搜索"、"查找"、"查询"等关键词，但没有具体URL
- 代码执行任务：包含"运行"、"执行"、"计算"等关键词
- 终端命令任务：包含"命令"、"终端"、"shell"等关键词

URL识别和保留：
- 如果任务描述中包含URL，必须在description中保留完整的URL信息
- 不要将URL替换为"指定网页"、"目标网页"等模糊描述
- 保持URL的完整性和准确性

工具选择指南：
- web_reader: 用于直接访问网页URL并提取内容（标题、文本等）
- search: 用于网络搜索信息，不直接访问特定URL
- code: 用于执行Python代码
- terminal/enhanced_terminal: 用于执行系统命令

工具创建指南：
- 如果任务需要访问网页但web_reader工具不存在，创建web_reader工具
- 如果任务需要特定数据处理但现有工具不支持，创建相应的数据处理工具
- 如果任务需要调用特定API但现有工具不支持，创建API调用工具

当前可用工具：
- web_reader: 获取网页内容并提取信息（标题、文本等）
- code: 执行Python代码
- terminal: 执行终端命令
- search: 网络搜索
- enhanced_terminal: 复杂终端操作"""
            
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
                            logging.info(f"任务分析完成: {analysis.get('description', '未知')}")
                            
                            # 如果分析结果显示需要创建新工具，直接返回工具规范
                            if analysis.get("need_new_tool", False) and analysis.get("tool_creation_spec"):
                                logging.info(f"检测到需要创建新工具: {analysis['tool_creation_spec'].get('name', '未知')}")
                                # 将工具规范存储到上下文中，供后续使用
                                context["tool_creation_spec"] = analysis["tool_creation_spec"]
                            
                            return analysis
                        except json.JSONDecodeError:
                            logging.warning("任务分析JSON解析失败，使用默认分析")
                            pass
                    
                    # Fallback to simple analysis
                    logging.warning("使用默认任务分析")
                    return {
                        "description": task_description,
                        "complexity": "simple",
                        "required_tools": ["code"],
                        "execution_plan": "直接执行任务",
                        "need_new_tool": False,
                        "tool_creation_spec": None
                    }
                else:
                    logging.error(f"任务分析失败: {response.get('error', '未知错误')}")
                    return {
                        "description": task_description,
                        "complexity": "simple",
                        "required_tools": ["code"],
                        "execution_plan": "直接执行任务",
                        "need_new_tool": False,
                        "tool_creation_spec": None
                    }
                
        except Exception as e:
            logging.error(f"Task analysis failed: {e}")
            return {
                "description": task_description,
                "complexity": "simple",
                "required_tools": ["code"],
                "execution_plan": "直接执行任务",
                "need_new_tool": False,
                "tool_creation_spec": None
            }
    
    async def _execute_task_internal(self, task_analysis: Dict) -> Dict:
        """内部任务执行逻辑"""
        try:
            task_description = task_analysis.get("description", "")  # 使用description而不是task_description
            context = task_analysis.get("context", {})
            
            # 检查是否需要创建新工具（从任务分析中获取）
            need_new_tool = task_analysis.get("need_new_tool", False)
            tool_creation_spec = task_analysis.get("tool_creation_spec")
            
            # 如果任务分析中没有工具规范，尝试从上下文中获取
            if not tool_creation_spec and context.get("tool_creation_spec"):
                tool_creation_spec = context["tool_creation_spec"]
                need_new_tool = True
            
            if need_new_tool and tool_creation_spec:
                logging.info(f"检测到需要创建新工具: {tool_creation_spec.get('name')}")
                await self._send_log_to_frontend(f"检测到需要创建新工具: {tool_creation_spec.get('name')}")
                
                # 创建新工具
                creation_result = await self.create_new_tool(tool_creation_spec)
                
                if creation_result["success"]:
                    logging.info(f"新工具创建成功: {creation_result['tool_name']}")
                    await self._send_log_to_frontend(f"新工具创建成功: {creation_result['tool_name']}")
                    
                    # 工具创建成功后，重新分析任务以使用新工具
                    logging.info("重新分析任务以使用新创建的工具...")
                    await self._send_log_to_frontend("重新分析任务以使用新创建的工具...")
                    
                    # 重新分析任务
                    new_context = {"task_description": task_description, "agent_id": self.id}
                    new_task_analysis = await self._analyze_task(task_description, new_context)
                    
                    # 使用新的任务分析结果
                    task_analysis = new_task_analysis
                else:
                    logging.warning(f"工具创建失败: {creation_result['error']}")
                    await self._send_log_to_frontend(f"工具创建失败: {creation_result['error']}")
                    
                    # 如果有验证问题，向用户提供详细信息
                    if "validation_issues" in creation_result:
                        issues = creation_result["validation_issues"]
                        await self._send_log_to_frontend(f"验证问题: {', '.join(issues)}")
                        logging.warning(f"验证问题详情: {issues}")
                    
                    # 尝试使用现有工具完成类似功能
                    await self._send_log_to_frontend("尝试使用现有工具完成类似功能...")
            else:
                logging.info("无需创建新工具，继续执行任务")
            
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
                        
                        # 检查是否需要自动修复代码错误
                        if (tool_name == "code" and not tool_result.success):
                            error_str = str(tool_result.error)
                            
                            # 检测各种类型的错误
                            missing_module = None
                            error_type = None
                            fix_attempted = False
                            
                            # 检测 ModuleNotFoundError
                            module_match = re.search(r"No module named '([^']+)'", error_str)
                            if module_match:
                                missing_module = module_match.group(1)
                                error_type = "ModuleNotFoundError"
                            
                            # 检测 NameError (未定义的名称)
                            name_match = re.search(r"name '([^']+)' is not defined", error_str)
                            if name_match:
                                missing_name = name_match.group(1)
                                # 检查是否是常见的包名
                                common_packages = ['requests', 'pandas', 'numpy', 'matplotlib', 'bs4', 'beautifulsoup4', 'pillow', 'opencv', 'cv2', 'sklearn', 'tensorflow', 'torch', 're', 'json', 'os', 'sys', 'time', 'datetime']
                                if missing_name.lower() in [pkg.lower() for pkg in common_packages]:
                                    missing_module = missing_name
                                    error_type = "NameError"
                            
                            # 检测 ImportError
                            import_match = re.search(r"cannot import name '([^']+)'", error_str)
                            if import_match:
                                missing_import = import_match.group(1)
                                missing_module = missing_import
                                error_type = "ImportError"
                            
                            # 如果检测到缺失模块，尝试安装
                            if missing_module and error_type:
                                logging.info(f"   检测到{error_type}: {missing_module}")
                                await self._send_log_to_frontend(f"   检测到{error_type}: {missing_module}")
                                
                                # 尝试安装缺失的包
                                install_result = await self._try_install_missing_package(missing_module)
                                if install_result["success"]:
                                    logging.info(f"   包安装成功，重新执行代码...")
                                    await self._send_log_to_frontend(f"   包安装成功，重新执行代码...")
                                    
                                    # 重新执行代码
                                    tool_result = await tool.execute(**tool_params)
                                    fix_attempted = True
                                else:
                                    logging.warning(f"   包安装失败: {install_result.get('error', '未知错误')}")
                                    await self._send_log_to_frontend(f"   包安装失败: {install_result.get('error', '未知错误')}")
                            
                            # 如果没有尝试修复或修复失败，尝试自动修复代码
                            if not fix_attempted and not tool_result.success:
                                logging.info(f"   尝试自动修复代码错误...")
                                await self._send_log_to_frontend(f"   尝试自动修复代码错误...")
                                
                                # 尝试自动修复代码
                                fixed_code_result = await self._auto_fix_code_error(tool_params.get('code', ''), error_str)
                                if fixed_code_result["success"]:
                                    logging.info(f"   代码修复成功，重新执行...")
                                    await self._send_log_to_frontend(f"   代码修复成功，重新执行...")
                                    
                                    # 使用修复后的代码重新执行
                                    fixed_tool_params = tool_params.copy()
                                    fixed_tool_params['code'] = fixed_code_result['fixed_code']
                                    tool_result = await tool.execute(**fixed_tool_params)
                                else:
                                    logging.warning(f"   代码修复失败: {fixed_code_result.get('error', '未知错误')}")
                                    await self._send_log_to_frontend(f"   代码修复失败: {fixed_code_result.get('error', '未知错误')}")
                        
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
                            
                            # 如果是代码工具失败，尝试重新分析任务
                            if tool_name == "code" and not tool_result.success:
                                logging.info(f"   代码执行失败，尝试重新分析任务...")
                                await self._send_log_to_frontend(f"   代码执行失败，尝试重新分析任务...")
                                
                                # 重新分析任务，提供错误上下文
                                error_context = {
                                    "task_description": task_description,
                                    "agent_id": self.id,
                                    "failed_step": i,
                                    "error_message": tool_result.error,
                                    "original_code": tool_params.get('code', '')
                                }
                                
                                new_task_analysis = await self._analyze_task_with_error_context(task_description, error_context)
                                if new_task_analysis:
                                    logging.info(f"   重新分析任务完成，生成新的执行计划")
                                    await self._send_log_to_frontend(f"   重新分析任务完成，生成新的执行计划")
                                    
                                    # 使用新的任务分析结果重新执行
                                    return await self._execute_task_internal(new_task_analysis)
                            
                            # 如果是动态工具失败，尝试自动修复工具代码
                            elif tool_name.startswith("dynamic_") and not tool_result.success:
                                logging.info(f"   动态工具执行失败，尝试自动修复工具代码...")
                                await self._send_log_to_frontend(f"   动态工具执行失败，尝试自动修复工具代码...")
                                
                                # 获取工具代码
                                tool = self.get_tool(tool_name)
                                if tool and hasattr(tool, 'code'):
                                    original_code = tool.code
                                    
                                    # 尝试自动修复工具代码
                                    fix_result = await self._auto_fix_tool_code(tool_name, tool_result.error, original_code)
                                    
                                    if fix_result["success"]:
                                        logging.info(f"   工具代码修复成功，更新工具代码...")
                                        await self._send_log_to_frontend(f"   工具代码修复成功，更新工具代码...")
                                        
                                        # 直接更新工具代码
                                        update_result = await self.update_tool_code(tool_name, fix_result["fixed_code"])
                                        if update_result["success"]:
                                            logging.info(f"   工具代码更新成功，重新执行...")
                                            await self._send_log_to_frontend(f"   工具代码更新成功，重新执行...")
                                            
                                            # 重新执行当前步骤
                                            updated_tool = self.get_tool(tool_name)
                                            if updated_tool:
                                                tool_result = await updated_tool.execute(**tool_params)
                                        else:
                                            logging.warning(f"   工具代码更新失败: {update_result.get('error')}")
                                            await self._send_log_to_frontend(f"   工具代码更新失败: {update_result.get('error')}")
                                    else:
                                        logging.warning(f"   工具代码修复失败: {fix_result.get('error')}")
                                        await self._send_log_to_frontend(f"   工具代码修复失败: {fix_result.get('error')}")
                                else:
                                    logging.warning(f"   无法获取工具代码进行修复")
                                    await self._send_log_to_frontend(f"   无法获取工具代码进行修复")
                        
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
                            "result": {
                                "success": False,
                                "error": error_msg
                            },
                            "success": False
                        })
                else:
                    error_msg = f"工具 {tool_name} 不可用"
                    logging.error(f"   工具不可用: {tool_name}")
                    await self._send_log_to_frontend(f"   工具不可用: {tool_name}")
                    
                    results.append({
                        "tool": tool_name,
                        "result": {
                            "success": False,
                            "error": error_msg
                        },
                        "success": False
                    })
            
            # Generate final result
            logging.info(f"生成最终结果...")
            await self._send_log_to_frontend(f"生成最终结果...")
            final_result = await self._generate_final_result(task_description, results, tool_plan)
            
            return {
                "success": any(r.get("success", False) for r in results),
                "result": final_result,
                "tool_results": results
            }
            
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            logging.error(error_msg)
            await self._send_log_to_frontend(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
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

重要指导原则：
1. 如果任务需要Python包但可能缺失，优先使用terminal工具安装包
2. 如果代码执行失败且错误提示缺少模块，使用terminal工具安装相应包
3. 对于系统级操作（安装、配置、文件操作），优先使用terminal工具
4. 对于代码执行和计算任务，使用code工具
5. 对于网络搜索和信息获取，使用search工具
6. 对于直接访问网页URL并提取内容，使用web_reader工具

工具选择策略：
- web_reader: 用于直接访问网页URL并提取内容（标题、文本等）
- terminal: 用于系统命令、包安装、文件操作、环境配置
- code: 用于Python代码执行、计算、数据处理
- search: 用于网络搜索、信息查询
- enhanced_terminal: 用于复杂的终端操作

任务类型识别：
- 网页访问任务：包含URL、网址、网页、网站等关键词，或直接提供http/https链接
- 搜索任务：包含"搜索"、"查找"、"查询"等关键词，但没有具体URL
- 代码执行任务：包含"运行"、"执行"、"计算"等关键词
- 终端命令任务：包含"命令"、"终端"、"shell"等关键词

参数提取指南：
- 对于web_reader工具：必须从任务描述中提取实际的URL，不要使用占位符
- 对于search工具：提取搜索关键词
- 对于code工具：生成相应的代码
- 对于terminal工具：生成相应的命令

URL提取规则：
- 如果任务描述中包含http://或https://开头的URL，直接使用该URL
- 如果任务描述中包含域名（如www.example.com），添加https://前缀
- 不要使用"指定网页URL"、"目标URL"等占位符

对于每个任务，请仔细分析：
1. 用户想要完成什么
2. 是否需要安装依赖包
3. 哪些工具有能力帮助
4. 每个选定工具的最佳参数（特别是URL参数）
5. 工具执行的顺序

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
            from pathlib import Path
            
            self.dynamic_tool_creator = dynamic_tool_creator
            
            # 重新加载已存在的动态工具（确保在正确的工作目录下）
            logging.info("重新加载动态工具...")
            logging.info(f"当前工作目录: {Path.cwd()}")
            logging.info(f"动态工具目录: {self.dynamic_tool_creator.tools_dir}")
            logging.info(f"动态工具目录是否存在: {self.dynamic_tool_creator.tools_dir.exists()}")
            
            # 列出目录中的所有文件
            if self.dynamic_tool_creator.tools_dir.exists():
                logging.info(f"动态工具目录中的文件:")
                for file in self.dynamic_tool_creator.tools_dir.iterdir():
                    logging.info(f"  - {file.name}")
            
            # 重新加载动态工具
            self.dynamic_tool_creator.load_existing_tools()
            
            # 加载动态工具到Agent的工具列表
            self._load_dynamic_tools()
            
            logging.info("Dynamic tool creator initialized")
        except Exception as e:
            logging.error(f"Failed to initialize dynamic tool creator: {e}")
            import traceback
            traceback.print_exc()
    
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
            
            # 使用绝对路径
            project_root = Path(__file__).parent.parent.parent  # 回到项目根目录
            tool_file = project_root / "python/tools/dynamic" / f"dynamic_{tool_name}.py"
            
            logging.info(f"尝试导入动态工具: {tool_name}")
            logging.info(f"工具文件路径: {tool_file}")
            logging.info(f"工具文件是否存在: {tool_file.exists()}")
            
            if tool_file.exists():
                spec = importlib.util.spec_from_file_location(f"dynamic_{tool_name}", tool_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找工具类
                tool_class_name = f"Dynamic{tool_name.capitalize()}Tool"
                if hasattr(module, tool_class_name):
                    tool_class = getattr(module, tool_class_name)
                    logging.info(f"找到工具类: {tool_class_name}")
                    return tool_class()
                
                # 如果没有找到特定类名，查找任何继承自BaseTool的类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseTool) and 
                        attr != BaseTool):
                        logging.info(f"找到工具类: {attr_name}")
                        return attr()
                
                logging.warning(f"在模块中未找到工具类: {tool_name}")
            else:
                logging.warning(f"工具文件不存在: {tool_file}")
            
            return None
        except Exception as e:
            logging.error(f"Failed to import dynamic tool {tool_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _analyze_tool_creation_need(self, task_description: str) -> Optional[Dict[str, Any]]:
        """分析是否需要创建新工具"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            import json
            
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
            
            async with DeepSeekClient() as llm_client:
                response = await llm_client.chat_completion(analysis_prompt)
                
                if response["success"]:
                    try:
                        # 尝试解析JSON响应
                        import re
                        json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
                        if json_match:
                            analysis_result = json.loads(json_match.group())
                            
                            if analysis_result.get("need_new_tool", False):
                                return analysis_result.get("tool_spec")
                            else:
                                return None
                        else:
                            logging.error("工具创建需求分析响应格式错误")
                            return None
                            
                    except json.JSONDecodeError:
                        logging.error("工具创建需求分析JSON解析失败")
                        return None
                else:
                    logging.error(f"工具创建需求分析失败: {response.get('error', '未知错误')}")
                    return None
                
        except Exception as e:
            logging.error(f"分析工具创建需求失败: {e}")
            return None
    
    async def create_new_tool(self, tool_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Agent创建新工具的方法"""
        try:
            logging.info(f"Agent {self.config.name} 开始创建新工具: {tool_spec.get('name', 'unknown')}")
            
            # 使用LLM验证工具规范
            validation_result = await self._validate_tool_spec_with_llm(tool_spec)
            
            if not validation_result:
                return {
                    "success": False,
                    "error": "工具规范验证失败"
                }
            
            # 如果验证失败，尝试基于验证反馈重新生成工具
            if not validation_result.get("is_valid", False):
                logging.info("工具验证失败，尝试基于反馈重新生成...")
                await self._send_log_to_frontend("工具验证失败，正在基于反馈重新生成...")
                
                # 基于验证反馈重新生成工具
                improved_spec = await self._improve_tool_spec_with_feedback(tool_spec, validation_result)
                
                if improved_spec:
                    logging.info("基于验证反馈重新生成工具规范")
                    # 递归调用，验证改进后的规范
                    return await self.create_new_tool(improved_spec)
                else:
                    logging.warning("无法基于验证反馈改进工具规范")
                    return {
                        "success": False,
                        "error": "工具规范验证失败，且无法改进",
                        "validation_issues": validation_result.get("issues", [])
                    }
            
            # 使用验证通过的规范创建工具
            validated_spec = validation_result.get("validated_spec", tool_spec)
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
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"创建工具时发生错误: {e}")
            logging.error(f"详细错误信息: {error_details}")
            return {
                "success": False,
                "error": f"工具创建失败: {str(e)}",
                "details": error_details
            }
    
    async def _validate_tool_spec_with_llm(self, tool_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用LLM验证工具规范"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            import json
            
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
            
            async with DeepSeekClient() as llm_client:
                response = await llm_client.chat_completion(validation_prompt)
                
                if response["success"]:
                    try:
                        # 尝试解析JSON响应
                        import re
                        json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
                        if json_match:
                            validation_result = json.loads(json_match.group())
                            
                            if validation_result.get("is_valid", False):
                                return validation_result
                            else:
                                logging.warning(f"工具规范验证失败: {validation_result.get('issues', [])}")
                                return validation_result
                        else:
                            logging.error("LLM验证响应格式错误")
                            return None
                            
                    except json.JSONDecodeError as e:
                        logging.error(f"LLM验证JSON解析失败: {e}")
                        logging.error(f"原始响应内容: {response['content']}")
                        return None
                else:
                    logging.error(f"LLM验证工具规范失败: {response.get('error', '未知错误')}")
                    return None
                
        except Exception as e:
            logging.error(f"LLM验证工具规范失败: {e}")
            return None
    
    async def _try_install_missing_package(self, package_name: str) -> Dict[str, Any]:
        """尝试安装缺失的包"""
        try:
            logging.info(f"尝试安装包: {package_name}")
            await self._send_log_to_frontend(f"尝试安装包: {package_name}")
            
            # 获取终端工具
            terminal_tool = self.get_tool("terminal")
            if not terminal_tool:
                logging.error("终端工具不可用")
                return {"success": False, "error": "终端工具不可用"}
            
            # 构建安装命令
            install_command = f"pip install {package_name}"
            
            # 执行安装命令
            install_result = await terminal_tool.execute(command=install_command)
            
            if install_result.success:
                logging.info(f"包 {package_name} 安装成功")
                await self._send_log_to_frontend(f"包 {package_name} 安装成功")
                return {"success": True, "message": f"包 {package_name} 安装成功"}
            else:
                logging.error(f"包 {package_name} 安装失败: {install_result.error}")
                await self._send_log_to_frontend(f"包 {package_name} 安装失败: {install_result.error}")
                return {"success": False, "error": f"包安装失败: {install_result.error}"}
                
        except Exception as e:
            logging.error(f"安装包时发生错误: {e}")
            await self._send_log_to_frontend(f"安装包时发生错误: {e}")
            return {"success": False, "error": str(e)} 

    async def _improve_tool_spec_with_feedback(self, original_spec: Dict[str, Any], validation_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """基于验证反馈改进工具规范"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            import json
            
            issues = validation_result.get("issues", [])
            suggestions = validation_result.get("suggestions", [])
            
            improvement_prompt = f"""
你是一个专业的Python代码改进专家。请根据验证反馈改进以下工具规范。

原始工具规范：
{json.dumps(original_spec, ensure_ascii=False, indent=2)}

验证发现的问题：
{json.dumps(issues, ensure_ascii=False, indent=2)}

验证建议：
{json.dumps(suggestions, ensure_ascii=False, indent=2)}

请根据以上反馈，生成改进后的工具规范。重点关注：

1. 代码安全性改进：
   - 添加适当的超时设置
   - 改进异常处理，避免过于宽泛的except
   - 添加输入验证（如URL格式验证）
   - 避免危险操作（如eval、exec等）

2. 参数完整性：
   - 确保所有必要参数都有定义
   - 添加参数类型和默认值

3. 功能合理性：
   - 确保工具功能明确且可实现
   - 添加适当的错误处理

4. 命名规范性：
   - 使用清晰、描述性的名称
   - 遵循Python命名约定

请返回改进后的完整工具规范（JSON格式）：
{{
    "name": "改进后的工具名称",
    "description": "改进后的工具描述",
    "code": "改进后的代码（包含所有必要的导入和安全检查）",
    "parameters": {{"参数名": "参数描述"}}
}}

注意：
- 保持原有功能不变
- 添加必要的安全检查和错误处理
- 确保代码可以直接执行
- 包含所有必要的导入语句
"""
            
            async with DeepSeekClient() as llm_client:
                response = await llm_client.generate_response(
                    prompt=improvement_prompt,
                    temperature=0.3
                )
                
                if response["success"]:
                    # 尝试解析JSON响应
                    import re
                    json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
                    if json_match:
                        try:
                            improved_spec = json.loads(json_match.group())
                            
                            # 验证改进后的规范是否包含必要字段
                            required_fields = ["name", "description", "code"]
                            if all(field in improved_spec for field in required_fields):
                                logging.info(f"成功基于验证反馈改进工具规范: {improved_spec['name']}")
                                return improved_spec
                            else:
                                logging.error("改进后的工具规范缺少必要字段")
                                return None
                                
                        except json.JSONDecodeError as e:
                            logging.error(f"改进工具规范JSON解析失败: {e}")
                            logging.error(f"原始响应内容: {response['content']}")
                            return None
                    else:
                        logging.error("无法从LLM响应中提取JSON")
                        return None
                else:
                    logging.error(f"LLM改进工具规范失败: {response.get('error', '未知错误')}")
                    return None
                    
        except Exception as e:
            logging.error(f"改进工具规范时发生错误: {e}")
            return None 

    async def _auto_fix_code_error(self, original_code: str, error_message: str) -> Dict[str, Any]:
        """自动修复代码错误"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            import json
            
            fix_prompt = f"""
你是一个专业的Python代码修复专家。请根据错误信息修复以下代码。

原始代码：
```python
{original_code}
```

错误信息：
{error_message}

请分析错误原因并修复代码。常见的修复包括：
1. 添加缺失的import语句
2. 修复变量名拼写错误
3. 修复语法错误
4. 添加必要的函数定义
5. 修复缩进问题

请返回修复后的完整代码，确保：
- 包含所有必要的import语句
- 修复所有语法错误
- 保持原有功能不变
- 代码可以直接执行

请只返回修复后的代码，不要包含任何解释或注释。
"""
            
            async with DeepSeekClient() as llm_client:
                response = await llm_client.generate_response(
                    prompt=fix_prompt,
                    temperature=0.2
                )
                
                if response["success"]:
                    # 提取修复后的代码
                    content = response["content"]
                    
                    # 尝试提取代码块
                    import re
                    code_match = re.search(r'```(?:python)?\s*(.*?)\s*```', content, re.DOTALL)
                    if code_match:
                        fixed_code = code_match.group(1)
                    else:
                        # 如果没有代码块，直接使用内容
                        fixed_code = content
                    
                    # 验证修复后的代码是否包含必要的元素
                    if fixed_code and len(fixed_code.strip()) > 0:
                        logging.info(f"代码修复成功")
                        return {
                            "success": True,
                            "fixed_code": fixed_code,
                            "original_error": error_message
                        }
                    else:
                        return {
                            "success": False,
                            "error": "修复后的代码为空"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"LLM修复代码失败: {response.get('error', '未知错误')}"
                    }
                    
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"自动修复代码错误时发生异常: {e}")
            logging.error(f"详细错误信息: {error_details}")
            return {
                "success": False,
                "error": f"自动修复代码错误失败: {str(e)}"
            } 

    async def _auto_fix_tool_code(self, tool_name: str, error_message: str, original_code: str) -> Dict[str, Any]:
        """根据错误自动修改工具代码"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            import json
            
            fix_prompt = f"""
你是一个专业的Python工具代码修复专家。请根据错误信息修复以下工具代码。

工具名称: {tool_name}
原始代码:
```python
{original_code}
```

错误信息:
{error_message}

请分析错误原因并修复工具代码。修复要求：
1. 添加缺失的import语句
2. 修复语法错误
3. 修复变量名或函数名错误
4. 确保工具功能完整可用
5. 保持工具接口不变
6. 添加必要的错误处理

请返回修复后的完整工具代码，确保：
- 包含所有必要的import语句
- 修复所有语法错误
- 保持原有功能不变
- 代码可以直接执行
- 工具接口保持一致

请只返回修复后的代码，不要包含任何解释或注释。
"""
            
            async with DeepSeekClient() as llm_client:
                response = await llm_client.generate_response(
                    prompt=fix_prompt,
                    temperature=0.2
                )
                
                if response["success"]:
                    # 提取修复后的代码
                    content = response["content"]
                    
                    # 尝试提取代码块
                    import re
                    code_match = re.search(r'```(?:python)?\s*(.*?)\s*```', content, re.DOTALL)
                    if code_match:
                        fixed_code = code_match.group(1)
                    else:
                        # 如果没有代码块，直接使用内容
                        fixed_code = content
                    
                    # 验证修复后的代码是否包含必要的元素
                    if fixed_code and len(fixed_code.strip()) > 0:
                        logging.info(f"工具代码修复成功: {tool_name}")
                        return {
                            "success": True,
                            "fixed_code": fixed_code,
                            "original_error": error_message,
                            "tool_name": tool_name
                        }
                    else:
                        return {
                            "success": False,
                            "error": "修复后的代码为空"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"LLM修复工具代码失败: {response.get('error', '未知错误')}"
                    }
                    
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"自动修复工具代码时发生异常: {e}")
            logging.error(f"详细错误信息: {error_details}")
            return {
                "success": False,
                "error": f"自动修复工具代码失败: {str(e)}"
            }
    
    async def _analyze_task_with_error_context(self, task_description: str, error_context: Dict) -> Optional[Dict]:
        """带错误上下文的任务分析"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            system_prompt = """你是一个任务分析专家，负责分析用户任务并确定最佳执行策略。

当前任务执行遇到了错误，请根据错误信息重新分析任务并提供更好的解决方案。

请分析任务并返回JSON格式的分析结果：
{
    "description": "任务描述",
    "complexity": "simple|medium|complex",
    "required_tools": ["tool1", "tool2"],
    "execution_plan": "执行计划描述",
    "need_new_tool": true/false,
    "tool_creation_spec": {
        "name": "工具名称",
        "description": "工具描述", 
        "code": "纯函数定义代码，不包含交互式输入输出",
        "parameters": {"param1": "类型描述"}
    },
    "error_analysis": {
        "error_type": "错误类型",
        "root_cause": "根本原因",
        "suggested_fix": "建议的修复方案"
    }
}

错误分析指南：
1. 分析错误的具体原因（如缺少import、语法错误等）
2. 提供针对性的修复方案
3. 考虑是否需要使用不同的工具或方法
4. 确保修复后的代码包含所有必要的导入和依赖

重要判断标准：
1. 如果任务明确要求"创建"、"制作"、"开发"、"实现"新工具/功能，则need_new_tool应为true
2. 如果任务需要访问网页URL但现有工具无法处理，则need_new_tool应为true
3. 如果任务需要特定功能但现有工具不包含，则need_new_tool应为true
4. 如果任务只是使用现有工具执行计算或操作，则need_new_tool应为false
5. 如果需要创建新工具，请提供完整的tool_creation_spec
6. 代码应该只包含函数定义，不包含input()、print()等交互式代码
7. 如果不需要创建新工具，tool_creation_spec可以为null

当前可用工具：
- web_reader: 获取网页内容并提取信息（标题、文本等）
- code: 执行Python代码
- terminal: 执行终端命令
- search: 网络搜索
- enhanced_terminal: 复杂终端操作"""
            
            error_info = f"""
错误上下文：
- 失败步骤: {error_context.get('failed_step', 'unknown')}
- 错误信息: {error_context.get('error_message', 'unknown')}
- 原始代码: {error_context.get('original_code', 'none')}
"""
            
            prompt = f"任务：{task_description}\n\n{error_info}\n\n请根据错误信息重新分析此任务并提供更好的解决方案："
            
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
                            logging.info(f"带错误上下文的任务分析完成: {analysis.get('description', '未知')}")
                            
                            # 如果分析结果显示需要创建新工具，直接返回工具规范
                            if analysis.get("need_new_tool", False) and analysis.get("tool_creation_spec"):
                                logging.info(f"检测到需要创建新工具: {analysis['tool_creation_spec'].get('name', '未知')}")
                                # 将工具规范存储到上下文中，供后续使用
                                error_context["tool_creation_spec"] = analysis["tool_creation_spec"]
                            
                            return analysis
                        except json.JSONDecodeError:
                            logging.warning("带错误上下文的任务分析JSON解析失败")
                            return None
                    
                    # Fallback to simple analysis
                    logging.warning("使用默认任务分析")
                    return {
                        "description": task_description,
                        "complexity": "simple",
                        "required_tools": ["code"],
                        "execution_plan": "直接执行任务",
                        "need_new_tool": False,
                        "error_analysis": {
                            "error_type": "unknown",
                            "root_cause": "无法解析错误",
                            "suggested_fix": "请手动检查代码"
                        }
                    }
                else:
                    logging.error(f"LLM任务分析失败: {response.get('error', '未知错误')}")
                    return None
                    
        except Exception as e:
            logging.error(f"带错误上下文的任务分析失败: {e}")
            return None 

    async def update_tool_code(self, tool_name: str, new_code: str) -> Dict[str, Any]:
        """更新工具代码"""
        try:
            logging.info(f"Agent {self.config.name} 开始更新工具代码: {tool_name}")
            
            # 检查工具是否存在
            if tool_name not in self.tools:
                return {
                    "success": False,
                    "error": f"工具 {tool_name} 不存在"
                }
            
            # 如果是动态工具，使用动态工具创建器更新
            if tool_name.startswith("dynamic_"):
                # 移除dynamic_前缀
                base_name = tool_name.replace("dynamic_", "")
                
                # 使用动态工具创建器更新代码
                success = self.dynamic_tool_creator.update_tool_code(base_name, new_code)
                
                if success:
                    # 重新加载工具
                    new_tool = await self.dynamic_tool_creator.create_tool_from_spec({
                        "name": base_name,
                        "description": f"更新后的{base_name}工具",
                        "code": new_code,
                        "parameters": {}
                    })
                    
                    if new_tool:
                        # 更新工具注册
                        self.tools[tool_name] = new_tool
                        
                        # 重新加载系统提示词
                        self.system_prompt = self._load_system_prompt()
                        
                        logging.info(f"成功更新工具代码: {tool_name}")
                        return {
                            "success": True,
                            "tool_name": tool_name,
                            "message": f"工具 {tool_name} 代码更新成功"
                        }
                    else:
                        return {
                            "success": False,
                            "error": "工具重新创建失败"
                        }
                else:
                    return {
                        "success": False,
                        "error": "工具代码更新失败"
                    }
            else:
                return {
                    "success": False,
                    "error": f"工具 {tool_name} 不是动态工具，无法更新"
                }
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"更新工具代码时发生错误: {e}")
            logging.error(f"详细错误信息: {error_details}")
            return {
                "success": False,
                "error": f"更新工具代码失败: {str(e)}",
                "details": error_details
            } 