"""
Tool Descriptions Configuration
独立存储所有工具的详细描述，便于维护和扩展。
"""

from typing import Dict, Any
from enum import Enum

class ToolCategory(Enum):
    """Tool categories for better organization."""
    SEARCH = "search"
    SYSTEM = "system"
    PROGRAMMING = "programming"
    COMMUNICATION = "communication"
    UTILITY = "utility"

# 工具描述配置
TOOL_DESCRIPTIONS = {
    "terminal": {
        "name": "terminal",
        "category": ToolCategory.SYSTEM,
        "description": "Execute system commands and terminal operations safely",
        "capabilities": [
            "Execute system commands",
            "List files and directories",
            "Check system information",
            "Run safe system utilities",
            "Navigate file system"
        ],
        "use_cases": [
            "查看当前目录文件",
            "检查系统信息",
            "列出文件结构",
            "运行系统命令",
            "检查Python版本"
        ],
        "parameters": {
            "command": {
                "type": "string",
                "description": "System command to execute",
                "required": True,
                "examples": ["dir", "ls", "pwd", "python --version"]
            },
            "working_dir": {
                "type": "string", 
                "description": "Working directory for command",
                "required": False,
                "default": "current directory"
            }
        },
        "examples": [
            {
                "task": "查看当前目录文件",
                "parameters": {"command": "dir"},
                "reason": "Need to list files in current directory"
            },
            {
                "task": "检查Python版本",
                "parameters": {"command": "python --version"},
                "reason": "Need to check Python installation"
            }
        ],
        "limitations": [
            "Only safe commands allowed",
            "No dangerous operations (rm, format, etc.)",
            "Limited to system utilities"
        ]
    },
    
    "search": {
        "name": "search",
        "category": ToolCategory.SEARCH,
        "description": "Perform basic web searches using multiple search engines",
        "capabilities": [
            "Web search across multiple engines",
            "Extract search results",
            "Parse webpage content",
            "Filter and rank results",
            "Handle different search engines"
        ],
        "use_cases": [
            "搜索一般信息",
            "查找网页内容",
            "获取搜索结果",
            "查找文档资料"
        ],
        "parameters": {
            "query": {
                "type": "string",
                "description": "Search query",
                "required": True,
                "examples": ["Python tutorial", "machine learning basics"]
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results",
                "required": False,
                "default": 5
            },
            "engine": {
                "type": "string",
                "description": "Search engine to use",
                "required": False,
                "default": "google",
                "options": ["google", "bing", "duckduckgo"]
            }
        },
        "examples": [
            {
                "task": "搜索Python教程",
                "parameters": {"query": "Python tutorial", "max_results": 5},
                "reason": "Need to find Python learning resources"
            }
        ],
        "limitations": [
            "Basic search functionality",
            "Limited to web search",
            "May not handle complex queries well"
        ]
    },
    
    # "tavily_search": {  # Disabled Tavily search
    #     "name": "tavily_search",
    #     "category": ToolCategory.SEARCH,
    #     "description": "AI-powered search with enhanced understanding and answer generation",
    #     "capabilities": [
    #         "AI-enhanced search",
    #         "Generate direct answers",
    #         "Understand complex queries",
    #         "Provide structured results",
    #         "Include answer synthesis"
    #     ],
    #     "use_cases": [
    #         "搜索最新新闻",
    #         "查找技术信息",
    #         "获取AI生成的答案",
    #         "复杂信息查询",
    #         "需要综合回答的问题"
    #     ],
    #     "parameters": {
    #         "query": {
    #             "type": "string",
    #             "description": "Search query",
    #             "required": True,
    #             "examples": ["最近保险新闻", "AI发展趋势", "Python最佳实践"]
    #         },
    #         "max_results": {
    #             "type": "integer",
    #             "description": "Maximum number of results",
    #             "required": False,
    #             "default": 5
    #         },
    #         "search_depth": {
    #             "type": "string",
    #             "description": "Search depth level",
    #             "required": False,
    #             "default": "basic",
    #             "options": ["basic", "advanced"]
    #         },
    #         "include_answer": {
    #             "type": "boolean",
    #             "description": "Include AI-generated answer",
    #             "required": False,
    #             "default": True
    #         }
    #     },
    #     "examples": [
    #         {
    #             "task": "搜索最近保险新闻",
    #             "parameters": {"query": "最近保险新闻", "max_results": 5, "search_depth": "basic"},
    #             "reason": "Need to find recent insurance industry news"
    #         },
    #         {
    #             "task": "查询AI发展趋势",
    #             "parameters": {"query": "2024年AI发展趋势", "search_depth": "advanced"},
    #             "reason": "Need comprehensive information about AI trends"
    #         }
    #     ],
    #     "limitations": [
    #         "Requires API key",
    #         "May have rate limits",
    #         "Depends on external service"
    #     ]
    # },
    
    "code": {
        "name": "code",
        "category": ToolCategory.PROGRAMMING,
        "description": "Execute Python code safely in a controlled environment",
        "capabilities": [
            "Execute Python code",
            "Perform calculations",
            "Data processing",
            "File operations",
            "Generate reports"
        ],
        "use_cases": [
            "计算数学公式",
            "处理数据",
            "生成图表",
            "执行算法",
            "创建文件"
        ],
        "parameters": {
            "code": {
                "type": "string",
                "description": "Python code to execute",
                "required": True,
                "examples": ["print('Hello World')", "import math; print(math.pi)"]
            },
            "timeout": {
                "type": "integer",
                "description": "Execution timeout in seconds",
                "required": False,
                "default": 30
            }
        },
        "examples": [
            {
                "task": "计算斐波那契数列",
                "parameters": {
                    "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""
                },
                "reason": "Need to calculate Fibonacci sequence"
            }
        ],
        "limitations": [
            "Only safe Python modules allowed",
            "No system access",
            "Limited execution time",
            "No network access"
        ]
    }
}

# 工具分类配置
TOOL_CATEGORIES = {
    ToolCategory.SEARCH: {
        "description": "Search and information retrieval tools",
        "tools": ["search"]  # Removed tavily_search
    },
    ToolCategory.SYSTEM: {
        "description": "System operation and management tools",
        "tools": ["terminal"]
    },
    ToolCategory.PROGRAMMING: {
        "description": "Code execution and programming tools",
        "tools": ["code"]
    },
    ToolCategory.COMMUNICATION: {
        "description": "Communication and messaging tools",
        "tools": []
    },
    ToolCategory.UTILITY: {
        "description": "Utility and helper tools",
        "tools": []
    }
}

def get_tool_description(tool_name: str) -> Dict[str, Any]:
    """Get tool description by name."""
    return TOOL_DESCRIPTIONS.get(tool_name, {})

def get_all_tool_descriptions() -> Dict[str, Dict[str, Any]]:
    """Get all tool descriptions."""
    return TOOL_DESCRIPTIONS.copy()

def get_tools_by_category(category: ToolCategory) -> Dict[str, Dict[str, Any]]:
    """Get tools filtered by category."""
    return {name: desc for name, desc in TOOL_DESCRIPTIONS.items() 
            if desc.get("category") == category}

def get_available_tools() -> list:
    """Get list of available tool names."""
    return list(TOOL_DESCRIPTIONS.keys()) 