#!/usr/bin/env python3
"""
Tool Duplication Check Demo
工具重复检查演示
展示如何避免重复创建相似功能的工具
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

from python.agent.self_evolving_core import create_self_evolving_agent
from python.agent.core import AgentConfig


async def demo_tool_duplication_check():
    """演示工具重复检查功能"""
    
    print("🔍 Tool Duplication Check Demo")
    print("=" * 50)
    
    # 创建 Agent
    config = AgentConfig(
        name="Duplication Check Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = create_self_evolving_agent(config)
    
    print(f"🤖 Created duplication check agent: {agent.config.name}")
    
    # 获取当前工具状态
    from python.agent.dynamic_tool_creator import dynamic_tool_creator
    initial_stats = dynamic_tool_creator.get_tool_statistics()
    print(f"\n📦 Initial dynamic tools: {len(initial_stats.get('tools', []))}")
    
    # 演示不同类型的建议
    test_suggestions = [
        # 第一个建议 - 应该创建新工具
        {
            "suggestion": "建议创建一个文本分析工具，能够分析文本的情感倾向",
            "expected": "CREATE",
            "description": "新的文本分析功能"
        },
        
        # 第二个建议 - 可能重复
        {
            "suggestion": "需要创建一个文本处理工具，可以统计文本中的词汇",
            "expected": "DUPLICATE",
            "description": "可能与第一个工具重复"
        },
        
        # 第三个建议 - 不同功能
        {
            "suggestion": "建议创建一个数据可视化工具，能够生成图表",
            "expected": "CREATE",
            "description": "数据可视化功能"
        },
        
        # 第四个建议 - 明确重复
        {
            "suggestion": "需要创建一个文本情感分析工具",
            "expected": "DUPLICATE",
            "description": "明确重复第一个工具"
        },
        
        # 第五个建议 - 统计功能
        {
            "suggestion": "建议创建一个数据统计工具，计算平均值和标准差",
            "expected": "CREATE",
            "description": "数据统计功能"
        },
        
        # 第六个建议 - 可能重复统计
        {
            "suggestion": "需要创建一个数学计算工具，进行统计分析",
            "expected": "DUPLICATE",
            "description": "可能与统计工具重复"
        }
    ]
    
    print("\n📋 Testing Tool Creation with Duplication Check...")
    print("-" * 50)
    
    for i, test_case in enumerate(test_suggestions, 1):
        print(f"\n💡 Test {i}: {test_case['description']}")
        print(f"📝 Suggestion: {test_case['suggestion']}")
        print(f"🎯 Expected: {test_case['expected']}")
        
        try:
            # 分析工具创建需求
            await agent._analyze_tool_creation_need(test_case['suggestion'])
            
            # 获取当前工具数量
            current_stats = dynamic_tool_creator.get_tool_statistics()
            current_tools = len(current_stats.get('tools', []))
            initial_tools = len(initial_stats.get('tools', []))
            
            if current_tools > initial_tools:
                print(f"✅ Tool created - Total tools: {current_tools}")
            else:
                print(f"⏭️  Tool creation skipped - Total tools: {current_tools}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 显示最终工具列表
    print("\n📊 Final Tool Statistics")
    print("-" * 50)
    
    final_stats = dynamic_tool_creator.get_tool_statistics()
    print(f"📦 Total Dynamic Tools: {final_stats.get('total_dynamic_tools', 0)}")
    print(f"📊 Total Usage: {final_stats.get('total_usage', 0)}")
    print(f"🎯 Average Success Rate: {final_stats.get('average_success_rate', 0.0):.1%}")
    
    tools_list = final_stats.get("tools", [])
    if tools_list:
        print("\n🛠️  Created Tools:")
        for tool in tools_list:
            print(f"   • {tool['name']}: {tool['usage_count']} uses, {tool['success_rate']:.1%} success")
    
    # 演示相似性检查
    print("\n🔍 Similarity Check Demo")
    print("-" * 50)
    
    test_pairs = [
        ("text_analyzer", "text_processor"),
        ("data_visualizer", "chart_generator"),
        ("calculator", "math_tool"),
        ("file_reader", "document_parser"),
        ("text_analyzer", "image_processor")  # 不相似
    ]
    
    for tool1, tool2 in test_pairs:
        similarity = agent._is_similar_functionality(tool1, tool2)
        print(f"🔍 {tool1} vs {tool2}: {'✅ Similar' if similarity else '❌ Different'}")
    
    print("\n🎉 Tool Duplication Check Demo Completed!")
    print("=" * 50)


async def demo_llm_analysis_improvement():
    """演示 LLM 分析改进"""
    
    print("\n🧠 LLM Analysis Improvement Demo")
    print("=" * 50)
    
    config = AgentConfig(name="Analysis Agent")
    agent = create_self_evolving_agent(config)
    
    # 模拟现有工具
    existing_tools = ["text_analyzer", "data_visualizer", "calculator"]
    
    # 测试建议
    test_suggestions = [
        "建议创建一个文本分析工具",
        "需要创建一个数据可视化工具",
        "建议创建一个新的数学计算工具"
    ]
    
    for suggestion in test_suggestions:
        print(f"\n📝 Suggestion: {suggestion}")
        print(f"🔍 Existing tools: {', '.join(existing_tools)}")
        
        # 模拟 LLM 分析
        print("🧠 LLM would analyze:")
        print("   • Check if functionality exists in current tools")
        print("   • Consider dynamic tools created previously")
        print("   • Evaluate if new tool adds value")
        print("   • Check for duplication")


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 工具重复检查演示
        await demo_tool_duplication_check()
        
        # LLM 分析改进演示
        await demo_llm_analysis_improvement()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 