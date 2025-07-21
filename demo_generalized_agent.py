#!/usr/bin/env python3
"""
Generalized Agent Demo
演示完全泛化的工具创建系统
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


async def demo_generalized_agent():
    """演示完全泛化的 Agent"""
    
    print("🤖 Generalized Agent Demo")
    print("=" * 60)
    print("这个演示展示了 Agent 如何自主分析任务并创建专门工具")
    print("=" * 60)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    # 创建 Agent
    config = AgentConfig(
        name="🛡️  Aegis Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    print(f"✅ Created {agent.config.name}")
    print()
    
    # 演示任务
    demo_tasks = [
        {
            "task": "现在伦敦几点了",
            "description": "时间查询任务 - Agent 应该识别需要创建时间工具"
        },
        {
            "task": "北京天气怎么样", 
            "description": "天气查询任务 - Agent 应该识别需要创建天气工具"
        },
        {
            "task": "计算 123 * 456 的结果",
            "description": "计算任务 - Agent 应该识别需要创建计算工具"
        },
        {
            "task": "翻译 'Hello World' 为中文",
            "description": "翻译任务 - Agent 应该识别需要创建翻译工具"
        }
    ]
    
    for i, demo in enumerate(demo_tasks, 1):
        print(f"🔍 Demo {i}: {demo['task']}")
        print(f"📝 Description: {demo['description']}")
        print("-" * 60)
        
        try:
            # 执行任务
            result = await agent.execute_task(demo['task'])
            
            print(f"✅ Task completed")
            print(f"📊 Result: {result.get('result', 'No result')}")
            
            # 检查是否创建了动态工具
            from python.agent.dynamic_tool_creator import dynamic_tool_creator
            stats = dynamic_tool_creator.get_tool_statistics()
            tools = stats.get("tools", [])
            
            if tools:
                print(f"🛠️  Dynamic tools created in this session: {len(tools)}")
                for tool in tools[-1:]:  # 只显示最新创建的工具
                    print(f"   • {tool['name']}: {tool['description']}")
            else:
                print("ℹ️  No new dynamic tools created")
                
        except Exception as e:
            print(f"❌ Task failed: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("🎉 Demo completed!")
    print("=" * 60)
    
    # 显示所有创建的工具
    from python.agent.dynamic_tool_creator import dynamic_tool_creator
    stats = dynamic_tool_creator.get_tool_statistics()
    tools = stats.get("tools", [])
    
    if tools:
        print(f"📋 All dynamic tools created: {len(tools)}")
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool['name']}: {tool['description']}")
    else:
        print("📋 No dynamic tools were created")
    
    print("=" * 60)


async def demo_agent_learning():
    """演示 Agent 学习能力"""
    
    print("\n🧠 Agent Learning Demo")
    print("=" * 60)
    print("这个演示展示了 Agent 如何从任务中学习并改进")
    print("=" * 60)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Learning Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    # 重复执行相似任务，观察 Agent 的学习
    similar_tasks = [
        "现在东京几点了",
        "现在纽约几点了", 
        "现在巴黎几点了",
        "现在悉尼几点了"
    ]
    
    for i, task in enumerate(similar_tasks, 1):
        print(f"🕐 Task {i}: {task}")
        
        try:
            result = await agent.execute_task(task)
            print(f"✅ Completed: {result.get('result', 'No result')}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        print()
    
    print("🎉 Learning demo completed!")
    print("=" * 60)


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await demo_generalized_agent()
        await demo_agent_learning()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 