"""
Web Reader Tool
获取网页内容并提取信息的工具
"""

import asyncio
import logging
import aiohttp
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import re

import sys
from pathlib import Path
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from python.tools.base import BaseTool, ToolResult


class WebReaderTool(BaseTool):
    """获取网页内容并提取信息的工具"""
    
    def __init__(self):
        super().__init__("web_reader", "获取网页内容并提取信息")
        self.session = None
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        获取网页内容并提取信息
        
        Args:
            url: 要访问的URL
            extract_title: 是否提取标题
            extract_text: 是否提取文本内容
            timeout: 超时时间（秒）
            
        Returns:
            ToolResult with webpage content
        """
        try:
            url = kwargs.get("url", "")
            extract_title = kwargs.get("extract_title", True)
            extract_text = kwargs.get("extract_text", False)
            timeout = kwargs.get("timeout", 30)
            
            if not url:
                return ToolResult(
                    success=False,
                    data=None,
                    error="No URL provided",
                    metadata={"tool_type": "web_reader"}
                )
            
            # 验证URL格式
            try:
                parsed_url = urlparse(url)
                if not parsed_url.scheme:
                    url = "https://" + url
            except Exception as e:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Invalid URL format: {e}",
                    metadata={"tool_type": "web_reader"}
                )
            
            logging.info(f"Fetching webpage: {url}")
            
            # 创建HTTP会话
            if not self.session:
                timeout_config = aiohttp.ClientTimeout(total=timeout)
                self.session = aiohttp.ClientSession(timeout=timeout_config)
            
            # 发送HTTP请求
            async with self.session.get(url) as response:
                if response.status != 200:
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status}: {response.reason}",
                        metadata={"tool_type": "web_reader", "status_code": response.status}
                    )
                
                # 读取内容
                content = await response.text()
                
                # 提取信息
                result_data = {
                    "url": url,
                    "status_code": response.status,
                    "content_length": len(content),
                    "content_type": response.headers.get("content-type", "unknown")
                }
                
                # 提取标题
                if extract_title:
                    title = self._extract_title(content)
                    result_data["title"] = title
                
                # 提取文本内容
                if extract_text:
                    text = self._extract_text(content)
                    result_data["text"] = text[:1000] + "..." if len(text) > 1000 else text
                
                logging.info(f"Successfully fetched webpage: {url}")
                return ToolResult(
                    success=True,
                    data=result_data,
                    metadata={
                        "tool_type": "web_reader",
                        "url": url,
                        "status_code": response.status
                    }
                )
                
        except asyncio.TimeoutError:
            logging.error(f"Request timeout: {url}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Request timeout after {timeout} seconds",
                metadata={"tool_type": "web_reader", "timeout": True}
            )
        except Exception as e:
            logging.error(f"Failed to fetch webpage: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to fetch webpage: {str(e)}",
                metadata={"tool_type": "web_reader"}
            )
    
    def _extract_title(self, html_content: str) -> str:
        """从HTML内容中提取标题"""
        try:
            # 尝试提取<title>标签
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()
                # 清理HTML标签
                title = re.sub(r'<[^>]+>', '', title)
                return title
            
            # 尝试提取h1标签
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
            if h1_match:
                title = h1_match.group(1).strip()
                title = re.sub(r'<[^>]+>', '', title)
                return title
            
            return "No title found"
        except Exception as e:
            logging.error(f"Error extracting title: {e}")
            return "Error extracting title"
    
    def _extract_text(self, html_content: str) -> str:
        """从HTML内容中提取纯文本"""
        try:
            # 移除HTML标签
            text = re.sub(r'<[^>]+>', ' ', html_content)
            # 移除多余的空白字符
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text: {e}")
            return "Error extracting text"
    
    def get_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        info = super().get_info()
        info.update({
            "supported_features": ["title_extraction", "text_extraction", "url_validation"],
            "max_timeout": 60,
            "supported_protocols": ["http", "https"]
        })
        return info
    
    async def cleanup(self):
        """清理资源"""
        if self.session:
            await self.session.close()
            self.session = None 