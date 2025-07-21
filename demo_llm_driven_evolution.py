#!/usr/bin/env python3
"""
LLM-Driven Self-Evolution Demo
LLM 驱动的自进化演示
展示如何使用 LLM 进行智能分析、分类和推荐
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

from python.agent.self_evolving_core import create_self_evolving_agent
from python.agent.core import AgentConfig


async def demo_llm_driven_analysis():
    """演示 LLM 驱动的分析功能"""
    
    print("🧠 LLM-Driven Self-Evolution Demo")
    print("=" * 50)
    
    # 创建自进化 Agent
    config = AgentConfig(
        name="LLM-Evolving Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = create_self_evolving_agent(config)
    
    print(f"🤖 Created LLM-driven agent: {agent.config.name}")
    
    # 演示不同类型的任务
    demo_tasks = [
        "搜索最新的 AI 发展趋势",
        "计算 25 * 13 + 47 的结果",
        "分析当前目录的文件结构",
        "统计字符串 'Hello World' 中字母的数量",
        "查找 Python 编程最佳实践",
        "创建一个简单的文本处理工具"
    ]
    
    print("\n📋 Executing tasks with LLM-driven analysis...")
    print("-" * 50)
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n🔧 Task {i}: {task}")
        
        try:
            # 执行任务
            result = await agent.execute_task(task)
            
            # 显示结果摘要
            status = result.get("status", "unknown")
            result_content = result.get("result", "")[:100]
            print(f"✅ Status: {status}")
            print(f"📝 Result: {result_content}...")
            
            # 显示 LLM 分析信息
            if "metadata" in result:
                metadata = result["metadata"]
                if "tool_results" in metadata:
                    tools_used = [r["tool"] for r in metadata["tool_results"]]
                    print(f"🛠️  Tools used: {', '.join(tools_used)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 获取进化报告
    print("\n📊 LLM-Driven Evolution Report")
    print("-" * 50)
    
    evolution_report = await agent.get_evolution_report()
    
    if "error" not in evolution_report:
        metrics = evolution_report.get("evolution_metrics", {})
        print(f"📈 Total Tasks: {metrics.get('total_tasks', 0)}")
        print(f"🎯 Success Rate: {metrics.get('success_rate', 0.0):.1%}")
        print(f"⏱️  Avg Execution Time: {metrics.get('average_execution_time', 0.0):.2f}s")
        print(f"🛠️  Tools Created: {metrics.get('tools_created', 0)}")
        print(f"📚 Improvement Score: {metrics.get('improvement_score', 0.0):.1%}")
        
        # 显示 LLM 生成的建议
        recommendations = evolution_report.get("recommendations", [])
        if recommendations:
            print("\n💡 LLM-Generated Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
    
    # 演示 LLM 驱动的工具创建
    print("\n🛠️  LLM-Driven Tool Creation Demo")
    print("-" * 50)
    
    # 创建一个基于 LLM 分析的工具
    tool_name = "smart_text_analyzer"
    tool_description = "Intelligent text analysis with LLM-driven insights"
    tool_code = """
# LLM 驱动的文本分析工具
text = params.get('text', '')
analysis_type = params.get('analysis_type', 'basic')

if analysis_type == 'basic':
    result = f"Text length: {len(text)}, Word count: {len(text.split())}"
elif analysis_type == 'sentiment':
    # 这里可以集成 LLM 进行情感分析
    result = "Sentiment analysis: Neutral (placeholder)"
elif analysis_type == 'complexity':
    # 文本复杂度分析
    words = text.split()
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    result = f"Average word length: {avg_word_length:.2f}"
else:
    result = f"Unknown analysis type: {analysis_type}"
"""
    tool_parameters = {
        "text": {"type": "string", "description": "Text to analyze", "required": True},
        "analysis_type": {"type": "string", "description": "Type of analysis", "required": False, "default": "basic"}
    }
    
    success = await agent.create_dynamic_tool(tool_name, tool_description, tool_code, tool_parameters)
    
    if success:
        print(f"✅ Created LLM-driven tool: {tool_name}")
        print(f"📝 Description: {tool_description}")
        print(f"⚙️  Parameters: {len(tool_parameters)} parameters")
    else:
        print(f"❌ Failed to create LLM-driven tool: {tool_name}")
    
    # 执行进化过程
    print("\n🔄 LLM-Driven Evolution Process")
    print("-" * 50)
    
    evolution_result = await agent.evolve()
    
    if evolution_result.get("evolution_completed"):
        evolution_score = evolution_result.get("evolution_score", 0.0)
        print(f"✅ Evolution completed with score: {evolution_score:.1%}")
        
        improvements = evolution_result.get("improvements_made", [])
        if improvements:
            print("📈 LLM-Suggested Improvements:")
            for improvement in improvements:
                print(f"   • {improvement}")
        
        new_capabilities = evolution_result.get("new_capabilities", [])
        if new_capabilities:
            print("🆕 New Capabilities:")
            for capability in new_capabilities:
                print(f"   • {capability}")
    else:
        print(f"❌ Evolution failed: {evolution_result.get('error', 'Unknown error')}")
    
    # 最终状态
    print("\n📊 Final LLM-Driven Evolution Status")
    print("-" * 50)
    
    final_status = agent.get_evolution_status()
    print(f"🤖 Agent: {final_status.get('evolution_enabled', False)}")
    print(f"📚 Learning: {final_status.get('learning_enabled', False)}")
    print(f"🔄 Reflection: {final_status.get('reflection_enabled', False)}")
    
    metrics = final_status.get("metrics", {})
    print(f"📈 Total Tasks: {metrics.get('total_tasks', 0)}")
    print(f"🎯 Success Rate: {metrics.get('success_rate', 0.0):.1%}")
    print(f"🛠️  Tools Created: {metrics.get('tools_created', 0)}")
    
    capabilities = final_status.get("capabilities", {})
    print("\n🔧 LLM-Enhanced Capabilities:")
    for capability, enabled in capabilities.items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {capability}")
    
    print("\n🎉 LLM-Driven Self-Evolution Demo Completed!")
    print("=" * 50)


async def demo_llm_analysis_comparison():
    """演示 LLM 分析与传统方法的对比"""
    
    print("\n🔍 LLM Analysis vs Traditional Methods")
    print("=" * 50)
    
    from python.agent.adaptive_learning import adaptive_learning
    
    # 测试任务
    test_tasks = [
        "搜索 Python 机器学习教程",
        "计算复杂的数学公式",
        "分析系统性能数据",
        "创建自定义数据处理工具"
    ]
    
    for task in test_tasks:
        print(f"\n📝 Task: {task}")
        
        # 传统方法（关键词匹配）
        traditional_recommendations = adaptive_learning.get_recommendations(task)
        print(f"🔧 Traditional: {traditional_recommendations.get('recommended_tools', [])}")
        
        # LLM 方法
        llm_recommendations = await adaptive_learning.get_llm_recommendations(task)
        print(f"🧠 LLM-Driven: {llm_recommendations.get('recommended_tools', [])}")
        print(f"💡 Reasoning: {llm_recommendations.get('reasoning', 'No reasoning')}")
        print(f"📊 Success Probability: {llm_recommendations.get('estimated_success_probability', 0.0):.1%}")


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # LLM 驱动的自进化演示
        await demo_llm_driven_analysis()
        
        # LLM 分析对比演示
        await demo_llm_analysis_comparison()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 