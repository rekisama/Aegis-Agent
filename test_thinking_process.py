#!/usr/bin/env python3
"""
测试Agent思考过程展示功能
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_thinking_process():
    """测试思考过程展示功能"""
    
    print("🧠 测试Agent思考过程展示功能")
    print("=" * 50)
    
    # 导入Agent类
    from python.agent.core import Agent
    
    # 创建Agent实例
    agent = Agent()
    
    # 模拟前端日志发送
    original_send_log = agent._send_log_to_frontend
    
    async def mock_send_log(message: str, level: str = "info"):
        """模拟发送日志到前端"""
        emoji = "🔍" if level == "info" else "❌" if level == "error" else "⚠️"
        print(f"{emoji} {message}")
    
    # 替换日志发送方法
    agent._send_log_to_frontend = mock_send_log
    
    # 测试用例1：正常任务执行
    print("\n📋 测试用例1：正常任务执行")
    print("-" * 30)
    
    test_task = "计算1+1的结果"
    result = await agent.execute_task(test_task)
    
    print(f"\n结果: {result}")
    
    # 测试用例2：包含错误的代码执行
    print("\n📋 测试用例2：包含错误的代码执行")
    print("-" * 30)
    
    test_task_with_error = "执行代码：print(undefined_variable)"
    result = await agent.execute_task(test_task_with_error)
    
    print(f"\n结果: {result}")
    
    # 测试用例3：工具创建
    print("\n📋 测试用例3：工具创建")
    print("-" * 30)
    
    test_tool_spec = {
        "name": "test_calculator",
        "description": "简单的计算器工具",
        "code": '''def test_calculator(a, b):
    """
    简单的计算器
    :param a: 第一个数字
    :param b: 第二个数字
    """
    return a + b''',
        "parameters": {"a": "int", "b": "int"}
    }
    
    result = await agent.create_new_tool(test_tool_spec)
    
    print(f"\n结果: {result}")
    
    # 测试用例4：错误分析
    print("\n📋 测试用例4：错误分析")
    print("-" * 30)
    
    test_error = "SyntaxError: invalid character '，' (U+FF0C) (test.py, line 5)"
    error_analysis = agent._analyze_tool_creation_error(test_error, {})
    
    print(f"错误信息: {test_error}")
    print(f"分析结果: {error_analysis}")
    
    # 测试用例5：Unicode字符修复
    print("\n📋 测试用例5：Unicode字符修复")
    print("-" * 30)
    
    test_code_with_unicode = '''def test_function（param1，param2）:
    """
    测试函数
    :param param1: 参数1
    :param param2: 参数2，如果为None则不保存
    """
    result = param1 + param2
    return result'''
    
    fixed_code = agent._fix_unicode_characters(test_code_with_unicode)
    
    print(f"原始代码: {test_code_with_unicode}")
    print(f"修复后代码: {fixed_code}")
    
    print("\n" + "=" * 50)
    print("✅ 思考过程展示功能测试完成！")

if __name__ == "__main__":
    asyncio.run(test_thinking_process()) 