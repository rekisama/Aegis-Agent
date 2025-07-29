"""
SearXNG Search Tool for Aegis Agent
提供基于SearXNG元搜索引擎的统一搜索接口
"""

import asyncio
import aiohttp
import logging
import json
import re
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus, urlparse
from datetime import datetime
import time

import sys
from pathlib import Path
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from python.tools.base import BaseTool, ToolResult


class SearchTool(BaseTool):
    """
    SearXNG元搜索引擎工具
    
    Features:
    - 统一的搜索接口
    - 异步搜索多个引擎
    - 结果格式化和去重
    - 安全搜索和内容过滤
    - 结果缓存
    """
    
    def __init__(self):
        super().__init__("search", "SearXNG元搜索引擎，提供统一的搜索接口")
        
        # SearXNG配置
        self.searxng_url = "http://localhost:8888"  # 默认SearXNG地址
        self.api_endpoint = "/search"
        self.session = None
        self.user_agent = "AegisAgent/1.0 (SearXNG Search Tool)"
        
        # 搜索配置
        self.timeout = 15
        self.max_results = 10
        self.engines = ["google", "bing", "duckduckgo", "wikipedia"]
        self.categories = ["general", "science", "news", "social media"]
        
        # 结果缓存
        self.cache = {}
        self.cache_timeout = 300  # 5分钟缓存
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载SearXNG配置"""
        try:
            from .searxng_config import searxng_config
            
            # 从SearXNG配置管理器加载设置
            self.searxng_url = searxng_config.get_searxng_url()
            self.timeout = searxng_config.get_timeout()
            self.max_results = searxng_config.get_max_results()
            self.engines = searxng_config.get_default_engines()
            self.categories = searxng_config.get_default_categories()
            
            # 设置缓存
            if searxng_config.is_cache_enabled():
                self.cache_timeout = searxng_config.get_cache_timeout()
            else:
                self.cache_timeout = 0  # 禁用缓存
            
        except Exception as e:
            logging.warning(f"Failed to load SearXNG config: {e}")
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行搜索操作"""
        query = kwargs.get("query", "")
        engines = kwargs.get("engines", self.engines) or self.engines
        category = kwargs.get("category", "general") or "general"
        max_results = kwargs.get("max_results", self.max_results) or self.max_results
        format_type = kwargs.get("format", "json") or "json"
        language = kwargs.get("language", "zh-CN") or "zh-CN"
        
        if not query:
            return ToolResult(
                success=False,
                data=None,
                error="No search query provided",
                metadata={"tool_type": "searxng_search"}
            )
        
        try:
            # 检查缓存
            cache_key = f"{query}_{engines}_{category}_{max_results}"
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return ToolResult(
                    success=True,
                    data=cached_result,
                    metadata={"tool_type": "searxng_search", "cached": True}
                )
            
            # 初始化会话
            if self.session is None:
                self.session = aiohttp.ClientSession(
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )
            
            # 执行搜索
            search_results = await self._perform_searxng_search(
                query, engines, category, max_results, format_type, language
            )
            
            # 缓存结果
            self._cache_result(cache_key, search_results)
            
            return ToolResult(
                success=True,
                data=search_results,
                metadata={"tool_type": "searxng_search", "engines": engines}
            )
            
        except Exception as e:
            logging.error(f"SearXNG search failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Search failed: {str(e)}",
                metadata={"tool_type": "searxng_search"}
            )
    
    async def _perform_searxng_search(
        self, 
        query: str, 
        engines: List[str], 
        category: str, 
        max_results: int,
        format_type: str,
        language: str
    ) -> Dict[str, Any]:
        """执行SearXNG搜索"""
        
        # 构建搜索参数
        search_params = {
            "q": query,
            "engines": ",".join(engines),
            "categories": category,
            "format": format_type,
            "language": language,
            "pageno": 1,
            "safesearch": 1,
            "theme": "simple"
        }
        
        # 只添加非None的参数
        if category and category != "general":
            search_params["categories"] = category
        
        # 构建URL
        search_url = f"{self.searxng_url}{self.api_endpoint}"
        
        try:
            async with self.session.get(search_url, params=search_params) as response:
                if response.status != 200:
                    raise Exception(f"SearXNG API returned status {response.status}")
                
                content = await response.text()
                
                # 解析搜索结果
                if format_type == "json":
                    return await self._parse_json_results(content, max_results)
                else:
                    return await self._parse_html_results(content, max_results)
                    
        except Exception as e:
            logging.error(f"SearXNG API request failed: {e}")
            # 如果SearXNG不可用，回退到直接搜索
            return await self._fallback_search(query, engines, max_results)
    
    async def _parse_json_results(self, content: str, max_results: int) -> Dict[str, Any]:
        """解析JSON格式的搜索结果"""
        try:
            data = json.loads(content)
            
            results = []
            if "results" in data:
                for result in data["results"][:max_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "engine": result.get("engine", ""),
                        "score": result.get("score", 0),
                        "category": result.get("category", ""),
                        "published_date": result.get("publishedDate", "")
                    })
            
            return {
                "query": data.get("query", ""),
                "results": results,
                "total_results": len(results),
                "search_time": data.get("search_time", 0),
                "engines": data.get("engines", []),
                "format": "json"
            }
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON results: {e}")
            return {"results": [], "error": "Failed to parse results"}
    
    async def _parse_html_results(self, content: str, max_results: int) -> Dict[str, Any]:
        """解析HTML格式的搜索结果"""
        try:
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                logging.error("BeautifulSoup4 not available, cannot parse HTML results")
                return {"results": [], "error": "BeautifulSoup4 not available"}
            
            soup = BeautifulSoup(content, 'html.parser')
            results = []
            
            # 查找搜索结果
            result_elements = soup.find_all("div", class_="result")
            
            for element in result_elements[:max_results]:
                title_elem = element.find("h3")
                url_elem = element.find("a")
                content_elem = element.find("p")
                
                if title_elem and url_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "url": url_elem.get("href", ""),
                        "content": content_elem.get_text(strip=True) if content_elem else "",
                        "engine": element.get("data-engine", ""),
                        "score": 0,
                        "category": "",
                        "published_date": ""
                    })
            
            return {
                "query": "",
                "results": results,
                "total_results": len(results),
                "search_time": 0,
                "engines": [],
                "format": "html"
            }
            
        except Exception as e:
            logging.error(f"Failed to parse HTML results: {e}")
            return {"results": [], "error": "Failed to parse results"}
    
    async def _fallback_search(self, query: str, engines: List[str], max_results: int) -> Dict[str, Any]:
        """回退搜索（当SearXNG不可用时）"""
        logging.warning("SearXNG unavailable, using fallback search")
        
        results = []
        for engine in engines[:2]:  # 只使用前两个引擎
            try:
                engine_results = await self._direct_search(query, engine, max_results // 2)
                results.extend(engine_results)
            except Exception as e:
                logging.error(f"Fallback search for {engine} failed: {e}")
        
        return {
            "query": query,
            "results": results[:max_results],
            "total_results": len(results),
            "search_time": 0,
            "engines": engines,
            "format": "fallback"
        }
    
    async def _direct_search(self, query: str, engine: str, max_results: int) -> List[Dict]:
        """直接搜索（不使用SearXNG）"""
        search_urls = {
            "google": f"https://www.google.com/search?q={quote_plus(query)}",
            "bing": f"https://www.bing.com/search?q={quote_plus(query)}",
            "duckduckgo": f"https://duckduckgo.com/?q={quote_plus(query)}"
        }
        
        if engine not in search_urls:
            return []
        
        try:
            async with self.session.get(search_urls[engine]) as response:
                if response.status == 200:
                    content = await response.text()
                    return self._parse_direct_results(content, engine, max_results)
        except Exception as e:
            logging.error(f"Direct search failed for {engine}: {e}")
        
        return []
    
    def _parse_direct_results(self, content: str, engine: str, max_results: int) -> List[Dict]:
        """解析直接搜索结果"""
        try:
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                logging.error("BeautifulSoup4 not available, cannot parse direct results")
                return []
            
            soup = BeautifulSoup(content, 'html.parser')
            results = []
            
            if engine == "google":
                result_elements = soup.find_all("div", class_="g")
            elif engine == "bing":
                result_elements = soup.find_all("li", class_="b_algo")
            else:
                result_elements = soup.find_all("div", class_="result")
            
            for element in result_elements[:max_results]:
                title_elem = element.find("h3") or element.find("a")
                url_elem = element.find("a")
                content_elem = element.find("p") or element.find("span")
                
                if title_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "url": url_elem.get("href", "") if url_elem else "",
                        "content": content_elem.get_text(strip=True) if content_elem else "",
                        "engine": engine,
                        "score": 0,
                        "category": "",
                        "published_date": ""
                    })
            
            return results
            
        except Exception as e:
            logging.error(f"Failed to parse direct results for {engine}: {e}")
            return []
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """获取缓存结果"""
        if cache_key in self.cache:
            timestamp, result = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return result
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        """缓存搜索结果"""
        self.cache[cache_key] = (time.time(), result)
        
        # 清理过期缓存
        current_time = time.time()
        expired_keys = [
            key for key, (timestamp, _) in self.cache.items()
            if current_time - timestamp > self.cache_timeout
        ]
        for key in expired_keys:
            del self.cache[key]
    
    async def search_knowledge(self, topic: str, max_results: int = 5) -> Dict:
        """知识搜索"""
        return await self.execute(
            query=topic,
            engines=["wikipedia", "google"],
            category="science",
            max_results=max_results
        )
    
    async def search_news(self, topic: str, max_results: int = 5) -> Dict:
        """新闻搜索"""
        return await self.execute(
            query=topic,
            engines=["bing", "google"],
            category="news",
            max_results=max_results
        )
    
    async def search_social(self, topic: str, max_results: int = 5) -> Dict:
        """社交媒体搜索"""
        return await self.execute(
            query=topic,
            engines=["twitter", "reddit"],
            category="social media",
            max_results=max_results
        )
    
    def get_available_engines(self) -> List[str]:
        """获取可用的搜索引擎"""
        return self.engines.copy()
    
    def get_available_categories(self) -> List[str]:
        """获取可用的搜索分类"""
        return self.categories.copy()
    
    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()
            self.session = None 