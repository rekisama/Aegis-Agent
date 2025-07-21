"""
DeepSeek API Client for Aegis Agent
Provides integration with DeepSeek's language models.
"""

import aiohttp
import json
import logging
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
    Client for interacting with DeepSeek API.
    
    Features:
    - Async API calls
    - Conversation management
    - Error handling and retries
    - Context management
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
        """
        Generate a response using DeepSeek API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Response randomness (0-2)
            max_tokens: Maximum tokens in response
            context: Additional context information
            
        Returns:
            Dict containing response and metadata
        """
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
    
    async def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        Analyze a task using DeepSeek to determine the best approach.
        
        Args:
            task_description: Description of the task to analyze
            
        Returns:
            Dict containing analysis results
        """
        system_prompt = """You are a task analysis expert. Analyze the given task and provide:
1. Task complexity (simple, medium, complex)
2. Whether delegation would be beneficial (true/false)
3. Required tools (list of tool names)
4. Estimated duration (short, medium, long)
5. Recommended approach (description)

Respond in JSON format only."""

        prompt = f"Analyze this task: {task_description}"
        
        result = await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=500
        )
        
        if result["success"]:
            try:
                # Try to parse JSON response
                analysis = json.loads(result["content"])
                return {
                    "success": True,
                    "analysis": analysis
                }
            except json.JSONDecodeError:
                # Fallback to text analysis
                return {
                    "success": True,
                    "analysis": {
                        "complexity": "medium",
                        "requires_delegation": False,
                        "required_tools": [],
                        "estimated_duration": "unknown",
                        "recommended_approach": result["content"]
                    }
                }
        else:
            return result
    
    async def generate_code(self, description: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate code based on a description.
        
        Args:
            description: Code description
            language: Programming language
            
        Returns:
            Dict containing generated code
        """
        system_prompt = f"""You are a code generation expert. Generate {language} code based on the description.
Requirements:
1. Generate only the code, no explanations
2. Include necessary imports
3. Add appropriate comments
4. Follow best practices
5. Make it safe and secure"""

        prompt = f"Generate {language} code for: {description}"
        
        result = await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=2000
        )
        
        return result
    
    async def summarize_text(self, text: str, max_length: int = 200) -> Dict[str, Any]:
        """
        Summarize text using DeepSeek.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Dict containing summary
        """
        system_prompt = f"""You are a text summarization expert. Create a concise summary of the given text.
Requirements:
1. Keep the summary under {max_length} characters
2. Maintain key information
3. Use clear, concise language
4. Focus on the main points"""

        prompt = f"Summarize this text: {text}"
        
        result = await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=300
        )
        
        return result
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        logging.info("Conversation history cleared")
    
    def get_conversation_length(self) -> int:
        """Get the number of messages in conversation history."""
        return len(self.conversation_history)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation."""
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m.role == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m.role == "assistant"]),
            "system_messages": len([m for m in self.conversation_history if m.role == "system"])
        } 