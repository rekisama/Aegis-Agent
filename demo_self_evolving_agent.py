#!/usr/bin/env python3
"""
Self-Evolving Agent Demo
自进化 Agent 演示脚本
展示动态工具创建、自适应学习和自我反思功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

from python.agent.self_evolving_core import create_self_evolving_agent
from python.agent.core import AgentConfig


async def demo_self_evolving_agent():
    """演示自进化 Agent 功能"""
    
    print("🚀 Self-Evolving Agent Demo")
    print("=" * 50)
    
    # 创建自进化 Agent
    config = AgentConfig(
        name="Evolving Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = create_self_evolving_agent(config)
    
    print(f"🤖 Created self-evolving agent: {agent.config.name}")
    print(f"📊 Evolution status: {agent.get_evolution_status()}")
    
    # 演示任务执行和学习
    demo_tasks = [
        "计算 15 + 27 的结果",
        "搜索 Python 编程最佳实践",
        "列出当前目录的文件",
        "分析字符串 'Hello World' 的长度"
    ]
    
    print("\n📋 Executing demo tasks...")
    print("-" * 30)
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n🔧 Task {i}: {task}")
        try:
            result = await agent.execute_task(task)
            print(f"✅ Result: {result.get('result', 'No result')[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 获取进化报告
    print("\n📊 Evolution Report")
    print("-" * 30)
    
    evolution_report = await agent.get_evolution_report()
    
    if "error" not in evolution_report:
        metrics = evolution_report.get("evolution_metrics", {})
        print(f"📈 Total Tasks: {metrics.get('total_tasks', 0)}")
        print(f"🎯 Success Rate: {metrics.get('success_rate', 0.0):.1%}")
        print(f"⏱️  Avg Execution Time: {metrics.get('average_execution_time', 0.0):.2f}s")
        print(f"🛠️  Tools Created: {metrics.get('tools_created', 0)}")
        print(f"📚 Improvement Score: {metrics.get('improvement_score', 0.0):.1%}")
        
        # 显示建议
        recommendations = evolution_report.get("recommendations", [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
    
    # 演示动态工具创建
    print("\n🛠️  Dynamic Tool Creation Demo")
    print("-" * 30)
    
    # 创建一个简单的文本处理工具
    tool_name = "text_processor"
    tool_description = "Process and analyze text content"
    tool_code = """
# 文本处理代码
text = params.get('text', '')
operation = params.get('operation', 'length')

if operation == 'length':
    result = len(text)
elif operation == 'word_count':
    result = len(text.split())
elif operation == 'uppercase':
    result = text.upper()
else:
    result = f"Unknown operation: {operation}"
"""
    tool_parameters = {
        "text": {"type": "string", "description": "Text to process", "required": True},
        "operation": {"type": "string", "description": "Operation type", "required": False, "default": "length"}
    }
    
    success = await agent.create_dynamic_tool(tool_name, tool_description, tool_code, tool_parameters)
    
    if success:
        print(f"✅ Created dynamic tool: {tool_name}")
        
        # 测试新创建的工具
        print(f"🧪 Testing dynamic tool...")
        # 这里可以测试新工具，但需要先集成到工具系统中
        
    else:
        print(f"❌ Failed to create dynamic tool: {tool_name}")
    
    # 执行进化过程
    print("\n🔄 Evolution Process")
    print("-" * 30)
    
    evolution_result = await agent.evolve()
    
    if evolution_result.get("evolution_completed"):
        print(f"✅ Evolution completed with score: {evolution_result.get('evolution_score', 0.0):.1%}")
        
        improvements = evolution_result.get("improvements_made", [])
        if improvements:
            print("📈 Improvements made:")
            for improvement in improvements:
                print(f"   • {improvement}")
    else:
        print(f"❌ Evolution failed: {evolution_result.get('error', 'Unknown error')}")
    
    # 最终状态
    print("\n📊 Final Evolution Status")
    print("-" * 30)
    
    final_status = agent.get_evolution_status()
    print(f"🤖 Agent: {final_status.get('evolution_enabled', False)}")
    print(f"📚 Learning: {final_status.get('learning_enabled', False)}")
    print(f"🔄 Reflection: {final_status.get('reflection_enabled', False)}")
    
    metrics = final_status.get("metrics", {})
    print(f"📈 Total Tasks: {metrics.get('total_tasks', 0)}")
    print(f"🎯 Success Rate: {metrics.get('success_rate', 0.0):.1%}")
    print(f"🛠️  Tools Created: {metrics.get('tools_created', 0)}")
    
    capabilities = final_status.get("capabilities", {})
    print("\n🔧 Capabilities:")
    for capability, enabled in capabilities.items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {capability}")
    
    print("\n🎉 Self-Evolving Agent Demo Completed!")
    print("=" * 50)


async def demo_advanced_features():
    """演示高级功能"""
    
    print("\n🚀 Advanced Features Demo")
    print("=" * 50)
    
    from python.agent.adaptive_learning import adaptive_learning
    from python.agent.self_reflection import self_reflection
    from python.agent.dynamic_tool_creator import dynamic_tool_creator
    
    # 演示学习洞察
    print("\n📚 Learning Insights")
    print("-" * 20)
    
    insights = adaptive_learning.get_learning_insights()
    print(f"📊 Total Experiences: {insights.get('total_experiences', 0)}")
    print(f"🎯 Success Rate: {insights.get('success_rate', 0.0):.1%}")
    
    best_tools = insights.get("best_performing_tools", [])
    if best_tools:
        print("🏆 Best Performing Tools:")
        for tool in best_tools[:3]:
            print(f"   • {tool['tool']}: {tool['success_rate']:.1%}")
    
    # 演示反思历史
    print("\n🔄 Reflection History")
    print("-" * 20)
    
    reflection_history = self_reflection.get_reflection_history(limit=3)
    for session in reflection_history:
        print(f"📝 {session['task_description'][:50]}...")
        print(f"   Score: {session['overall_score']:.1%}")
        print(f"   Suggestions: {len(session['improvement_suggestions'])}")
    
    # 演示工具性能报告
    print("\n🛠️  Tool Performance Report")
    print("-" * 20)
    
    tool_performance = adaptive_learning.get_tool_performance_report()
    print(f"📊 Total Tools: {tool_performance.get('total_tools', 0)}")
    
    tools = tool_performance.get("tools", [])
    if tools:
        print("🔧 Tool Performance:")
        for tool in tools[:3]:
            print(f"   • {tool['tool_name']}: {tool['success_rate']:.1%} ({tool['usage_count']} uses)")
    
    # 演示动态工具统计
    print("\n⚡ Dynamic Tools Statistics")
    print("-" * 20)
    
    dynamic_stats = dynamic_tool_creator.get_tool_statistics()
    print(f"📦 Total Dynamic Tools: {dynamic_stats.get('total_dynamic_tools', 0)}")
    print(f"📊 Total Usage: {dynamic_stats.get('total_usage', 0)}")
    print(f"🎯 Average Success Rate: {dynamic_stats.get('average_success_rate', 0.0):.1%}")
    
    tools_list = dynamic_stats.get("tools", [])
    if tools_list:
        print("🛠️  Dynamic Tools:")
        for tool in tools_list:
            print(f"   • {tool['name']}: {tool['usage_count']} uses, {tool['success_rate']:.1%} success")


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 基本演示
        await demo_self_evolving_agent()
        
        # 高级功能演示
        await demo_advanced_features()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 