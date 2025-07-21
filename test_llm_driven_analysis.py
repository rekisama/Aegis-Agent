#!/usr/bin/env python3
"""
LLM-Driven Task Analysis Test
测试完全由 LLM 驱动的任务分析
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


async def test_llm_driven_analysis():
    """测试完全由 LLM 驱动的任务分析"""
    
    print("🧪 LLM-Driven Task Analysis Test")
    print("=" * 50)
    print("这个测试验证 Agent 是否完全由 LLM 自主判断任务类型")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="LLM-Driven Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    print(f"🤖 Created agent: {agent.config.name}")
    
    # 测试各种不同类型的任务
    test_tasks = [
        "东京现在几点了",
        "北京天气怎么样",
        "计算 123 * 456 的结果",
        "翻译 'Hello World' 为中文",
        "获取美元兑人民币的汇率",
        "分析这段文本的情感倾向：今天天气真好，心情很愉快",
        "生成一个随机密码",
        "检查这个邮箱地址是否有效：test@example.com",
        "帮我写一个 Python 函数",
        "查找最新的科技新闻"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔍 Test {i}: {task}")
        print("-" * 50)
        
        try:
            # 直接测试任务分析功能
            analysis = await agent._analyze_task_for_tool_creation(task)
            
            print(f"📊 Analysis Result:")
            print(f"   Should create tool: {analysis.get('should_create_tool', False)}")
            
            if analysis.get('should_create_tool', False):
                print(f"   Tool name: {analysis.get('tool_name', 'N/A')}")
                print(f"   Tool description: {analysis.get('tool_description', 'N/A')}")
                print(f"   Implementation approach: {analysis.get('implementation_approach', 'N/A')}")
                print(f"   Reasoning: {analysis.get('reasoning', 'N/A')}")
                print(f"   Existing tools analysis: {analysis.get('existing_tools_analysis', 'N/A')}")
                
                # 测试工具创建
                tool_created = await agent._create_dynamic_tool_from_analysis(analysis)
                print(f"   Tool creation: {'✅ Success' if tool_created else '❌ Failed'}")
            else:
                print(f"   Reasoning: {analysis.get('reasoning', 'No specialized tool needed')}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 LLM-Driven Analysis Test Completed!")
    print("=" * 50)


async def test_full_execution_with_llm_analysis():
    """测试完整执行流程中的 LLM 分析"""
    
    print("\n🚀 Full Execution with LLM Analysis Test")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="LLM-Driven Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    test_tasks = [
        "东京现在几点了",
        "北京天气怎么样",
        "计算 123 * 456 的结果"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔍 Executing task {i}: {task}")
        print("-" * 50)
        
        try:
            # 执行任务
            result = await agent.execute_task(task)
            
            print(f"✅ Task completed")
            print(f"📊 Result: {result.get('result', 'No result')}")
            
            # 检查是否创建了动态工具
            from python.agent.dynamic_tool_creator import dynamic_tool_creator
            stats = dynamic_tool_creator.get_tool_statistics()
            tools = stats.get("tools", [])
            
            if tools:
                print(f"🛠️  Dynamic tools available: {len(tools)}")
                for tool in tools[-1:]:  # 只显示最新创建的工具
                    print(f"   • {tool['name']}: {tool['description']}")
            else:
                print("ℹ️  No new dynamic tools created")
                
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
        await test_llm_driven_analysis()
        await test_full_execution_with_llm_analysis()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 