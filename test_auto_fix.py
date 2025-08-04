#!/usr/bin/env python3
"""
测试Agent自动错误修复功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_auto_fix():
    """测试自动错误修复功能"""
    
    # 导入Agent类
    from python.agent.core import Agent
    
    # 创建Agent实例
    agent = Agent()
    
    # 测试用例：包含Unicode字符错误的代码
    test_tool_spec = {
        "name": "test_tool",
        "description": "测试工具",
        "code": '''def test_function（param1，param2）:
    """
    测试函数
    :param param1: 参数1
    :param param2: 参数2，如果为None则不保存
    """
    result = param1 + param2
    return result''',
        "parameters": {"param1": "str", "param2": "str"}
    }
    
    print("开始测试自动错误修复功能...")
    print("=" * 50)
    
    # 测试Unicode字符修复
    print("1. 测试Unicode字符修复...")
    original_code = test_tool_spec["code"]
    fixed_code = agent._fix_unicode_characters(original_code)
    
    print(f"原始代码: {original_code}")
    print(f"修复后代码: {fixed_code}")
    
    if fixed_code != original_code:
        print("✅ Unicode字符修复功能正常")
    else:
        print("❌ Unicode字符修复功能未生效")
    
    # 测试错误分析
    print("\n2. 测试错误分析...")
    test_error = "SyntaxError: invalid character '，' (U+FF0C) (test.py, line 5)"
    error_analysis = agent._analyze_tool_creation_error(test_error, test_tool_spec)
    
    print(f"错误信息: {test_error}")
    print(f"分析结果: {error_analysis}")
    
    if error_analysis["error_type"] == "syntax_error":
        print("✅ 错误分析功能正常")
    else:
        print("❌ 错误分析功能异常")
    
    # 测试语法错误修复
    print("\n3. 测试语法错误修复...")
    syntax_error_code = '''def test_func（param）:
    return param'''
    
    fixed_syntax_code = await agent._auto_fix_syntax_error(syntax_error_code, test_error)
    
    if fixed_syntax_code and "（" not in fixed_syntax_code and "）" not in fixed_syntax_code:
        print("✅ 语法错误修复功能正常")
        print(f"修复后代码: {fixed_syntax_code}")
    else:
        print("❌ 语法错误修复功能异常")
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_auto_fix()) 