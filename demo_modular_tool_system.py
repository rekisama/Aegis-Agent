#!/usr/bin/env python3
"""
演示模块化工具注册系统
展示如何将工具描述独立配置，避免代码臃肿
"""

import asyncio
from python.agent.tool_manager import tool_manager
from python.agent.tool_descriptions import TOOL_DESCRIPTIONS, get_available_tools
from python.agent.core import Agent

async def demo_modular_tool_system():
    """演示模块化工具注册系统"""
    print("🛡️ Aegis Agent - 模块化工具注册系统演示")
    print("=" * 60)
    
    # 1. 显示独立配置的工具描述
    print("📋 1. 独立配置的工具描述")
    print("-" * 40)
    
    available_tools = get_available_tools()
    print(f"可用工具数量: {len(available_tools)}")
    print(f"工具列表: {available_tools}")
    print()
    
    # 2. 显示工具描述配置
    print("📝 2. 工具描述配置示例")
    print("-" * 40)
    
    for tool_name, config in TOOL_DESCRIPTIONS.items():
        print(f"📦 {tool_name}:")
        print(f"   类别: {config['category'].value}")
        print(f"   描述: {config['description']}")
        print(f"   能力: {len(config['capabilities'])} 项")
        print(f"   用例: {len(config['use_cases'])} 项")
        print(f"   参数: {len(config['parameters'])} 个")
        print(f"   示例: {len(config['examples'])} 个")
        print(f"   限制: {len(config['limitations'])} 项")
        print()
    
    # 3. 演示工具管理器功能
    print("🔧 3. 工具管理器功能演示")
    print("-" * 40)
    
    # 注册工具
    from python.tools.terminal import TerminalTool
    from python.tools.search import SearchTool
    from python.tools.tavily_search import TavilySearchTool
    from python.tools.code import CodeExecutionTool
    
    print("注册工具...")
    tool_manager.register_tool("terminal", TerminalTool)
    tool_manager.register_tool("search", SearchTool)
    tool_manager.register_tool("tavily_search", TavilySearchTool)
    tool_manager.register_tool("code", CodeExecutionTool)
    
    print(f"已注册工具: {tool_manager.list_available_tools()}")
    print()
    
    # 4. 演示工具分类
    print("📂 4. 工具分类演示")
    print("-" * 40)
    
    categories = tool_manager.get_tool_categories()
    for category, tools in categories.items():
        if tools:
            print(f"📂 {category.value.upper()}:")
            for tool_name in tools:
                tool_desc = tool_manager.get_tool_description(tool_name)
                if tool_desc:
                    print(f"   📦 {tool_name}: {tool_desc.description}")
            print()
    
    # 5. 演示工具帮助信息
    print("❓ 5. 工具帮助信息演示")
    print("-" * 40)
    
    for tool_name in ["tavily_search", "terminal"]:
        help_text = tool_manager.get_tool_help(tool_name)
        print(f"📦 {tool_name} 帮助:")
        print(help_text[:300] + "..." if len(help_text) > 300 else help_text)
        print()
    
    # 6. 演示参数验证
    print("✅ 6. 参数验证演示")
    print("-" * 40)
    
    # 测试 tavily_search 参数验证
    test_params = {"query": "测试查询"}
    validated_params = tool_manager.validate_tool_parameters("tavily_search", test_params)
    print(f"原始参数: {test_params}")
    print(f"验证后参数: {validated_params}")
    print()
    
    # 7. 演示任务匹配
    print("🎯 7. 任务匹配演示")
    print("-" * 40)
    
    test_tasks = [
        "搜索最近保险新闻",
        "查看当前目录文件",
        "计算斐波那契数列",
        "分析Python项目结构"
    ]
    
    for task in test_tasks:
        matching_tools = tool_manager.find_best_tools_for_task(task)
        print(f"任务: {task}")
        print(f"匹配工具: {matching_tools}")
        print()
    
    # 8. 演示系统摘要
    print("📊 8. 系统摘要演示")
    print("-" * 40)
    
    system_summary = tool_manager.get_system_summary()
    print(system_summary)

async def demo_dynamic_tool_registration():
    """演示动态工具注册"""
    print("\n🔄 动态工具注册演示")
    print("=" * 60)
    
    # 创建一个自定义工具
    from python.tools.base import BaseTool, ToolResult
    
    class CustomTool(BaseTool):
        def __init__(self):
            super().__init__("custom_tool", "A custom demonstration tool")
        
        async def execute(self, **kwargs) -> ToolResult:
            message = kwargs.get("message", "Hello from custom tool!")
            return ToolResult(
                success=True,
                data={"message": message, "timestamp": "2024-01-01"},
                error=None
            )
    
    # 自定义工具描述配置
    custom_tool_config = {
        "name": "custom_tool",
        "category": "utility",
        "description": "A custom demonstration tool for testing",
        "capabilities": [
            "Custom message generation",
            "Timestamp creation",
            "Demonstration purposes"
        ],
        "use_cases": [
            "测试自定义工具",
            "演示工具注册",
            "验证工具系统"
        ],
        "parameters": {
            "message": {
                "type": "string",
                "description": "Message to display",
                "required": False,
                "default": "Hello from custom tool!",
                "examples": ["Hello World", "Custom message"]
            }
        },
        "examples": [
            {
                "task": "测试自定义工具",
                "parameters": {"message": "Hello World"},
                "reason": "Need to test custom tool functionality"
            }
        ],
        "limitations": [
            "Demo tool only",
            "No real functionality",
            "For testing purposes"
        ]
    }
    
    print("注册自定义工具...")
    tool_manager.register_tool("custom_tool", CustomTool, custom_tool_config)
    
    print(f"更新后的工具列表: {tool_manager.list_available_tools()}")
    
    # 测试自定义工具
    custom_tool = tool_manager.get_tool_instance("custom_tool")
    if custom_tool:
        result = await custom_tool.execute(message="测试消息")
        print(f"自定义工具执行结果: {result.data}")
    
    # 获取自定义工具帮助
    help_text = tool_manager.get_tool_help("custom_tool")
    print(f"自定义工具帮助:\n{help_text}")
    
    # 卸载自定义工具
    print("卸载自定义工具...")
    tool_manager.unregister_tool("custom_tool")
    print(f"卸载后的工具列表: {tool_manager.list_available_tools()}")

async def demo_agent_integration():
    """演示与智能体的集成"""
    print("\n🤖 智能体集成演示")
    print("=" * 60)
    
    # 创建智能体实例
    agent = Agent()
    
    # 执行任务测试
    test_task = "搜索最近保险新闻"
    print(f"执行任务: {test_task}")
    
    try:
        result = await agent.execute_task(test_task)
        print(f"任务执行成功: {result['status']}")
        print(f"结果预览: {result['result'][:200]}...")
    except Exception as e:
        print(f"任务执行失败: {e}")

if __name__ == "__main__":
    print("🚀 启动模块化工具注册系统演示...")
    asyncio.run(demo_modular_tool_system())
    asyncio.run(demo_dynamic_tool_registration())
    asyncio.run(demo_agent_integration()) 