#!/usr/bin/env python3
"""
简单任务执行测试
"""

import asyncio
from python.agent.core import Agent

async def test_simple_task():
    """测试简单任务执行"""
    print("🧪 测试简单任务执行")
    print("=" * 40)
    
    agent = Agent()
    
    # 测试任务
    task = "查看当前目录文件"
    print(f"📝 任务: {task}")
    
    try:
        result = await agent.execute_task(task)
        print(f"✅ 任务完成!")
        print(f"📋 结果: {result['result']}")
        
        # 显示元数据
        if 'metadata' in result and 'tool_plan' in result['metadata']:
            plan = result['metadata']['tool_plan']
            print(f"🤖 执行计划: {plan.get('description', 'N/A')}")
            
            if 'steps' in plan:
                print("🔧 使用的工具:")
                for step in plan['steps']:
                    print(f"   - {step['tool']}: {step.get('reason', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 任务执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_task()) 