#!/usr/bin/env python3
"""
Enhanced Agent Test
测试改进后的 Agent 是否能正确创建时间工具
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

from python.agent.self_evolving_core import create_self_evolving_agent
from python.agent.core import AgentConfig


async def test_enhanced_agent():
    """测试改进后的 Agent"""
    
    print("🧪 Enhanced Agent Test")
    print("=" * 50)
    
    # 创建 Agent
    config = AgentConfig(
        name="Enhanced Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = create_self_evolving_agent(config)
    
    print(f"🤖 Created enhanced agent: {agent.config.name}")
    
    # 测试时间查询任务
    test_tasks = [
        "华盛顿现在几点了",
        "北京现在几点了", 
        "东京现在几点了",
        "伦敦现在几点了"
    ]
    
    for task in test_tasks:
        print(f"\n🕐 Testing task: {task}")
        print("-" * 50)
        
        try:
            # 执行任务
            result = await agent.execute_task(task)
            
            print(f"📋 Task result: {result.get('result', 'No result')}")
            
            # 检查是否创建了新工具
            from python.agent.dynamic_tool_creator import dynamic_tool_creator
            stats = dynamic_tool_creator.get_tool_statistics()
            tools = stats.get("tools", [])
            
            if tools:
                print(f"🛠️  Dynamic tools created: {len(tools)}")
                for tool in tools:
                    print(f"   • {tool['name']}: {tool['description']}")
            else:
                print("ℹ️  No dynamic tools created")
                
        except Exception as e:
            print(f"❌ Task failed: {e}")
    
    print("\n🎉 Enhanced Agent Test Completed!")
    print("=" * 50)


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await test_enhanced_agent()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 