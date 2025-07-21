#!/usr/bin/env python3
"""
测试 Tavily 搜索功能
"""

import asyncio
from python.agent.core import Agent

async def test_tavily_search():
    """测试Tavily搜索功能"""
    print("🔍 测试 Tavily 搜索功能")
    print("=" * 50)
    
    # 创建智能体实例
    agent = Agent()
    
    # 检查Tavily工具是否可用
    tavily_tool = agent.get_tool("tavily_search")
    if tavily_tool and hasattr(tavily_tool, 'is_available'):
        if tavily_tool.is_available():
            print("✅ Tavily搜索工具已初始化")
        else:
            print("❌ Tavily搜索工具不可用")
            return
    else:
        print("❌ Tavily搜索工具未找到")
        return
    
    # 测试搜索任务
    test_tasks = [
        "搜索最近保险新闻",
        "查找Python机器学习教程",
        "查询2024年AI发展趋势"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔍 测试 {i}: {task}")
        print("-" * 40)
        
        try:
            # 执行任务
            result = await agent.execute_task(task)
            
            # 显示结果
            print(f"✅ 任务完成!")
            print(f"📋 结果: {result['result'][:300]}...")
            
            # 显示元数据
            if 'metadata' in result and 'tool_plan' in result['metadata']:
                plan = result['metadata']['tool_plan']
                print(f"🤖 执行计划: {plan.get('description', 'N/A')}")
                
                if 'steps' in plan:
                    print("🔧 使用的工具:")
                    for step in plan['steps']:
                        print(f"   - {step['tool']}: {step.get('reason', 'N/A')}")
            
        except Exception as e:
            print(f"❌ 任务执行失败: {e}")
            import traceback
            traceback.print_exc()
        
        print()

async def test_direct_tavily():
    """直接测试Tavily工具"""
    print("\n🧪 直接测试 Tavily 工具")
    print("=" * 50)
    
    from python.tools.tavily_search import TavilySearchTool
    
    tavily_tool = TavilySearchTool()
    
    if not tavily_tool.is_available():
        print("❌ Tavily工具不可用")
        return
    
    # 测试基本搜索
    print("🔍 测试基本搜索...")
    result = await tavily_tool.execute(
        query="最近保险新闻",
        max_results=3,
        search_depth="basic"
    )
    
    if result.success:
        print("✅ 搜索成功!")
        data = result.data
        print(f"📊 找到 {data['total_results']} 个结果")
        
        if data.get('answer'):
            print(f"🤖 AI回答: {data['answer']}")
        
        for i, item in enumerate(data['results'][:3], 1):
            print(f"\n📄 结果 {i}:")
            print(f"   标题: {item['title']}")
            print(f"   链接: {item['url']}")
            print(f"   内容: {item['content'][:100]}...")
    else:
        print(f"❌ 搜索失败: {result.error}")

if __name__ == "__main__":
    asyncio.run(test_tavily_search())
    asyncio.run(test_direct_tavily()) 