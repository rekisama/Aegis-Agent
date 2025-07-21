# 🛡️ Aegis Agent 增强工具注册系统

## 📋 概述

Aegis Agent 的增强工具注册系统实现了您所期望的功能：**将所有工具连同详细描述注册起来，然后LLM将这个注册表和需求进行对比，选择合适的工具**。

## 🏗️ 系统架构

### 1. 工具注册表 (Tool Registry)
```python
class ToolRegistry:
    """Comprehensive tool registry with detailed descriptions."""
    
    def __init__(self):
        self.tools: Dict[str, ToolDescription] = {}
        self._initialize_tool_descriptions()
```

### 2. 工具描述结构 (Tool Description)
```python
@dataclass
class ToolDescription:
    """Detailed tool description for LLM understanding."""
    name: str
    category: ToolCategory
    description: str
    capabilities: List[str]
    use_cases: List[str]
    parameters: Dict[str, Any]
    examples: List[Dict[str, Any]]
    limitations: List[str]
```

### 3. 工具分类 (Tool Categories)
```python
class ToolCategory(Enum):
    """Tool categories for better organization."""
    SEARCH = "search"
    SYSTEM = "system"
    PROGRAMMING = "programming"
    COMMUNICATION = "communication"
    UTILITY = "utility"
```

## 🔧 工具注册示例

### Terminal Tool 注册
```python
self.tools["terminal"] = ToolDescription(
    name="terminal",
    category=ToolCategory.SYSTEM,
    description="Execute system commands and terminal operations safely",
    capabilities=[
        "Execute system commands",
        "List files and directories",
        "Check system information",
        "Run safe system utilities",
        "Navigate file system"
    ],
    use_cases=[
        "查看当前目录文件",
        "检查系统信息",
        "列出文件结构",
        "运行系统命令",
        "检查Python版本"
    ],
    parameters={
        "command": {
            "type": "string",
            "description": "System command to execute",
            "required": True,
            "examples": ["dir", "ls", "pwd", "python --version"]
        }
    },
    examples=[
        {
            "task": "查看当前目录文件",
            "parameters": {"command": "dir"},
            "reason": "Need to list files in current directory"
        }
    ],
    limitations=[
        "Only safe commands allowed",
        "No dangerous operations (rm, format, etc.)",
        "Limited to system utilities"
    ]
)
```

### Tavily Search Tool 注册
```python
self.tools["tavily_search"] = ToolDescription(
    name="tavily_search",
    category=ToolCategory.SEARCH,
    description="AI-powered search with enhanced understanding and answer generation",
    capabilities=[
        "AI-enhanced search",
        "Generate direct answers",
        "Understand complex queries",
        "Provide structured results",
        "Include answer synthesis"
    ],
    use_cases=[
        "搜索最新新闻",
        "查找技术信息",
        "获取AI生成的答案",
        "复杂信息查询",
        "需要综合回答的问题"
    ],
    parameters={
        "query": {
            "type": "string",
            "description": "Search query",
            "required": True,
            "examples": ["最近保险新闻", "AI发展趋势", "Python最佳实践"]
        },
        "search_depth": {
            "type": "string",
            "description": "Search depth level",
            "required": False,
            "default": "basic",
            "options": ["basic", "advanced"]
        }
    },
    examples=[
        {
            "task": "搜索最近保险新闻",
            "parameters": {"query": "最近保险新闻", "max_results": 5, "search_depth": "basic"},
            "reason": "Need to find recent insurance industry news"
        }
    ],
    limitations=[
        "Requires API key",
        "May have rate limits",
        "Depends on external service"
    ]
)
```

## 🧠 LLM工具选择机制

### 1. 工具注册表生成
```python
def generate_tool_summary_for_llm(self) -> str:
    """Generate a comprehensive tool summary for LLM."""
    summary = "Available Tools:\n\n"
    
    for name, tool in self.tools.items():
        summary += f"📦 {name} ({tool.category.value})\n"
        summary += f"   Description: {tool.description}\n"
        summary += f"   Capabilities: {', '.join(tool.capabilities)}\n"
        summary += f"   Use Cases: {', '.join(tool.use_cases)}\n"
        summary += f"   Parameters: {tool.parameters}\n"
        summary += f"   Examples:\n"
        for example in tool.examples:
            summary += f"     - Task: {example['task']}\n"
            summary += f"       Parameters: {example['parameters']}\n"
            summary += f"       Reason: {example['reason']}\n"
        summary += f"   Limitations: {', '.join(tool.limitations)}\n\n"
    
    return summary
```

