#!/usr/bin/env python3
"""
Tool Creation and Usage Test
测试工具创建后立即使用的功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


async def test_tool_creation_and_usage():
    """测试工具创建后立即使用"""
    
    print("🛠️  Tool Creation and Usage Test")
    print("=" * 50)
    print("测试工具创建后是否立即使用新工具而不是搜索工具")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Tool Creation Test Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    # 测试用例：这些任务应该创建专门工具而不是使用搜索
    test_tasks = [
        "东京现在几点了",
        "北京天气怎么样",
        "计算 123 * 456 的结果"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔍 Test {i}: {task}")
        print("-" * 50)
        
        try:
            # 执行任务
            result = await agent.execute_task(task)
            
            print(f"✅ Task completed")
            print(f"📊 Result: {result.get('result', 'No result')}")
            
            # 检查是否使用了搜索工具
            if "metadata" in result and "tool_results" in result["metadata"]:
                tools_used = [r["tool"] for r in result["metadata"]["tool_results"]]
                print(f"🔧 Tools used: {tools_used}")
                
                # 检查是否使用了搜索工具
                search_tools = ["search", "tavily_search"]
                used_search = any(tool in search_tools for tool in tools_used)
                
                if used_search:
                    print("⚠️  WARNING: Still using search tools instead of specialized tools")
                    print("   This indicates the tool creation or reload mechanism needs improvement")
                else:
                    print("✅ SUCCESS: Used specialized tools instead of search tools")
            else:
                print("ℹ️  INFO: No tool usage information available")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Tool Creation and Usage Test Completed!")
    print("=" * 50)


async def test_dynamic_tool_reload():
    """测试动态工具重新加载"""
    
    print("\n🔄 Dynamic Tool Reload Test")
    print("=" * 50)
    print("测试动态工具重新加载功能")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Reload Test Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    print(f"🔧 Initial tools: {list(agent.tools.keys())}")
    
    try:
        # 测试重新加载工具
        await agent._reload_tools()
        
        print(f"🔧 Tools after reload: {list(agent.tools.keys())}")
        
        # 检查是否有新的动态工具
        from python.agent.dynamic_tool_creator import dynamic_tool_creator
        dynamic_tools = dynamic_tool_creator.list_dynamic_tools()
        
        if dynamic_tools:
            print(f"🛠️  Available dynamic tools: {dynamic_tools}")
            
            for tool_name in dynamic_tools:
                if tool_name in agent.tools:
                    print(f"✅ Dynamic tool '{tool_name}' successfully loaded")
                else:
                    print(f"❌ Dynamic tool '{tool_name}' not loaded")
        else:
            print("ℹ️  No dynamic tools available")
            
    except Exception as e:
        print(f"❌ Reload test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Dynamic Tool Reload Test Completed!")
    print("=" * 50)


async def test_enhanced_prompt_for_tool_creation():
    """测试增强的提示词是否能更好地触发工具创建"""
    
    print("\n📝 Enhanced Prompt Test")
    print("=" * 50)
    print("测试增强的提示词是否能更好地触发工具创建")
    print("=" * 50)
    
    from python.agent.self_evolving_core import TaskAnalyzer
    
    # 使用更明确的提示词来触发工具创建
    enhanced_tasks = [
        "我需要一个专门的时间工具，因为现有的搜索工具不够准确，请创建一个时间查询工具",
        "请创建一个天气工具，因为现有的API调用太复杂，我需要一个简化的天气查询工具",
        "开发一个计算工具，因为现有的计算器功能有限，我需要一个高级计算器"
    ]
    
    for i, task in enumerate(enhanced_tasks, 1):
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
                print("✅ SUCCESS: Enhanced prompt triggered tool creation")
            else:
                print(f"💡 Reasoning: {reasoning}")
                print("⚠️  WARNING: Enhanced prompt did not trigger tool creation")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Enhanced Prompt Test Completed!")
    print("=" * 50)


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await test_tool_creation_and_usage()
        await test_dynamic_tool_reload()
        await test_enhanced_prompt_for_tool_creation()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 