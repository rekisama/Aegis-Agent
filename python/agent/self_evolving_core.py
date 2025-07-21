"""
Self-Evolving Agent Core
自进化 Agent 核心，集成动态工具创建、自适应学习和自我反思
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from .core import Agent, AgentConfig
from .dynamic_tool_creator import dynamic_tool_creator
from .adaptive_learning import adaptive_learning, LearningExperience
from .self_reflection import self_reflection


@dataclass
class EvolutionMetrics:
    """进化指标"""
    total_tasks: int
    success_rate: float
    average_execution_time: float
    tools_created: int
    learning_sessions: int
    improvement_score: float


class TaskAnalyzer:
    """统一的任务分析工具类"""
    
    @staticmethod
    async def analyze_task(task_description: str, analysis_type: str = "tool_creation") -> Dict[str, Any]:
        """统一的任务分析方法"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            async with DeepSeekClient() as llm_client:
                if analysis_type == "tool_creation":
                    system_prompt = """You are an intelligent task analyzer. Your job is to analyze tasks and determine if a specialized tool should be created to better handle this type of task.

ANALYSIS CRITERIA:
1. Does this task require specialized functionality not covered by existing tools?
2. Would a dedicated tool provide more accurate and reliable results than generic tools?
3. Is this a recurring type of task that would benefit from a specialized tool?
4. Are there existing tools that can handle this, or would a new tool be more appropriate?

IMPORTANT CONSIDERATIONS:
- Real-time data requirements (time, weather, currency, etc.)
- Accuracy and reliability needs
- Complexity that existing tools can't handle well
- Repetitive tasks that would benefit from automation
- Tasks requiring specific APIs or services

Think carefully about each task and make your own judgment. Do not rely on predefined patterns.

Respond in JSON format:
{
    "should_create_tool": true/false,
    "tool_name": "suggested_name",
    "tool_description": "description",
    "tool_parameters": {"param1": {"type": "string", "required": true}},
    "implementation_approach": "brief description",
    "reasoning": "explanation for the decision",
    "existing_tools_analysis": "analysis of why existing tools are insufficient"
}"""
                elif analysis_type == "task_type":
                    system_prompt = """You are a task analysis expert. Analyze the given task and determine the most appropriate task type.

Consider the task content, context, and requirements to classify it appropriately. You can use any descriptive category that best fits the task.

Examples of task types:
- time: Time-related queries, timezone conversions, current time
- weather: Weather information, climate data
- calculation: Mathematical computations, data processing
- search: Information retrieval, web search, finding data
- system: Operating system operations, file management
- programming: Code execution, software development
- communication: Text processing, language analysis
- utility: General utility tasks, data formatting
- analysis: Data analysis, pattern recognition
- custom: Specialized tasks requiring custom tools

Respond with ONLY the task type, no additional text. Use the most specific and appropriate category."""
                else:
                    system_prompt = """Analyze if this task needs a specialized tool. Respond with ONLY a JSON object:

{
    "should_create_tool": true/false,
    "tool_name": "name",
    "tool_description": "description", 
    "tool_parameters": {"param": {"type": "string", "required": true}},
    "implementation_approach": "approach",
    "reasoning": "reason"
}"""

                prompt = f"Analyze this task: {task_description}"

                result = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=500
                )
                
                if result["success"]:
                    return TaskAnalyzer._parse_llm_response(result["content"], analysis_type)
                else:
                    logging.warning(f"Task analysis failed for type: {analysis_type}")
                    return TaskAnalyzer._get_default_response(analysis_type)
                    
        except Exception as e:
            logging.error(f"Task analysis failed: {e}")
            return TaskAnalyzer._get_default_response(analysis_type)
    
    @staticmethod
    def _parse_llm_response(content: str, analysis_type: str) -> Dict[str, Any]:
        """解析 LLM 响应"""
        try:
            import json
            content = content.strip()
            
            # 清理可能的 markdown 代码块格式
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            if analysis_type == "task_type":
                # 任务类型分析返回字符串 - 让 LLM 完全自主判断
                category = content.lower().strip()
                if category:
                    return {"task_type": category}
                else:
                    logging.warning("Empty task category, using 'general'")
                    return {"task_type": "general"}
            else:
                # 工具创建分析返回 JSON
                analysis = json.loads(content)
                logging.info(f"Task analysis result: {analysis}")
                return analysis
                
        except json.JSONDecodeError as e:
            logging.warning(f"Failed to parse LLM response: {e}")
            logging.warning(f"Raw content: {content}")
            return TaskAnalyzer._get_default_response(analysis_type)
    
    @staticmethod
    def _get_default_response(analysis_type: str) -> Dict[str, Any]:
        """获取默认响应"""
        if analysis_type == "task_type":
            return {"task_type": "general"}
        else:
            return {"should_create_tool": False}


