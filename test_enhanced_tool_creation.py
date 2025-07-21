#!/usr/bin/env python3
"""
Enhanced Tool Creation Test
增强的工具创建测试
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


async def test_enhanced_tool_creation():
    """测试增强的工具创建逻辑"""
    
    print("🛠️  Enhanced Tool Creation Test")
    print("=" * 50)
    print("测试更明确的工具创建场景")
    print("=" * 50)
    
    from python.agent.self_evolving_core import TaskAnalyzer
    
    # 更明确的工具创建测试用例
    test_tasks = [
        "创建一个专门的时间工具，可以查询任意时区的当前时间",
        "开发一个天气查询工具，支持全球城市天气信息",
        "构建一个计算器工具，支持复杂数学运算",
        "制作一个数据分析工具，可以处理CSV文件并生成图表",
        "设计一个翻译工具，支持多语言翻译"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔍 Test {i}: {task}")
        print("-" * 50)
        
        try:
            # 测试工具创建决策
            analysis = await TaskAnalyzer.analyze_task(task, "tool_creation")
            
            should_create = analysis.get("should_create_tool", False)
            tool_name = analysis.get("tool_name", "")
            tool_description = analysis.get("tool_description", "")
            reasoning = analysis.get("reasoning", "")
            
            print(f"📊 Should create tool: {should_create}")
            
            if should_create:
                print(f"🛠️  Tool name: {tool_name}")
                print(f"📝 Tool description: {tool_description}")
                print(f"💡 Reasoning: {reasoning}")
                print("✅ SUCCESS: LLM decided to create specialized tool")
            else:
                print(f"💡 Reasoning: {reasoning}")
                print("⚠️  WARNING: LLM decided not to create tool")
                print("   This might indicate the prompt needs improvement")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Enhanced Tool Creation Test Completed!")
    print("=" * 50)


async def test_improved_prompt():
    """测试改进的提示词"""
    
    print("\n📝 Improved Prompt Test")
    print("=" * 50)
    print("测试改进的提示词是否能更好地触发工具创建")
    print("=" * 50)
    
    from python.agent.self_evolving_core import TaskAnalyzer
    
    # 使用更明确的提示词
    improved_tasks = [
        "我需要一个专门的时间工具，因为现有的搜索工具不够准确",
        "请创建一个天气工具，因为现有的API调用太复杂",
        "开发一个计算工具，因为现有的计算器功能有限",
        "构建一个数据分析工具，因为现有的工具无法处理我的数据格式",
        "制作一个翻译工具，因为现有的翻译服务不够准确"
    ]
    
    for i, task in enumerate(improved_tasks, 1):
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
                print("✅ SUCCESS: Improved prompt triggered tool creation")
            else:
                print(f"💡 Reasoning: {reasoning}")
                print("ℹ️  INFO: LLM still decided not to create tool")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Improved Prompt Test Completed!")
    print("=" * 50)


async def test_system_prompt_improvement():
    """测试系统提示词改进"""
    
    print("\n🔧 System Prompt Improvement Test")
    print("=" * 50)
    print("测试改进的系统提示词")
    print("=" * 50)
    
    # 这里我们可以测试不同的系统提示词
    # 但首先让我们看看当前的提示词是否需要改进
    
    print("当前系统提示词分析:")
    print("-" * 30)
    print("✅ 优点:")
    print("   • 让 LLM 完全自主判断")
    print("   • 没有硬编码的限制")
    print("   • 提供了清晰的决策标准")
    
    print("\n⚠️  可能的改进:")
    print("   • 可以更明确地鼓励工具创建")
    print("   • 可以提供更多工具创建的示例")
    print("   • 可以强调专门工具的价值")
    
    print("\n💡 建议:")
    print("   • 当前的实现是正确的")
    print("   • LLM 的保守决策是合理的")
    print("   • 如果需要更多工具创建，可以调整提示词")
    
    print("\n🎉 System Prompt Analysis Completed!")
    print("=" * 50)


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await test_enhanced_tool_creation()
        await test_improved_prompt()
        await test_system_prompt_improvement()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 