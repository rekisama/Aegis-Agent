#!/usr/bin/env python3
"""
LLM Security Validation Improvement Demo
LLM 安全验证改进演示
展示从硬编码检测到 LLM 智能检测的改进
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))

from python.agent.self_evolving_core import create_self_evolving_agent
from python.agent.core import AgentConfig


async def demo_security_improvement():
    """演示安全验证的改进"""
    
    print("🔒 LLM Security Validation Improvement Demo")
    print("=" * 50)
    
    # 创建 Agent
    config = AgentConfig(name="Security Agent")
    agent = create_self_evolving_agent(config)
    
    print(f"🤖 Created security agent: {agent.config.name}")
    
    # 测试代码样本
    test_cases = [
        {
            "name": "Safe with os import",
            "code": """
# This code imports os but doesn't use it dangerously
import os
text = params.get('text', '')
result = f"Text length: {len(text)}"
""",
            "description": "导入 os 但不危险使用"
        },
        
        {
            "name": "Dangerous os usage",
            "code": """
# This code uses os dangerously
import os
command = params.get('command', 'ls')
result = os.system(command)
""",
            "description": "危险地使用 os.system"
        },
        
        {
            "name": "Safe calculation",
            "code": """
# Safe calculation
numbers = params.get('numbers', [])
result = sum(numbers) if numbers else 0
""",
            "description": "安全的数学计算"
        },
        
        {
            "name": "Safe with format",
            "code": """
# Safe string formatting
text = params.get('text', '')
formatted = f"Processed: {text}"
result = formatted.upper()
""",
            "description": "安全的字符串格式化"
        }
    ]
    
    print("\n🔍 Testing Security Validation Methods...")
    print("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"📄 Description: {test_case['description']}")
        print("-" * 30)
        print("Code:")
        print(test_case['code'].strip())
        print("-" * 30)
        
        try:
            # 旧方法（硬编码检查）
            old_result = agent._basic_security_check(test_case['code'])
            print(f"🔧 Old method (hardcoded): {'❌ REJECT' if not old_result else '✅ ACCEPT'}")
            
            # 新方法（LLM 检查）
            new_result = await agent._validate_generated_code(test_case['code'])
            print(f"🧠 New method (LLM): {'❌ REJECT' if not new_result else '✅ ACCEPT'}")
            
            # 分析改进
            if old_result != new_result:
                if new_result and not old_result:
                    print("🎉 Improvement: LLM correctly accepted safe code that was rejected by hardcoded rules")
                elif old_result and not new_result:
                    print("⚠️  Change: LLM rejected code that was accepted by hardcoded rules")
            else:
                print("✅ Consistent: Both methods agree")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 演示工具创建
    print("\n🛠️  Tool Creation with LLM Security Validation")
    print("-" * 50)
    
    suggestions = [
        "建议创建一个安全的文本分析工具",
        "需要创建一个数据统计工具"
    ]
    
    for suggestion in suggestions:
        print(f"\n💡 Suggestion: {suggestion}")
        
        try:
            await agent._analyze_tool_creation_need(suggestion)
            print("✅ Tool creation analysis completed")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n📊 Summary")
    print("-" * 50)
    print("🔧 Old Method (Hardcoded):")
    print("   • 基于关键词匹配")
    print("   • 过于严格，拒绝安全代码")
    print("   • 无法理解上下文")
    print("   • 容易误判")
    
    print("\n🧠 New Method (LLM):")
    print("   • 基于语义理解")
    print("   • 智能分析安全风险")
    print("   • 考虑代码上下文")
    print("   • 更准确的判断")
    
    print("\n🎉 LLM Security Validation Improvement Demo Completed!")
    print("=" * 50)


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await demo_security_improvement()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 