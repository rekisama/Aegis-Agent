"""
Tavily Search Tool for Aegis Agent
Provides AI-powered search capabilities using Tavily API.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from tavily import TavilyClient

from .base import BaseTool, ToolResult


class TavilySearchTool(BaseTool):
    """
    Tool for performing AI-powered searches using Tavily API.
    
    Features:
    - AI-powered search with context understanding
    - Structured results with metadata
    - Answer generation for queries
    - Multiple search depths (basic, advanced)
    - Image search support
    """
    
    def __init__(self):
        super().__init__("tavily_search", "Perform AI-powered searches using Tavily API")
        
        # Load configuration from environment
        from ..utils.env_manager import env_manager
        tavily_config = env_manager.get_tavily_config()
        
        self.api_key = tavily_config["api_key"]
        self.search_depth = tavily_config["search_depth"]
        self.include_images = tavily_config["include_images"]
        self.include_answer = tavily_config["include_answer"]
        
        # Initialize Tavily client
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None
            logging.warning("Tavily API key not found. Tavily search tool will not be available.")
        
        # Load timeout from environment
        tools_config = env_manager.get_tools_config()
        self.timeout = tools_config.get("search_timeout", 30)
        self.max_results = 10
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute a Tavily search operation."""
        query = kwargs.get("query", "")
        search_depth = kwargs.get("search_depth", self.search_depth)
        max_results = kwargs.get("max_results", self.max_results)
        include_answer = kwargs.get("include_answer", self.include_answer)
        include_images = kwargs.get("include_images", self.include_images)
        
        if not query:
            return ToolResult(
                success=False,
                data=None,
                error="No search query provided",
                metadata={"tool_type": "tavily_search"}
            )
        
        if not self.client:
            return ToolResult(
                success=False,
                data=None,
                error="Tavily client not initialized. Check API key configuration.",
                metadata={"tool_type": "tavily_search"}
            )
        
        try:
            # Perform search with timeout
            search_result = await asyncio.wait_for(
                self._perform_search(query, search_depth, max_results, include_answer, include_images),
                timeout=self.timeout
            )
            
            return ToolResult(
                success=True,
                data=search_result,
                metadata={
                    "tool_type": "tavily_search",
                    "search_depth": search_depth,
                    "include_answer": include_answer,
                    "include_images": include_images
                }
            )
            
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                data=None,
                error=f"Search timed out after {self.timeout} seconds",
                metadata={"tool_type": "tavily_search", "timeout": True}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tavily search failed: {str(e)}",
                metadata={"tool_type": "tavily_search"}
            )
    
    async def _perform_search(self, query: str, search_depth: str, max_results: int, 
                             include_answer: bool, include_images: bool) -> Dict:
        """Perform a search using Tavily API."""
        try:
            # Prepare search parameters
            search_params = {
                "query": query,
                "search_depth": search_depth,
                "include_answer": include_answer,
                "include_images": include_images,
                "max_results": max_results
            }
            
            # Execute search
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.search(**search_params)
            )
            
            # Process and structure results
            processed_results = self._process_search_results(response, query)
            
            return {
                "query": query,
                "search_depth": search_depth,
                "results": processed_results,
                "total_results": len(processed_results),
                "answer": response.get("answer") if include_answer else None,
                "images": response.get("images", []) if include_images else [],
                "raw_response": response
            }
            
        except Exception as e:
            logging.error(f"Tavily search failed for query '{query}': {e}")
            raise
    
    def _process_search_results(self, response: Dict, query: str) -> List[Dict]:
        """Process and structure search results."""
        results = []
        
        # Extract results from response
        raw_results = response.get("results", [])
        
        for result in raw_results:
            processed_result = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0),
                "published_date": result.get("published_date"),
                "source": result.get("source", ""),
                "query": query
            }
            results.append(processed_result)
        
        return results
    
    async def search_knowledge(self, topic: str, max_results: int = 5) -> Dict:
        """Search for knowledge on a specific topic."""
        return await self.execute(
            query=topic,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
            include_images=False
        )
    
    async def search_news(self, topic: str, max_results: int = 5) -> Dict:
        """Search for recent news on a topic."""
        return await self.execute(
            query=f"recent news {topic}",
            search_depth="basic",
            max_results=max_results,
            include_answer=True,
            include_images=False
        )
    
    async def search_technical(self, query: str, max_results: int = 5) -> Dict:
        """Search for technical information."""
        return await self.execute(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
            include_images=False
        )
    
    def get_search_depths(self) -> List[str]:
        """Get available search depths."""
        return ["basic", "advanced"]
    
    def is_available(self) -> bool:
        """Check if Tavily search is available."""
        return self.client is not None and self.api_key is not None
    
    async def close(self):
        """Close the Tavily client."""
        if self.client:
            # Tavily client doesn't need explicit closing, but we can clean up
            self.client = None 