class ToolCreationManager:
    """统一的工具创建管理器"""
    
    @staticmethod
    async def create_tool_from_analysis(analysis: Dict[str, Any], agent) -> bool:
        """根据分析结果创建工具"""
        try:
            tool_name = analysis.get("tool_name", "")
            tool_description = analysis.get("tool_description", "")
            tool_parameters = analysis.get("tool_parameters", {})
            implementation_approach = analysis.get("implementation_approach", "")
            
            if not tool_name or not tool_description:
                logging.warning("Invalid tool analysis data")
                return False
            
            # 生成工具代码
            tool_code = await agent._generate_tool_code(
                tool_name, tool_description, tool_parameters, implementation_approach
            )
            
            # 创建动态工具
            success = await agent.create_dynamic_tool(
                tool_name, tool_description, tool_code, tool_parameters
            )
            
            if success:
                logging.info(f"Successfully created dynamic tool: {tool_name}")
                print(f"🛠️  Created specialized tool: {tool_name}")
                print(f"📝 Description: {tool_description}")
                print(f"💡 Approach: {implementation_approach}")
            else:
                logging.warning(f"Failed to create dynamic tool: {tool_name}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to create tool from analysis: {e}")
            return False


class SelfEvolvingAgent(Agent):
    """
    自进化 Agent
    具备动态工具创建、自适应学习和自我反思能力
    """
    
    def __init__(self, config: AgentConfig = None):
        super().__init__(config)
        self.evolution_enabled = True
        self.learning_enabled = True
        self.reflection_enabled = True
        self.evolution_metrics = EvolutionMetrics(0, 0.0, 0.0, 0, 0, 0.0)
        
        # 初始化自进化组件
        self._init_evolution_components()
        
        logging.info(f"Self-evolving agent {self.config.name} initialized")
    
    def _init_evolution_components(self):
        """初始化自进化组件"""
        # 加载动态工具
        dynamic_tools = dynamic_tool_creator.list_dynamic_tools()
        for tool_name in dynamic_tools:
            # 这里可以动态加载工具到 Agent 的工具集
            logging.info(f"Loaded dynamic tool: {tool_name}")
    
    async def execute_task(self, task_description: str) -> Dict[str, Any]:
        """执行任务"""
        try:
            logging.info(f"🛡️  {self.config.name} > task <{task_description}>")
            
            # 使用统一的任务分析工具
            tool_analysis = await TaskAnalyzer.analyze_task(task_description, "tool_creation")
            
            if tool_analysis.get("should_create_tool", False):
                logging.info(f"🔧 Task analysis suggests creating specialized tool: {tool_analysis.get('tool_name', 'unknown')}")
                
                # 使用统一的工具创建管理器
                tool_created = await ToolCreationManager.create_tool_from_analysis(tool_analysis, self)
                
                if tool_created:
                    logging.info(f"✅ Successfully created specialized tool: {tool_analysis.get('tool_name', 'unknown')}")
                    print(f"🛠️  Created specialized tool: {tool_analysis.get('tool_name', 'unknown')}")
                    print(f"📝 Description: {tool_analysis.get('tool_description', 'N/A')}")
                    print(f"💡 Reasoning: {tool_analysis.get('reasoning', 'N/A')}")
                    
                    # 重新加载工具集以包含新创建的工具
                    await self._reload_tools()
                    
                    # 使用新创建的工具重新执行任务
                    logging.info("🔄 Re-executing task with newly created tool")
                    return await super().execute_task(task_description)
                else:
                    logging.warning("❌ Failed to create specialized tool, proceeding with existing tools")
            
            # 继续执行任务
            return await super().execute_task(task_description)
            
        except Exception as e:
            logging.error(f"Task execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _reload_tools(self):
        """重新加载工具集"""
        try:
            from ..tools.dynamic_tool_creator import dynamic_tool_creator
            
            # 获取最新的动态工具
            dynamic_tools = dynamic_tool_creator.list_dynamic_tools()
            
            # 重新注册动态工具到 Agent 的工具集
            for tool_name in dynamic_tools:
                if tool_name not in self.tools:
                    tool_info = dynamic_tool_creator.get_tool_info(tool_name)
                    if tool_info:
                        # 动态导入并创建工具实例
                        try:
                            # 导入动态工具模块
                            module_name = f"python.tools.dynamic.dynamic_{tool_name}"
                            import importlib
                            module = importlib.import_module(module_name)
                            
                            # 获取工具类
                            tool_class = getattr(module, f"{tool_name.capitalize()}Tool", None)
                            if tool_class:
                                # 创建工具实例并添加到 Agent
                                tool_instance = tool_class()
                                self.add_tool(tool_name, tool_instance)
                                logging.info(f"Successfully reloaded dynamic tool: {tool_name}")
                            else:
                                logging.warning(f"Tool class not found for: {tool_name}")
                                
                        except ImportError as e:
                            logging.warning(f"Failed to import dynamic tool {tool_name}: {e}")
                        except Exception as e:
                            logging.error(f"Failed to create tool instance for {tool_name}: {e}")
                        
        except Exception as e:
            logging.error(f"Failed to reload tools: {e}")
    
    async def _record_learning_experience(self, task_id: str, task_description: str, 
                                        result: Dict, execution_time: float, 
                                        recommendations: Dict):
        """记录学习经验"""
        try:
            # 使用统一的任务分析工具
            task_analysis = await TaskAnalyzer.analyze_task(task_description, "task_type")
            task_type = task_analysis.get("task_type", "general")
            
            # 提取使用的工具
            tools_used = []
            if "metadata" in result and "tool_results" in result["metadata"]:
                tools_used = [r["tool"] for r in result["metadata"]["tool_results"]]
            
            # 计算成功率
            success = result.get("status") == "completed"
            
            # 计算结果质量
            result_quality = await self._calculate_result_quality(result)
            
            # 创建学习经验
            experience = LearningExperience(
                task_id=task_id,
                task_description=task_description,
                task_type=task_type,
                tools_used=tools_used,
                success=success,
                execution_time=execution_time,
                result_quality=result_quality
            )
            
            # 记录到学习系统
            adaptive_learning.record_experience(experience)
            
            logging.info(f"Recorded learning experience for task: {task_id}")
            
        except Exception as e:
            logging.error(f"Failed to record learning experience: {e}")
    
    async def _perform_self_reflection(self, task_id: str, task_description: str, result: Dict):
        """执行自我反思"""
        try:
            # 创建执行摘要
            execution_summary = {
                "status": result.get("status"),
                "success": result.get("status") == "completed",
                "execution_time": result.get("metadata", {}).get("execution_time", 0),
                "tools_used": result.get("metadata", {}).get("tool_results", []),
                "result_quality": await self._calculate_result_quality(result)
            }
            
            # 执行反思
            reflection_result = await self_reflection.analyze_performance(
                task_id, task_description, execution_summary
            )
            
            logging.info(f"Self-reflection completed for task: {task_id}")
            
            # 如果反思建议创建新工具，执行工具创建
            await self._handle_reflection_suggestions(reflection_result)
            
        except Exception as e:
            logging.error(f"Self-reflection failed: {e}")
    
    async def _handle_reflection_suggestions(self, reflection_result: Dict):
        """处理反思建议"""
        try:
            suggestions = reflection_result.get("suggestions", [])
            
            for suggestion in suggestions:
                if "创建工具" in suggestion or "create tool" in suggestion.lower():
                    # 使用统一的任务分析工具
                    analysis = await TaskAnalyzer.analyze_task(suggestion, "tool_creation")
                    
                    if analysis.get("should_create_tool", False):
                        # 使用统一的工具创建管理器
                        tool_created = await ToolCreationManager.create_tool_from_analysis(analysis, self)
                        
                        if tool_created:
                            logging.info(f"Created tool based on reflection suggestion: {analysis.get('tool_name', 'unknown')}")
                        else:
                            logging.warning("Failed to create tool based on reflection suggestion")
                    
        except Exception as e:
            logging.error(f"Failed to handle reflection suggestions: {e}")
    
    async def _generate_tool_code(self, tool_name: str, tool_description: str, 
                                 parameters: Dict[str, Any], approach: str) -> str:
        """使用 LLM 生成工具代码"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            async with DeepSeekClient() as llm_client:
                system_prompt = """You are a Python code generation expert. Generate safe and functional Python code for a custom tool based on the tool description and implementation approach.

SECURITY REQUIREMENTS:
1. NEVER use os.system, subprocess, eval, exec, or __import__
2. NEVER access the file system directly unless explicitly required
3. NEVER make network requests unless explicitly needed
4. Use safe alternatives for any potentially dangerous operations
5. Always validate and sanitize input parameters
6. Use try-catch blocks for error handling
7. Keep operations within the scope of the tool's purpose

CODE REQUIREMENTS:
1. Access parameters using params.get('param_name', default_value)
2. Process the parameters according to the tool description
3. Return the result in a variable called 'result'
4. Include proper error handling
5. Add comments explaining the logic
6. Keep the code focused and efficient
7. Use appropriate libraries for the specific functionality needed

IMPLEMENTATION GUIDELINES:
- For time-related tools: Use datetime and pytz libraries
- For weather tools: Use weather APIs or services
- For calculation tools: Use math, numpy, or other calculation libraries
- For data processing: Use pandas, json, or other data libraries
- For text processing: Use string operations, re, or nltk
- For API calls: Use requests library with proper error handling

Generate only the core logic code, not the full class structure. Focus on the specific functionality described in the tool description."""

                prompt = f"""Tool Name: {tool_name}
Tool Description: {tool_description}
Parameters: {parameters}
Implementation Approach: {approach}

Generate safe Python code for this tool. The code should:
1. Access parameters using params.get('param_name', default_value)
2. Process the parameters according to the tool description
3. Return the result in a variable called 'result'
4. Include proper error handling and input validation
5. Use appropriate libraries for the specific functionality
6. Follow the implementation approach provided

Generate only the core logic:"""

                result = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.2,
                    max_tokens=600
                )
                
                if result["success"]:
                    code = result["content"].strip()
                    
                    # 验证代码安全性
                    if await self._validate_generated_code(code):
                        return code
                    else:
                        logging.warning("Generated code failed security validation, using fallback")
                        return self._generate_fallback_code(tool_name, parameters)
                else:
                    logging.warning("LLM code generation failed, using fallback")
                    return self._generate_fallback_code(tool_name, parameters)
                    
        except Exception as e:
            logging.error(f"Code generation failed: {e}")
            return self._generate_fallback_code(tool_name, parameters)
    
    async def _validate_generated_code(self, code: str) -> bool:
        """使用 LLM 验证生成的代码安全性"""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            async with DeepSeekClient() as llm_client:
                system_prompt = """You are a code security expert. Analyze the given Python code for security risks.

Consider the following security aspects:
1. File system access (file operations, directory traversal)
2. System command execution (subprocess, os.system)
3. Code injection (eval, exec, __import__)
4. Network access (sockets, HTTP requests)
5. Resource exhaustion (infinite loops, large memory usage)
6. Data privacy (logging sensitive information)

Evaluate if the code is safe to execute in a controlled environment.
Focus on actual security risks, not just the presence of certain keywords.

Respond with ONLY 'SAFE' or 'UNSAFE' followed by a brief reason."""

                prompt = f"""Analyze this Python code for security:

```python
{code}
```

Is this code safe to execute? Consider the context that this is a tool that will be executed with user-provided parameters."""

                result = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.1,
                    max_tokens=100
                )
                
                if result["success"]:
                    response = result["content"].strip().upper()
                    if response.startswith("SAFE"):
                        return True
                    elif response.startswith("UNSAFE"):
                        logging.warning(f"Code security validation failed: {response}")
                        return False
                    else:
                        # 如果 LLM 响应不明确，进行保守判断
                        logging.warning(f"Unclear LLM response: {response}")
                        return False
                else:
                    logging.warning("LLM validation failed, using basic check")
                    return self._basic_security_check(code)
                    
        except Exception as e:
            logging.error(f"Code security validation failed: {e}")
            # 如果 LLM 验证失败，进行基本的保守检查
            return self._basic_security_check(code)
    
    def _basic_security_check(self, code: str) -> bool:
        """基本的保守安全检查"""
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess',
            'eval(', 'exec(', '__import__', 'open(',
            'delete', 'remove', 'format', 'shutdown',
            'rm -rf', 'del ', 'os.system', 'subprocess.call'
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                logging.warning(f"Basic security check: Dangerous pattern found: {pattern}")
                return False
        
        return True
    
    def _generate_fallback_code(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """生成回退代码"""
        param_names = list(parameters.keys())
        if param_names:
            param_name = param_names[0]
            return f"""
# Fallback code for {tool_name}
{param_name} = params.get('{param_name}', '')
result = f"Processed {param_name}: {{len({param_name})}} characters"
"""
        else:
            return f"""
# Fallback code for {tool_name}
result = "Tool {tool_name} executed successfully"
"""
    
    async def _calculate_result_quality(self, result: Dict) -> float:
        """使用 LLM 计算结果质量"""
        if result.get("status") != "completed":
            return 0.0
        
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            result_content = result.get("result", "")
            if not result_content:
                return 0.0
            
            async with DeepSeekClient() as llm_client:
                system_prompt = """You are a quality assessment expert. Evaluate the quality of a task execution result.

Consider the following factors:
1. Completeness - Does the result fully address the task?
2. Accuracy - Is the information correct and reliable?
3. Clarity - Is the result clear and well-formatted?
4. Usefulness - Does the result provide value to the user?

Rate the quality on a scale of 0.0 to 1.0, where:
- 0.0-0.3: Poor quality, incomplete or incorrect
- 0.4-0.6: Acceptable quality, basic completion
- 0.7-0.8: Good quality, well-executed
- 0.9-1.0: Excellent quality, comprehensive and accurate

Respond with ONLY the numerical score (e.g., 0.75), no additional text."""

                prompt = f"""Task Result: {result_content}

Please rate the quality of this result:"""

                result_llm = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.1,
                    max_tokens=20
                )
                
                if result_llm["success"]:
                    try:
                        quality_score = float(result_llm["content"].strip())
                        # 确保分数在有效范围内
                        return min(1.0, max(0.0, quality_score))
                    except ValueError:
                        logging.warning("Failed to parse quality score, using fallback")
                        return self._fallback_quality_calculation(result_content)
                else:
                    logging.warning("LLM quality assessment failed, using fallback")
                    return self._fallback_quality_calculation(result_content)
                    
        except Exception as e:
            logging.error(f"Quality calculation failed: {e}")
            return self._fallback_quality_calculation(result.get("result", ""))
    
    def _fallback_quality_calculation(self, result_content: str) -> float:
        """回退质量计算方法"""
        if not result_content:
            return 0.0
        
        quality = 0.5  # 基础分
        
        # 根据结果内容调整
        if len(result_content) > 50:
            quality += 0.2
        if "成功" in result_content or "success" in result_content.lower():
            quality += 0.1
        if "错误" in result_content or "error" in result_content.lower():
            quality -= 0.2
        
        return min(1.0, max(0.0, quality))
    
    def _update_evolution_metrics(self, result: Dict, execution_time: float):
        """更新进化指标"""
        self.evolution_metrics.total_tasks += 1
        
        # 更新成功率
        success = result.get("status") == "completed"
        current_success_rate = self.evolution_metrics.success_rate
        total_tasks = self.evolution_metrics.total_tasks
        
        self.evolution_metrics.success_rate = (
            (current_success_rate * (total_tasks - 1) + (1 if success else 0)) / total_tasks
        )
        
        # 更新平均执行时间
        current_avg_time = self.evolution_metrics.average_execution_time
        self.evolution_metrics.average_execution_time = (
            (current_avg_time * (total_tasks - 1) + execution_time) / total_tasks
        )
    
    async def create_dynamic_tool(self, name: str, description: str, code: str, 
                                 parameters: Dict[str, Any]) -> bool:
        """创建动态工具"""
        try:
            success = dynamic_tool_creator.create_tool(
                name, description, code, parameters
            )
            
            if success:
                self.evolution_metrics.tools_created += 1
                logging.info(f"Created dynamic tool: {name}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to create dynamic tool: {e}")
            return False
    
    async def get_evolution_report(self) -> Dict[str, Any]:
        """获取进化报告"""
        try:
            # 获取学习洞察
            learning_insights = adaptive_learning.get_learning_insights()
            
            # 获取反思报告
            reflection_report = await self_reflection.generate_learning_report()
            
            # 获取工具性能报告
            tool_performance = adaptive_learning.get_tool_performance_report()
            
            # 获取动态工具统计
            dynamic_tool_stats = dynamic_tool_creator.get_tool_statistics()
            
            return {
                "evolution_metrics": {
                    "total_tasks": self.evolution_metrics.total_tasks,
                    "success_rate": round(self.evolution_metrics.success_rate, 3),
                    "average_execution_time": round(self.evolution_metrics.average_execution_time, 2),
                    "tools_created": self.evolution_metrics.tools_created,
                    "learning_sessions": self.evolution_metrics.learning_sessions,
                    "improvement_score": round(reflection_report.get("average_score", 0.0), 3)
                },
                "learning_insights": learning_insights,
                "reflection_report": reflection_report,
                "tool_performance": tool_performance,
                "dynamic_tools": dynamic_tool_stats,
                "recommendations": self._generate_evolution_recommendations(
                    learning_insights, reflection_report
                )
            }
            
        except Exception as e:
            logging.error(f"Failed to generate evolution report: {e}")
            return {"error": str(e)}
    
    def _generate_evolution_recommendations(self, learning_insights: Dict, 
                                          reflection_report: Dict) -> List[str]:
        """生成进化建议"""
        recommendations = []
        
        # 基于学习洞察的建议
        if learning_insights.get("success_rate", 0.0) < 0.7:
            recommendations.append("成功率较低，建议分析失败案例并改进策略")
        
        # 基于反思报告的建议
        if reflection_report.get("average_score", 0.0) < 0.6:
            recommendations.append("自我反思评分较低，建议加强自我分析和改进")
        
        # 基于工具性能的建议
        tool_performance = learning_insights.get("best_performing_tools", [])
        if not tool_performance:
            recommendations.append("工具使用数据不足，建议增加更多任务执行")
        
        # 基于动态工具的建议
        dynamic_tools = learning_insights.get("total_dynamic_tools", 0)
        if dynamic_tools == 0:
            recommendations.append("尚未创建动态工具，建议在需要时创建专用工具")
        
        return recommendations
    
    async def evolve(self) -> Dict[str, Any]:
        """执行进化过程"""
        try:
            evolution_result = {
                "evolution_completed": True,
                "improvements_made": [],
                "new_capabilities": [],
                "evolution_score": 0.0
            }
            
            # 获取进化报告
            report = await self.get_evolution_report()
            
            # 基于报告进行进化
            if report.get("learning_insights", {}).get("improvement_suggestions"):
                evolution_result["improvements_made"].extend(
                    report["learning_insights"]["improvement_suggestions"]
                )
            
            # 计算进化评分
            metrics = report.get("evolution_metrics", {})
            success_rate = metrics.get("success_rate", 0.0)
            tools_created = metrics.get("tools_created", 0)
            avg_score = report.get("reflection_report", {}).get("average_score", 0.0)
            
            evolution_score = (success_rate * 0.4 + min(tools_created / 10, 1.0) * 0.3 + avg_score * 0.3)
            evolution_result["evolution_score"] = round(evolution_score, 3)
            
            logging.info(f"Evolution completed with score: {evolution_score}")
            
            return evolution_result
            
        except Exception as e:
            logging.error(f"Evolution failed: {e}")
            return {
                "evolution_completed": False,
                "error": str(e),
                "evolution_score": 0.0
            }
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """获取进化状态"""
        return {
            "evolution_enabled": self.evolution_enabled,
            "learning_enabled": self.learning_enabled,
            "reflection_enabled": self.reflection_enabled,
            "metrics": {
                "total_tasks": self.evolution_metrics.total_tasks,
                "success_rate": round(self.evolution_metrics.success_rate, 3),
                "tools_created": self.evolution_metrics.tools_created,
                "average_execution_time": round(self.evolution_metrics.average_execution_time, 2)
            },
            "capabilities": {
                "dynamic_tool_creation": True,
                "adaptive_learning": True,
                "self_reflection": True,
                "evolution_tracking": True
            }
        }


# 创建自进化 Agent 实例的便捷函数
def create_self_evolving_agent(config: AgentConfig = None) -> SelfEvolvingAgent:
    """创建自进化 Agent"""
    return SelfEvolvingAgent(config) 