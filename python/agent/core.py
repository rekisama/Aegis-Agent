"""
Aegis Agent - Core Agent Implementation
A general-purpose personal assistant with persistent memory and multi-agent cooperation.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..memory.memory_manager import MemoryManager
from ..tools.base import BaseTool
from ..tools.terminal import TerminalTool
from ..tools.search import SearchTool
from ..tools.tavily_search import TavilySearchTool
from ..tools.code import CodeExecutionTool
from ..communication.communication import CommunicationManager
from .tool_manager import tool_manager


from ..utils.config_types import AgentConfig


class Agent:
    """
    Core Agent class implementing the Agent Zero framework.
    
    Features:
    - Persistent memory
    - Multi-agent cooperation
    - Customizable tools
    - Real-time communication
    - Task delegation
    """
    
    def __init__(self, config: AgentConfig = None):
        # Load configuration from environment if not provided
        if config is None:
            from ..utils.env_manager import env_manager
            env_config = env_manager.get_agent_config()
            config = AgentConfig(
                name=env_config["name"],
                model=env_config["model"],
                temperature=env_config["temperature"],
                max_tokens=env_config["max_tokens"]
            )
        
        self.config = config
        self.agent_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        
        # Initialize core components
        self.memory = MemoryManager(self.config)
        self.communication = CommunicationManager(self)
        self.tools: Dict[str, BaseTool] = {}
        self.subordinates: List[Agent] = []
        self.superior: Optional[Agent] = None
        
        # Task tracking
        self.current_task = None
        self.task_history = []
        self.task_count = 0
        
        # Initialize default tools
        self._initialize_default_tools()
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
        logging.info(f"Agent {self.config.name} (ID: {self.agent_id}) initialized")
    
    def _initialize_default_tools(self):
        """Initialize default tools available to the agent."""
        if self.config.tools_enabled:
            # Register tools with tool manager
            from ..tools.terminal import TerminalTool
            from ..tools.search import SearchTool
            from ..tools.tavily_search import TavilySearchTool
            from ..tools.code import CodeExecutionTool
            
            tool_manager.register_tool("terminal", TerminalTool)
            tool_manager.register_tool("search", SearchTool)
            tool_manager.register_tool("tavily_search", TavilySearchTool)
            tool_manager.register_tool("code", CodeExecutionTool)
            
            # Get tool instances
            self.tools = tool_manager.get_all_tools()
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt from file."""
        try:
            with open("prompts/default/agent.system.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Default system prompt if file not found."""
        return """You are Agent Zero, a general-purpose personal assistant.

Your capabilities:
- Persistent memory for learning from past interactions
- Multi-agent cooperation for complex task decomposition
- Custom tool creation and usage
- Real-time communication with superiors and subordinates
- Code execution and terminal access

Core principles:
1. Always communicate clearly with your superior
2. Delegate complex tasks to subordinate agents when beneficial
3. Learn from past experiences and store solutions in memory
4. Create custom tools when needed for specific tasks
5. Report progress regularly and ask for guidance when uncertain

Remember: You are not limited by pre-programmed tools. You can create, modify, and use any tool necessary to accomplish your tasks."""
    
    async def execute_task(self, task_description: str, context: Dict = None) -> Dict:
        """
        Execute a task given by the superior.
        
        Args:
            task_description: Description of the task to execute
            context: Additional context information
            
        Returns:
            Dict containing task results and metadata
        """
        self.task_count += 1
        self.current_task = {
            "id": str(uuid.uuid4()),
            "description": task_description,
            "context": context or {},
            "started_at": datetime.now(),
            "status": "running"
        }
        
        logging.info(f"Agent {self.config.name} starting task: {task_description}")
        
        try:
            # Check if we should report to superior
            if self.superior and self.task_count % self.config.report_frequency == 0:
                await self.communication.report_to_superior(
                    f"Starting task #{self.task_count}: {task_description}"
                )
            
            # Analyze task and decide on approach
            task_analysis = await self._analyze_task(task_description, context)
            
            # Execute the task
            result = await self._execute_task_internal(task_analysis)
            
            # Store in memory
            if self.config.memory_enabled:
                await self.memory.store_task_result(
                    task_description, result, context
                )
            
            # Report completion
            if self.superior:
                await self.communication.report_to_superior(
                    f"Task completed successfully: {task_description}",
                    result
                )
            
            self.current_task["status"] = "completed"
            self.current_task["result"] = result
            self.task_history.append(self.current_task)
            
            return result
            
        except Exception as e:
            error_msg = f"Task failed: {str(e)}"
            logging.error(error_msg)
            
            if self.superior:
                await self.communication.report_to_superior(error_msg)
            
            self.current_task["status"] = "failed"
            self.current_task["error"] = str(e)
            self.task_history.append(self.current_task)
            
            raise
    
    async def _analyze_task(self, task_description: str, context: Dict) -> Dict:
        """Analyze the task and determine the best approach."""
        try:
            # Use DeepSeek API for task analysis
            from ..llm.deepseek_client import DeepSeekClient
            
            async with DeepSeekClient() as llm_client:
                analysis_result = await llm_client.analyze_task(task_description)
                
                if analysis_result["success"]:
                    return analysis_result["analysis"]
                else:
                    logging.warning(f"LLM analysis failed: {analysis_result.get('error', 'Unknown error')}")
                    # Fallback to basic analysis
                    return {
                        "complexity": "medium",
                        "requires_delegation": False,
                        "required_tools": [],
                        "estimated_duration": "unknown"
                    }
        except Exception as e:
            logging.error(f"Task analysis error: {e}")
            # Fallback to basic analysis
            return {
                "complexity": "medium",
                "requires_delegation": False,
                "required_tools": [],
                "estimated_duration": "unknown"
            }
    
    async def _execute_task_internal(self, task_analysis: Dict) -> Dict:
        """Internal task execution logic using LLM for intelligent tool selection."""
        try:
            task_description = self.current_task["description"]
            
            # Use LLM to analyze task and determine tool usage
            tool_selection_result = await self._select_tools_with_llm(task_description, task_analysis)
            
            if not tool_selection_result["success"]:
                return {
                    "status": "failed",
                    "result": f"工具选择失败: {tool_selection_result['error']}",
                    "metadata": task_analysis
                }
            
            tool_plan = tool_selection_result["plan"]
            print(f"🤖 LLM分析任务: {task_description}")
            print(f"📋 执行计划: {tool_plan['description']}")
            
            # Execute the planned tools
            results = []
            for tool_step in tool_plan["steps"]:
                tool_name = tool_step["tool"]
                tool_params = tool_step.get("parameters", {})
                
                if tool_name in self.tools:
                    print(f"🔧 执行工具: {tool_name}")
                    tool = self.tools[tool_name]
                    
                    # Execute tool with parameters
                    tool_result = await tool.execute(**tool_params)
                    
                    if tool_result.success:
                        results.append({
                            "tool": tool_name,
                            "success": True,
                            "data": tool_result.data,
                            "output": tool_result.data.get("results", tool_result.data.get("stdout", "No output"))
                        })
                        print(f"✅ {tool_name} 执行成功")
                    else:
                        results.append({
                            "tool": tool_name,
                            "success": False,
                            "error": tool_result.error
                        })
                        print(f"❌ {tool_name} 执行失败: {tool_result.error}")
                else:
                    print(f"⚠️ 工具 {tool_name} 不可用")
                    results.append({
                        "tool": tool_name,
                        "success": False,
                        "error": f"Tool {tool_name} not available"
                    })
            
            # Generate final result using LLM
            final_result = await self._generate_final_result(task_description, results, tool_plan)
            
            return {
                "status": "completed",
                "result": final_result,
                "metadata": {
                    **task_analysis,
                    "tool_plan": tool_plan,
                    "tool_results": results
                }
            }
                
        except Exception as e:
            logging.error(f"Task execution error: {e}")
            return {
                "status": "failed",
                "result": f"任务执行失败: {str(e)}",
                "metadata": task_analysis
            }
    
    async def _select_tools_with_llm(self, task_description: str, task_analysis: Dict) -> Dict:
        """Use LLM to intelligently select tools for task execution."""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            # Get comprehensive tool information from registry
            tool_summary = tool_manager.generate_tool_summary_for_llm()
            
            system_prompt = f"""You are an intelligent task planner for an AI agent. 

Your job is to analyze the user's task and select the most appropriate tools from the available tool registry.

{tool_summary}

For each task, carefully analyze:
1. What the user wants to accomplish
2. Which tools have the capabilities to help
3. The best parameters for each selected tool
4. The order of tool execution

IMPORTANT: Respond ONLY with valid JSON, no additional text.

JSON format:
{{
    "description": "Brief description of the execution plan",
    "steps": [
        {{
            "tool": "tool_name",
            "parameters": {{"param1": "value1", "param2": "value2"}},
            "reason": "Why this tool is needed"
        }}
    ]
}}

Guidelines:
- Choose tools based on their capabilities and use cases
- Consider tool limitations when making selections
- Extract relevant information from the task description for parameters
- For search tasks, prefer tavily_search for complex queries and recent information
- For system operations, use terminal with safe commands
- For calculations and data processing, use code tool
- Provide clear reasoning for each tool selection

Be specific and practical. Extract search queries and parameters from the task description."""

            prompt = f"Task: {task_description}\n\nTask Analysis: {task_analysis}\n\nCreate an execution plan:"
            
            async with DeepSeekClient() as llm_client:
                result = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=800
                )
                
                if result["success"]:
                    try:
                        import json
                        content = result["content"].strip()
                        
                        # 清理markdown代码块格式
                        if content.startswith('```json'):
                            content = content[7:]
                        elif content.startswith('```'):
                            content = content[3:]
                        if content.endswith('```'):
                            content = content[:-3]
                        content = content.strip()
                        
                        plan = json.loads(content)
                        return {
                            "success": True,
                            "plan": plan
                        }
                    except json.JSONDecodeError as e:
                        return {
                            "success": False,
                            "error": f"Failed to parse LLM response as JSON: {e}"
                        }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "LLM request failed")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool selection error: {str(e)}"
            }
    
    async def _generate_final_result(self, task_description: str, tool_results: List[Dict], tool_plan: Dict) -> str:
        """Use LLM to generate a coherent final result from tool outputs."""
        try:
            from ..llm.deepseek_client import DeepSeekClient
            
            system_prompt = """You are an AI assistant that synthesizes results from multiple tools into a coherent response.

Your task is to take the outputs from various tools and create a comprehensive, well-formatted response that directly answers the user's original question.

Format the response clearly and include relevant information from all successful tool executions."""

            # Prepare tool outputs for LLM
            successful_results = [r for r in tool_results if r["success"]]
            failed_results = [r for r in tool_results if not r["success"]]
            
            prompt = f"""Original Task: {task_description}

Execution Plan: {tool_plan['description']}

Successful Tool Results:
{chr(10).join([f"- {r['tool']}: {r['output']}" for r in successful_results])}

Failed Tool Results:
{chr(10).join([f"- {r['tool']}: {r['error']}" for r in failed_results])}

Please provide a comprehensive response that answers the original task:"""

            async with DeepSeekClient() as llm_client:
                result = await llm_client.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                if result["success"]:
                    return result["content"]
                else:
                    # Fallback to simple concatenation
                    outputs = [r["output"] for r in successful_results if r["success"]]
                    return f"任务执行完成。\n\n结果:\n{chr(10).join(outputs)}"
                    
        except Exception as e:
            # Fallback to simple concatenation
            outputs = [r["output"] for r in tool_results if r["success"]]
            return f"任务执行完成。\n\n结果:\n{chr(10).join(outputs)}"
    
    def create_subordinate(self, name: str, config: AgentConfig = None) -> 'Agent':
        """Create a subordinate agent for task delegation."""
        if not self.config.hierarchical_enabled:
            raise ValueError("Hierarchical mode is disabled")
        
        subordinate_config = config or AgentConfig()
        subordinate_config.name = name
        
        subordinate = Agent(subordinate_config)
        subordinate.superior = self
        self.subordinates.append(subordinate)
        
        logging.info(f"Created subordinate agent: {name}")
        return subordinate
    
    def add_tool(self, name: str, tool: BaseTool):
        """Add a custom tool to the agent."""
        self.tools[name] = tool
        logging.info(f"Added tool: {name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    async def communicate_with_superior(self, message: str, data: Any = None):
        """Send a message to the superior agent."""
        if self.superior:
            await self.superior.communication.receive_from_subordinate(self, message, data)
        else:
            # If no superior, this is the top-level agent - communicate with user
            print(f"[{self.config.name}]: {message}")
            if data:
                print(f"Data: {data}")
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.config.name,
            "task_count": self.task_count,
            "subordinates_count": len(self.subordinates),
            "tools_count": len(self.tools),
            "current_task": self.current_task,
            "memory_enabled": self.config.memory_enabled,
            "created_at": self.created_at.isoformat()
        } 