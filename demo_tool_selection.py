#!/usr/bin/env python3
"""
演示 Aegis Agent 的工具选择机制
"""

import asyncio
import json
from python.agent.core import Agent

async def demo_tool_selection_process():
    """演示工具选择过程"""
    print("🛡️ Aegis Agent - 工具选择机制演示")
    print("=" * 60)
    
    # 创建智能体实例
    agent = Agent()
    
    print(f"🔧 可用工具: {list(agent.tools.keys())}")
    print()
    
    # 演示不同任务的工具选择
    demo_tasks = [
        {
            "task": "搜索最近保险新闻",
            "expected_tools": ["tavily_search", "search"],
            "description": "信息搜索任务"
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
        print(f"🔍 演示 {i}: {task_info['task']}")
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
                        
                        print(f"   📦 {tool_name}")
                        print(f"      💭 原因: {reason}")
                        print(f"      ⚙️ 参数: {params}")
                        
                        # 检查是否符合预期
                        if tool_name in task_info['expected_tools']:
                            print(f"      ✅ 符合预期")
                        else:
                            print(f"      ⚠️ 超出预期")
                
                print(f"📋 最终结果: {result['result'][:200]}...")
            else:
                print("❌ 无法获取工具使用信息")
                
        except Exception as e:
            print(f"❌ 任务执行失败: {e}")
        
        print("\n" + "=" * 60 + "\n")

async def demo_llm_decision_making():
    """演示LLM决策过程"""
    print("🧠 LLM决策过程详解")
    print("=" * 60)
    
    agent = Agent()
    
    # 展示LLM如何分析任务
    task = "搜索最近保险新闻"
    print(f"📝 任务: {task}")
    print()
    
    # 步骤1: 任务分析
    print("1️⃣ 任务分析阶段")
    print("   - LLM分析任务的自然语言描述")
    print("   - 识别任务类型（搜索、系统操作、编程等）")
    print("   - 确定任务复杂度和所需资源")
    print()
    
    # 步骤2: 工具匹配
    print("2️⃣ 工具匹配阶段")
    print("   - 将任务需求与可用工具进行匹配")
    print("   - 考虑工具的特性和限制")
    print("   - 选择最适合的工具组合")
    print()
    
    # 步骤3: 参数提取
    print("3️⃣ 参数提取阶段")
    print("   - 从任务描述中提取关键信息")
    print("   - 为选定的工具生成合适的参数")
    print("   - 确保参数格式正确")
    print()
    
    # 实际演示
    print("🎯 实际决策演示:")
    try:
        result = await agent.execute_task(task)
        
        if 'metadata' in result and 'tool_plan' in result['metadata']:
            plan = result['metadata']['tool_plan']
            print(f"🤖 LLM决策结果:")
            print(f"   执行计划: {plan.get('description', 'N/A')}")
            
            if 'steps' in plan:
                for step in plan['steps']:
                    print(f"   选择工具: {step['tool']}")
                    print(f"   选择原因: {step.get('reason', 'N/A')}")
                    print(f"   参数设置: {step.get('parameters', {})}")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")

async def demo_tool_parameters():
    """演示工具参数设置"""
    print("\n⚙️ 工具参数设置演示")
    print("=" * 60)
    
    print("🔧 各工具的参数格式:")
    print()
    
    # 搜索工具参数
    print("🔍 搜索工具参数:")
    print("   - search: {'query': '搜索关键词', 'max_results': 5}")
    print("   - tavily_search: {'query': '搜索关键词', 'max_results': 5, 'search_depth': 'basic'}")
    print()
    
    # 终端工具参数
    print("💻 终端工具参数:")
    print("   - terminal: {'command': '系统命令'}")
    print("   - 示例: {'command': 'dir'} 或 {'command': 'ls'}")
    print()
    
    # 代码工具参数
    print("🐍 代码工具参数:")
    print("   - code: {'code': 'Python代码字符串'}")
    print("   - 示例: {'code': 'print(\"Hello World\")'}")
    print()
    
    print("🤖 LLM会自动:")
    print("   - 从任务描述中提取关键信息")
    print("   - 生成合适的参数值")
    print("   - 确保参数格式正确")

if __name__ == "__main__":
    print("🚀 启动工具选择机制演示...")
    asyncio.run(demo_tool_selection_process())
    asyncio.run(demo_llm_decision_making())
    asyncio.run(demo_tool_parameters()) 