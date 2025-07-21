# 🛡️ Aegis Agent 工具选择机制详解

## 📋 概述

Aegis Agent 采用**LLM驱动的智能工具选择机制**，能够自动分析任务意图并选择合适的工具组合。这个系统不是基于硬编码规则，而是通过AI智能分析来实现动态工具选择。

## 🏗️ 系统架构

### 1. 任务分析层 (Task Analysis Layer)
```python
async def _analyze_task(self, task_description: str, context: Dict) -> Dict:
    # 使用DeepSeek API分析任务复杂度
    # 确定是否需要委托给子智能体
    # 评估所需工具类型
```

### 2. 智能工具选择层 (Intelligent Tool Selection Layer)
```python
async def _select_tools_with_llm(self, task_description: str, task_analysis: Dict) -> Dict:
    # LLM分析任务意图
    # 从可用工具中选择合适的工具
    # 生成执行计划
```

### 3. 工具执行层 (Tool Execution Layer)
```python
# 按计划执行选定的工具
# 收集工具执行结果
# 处理成功和失败的工具
```

### 4. 结果合成层 (Result Synthesis Layer)
```python
async def _generate_final_result(self, task_description: str, tool_results: List[Dict], tool_plan: Dict) -> str:
    # LLM分析所有工具结果
    # 生成综合响应
    # 格式化最终输出
```

## 🔧 工具选择流程

### 步骤1: 任务接收
```
用户输入: "搜索最近保险新闻"
↓
系统接收任务描述
```

### 步骤2: 任务分析
```
LLM分析任务:
- 任务类型: 信息搜索
- 关键词: "最近保险新闻"
- 复杂度: 简单
- 所需工具: 搜索类工具
```

### 步骤3: 工具匹配
```
可用工具: ['terminal', 'search', 'tavily_search', 'code']
↓
LLM选择: tavily_search
原因: 需要搜索最新信息，Tavily提供AI增强搜索
```

### 步骤4: 参数提取
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
    "reason": "Need to search for recent insurance news"
}
```

### 步骤5: 工具执行
```
执行tavily_search工具
↓
获取搜索结果
↓
处理结果数据
```

### 步骤6: 结果合成
```
LLM分析搜索结果
↓
生成综合报告
↓
格式化输出
```

## 🧠 LLM决策机制

### 提示词设计
```python
system_prompt = f"""You are an intelligent task planner for an AI agent. 

Available tools: {available_tools}

For each task, analyze what tools are needed and create a step-by-step execution plan.

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

Tool parameters:
- search: {{"query": "search term", "max_results": 5}}
- tavily_search: {{"query": "search term", "max_results": 5, "search_depth": "basic"}}
- terminal: {{"command": "system command"}}
- code: {{"code": "python code to execute"}}

Examples:
For "搜索最近保险新闻":
{{
    "description": "Search for recent insurance news",
    "steps": [
        {{
            "tool": "tavily_search",
            "parameters": {{"query": "最近保险新闻", "max_results": 5}},
            "reason": "Need to search for recent insurance news"
        }}
    ]
}}
"""
```

### 决策过程
1. **任务理解**: LLM分析自然语言任务描述
2. **工具匹配**: 将任务需求与可用工具进行智能匹配
3. **参数生成**: 从任务描述中提取关键信息作为工具参数
4. **计划制定**: 生成详细的执行计划

## 📊 工具选择示例

### 示例1: 信息搜索任务
```
任务: "搜索最近保险新闻"
↓
LLM分析: 需要搜索最新信息
↓
选择工具: tavily_search
↓
参数设置: {"query": "最近保险新闻", "max_results": 5}
```

### 示例2: 系统操作任务
```
任务: "查看当前目录文件"
↓
LLM分析: 需要执行系统命令
↓
选择工具: terminal
↓
参数设置: {"command": "dir"}
```

### 示例3: 编程计算任务
```
任务: "计算斐波那契数列前10项"
↓
LLM分析: 需要执行Python代码
↓
选择工具: code
↓
参数设置: {"code": "def fib(n): ..."}
```

### 示例4: 复合任务
```
任务: "分析Python项目结构并搜索最佳实践"
↓
LLM分析: 需要多个工具组合
↓
选择工具: ["terminal", "tavily_search", "code"]
↓
执行计划: 先列出文件，再搜索最佳实践，最后分析结构
```

## 🔍 工具特性匹配

### 搜索工具
- **search**: 基础网页搜索，适合一般信息查询
- **tavily_search**: AI增强搜索，适合复杂查询和最新信息

### 系统工具
- **terminal**: 系统命令执行，适合文件操作和系统信息查询

### 编程工具
- **code**: Python代码执行，适合计算和数据处理

## ⚙️ 参数提取机制

### 关键词识别
```
任务描述: "搜索最近保险新闻"
↓
关键词提取: "最近保险新闻"
↓
参数生成: {"query": "最近保险新闻"}
```

### 智能参数设置
```
任务描述: "查看当前目录文件"
↓
命令识别: 目录查看
↓
参数生成: {"command": "dir"} 或 {"command": "ls"}
```

### 默认值处理
```
任务描述: "搜索Python教程"
↓
参数生成: {
    "query": "Python教程",
    "max_results": 5,  # 默认值
    "search_depth": "basic"  # 默认值
}
```

## 🎯 优势特点

### 1. 智能性
- ✅ 基于AI的意图理解
- ✅ 动态工具选择
- ✅ 智能参数提取

### 2. 灵活性
- ✅ 支持复合任务
- ✅ 多工具协调
- ✅ 可扩展架构

### 3. 鲁棒性
- ✅ 错误处理和回退
- ✅ JSON响应清理
- ✅ 优雅降级机制

### 4. 可扩展性
- ✅ 易于添加新工具
- ✅ 模块化设计
- ✅ 配置驱动

## 🔧 工具添加指南

### 1. 创建工具类
```python
class MyCustomTool(BaseTool):
    def __init__(self):
        super().__init__("my_tool", "Description of my tool")
    
    async def execute(self, **kwargs) -> ToolResult:
        # 工具实现
        pass
```

### 2. 注册工具
```python
def _initialize_default_tools(self):
    self.tools["my_tool"] = MyCustomTool()
```

### 3. 更新提示词
```python
Tool parameters:
- my_tool: {{"param1": "value1", "param2": "value2"}}
```

## 📈 性能优化

### 1. 缓存机制
- 工具选择结果缓存
- 搜索结果缓存
- 参数提取缓存

### 2. 并行执行
- 独立工具并行执行
- 异步处理机制
- 超时控制

### 3. 错误恢复
- 工具失败时的替代方案
- 重试机制
- 降级处理

## 🎉 总结

Aegis Agent 的工具选择机制是一个**智能、灵活、可扩展**的系统，通过LLM驱动的决策过程，能够自动分析任务意图并选择合适的工具组合。这种设计使得系统能够处理各种复杂的任务，同时保持高度的可维护性和可扩展性。 