### 2. LLM提示词设计
```python
system_prompt = f"""You are an intelligent task planner for an AI agent. 

Your job is to analyze the user's task and select the most appropriate tools from the available tool registry.

{tool_summary}

For each task, carefully analyze:
1. What the user wants to accomplish
2. Which tools have the capabilities to help
3. The best parameters for each selected tool
4. The order of tool execution

Guidelines:
- Choose tools based on their capabilities and use cases
- Consider tool limitations when making selections
- Extract relevant information from the task description for parameters
- For search tasks, prefer tavily_search for complex queries and recent information
- For system operations, use terminal with safe commands
- For calculations and data processing, use code tool
- Provide clear reasoning for each tool selection
"""
```

## 📊 工具选择流程

### 步骤1: 任务分析
```
用户输入: "搜索最近保险新闻"
↓
LLM分析任务需求:
- 需要搜索功能
- 需要最新信息
- 需要结构化结果
```

### 步骤2: 工具注册表对比
```
可用工具:
- search: 基础网页搜索
- tavily_search: AI增强搜索，支持答案生成
- terminal: 系统命令执行
- code: Python代码执行

对比结果:
- tavily_search 最适合（AI增强，支持最新信息）
```

### 步骤3: 参数提取
```
任务: "搜索最近保险新闻"
↓
提取参数:
{
    "tool": "tavily_search",
    "parameters": {
        "query": "最近保险新闻",
        "max_results": 5,
        "search_depth": "basic"
    },
    "reason": "Need to find recent insurance industry news with AI-enhanced search"
}
```

### 步骤4: 执行计划生成
```json
{
    "description": "Search for recent insurance news using AI-enhanced search",
    "steps": [
        {
            "tool": "tavily_search",
            "parameters": {
                "query": "最近保险新闻",
                "max_results": 5,
                "search_depth": "basic"
            },
            "reason": "Need to find recent insurance industry news with AI-enhanced search"
        }
    ]
}
```

## 🎯 优势特点

### 1. 详细描述
- ✅ 每个工具都有完整的描述
- ✅ 包含能力、用例、参数、示例
- ✅ 明确说明限制和注意事项

### 2. 智能匹配
- ✅ LLM基于工具描述进行选择
- ✅ 考虑工具能力和限制
- ✅ 支持多工具组合

### 3. 参数优化
- ✅ 自动提取任务中的关键信息
- ✅ 生成合适的参数值
- ✅ 提供默认值和示例

### 4. 可扩展性
- ✅ 易于添加新工具
- ✅ 标准化的注册格式
- ✅ 支持工具分类

## 🔧 添加新工具指南

### 1. 创建工具类
```python
class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__("my_tool", "Description of my tool")
    
    async def execute(self, **kwargs) -> ToolResult:
        # 工具实现
        pass
```

### 2. 注册工具描述
```python
self.tools["my_tool"] = ToolDescription(
    name="my_tool",
    category=ToolCategory.UTILITY,
    description="Description of what the tool does",
    capabilities=[
        "Capability 1",
        "Capability 2"
    ],
    use_cases=[
        "Use case 1",
        "Use case 2"
    ],
    parameters={
        "param1": {
            "type": "string",
            "description": "Parameter description",
            "required": True,
            "examples": ["example1", "example2"]
        }
    },
    examples=[
        {
            "task": "Example task",
            "parameters": {"param1": "value1"},
            "reason": "Why this tool is needed"
        }
    ],
    limitations=[
        "Limitation 1",
        "Limitation 2"
    ]
)
```

### 3. 添加到智能体
```python
def _initialize_default_tools(self):
    self.tools["my_tool"] = MyCustomTool()
```

## 📈 实际效果

### 任务1: "搜索最近保险新闻"
```
LLM分析:
- 需要搜索功能 ✓
- 需要最新信息 ✓
- tavily_search 最适合 ✓

选择: tavily_search
参数: {"query": "最近保险新闻", "max_results": 5}
```

### 任务2: "查看当前目录文件"
```
LLM分析:
- 需要系统操作 ✓
- 需要文件列表 ✓
- terminal 最适合 ✓

选择: terminal
参数: {"command": "dir"}
```

### 任务3: "计算斐波那契数列"
```
LLM分析:
- 需要计算功能 ✓
- 需要编程执行 ✓
- code 最适合 ✓

选择: code
参数: {"code": "def fib(n): ..."}
```

## 🎉 总结

这个增强的工具注册系统完美实现了您的需求：

1. **工具注册**: 所有工具都有详细的描述、能力、用例、参数和示例
2. **LLM对比**: LLM将任务需求与工具注册表进行智能对比
3. **智能选择**: 基于工具能力和限制选择最合适的工具
4. **参数优化**: 自动提取任务信息并生成合适的参数

这种设计使得系统能够：
- 更准确地选择工具
- 更好地理解工具能力
- 更智能地处理参数
- 更容易扩展新工具

这就是Aegis Agent如何实现"将所有工具连同描述注册起来，然后LLM将这个注册表和需求进行对比，选择合适的"的完整机制！ 