#!/usr/bin/env python3
"""
Task Classification Test
测试任务分类的修复效果
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


async def test_task_classification():
    """测试任务分类是否还有硬编码问题"""
    
    print("🧪 Task Classification Test")
    print("=" * 50)
    print("测试任务分类是否完全由 LLM 自主判断")
    print("=" * 50)
    
    from python.agent.self_evolving_core import TaskAnalyzer
    
    # 测试用例：这些任务应该被正确分类，而不是硬编码为 "search"
    test_tasks = [
        "东京现在几点了",
        "北京天气怎么样", 
        "计算 123 * 456 的结果",
        "帮我写一个Python函数",
        "分析这个数据集",
        "翻译这句话",
        "创建一个时间工具"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔍 Test {i}: {task}")
        print("-" * 50)
        
        try:
            # 测试任务分类
            analysis = await TaskAnalyzer.analyze_task(task, "task_type")
            task_type = analysis.get("task_type", "unknown")
            
            print(f"📊 Task Type: {task_type}")
            
            # 检查是否被错误分类为 search
            if task_type == "search":
                print("⚠️  WARNING: Task might be incorrectly classified as 'search'")
                print("   This could lead to using search tools instead of specialized tools")
            elif task_type in ["time", "weather", "calculation", "programming", "analysis", "translation", "custom"]:
                print("✅ GOOD: Task correctly classified with specific type")
            else:
                print(f"ℹ️  INFO: Task classified as '{task_type}'")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Task Classification Test Completed!")
    print("=" * 50)


async def test_tool_creation_decision():
    """测试工具创建决策是否完全由 LLM 判断"""
    
    print("\n🛠️  Tool Creation Decision Test")
    print("=" * 50)
    print("测试工具创建决策是否完全由 LLM 自主判断")
    print("=" * 50)
    
    from python.agent.self_evolving_core import TaskAnalyzer
    
    # 测试用例：这些任务应该触发工具创建
    test_tasks = [
        "东京现在几点了",  # 应该创建时间工具
        "北京天气怎么样",   # 应该创建天气工具
        "计算 123 * 456",  # 应该创建计算工具
        "帮我写一个Python函数",  # 应该创建编程工具
        "分析这个数据集",   # 应该创建分析工具
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔍 Test {i}: {task}")
        print("-" * 50)
        
        try:
            # 测试工具创建决策
            analysis = await TaskAnalyzer.analyze_task(task, "tool_creation")
            
            should_create = analysis.get("should_create_tool", False)
            tool_name = analysis.get("tool_name", "")
            reasoning = analysis.get("reasoning", "")
            
            print(f"📊 Should create tool: {should_create}")
            
            if should_create:
                print(f"🛠️  Tool name: {tool_name}")
                print(f"💡 Reasoning: {reasoning}")
                print("✅ GOOD: LLM decided to create specialized tool")
            else:
                print(f"💡 Reasoning: {reasoning}")
                print("ℹ️  INFO: LLM decided not to create tool")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Tool Creation Decision Test Completed!")
    print("=" * 50)


async def test_full_execution_with_classification():
    """测试完整执行流程中的任务分类"""
    
    print("\n🚀 Full Execution with Classification Test")
    print("=" * 50)
    print("测试完整执行流程中的任务分类和工具创建")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Classification Test Agent",
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
        
        # 检查是否创建了时间工具
        from python.agent.dynamic_tool_creator import dynamic_tool_creator
        stats = dynamic_tool_creator.get_tool_statistics()
        tools = stats.get("tools", [])
        
        if tools:
            print(f"🛠️  Dynamic tools available: {len(tools)}")
            for tool in tools[-1:]:  # 只显示最新创建的工具
                print(f"   • {tool['name']}: {tool['description']}")
                
                # 检查是否是时间相关的工具
                if "time" in tool['name'].lower() or "时间" in tool['description']:
                    print("✅ SUCCESS: Time tool was created correctly")
                else:
                    print("⚠️  WARNING: Tool might not be time-specific")
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
        await test_task_classification()
        await test_tool_creation_decision()
        await test_full_execution_with_classification()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 