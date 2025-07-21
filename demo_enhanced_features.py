#!/usr/bin/env python3
"""
Enhanced Features Demo
完善功能演示
展示完善后的占位功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

from python.agent.self_evolving_core import create_self_evolving_agent
from python.agent.core import AgentConfig


async def demo_enhanced_features():
    """演示完善后的功能"""
    
    print("🚀 Enhanced Features Demo")
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
    
    # 演示动态工具加载
    print("\n📦 Dynamic Tool Loading Demo")
    print("-" * 50)
    
    from python.agent.dynamic_tool_creator import dynamic_tool_creator
    
    # 获取动态工具列表
    dynamic_tools = dynamic_tool_creator.list_dynamic_tools()
    print(f"🔍 Found {len(dynamic_tools)} dynamic tools:")
    for tool in dynamic_tools:
        print(f"   • {tool}")
    
    # 演示参数验证
    print("\n🔍 Parameter Validation Demo")
    print("-" * 50)
    
    test_params = [
        {"text": "This is a test text", "length": 3},
        {"text": "A" * 60000, "length": 5},  # 超长文本
        {"text": "", "length": 2},  # 空文本
        {"text": "Valid text", "length": 15},  # 超长摘要
        {"text": "Another test", "length": "invalid"}  # 无效类型
    ]
    
    for i, params in enumerate(test_params, 1):
        print(f"\n📝 Test {i}: {params}")
        try:
            # 测试参数验证
            validated = agent._validate_parameters(params)
            print(f"✅ Validation passed: {validated}")
        except Exception as e:
            print(f"❌ Validation failed: {e}")
    
    # 演示智能工具推荐
    print("\n🧠 Intelligent Tool Recommendation Demo")
    print("-" * 50)
    
    test_tasks = [
        "分析这段文本的情感倾向",
        "计算这些数字的统计信息",
        "生成一个数据可视化图表",
        "读取并处理文件内容"
    ]
    
    for task in test_tasks:
        print(f"\n💡 Task: {task}")
        try:
            # 获取 LLM 推荐
            recommendations = await agent.adaptive_learning.get_llm_recommendations(task)
            print(f"🎯 LLM Recommendations:")
            print(f"   • Recommended tools: {recommendations.get('recommended_tools', [])}")
            print(f"   • Avoid tools: {recommendations.get('avoid_tools', [])}")
            print(f"   • Success probability: {recommendations.get('estimated_success_probability', 0.0):.1%}")
            print(f"   • Reasoning: {recommendations.get('reasoning', 'No reasoning')}")
        except Exception as e:
            print(f"❌ Recommendation failed: {e}")
    
    # 演示工具重复检测
    print("\n🔍 Tool Duplication Detection Demo")
    print("-" * 50)
    
    test_suggestions = [
        "建议创建一个文本分析工具",
        "需要创建一个数据统计工具",
        "建议创建一个新的计算器工具"
    ]
    
    for suggestion in test_suggestions:
        print(f"\n💡 Suggestion: {suggestion}")
        try:
            await agent._analyze_tool_creation_need(suggestion)
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    # 演示安全验证
    print("\n🔒 Security Validation Demo")
    print("-" * 50)
    
    test_codes = [
        # 安全代码
        """
text = params.get('text', '')
result = f"Processed: {len(text)} characters"
""",
        # 危险代码
        """
import os
result = os.system(params.get('command', 'ls'))
""",
        # 边界情况
        """
import requests
result = requests.get(params.get('url', 'https://example.com'))
"""
    ]
    
    for i, code in enumerate(test_codes, 1):
        print(f"\n📝 Code sample {i}:")
        print(code.strip())
        
        try:
            is_safe = await agent._validate_generated_code(code)
            print(f"🔒 Security validation: {'✅ SAFE' if is_safe else '❌ UNSAFE'}")
        except Exception as e:
            print(f"❌ Validation failed: {e}")
    
    # 获取最终统计
    print("\n📊 Final Statistics")
    print("-" * 50)
    
    stats = dynamic_tool_creator.get_tool_statistics()
    print(f"📦 Total Dynamic Tools: {stats.get('total_dynamic_tools', 0)}")
    print(f"📊 Total Usage: {stats.get('total_usage', 0)}")
    print(f"🎯 Average Success Rate: {stats.get('average_success_rate', 0.0):.1%}")
    
    tools_list = stats.get("tools", [])
    if tools_list:
        print("\n🛠️  Available Tools:")
        for tool in tools_list:
            print(f"   • {tool['name']}: {tool['usage_count']} uses, {tool['success_rate']:.1%} success")
    
    print("\n🎉 Enhanced Features Demo Completed!")
    print("=" * 50)


async def demo_parameter_validation():
    """演示参数验证功能"""
    
    print("\n🔍 Parameter Validation Enhancement Demo")
    print("=" * 50)
    
    from python.agent.dynamic_tool_creator import dynamic_tool_creator
    
    # 测试参数验证
    test_cases = [
        {
            "name": "Valid parameters",
            "params": {"text": "Hello world", "numbers": [1, 2, 3]},
            "expected": "PASS"
        },
        {
            "name": "Long string",
            "params": {"text": "A" * 15000},
            "expected": "TRUNCATED"
        },
        {
            "name": "Long list",
            "params": {"numbers": list(range(1500))},
            "expected": "TRUNCATED"
        },
        {
            "name": "Deep dict",
            "params": {"data": {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": "value"}}}}}}},
            "expected": "TRUNCATED"
        },
        {
            "name": "None values",
            "params": {"text": None, "valid": "ok"},
            "expected": "FILTERED"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        print(f"📄 Params: {test_case['params']}")
        
        try:
            validated = dynamic_tool_creator._validate_parameters(test_case['params'])
            print(f"✅ Validated: {validated}")
            
            if test_case['expected'] == "TRUNCATED":
                # 检查是否被截断
                original_text = str(test_case['params'])
                validated_text = str(validated)
                if len(validated_text) < len(original_text):
                    print("✅ Correctly truncated")
                else:
                    print("⚠️  Not truncated as expected")
            elif test_case['expected'] == "FILTERED":
                # 检查 None 值是否被过滤
                if None not in validated.values():
                    print("✅ Correctly filtered None values")
                else:
                    print("⚠️  None values not filtered")
            else:
                print("✅ Validation passed")
                
        except Exception as e:
            print(f"❌ Validation failed: {e}")


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 增强功能演示
        await demo_enhanced_features()
        
        # 参数验证演示
        await demo_parameter_validation()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 