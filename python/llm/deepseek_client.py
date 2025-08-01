"""
DeepSeek API Client
"""

import aiohttp
import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..utils.env_manager import env_manager


@dataclass
class Message:
    """A message in the conversation."""
    role: str  # "system", "user", "assistant"
    content: str


class DeepSeekClient:
    """
    DeepSeek API Client
    """
    
    def __init__(self):
        self.config = env_manager.get_deepseek_config()
        self.api_key = self.config["api_key"]
        self.api_base_url = self.config["api_base_url"]
        self.model = self.config["model"]
        
        self.session = None
        self.conversation_history: List[Message] = []
        
        logging.info(f"DeepSeek client initialized with model: {self.model}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        context: Dict = None
    ) -> Dict[str, Any]:
        """Generate a response using DeepSeek API."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Prepare messages
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append(Message("system", system_prompt))
        
        # Add conversation history
        for msg in self.conversation_history[-10:]:  # Keep last 10 messages
            messages.append(msg)
        
        # Add current prompt
        messages.append(Message("user", prompt))
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            async with self.session.post(
                f"{self.api_base_url}/chat/completions",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract response
                    if "choices" in data and len(data["choices"]) > 0:
                        choice = data["choices"][0]
                        content = choice["message"]["content"]
                        
                        # Add to conversation history
                        self.conversation_history.append(Message("user", prompt))
                        self.conversation_history.append(Message("assistant", content))
                        
                        return {
                            "success": True,
                            "content": content,
                            "usage": data.get("usage", {}),
                            "model": data.get("model", self.model),
                            "finish_reason": choice.get("finish_reason", "stop")
                        }
                    else:
                        return {
                            "success": False,
                            "error": "No response content in API response",
                            "data": data
                        }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"API request failed with status {response.status}: {error_text}",
                        "status_code": response.status
                    }
                    
        except aiohttp.ClientError as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    async def chat_completion(
        self, 
        user_prompt: str, 
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """Chat completion method - alias for generate_response."""
        return await self.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    async def analyze_task(self, task_description: str) -> Dict:
        """Analyze a task and provide structured analysis."""
        try:
            system_prompt = """你是一个智能AI助手，专门分析用户任务并制定执行计划。

你的能力包括：
- 代码执行（Python代码）
- 终端命令执行
- 文件操作
- 网络搜索
- 文本处理和分析

分析任务时，请考虑：
1. 任务是否需要编程计算
2. 是否需要执行系统命令
3. 是否需要搜索信息
4. 是否需要文件操作
5. 任务的复杂程度

请以JSON格式回复，包含以下字段：
{
  "complexity": "简单/中等/复杂",
  "description": "任务的具体描述和解决方案",
  "requires_delegation": false,
  "estimated_duration": "估计完成时间（如：1-2分钟）",
  "required_tools": ["需要的工具列表，如：code, terminal, search等"]
}

可用工具：
- code: 执行Python代码
- terminal: 执行终端命令
- search: 网络搜索
- file_reader: 读取文件内容

请确保description字段包含详细的任务分析和解决方案描述。"""

            prompt = f"分析这个任务：{task_description}"
            
            response = await self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            if response["success"]:
                try:
                    content = response["content"]
                    
                    # 清理markdown代码块格式
                    content = re.sub(r'^```json\s*', '', content, flags=re.MULTILINE)
                    content = re.sub(r'\s*```$', '', content, flags=re.MULTILINE)
                    
                    # 尝试解析JSON
                    analysis = json.loads(content)
                    return {
                        "success": True,
                        "analysis": analysis
                    }
                except json.JSONDecodeError:
                    # 如果直接解析失败，尝试提取JSON部分
                    try:
                        json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                            analysis = json.loads(json_str)
                            return {
                                "success": True,
                                "analysis": analysis
                            }
                    except (json.JSONDecodeError, AttributeError):
                        pass
                    
                    return {
                        "success": False,
                        "error": "无法解析任务分析结果"
                    }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "任务分析失败")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"任务分析异常：{str(e)}"
            }
