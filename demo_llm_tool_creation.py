#!/usr/bin/env python3
"""
LLM-Driven Tool Creation Demo
LLM 驱动工具创建演示
展示如何使用 LLM 分析建议并自动创建新工具
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

from python.agent.self_evolving_core import create_self_evolving_agent
from python.agent.core import AgentConfig


async def demo_llm_tool_creation():
    """演示 LLM 驱动的工具创建"""
    
    print("🛠️  LLM-Driven Tool Creation Demo")
    print("=" * 50)
    
    # 创建自进化 Agent
    config = AgentConfig(
        name="Tool Creator Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = create_self_evolving_agent(config)
    
    print(f"🤖 Created tool creator agent: {agent.config.name}")
    
    # 演示不同类型的建议
    demo_suggestions = [
        "建议创建一个文本情感分析工具，可以分析用户评论的情感倾向",
        "需要创建一个数据可视化工具，能够生成简单的图表",
        "应该创建一个文件格式转换工具，支持不同格式之间的转换",
        "建议改进现有的搜索功能，不需要创建新工具",
        "需要创建一个时间管理工具，帮助用户安排任务",
        "建议创建一个语言翻译工具，支持多语言翻译"
    ]
    
    print("\n📋 Testing LLM tool creation analysis...")
    print("-" * 50)
    
    for i, suggestion in enumerate(demo_suggestions, 1):
        print(f"\n💡 Suggestion {i}: {suggestion}")
        
        try:
            # 模拟反思建议处理
            await agent._handle_reflection_suggestions({
                "suggestions": [suggestion]
            })
            
            print("✅ Suggestion processed")
            
        except Exception as e:
            print(f"❌ Error processing suggestion: {e}")
    
    # 演示直接工具创建
    print("\n🛠️  Direct LLM Tool Creation Demo")
    print("-" * 50)
    
    # 测试 LLM 代码生成
    test_tool_name = "smart_calculator"
    test_tool_description = "Advanced calculator with mathematical expression evaluation"
    test_parameters = {
        "expression": {"type": "string", "description": "Mathematical expression to evaluate", "required": True},
        "precision": {"type": "integer", "description": "Decimal precision", "required": False, "default": 2}
    }
    
    print(f"🔧 Testing code generation for: {test_tool_name}")
    
    try:
        # 生成工具代码
        tool_code = await agent._generate_tool_code(
            test_tool_name, 
            test_tool_description, 
            test_parameters, 
            "Evaluate mathematical expressions safely"
        )
        
        print("✅ Code generation successful")
        print(f"📝 Generated code length: {len(tool_code)} characters")
        print("📄 Code preview:")
        print("-" * 30)
        print(tool_code[:200] + "..." if len(tool_code) > 200 else tool_code)
        print("-" * 30)
        
        # 验证代码安全性
        is_safe = agent._validate_generated_code(tool_code)
        print(f"🔒 Code safety validation: {'✅ PASS' if is_safe else '❌ FAIL'}")
        
        # 创建工具
        success = await agent.create_dynamic_tool(
            test_tool_name, 
            test_tool_description, 
            tool_code, 
            test_parameters
        )
        
        if success:
            print(f"✅ Successfully created tool: {test_tool_name}")
        else:
            print(f"❌ Failed to create tool: {test_tool_name}")
            
    except Exception as e:
        print(f"❌ Tool creation failed: {e}")
    
    # 演示复杂工具创建
    print("\n🔬 Complex Tool Creation Demo")
    print("-" * 50)
    
    complex_suggestions = [
        "建议创建一个智能文本摘要工具，能够自动提取文章的关键信息",
        "需要创建一个数据清洗工具，能够处理各种格式的数据文件",
        "建议创建一个代码质量分析工具，检查代码的复杂度和可读性"
    ]
    
    for suggestion in complex_suggestions:
        print(f"\n💡 Complex suggestion: {suggestion}")
        
        try:
            # 分析工具创建需求
            await agent._analyze_tool_creation_need(suggestion)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 获取工具统计
    print("\n📊 Tool Creation Statistics")
    print("-" * 50)
    
    from python.agent.dynamic_tool_creator import dynamic_tool_creator
    
    stats = dynamic_tool_creator.get_tool_statistics()
    print(f"📦 Total Dynamic Tools: {stats.get('total_dynamic_tools', 0)}")
    print(f"📊 Total Usage: {stats.get('total_usage', 0)}")
    print(f"🎯 Average Success Rate: {stats.get('average_success_rate', 0.0):.1%}")
    
    tools_list = stats.get("tools", [])
    if tools_list:
        print("\n🛠️  Created Tools:")
        for tool in tools_list:
            print(f"   • {tool['name']}: {tool['usage_count']} uses, {tool['success_rate']:.1%} success")
    
    print("\n🎉 LLM-Driven Tool Creation Demo Completed!")
    print("=" * 50)


async def demo_llm_analysis_comparison():
    """演示 LLM 分析与传统方法的对比"""
    
    print("\n🔍 LLM vs Traditional Tool Creation Analysis")
    print("=" * 50)
    
    # 创建 Agent
    config = AgentConfig(name="Comparison Agent")
    agent = create_self_evolving_agent(config)
    
    # 测试建议
    test_suggestions = [
        "建议创建一个新的搜索工具",
        "需要改进现有工具的性能",
        "建议创建一个数据分析工具",
        "应该优化代码执行效率"
    ]
    
    for suggestion in test_suggestions:
        print(f"\n📝 Suggestion: {suggestion}")
        
        # 传统方法（简单关键词匹配）
        traditional_result = "create" in suggestion.lower() or "new" in suggestion.lower()
        print(f"🔧 Traditional analysis: {'Create tool' if traditional_result else 'No action'}")
        
        # LLM 方法（智能分析）
        try:
            # 这里我们模拟 LLM 分析结果
            print(f"🧠 LLM analysis: Intelligent analysis would be performed")
            print(f"💡 LLM would consider: tool necessity, implementation feasibility, etc.")
        except Exception as e:
            print(f"❌ LLM analysis failed: {e}")


async def demo_safety_validation():
    """演示代码安全性验证"""
    
    print("\n🔒 Code Safety Validation Demo")
    print("=" * 50)
    
    config = AgentConfig(name="Safety Agent")
    agent = create_self_evolving_agent(config)
    
    # 测试代码样本
    test_codes = [
        # 安全代码
        """
# Safe code
text = params.get('text', '')
result = f"Processed text: {len(text)} characters"
""",
        # 危险代码
        """
# Dangerous code
import os
result = os.system(params.get('command', 'ls'))
""",
        # 边界情况
        """
# Edge case
eval(params.get('expression', '1+1'))
""",
        # 正常代码
        """
# Normal code
numbers = params.get('numbers', [])
result = sum(numbers) if numbers else 0
"""
    ]
    
    for i, code in enumerate(test_codes, 1):
        print(f"\n🔍 Testing code sample {i}:")
        print("-" * 30)
        print(code.strip())
        print("-" * 30)
        
        is_safe = agent._validate_generated_code(code)
        print(f"🔒 Safety validation: {'✅ PASS' if is_safe else '❌ FAIL'}")
        
        if not is_safe:
            print("⚠️  Dangerous patterns detected!")


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # LLM 驱动工具创建演示
        await demo_llm_tool_creation()
        
        # 分析对比演示
        await demo_llm_analysis_comparison()
        
        # 安全性验证演示
        await demo_safety_validation()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 