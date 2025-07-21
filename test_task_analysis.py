#!/usr/bin/env python3
"""
Task Analysis Test
测试任务分析功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


async def test_task_analysis():
    """测试任务分析功能"""
    
    print("🧪 Task Analysis Test")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Test Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    print(f"🤖 Created test agent: {agent.config.name}")
    
    # 测试时间查询任务
    test_task = "东京现在几点了"
    
    print(f"\n🔍 Testing task: {test_task}")
    print("-" * 50)
    
    try:
        # 直接测试任务分析功能
        analysis = await agent._analyze_task_for_tool_creation(test_task)
        
        print(f"📊 Analysis Result:")
        print(f"   Should create tool: {analysis.get('should_create_tool', False)}")
        print(f"   Tool name: {analysis.get('tool_name', 'N/A')}")
        print(f"   Tool description: {analysis.get('tool_description', 'N/A')}")
        print(f"   Implementation approach: {analysis.get('implementation_approach', 'N/A')}")
        print(f"   Reasoning: {analysis.get('reasoning', 'N/A')}")
        print(f"   Existing tools analysis: {analysis.get('existing_tools_analysis', 'N/A')}")
        
        if analysis.get('should_create_tool', False):
            print(f"\n🔧 Testing tool creation...")
            
            # 测试工具创建
            tool_created = await agent._create_dynamic_tool_from_analysis(analysis)
            print(f"   Tool creation: {'✅ Success' if tool_created else '❌ Failed'}")
            
            if tool_created:
                # 检查动态工具是否被创建
                from python.agent.dynamic_tool_creator import dynamic_tool_creator
                stats = dynamic_tool_creator.get_tool_statistics()
                tools = stats.get("tools", [])
                
                if tools:
                    print(f"   🛠️  Dynamic tools available: {len(tools)}")
                    for tool in tools:
                        print(f"      • {tool['name']}: {tool['description']}")
                else:
                    print(f"   ℹ️  No dynamic tools found")
        else:
            print(f"   ℹ️  No specialized tool needed")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Task Analysis Test Completed!")
    print("=" * 50)


async def test_full_execution():
    """测试完整执行流程"""
    
    print("\n🚀 Full Execution Test")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Test Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    test_task = "东京现在几点了"
    
    print(f"🔍 Executing task: {test_task}")
    print("-" * 50)
    
    try:
        # 执行任务
        result = await agent.execute_task(test_task)
        
        print(f"✅ Task completed")
        print(f"📊 Result: {result.get('result', 'No result')}")
        
        # 检查是否创建了动态工具
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
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Full Execution Test Completed!")
    print("=" * 50)


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await test_task_analysis()
        await test_full_execution()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 