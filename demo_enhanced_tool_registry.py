#!/usr/bin/env python3
"""
演示增强的工具注册系统
"""

import asyncio
from python.agent.core import Agent
from python.agent.tool_registry import tool_registry

async def demo_tool_registry():
    """演示工具注册表系统"""
    print("🛡️ Aegis Agent - 增强工具注册系统演示")
    print("=" * 60)
    
    # 显示工具注册表
    print("📋 工具注册表概览:")
    print("-" * 40)
    
    all_tools = tool_registry.get_all_tools()
    for name, tool in all_tools.items():
        print(f"📦 {name} ({tool.category.value})")
        print(f"   📝 描述: {tool.description}")
        print(f"   🔧 能力: {', '.join(tool.capabilities[:3])}...")
        print(f"   💡 用例: {', '.join(tool.use_cases[:3])}...")
        print()
    
    print("=" * 60)
    print("🧠 LLM工具选择演示")
    print("=" * 60)
    
    # 创建智能体实例
    agent = Agent()
    
    # 演示不同任务的工具选择
    demo_tasks = [
        {
            "task": "搜索最近保险新闻",
            "expected_tools": ["tavily_search"],
            "description": "需要最新信息的搜索任务"
        },
        {
            "task": "查看当前目录文件",
            "expected_tools": ["terminal"],
            "description": "系统操作任务"
        },
        {
            "task": "计算斐波那契数列前10项",
            "expected_tools": ["code"],
            "description": "编程计算任务"
        },
        {
            "task": "分析Python项目结构并搜索最佳实践",
            "expected_tools": ["terminal", "tavily_search", "code"],
            "description": "复合任务"
        }
    ]
    
    for i, task_info in enumerate(demo_tasks, 1):
        print(f"\n🔍 演示 {i}: {task_info['task']}")
        print(f"📝 任务类型: {task_info['description']}")
        print(f"🎯 预期工具: {task_info['expected_tools']}")
        print("-" * 50)
        
        try:
            # 执行任务
            result = await agent.execute_task(task_info['task'])
            
            # 分析工具使用情况
            if 'metadata' in result and 'tool_plan' in result['metadata']:
                plan = result['metadata']['tool_plan']
                print(f"🤖 LLM选择的执行计划: {plan.get('description', 'N/A')}")
                
                if 'steps' in plan:
                    print("🔧 实际使用的工具:")
                    for step in plan['steps']:
                        tool_name = step['tool']
                        reason = step.get('reason', 'N/A')
                        params = step.get('parameters', {})
                        
                        # 获取工具的详细信息
                        tool_desc = tool_registry.get_tool_description(tool_name)
                        if tool_desc:
                            print(f"   📦 {tool_name} ({tool_desc.category.value})")
                            print(f"      💭 原因: {reason}")
                            print(f"      ⚙️ 参数: {params}")
                            print(f"      📝 描述: {tool_desc.description}")
                            
                            # 检查是否符合预期
                            if tool_name in task_info['expected_tools']:
                                print(f"      ✅ 符合预期")
                            else:
                                print(f"      ⚠️ 超出预期")
                        else:
                            print(f"   📦 {tool_name} (未注册)")
                
                print(f"📋 最终结果: {result['result'][:200]}...")
            else:
                print("❌ 无法获取工具使用信息")
                
        except Exception as e:
            print(f"❌ 任务执行失败: {e}")
        
        print()

async def demo_tool_capabilities():
    """演示工具能力匹配"""
    print("\n🔍 工具能力匹配演示")
    print("=" * 60)
    
    test_tasks = [
        "搜索Python教程",
        "查看系统信息",
        "计算数学公式",
        "查找最新技术新闻"
    ]
    
    for task in test_tasks:
        print(f"\n📝 任务: {task}")
        
        # 使用工具注册表进行匹配
        matching_tools = tool_registry.find_best_tools_for_task(task)
        print(f"🎯 匹配的工具: {matching_tools}")
        
        # 显示匹配的工具详情
        for tool_name in matching_tools:
            tool_desc = tool_registry.get_tool_description(tool_name)
            if tool_desc:
                print(f"   📦 {tool_name}:")
                print(f"      📝 {tool_desc.description}")
                print(f"      🔧 能力: {', '.join(tool_desc.capabilities[:2])}...")
        
        print()

async def demo_tool_parameters():
    """演示工具参数说明"""
    print("\n⚙️ 工具参数说明演示")
    print("=" * 60)
    
    # 显示每个工具的详细参数
    for name, tool in tool_registry.get_all_tools().items():
        print(f"\n📦 {name} 参数说明:")
        print(f"   📝 描述: {tool.description}")
        print(f"   ⚙️ 参数:")
        for param_name, param_info in tool.parameters.items():
            print(f"      - {param_name}: {param_info['description']}")
            if 'examples' in param_info:
                print(f"        示例: {param_info['examples']}")
            if 'default' in param_info:
                print(f"        默认值: {param_info['default']}")
        print(f"   ⚠️ 限制: {', '.join(tool.limitations)}")

if __name__ == "__main__":
    print("🚀 启动增强工具注册系统演示...")
    asyncio.run(demo_tool_registry())
    asyncio.run(demo_tool_capabilities())
    asyncio.run(demo_tool_parameters()) 