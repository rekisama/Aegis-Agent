#!/usr/bin/env python3
"""
Generalized Tool Creation Test
测试完全泛化的工具创建系统
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


async def test_generalized_tool_creation():
    """测试完全泛化的工具创建"""
    
    print("🧪 Generalized Tool Creation Test")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Generalized Agent",
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
        "现在伦敦几点了",
        "北京天气怎么样",
        "计算 123 * 456 的结果",
        "翻译 'Hello World' 为中文",
        "获取美元兑人民币的汇率",
        "分析这段文本的情感倾向：今天天气真好，心情很愉快",
        "生成一个随机密码",
        "检查这个邮箱地址是否有效：test@example.com"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n🔍 Test {i}: {task}")
        print("-" * 50)
        
        try:
            # 直接测试任务分析
            analysis = await agent._analyze_task_for_tool_creation(task)
            
            print(f"📊 Analysis Result:")
            print(f"   Should create tool: {analysis.get('should_create_tool', False)}")
            
            if analysis.get('should_create_tool', False):
                print(f"   Tool name: {analysis.get('tool_name', 'N/A')}")
                print(f"   Tool description: {analysis.get('tool_description', 'N/A')}")
                print(f"   Implementation approach: {analysis.get('implementation_approach', 'N/A')}")
                print(f"   Reasoning: {analysis.get('reasoning', 'N/A')}")
                
                # 测试工具创建
                tool_created = await agent._create_dynamic_tool_from_analysis(analysis)
                print(f"   Tool creation: {'✅ Success' if tool_created else '❌ Failed'}")
            else:
                print(f"   Reasoning: {analysis.get('reasoning', 'No specialized tool needed')}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Generalized Tool Creation Test Completed!")
    print("=" * 50)


async def test_llm_code_generation():
    """测试 LLM 代码生成"""
    
    print("\n🔧 LLM Code Generation Test")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Code Generation Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    # 测试不同类型的工具代码生成
    test_tools = [
        {
            "name": "time_tool",
            "description": "获取指定地点的当前时间",
            "parameters": {"location": {"type": "string", "required": True}},
            "approach": "使用 datetime 和 pytz 库获取实时时间"
        },
        {
            "name": "weather_tool", 
            "description": "获取指定城市的天气信息",
            "parameters": {"city": {"type": "string", "required": True}},
            "approach": "使用天气 API 获取实时天气数据"
        },
        {
            "name": "calculator_tool",
            "description": "执行数学计算",
            "parameters": {"expression": {"type": "string", "required": True}},
            "approach": "使用 eval 函数安全地计算数学表达式"
        }
    ]
    
    for i, tool in enumerate(test_tools, 1):
        print(f"\n🔧 Test {i}: {tool['name']}")
        print("-" * 50)
        
        try:
            # 生成工具代码
            code = await agent._generate_tool_code(
                tool['name'], 
                tool['description'], 
                tool['parameters'], 
                tool['approach']
            )
            
            print(f"✅ Generated code for: {tool['name']}")
            print(f"📝 Code length: {len(code)} characters")
            print(f"🔍 Code preview: {code[:200]}...")
            
            # 验证代码安全性
            is_safe = await agent._validate_generated_code(code)
            print(f"🔒 Code safety: {'✅ SAFE' if is_safe else '❌ UNSAFE'}")
            
        except Exception as e:
            print(f"❌ Code generation failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 LLM Code Generation Test Completed!")
    print("=" * 50)


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await test_generalized_tool_creation()
        await test_llm_code_generation()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 