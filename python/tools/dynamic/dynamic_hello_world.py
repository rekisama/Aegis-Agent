"""
Hello World Tool for Testing Dynamic Tool Discovery
A simple tool to test the dynamic tool loading system.
"""

import logging
from typing import Dict, Any

import sys
from pathlib import Path
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from python.tools.base import BaseTool, ToolResult


class HelloWorldTool(BaseTool):
    """
    A simple hello world tool for testing dynamic tool discovery.
    
    This tool demonstrates basic tool functionality and can be used
    to test the dynamic loading system.
    """
    
    def __init__(self):
        super().__init__("hello_world", "A simple hello world tool for testing")
        self.greeting_count = 0
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the hello world tool.
        
        Args:
            name: Name to greet (optional)
            language: Language for greeting (optional, default: "en")
            count: Number of greetings (optional, default: 1)
            
        Returns:
            ToolResult with greeting message
        """
        try:
            name = kwargs.get("name", "World")
            language = kwargs.get("language", "en")
            count = kwargs.get("count", 1)
            
            # Increment greeting count
            self.greeting_count += 1
            
            # Generate greeting based on language
            greetings = {
                "en": f"Hello, {name}!",
                "zh": f"你好，{name}！",
                "es": f"¡Hola, {name}!",
                "fr": f"Bonjour, {name}!",
                "de": f"Hallo, {name}!",
                "ja": f"こんにちは、{name}さん！"
            }
            
            greeting = greetings.get(language, greetings["en"])
            
            # Repeat greeting if count > 1
            if count > 1:
                greeting = "\n".join([greeting] * count)
            
            result_data = {
                "greeting": greeting,
                "name": name,
                "language": language,
                "count": count,
                "total_greetings": self.greeting_count,
                "timestamp": self.created_at.isoformat()
            }
            
            logging.info(f"HelloWorldTool executed: {greeting}")
            
            return ToolResult(
                success=True,
                data=result_data,
                metadata={
                    "tool_type": "hello_world",
                    "greeting_count": self.greeting_count
                }
            )
            
        except Exception as e:
            logging.error(f"HelloWorldTool execution failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"tool_type": "hello_world"}
            )
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        info = super().get_info()
        info.update({
            "greeting_count": self.greeting_count,
            "supported_languages": ["en", "zh", "es", "fr", "de", "ja"]
        })
        return info 