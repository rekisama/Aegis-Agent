#!/usr/bin/env python3
"""
Time Tool Creation Test
测试时间工具创建功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent))


async def test_time_tool_creation():
    """测试时间工具创建功能"""
    
    print("🧪 Time Tool Creation Test")
    print("=" * 50)
    
    # 测试任务分析功能
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Test Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    print(f"🤖 Created test agent: {agent.config.name}")
    
    # 测试时间查询任务
    test_task = "华盛顿现在几点了"
    print(f"\n🕐 Testing task: {test_task}")
    print("-" * 50)
    
    try:
        # 直接测试任务分析功能
        await agent._analyze_task_for_tool_creation(test_task)
        
        print("✅ Task analysis completed")
        
        # 检查是否创建了动态工具
        from python.agent.dynamic_tool_creator import dynamic_tool_creator
        stats = dynamic_tool_creator.get_tool_statistics()
        tools = stats.get("tools", [])
        
        if tools:
            print(f"🛠️  Dynamic tools created: {len(tools)}")
            for tool in tools:
                print(f"   • {tool['name']}: {tool['description']}")
        else:
            print("ℹ️  No dynamic tools created")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Time Tool Creation Test Completed!")
    print("=" * 50)


async def test_time_tool_code_generation():
    """测试时间工具代码生成"""
    
    print("\n🔧 Time Tool Code Generation Test")
    print("=" * 50)
    
    from python.agent.self_evolving_core import SelfEvolvingAgent
    from python.agent.core import AgentConfig
    
    config = AgentConfig(
        name="Test Agent",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=4000,
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = SelfEvolvingAgent(config)
    
    # 测试时间工具代码生成
    tool_name = "time_tool"
    tool_description = "获取指定地点的当前时间"
    parameters = {
        "location": {"type": "string", "required": True},
        "timezone": {"type": "string", "required": False},
        "format": {"type": "string", "required": False}
    }
    approach = "使用 pytz 库获取实时时间信息"
    
    try:
        # 生成时间工具代码
        code = agent._generate_time_tool_code(tool_name, parameters)
        print(f"✅ Generated time tool code for: {tool_name}")
        print(f"📝 Code length: {len(code)} characters")
        print(f"🔍 Code preview: {code[:200]}...")
        
        # 验证代码安全性
        is_safe = await agent._validate_generated_code(code)
        print(f"🔒 Code safety validation: {'✅ SAFE' if is_safe else '❌ UNSAFE'}")
        
    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Time Tool Code Generation Test Completed!")
    print("=" * 50)


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        await test_time_tool_creation()
        await test_time_tool_code_generation()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logging.error(f"Test error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 