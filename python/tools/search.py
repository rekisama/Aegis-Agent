"""
Search Tool for Agent Zero
Provides online search capabilities for information gathering.
"""

import asyncio
import aiohttp
import logging
import json
import re
from typing import Dict, List, Optional
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup

from .base import BaseTool, ToolResult


class SearchTool(BaseTool):
    """
    Tool for performing online searches and web scraping.
    
    Features:
    - Web search using multiple engines
    - Web page content extraction
    - Safe browsing with timeouts
    - Result caching and filtering
    """
    
    def __init__(self):
        super().__init__("search", "Perform online searches and web scraping")
        self.search_engines = {
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}"
        }
        self.session = None
        self.user_agent = "AegisAgent/1.0 (Search Tool)"
        
        # Load timeout from environment
        from ..utils.env_manager import env_manager
        tools_config = env_manager.get_tools_config()
        self.timeout = tools_config.get("search_timeout", 10)
        self.max_results = 5
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute a search operation."""
        query = kwargs.get("query", "")
        engine = kwargs.get("engine", "google")
        max_results = kwargs.get("max_results", self.max_results)
        scrape_content = kwargs.get("scrape_content", False)
        
        if not query:
            return ToolResult(
                success=False,
                data=None,
                error="No search query provided",
                metadata={"tool_type": "search"}
            )
        
        try:
            # Initialize session if needed
            if self.session is None:
                self.session = aiohttp.ClientSession(
                    headers={"User-Agent": self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                )
            
            # Perform search
            search_results = await self._perform_search(query, engine, max_results)
            
            # Scrape content if requested
            if scrape_content and search_results.get("results"):
                await self._scrape_content(search_results["results"])
            
            return ToolResult(
                success=True,
                data=search_results,
                metadata={"tool_type": "search", "engine": engine}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Search failed: {str(e)}",
                metadata={"tool_type": "search"}
            )
    
    async def _perform_search(self, query: str, engine: str, max_results: int) -> Dict:
        """Perform a web search using the specified engine."""
        if engine not in self.search_engines:
            engine = "google"
        
        search_url = self.search_engines[engine].format(quote_plus(query))
        
        try:
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    raise Exception(f"Search request failed with status {response.status}")
                
                html_content = await response.text()
                results = self._parse_search_results(html_content, engine, max_results)
                
                return {
                    "query": query,
                    "engine": engine,
                    "results": results,
                    "total_results": len(results)
                }
                
        except Exception as e:
            logging.error(f"Search failed for query '{query}': {e}")
            raise
    
    def _parse_search_results(self, html_content: str, engine: str, max_results: int) -> List[Dict]:
        """Parse search results from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        if engine == "google":
            results = self._parse_google_results(soup, max_results)
        elif engine == "bing":
            results = self._parse_bing_results(soup, max_results)
        elif engine == "duckduckgo":
            results = self._parse_duckduckgo_results(soup, max_results)
        
        return results
    
    def _parse_google_results(self, soup: BeautifulSoup, max_results: int) -> List[Dict]:
        """Parse Google search results."""
        results = []
        
        # Look for search result containers
        search_results = soup.find_all('div', class_='g')
        
        for result in search_results[:max_results]:
            try:
                # Extract title and link
                title_elem = result.find('h3')
                link_elem = result.find('a')
                snippet_elem = result.find('div', class_='VwiC3b')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # Clean URL
                    if url.startswith('/url?q='):
                        url = url.split('/url?q=')[1].split('&')[0]
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "google"
                    })
            except Exception as e:
                logging.warning(f"Failed to parse Google result: {e}")
                continue
        
        return results
    
    def _parse_bing_results(self, soup: BeautifulSoup, max_results: int) -> List[Dict]:
        """Parse Bing search results."""
        results = []
        
        # Look for search result containers
        search_results = soup.find_all('li', class_='b_algo')
        
        for result in search_results[:max_results]:
            try:
                # Extract title and link
                title_elem = result.find('h2')
                link_elem = title_elem.find('a') if title_elem else None
                snippet_elem = result.find('p')
                
                if title_elem and link_elem:
                    title = title_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "bing"
                    })
            except Exception as e:
                logging.warning(f"Failed to parse Bing result: {e}")
                continue
        
        return results
    
    def _parse_duckduckgo_results(self, soup: BeautifulSoup, max_results: int) -> List[Dict]:
        """Parse DuckDuckGo search results."""
        results = []
        
        # Look for search result containers
        search_results = soup.find_all('div', class_='result')
        
        for result in search_results[:max_results]:
            try:
                # Extract title and link
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source": "duckduckgo"
                    })
            except Exception as e:
                logging.warning(f"Failed to parse DuckDuckGo result: {e}")
                continue
        
        return results
    
    async def _scrape_content(self, results: List[Dict]):
        """Scrape content from search result URLs."""
        for result in results:
            try:
                url = result.get("url", "")
                if url and url.startswith("http"):
                    content = await self._fetch_webpage_content(url)
                    if content:
                        result["content"] = content[:1000]  # Limit content length
            except Exception as e:
                logging.warning(f"Failed to scrape content from {url}: {e}")
                continue
    
    async def _fetch_webpage_content(self, url: str) -> Optional[str]:
        """Fetch and extract content from a webpage."""
        try:
            async with self.session.get(url, timeout=self.timeout) as response:
                if response.status != 200:
                    return None
                
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract text content
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text
                
        except Exception as e:
            logging.warning(f"Failed to fetch webpage content from {url}: {e}")
            return None
    
    async def search_knowledge(self, topic: str, max_results: int = 3) -> Dict:
        """Search for knowledge on a specific topic."""
        search_results = await self.execute(
            query=topic,
            engine="google",
            max_results=max_results,
            scrape_content=True
        )
        
        if search_results.success:
            # Extract and summarize content
            knowledge = []
            for result in search_results.data.get("results", []):
                if "content" in result:
                    knowledge.append({
                        "title": result["title"],
                        "url": result["url"],
                        "content": result["content"][:500],  # Limit content
                        "source": "web_search"
                    })
            
            return {
                "topic": topic,
                "knowledge": knowledge,
                "sources": len(knowledge)
            }
        else:
            return {
                "topic": topic,
                "knowledge": [],
                "sources": 0,
                "error": search_results.error
            }
    
    def get_search_engines(self) -> List[str]:
        """Get available search engines."""
        return list(self.search_engines.keys())
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None 