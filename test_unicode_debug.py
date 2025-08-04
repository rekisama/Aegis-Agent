#!/usr/bin/env python3
"""
调试Unicode字符修复问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_unicode_debug():
    """调试Unicode字符修复问题"""
    
    # 导入Agent类
    from python.agent.core import Agent
    
    # 创建Agent实例
    agent = Agent()
    
    # 模拟LLM修复后的代码（包含中文注释中的Unicode字符）
    llm_fixed_code = '''def test_calculator(a, b):
    """
    简单的计算器
    :param a: 第一个数字
    :param b: 第二个数字
    :return: 两个数字的和
    """
    if a is None or b is None:
        raise ValueError("参数不能为None")
    return a + b'''
    
    print("🔍 调试Unicode字符修复问题")
    print("=" * 50)
    
    print("LLM修复后的代码:")
    print(llm_fixed_code)
    print("\n" + "-" * 50)
    
    # 检查Unicode字符
    unicode_chars = ['（', '）', '：', '，']
    
    print("检查Unicode字符:")
    for char in unicode_chars:
        if char in llm_fixed_code:
            print(f"❌ 发现Unicode字符: {char}")
        else:
            print(f"✅ 未发现Unicode字符: {char}")
    
    print("\n" + "-" * 50)
    
    # 应用Unicode字符修复
    fixed_code = agent._fix_unicode_characters(llm_fixed_code)
    
    print("修复后的代码:")
    print(fixed_code)
    print("\n" + "-" * 50)
    
    # 再次检查Unicode字符
    print("修复后检查Unicode字符:")
    for char in unicode_chars:
        if char in fixed_code:
            print(f"❌ 修复后仍包含Unicode字符: {char}")
        else:
            print(f"✅ 修复后不包含Unicode字符: {char}")
    
    # 检查是否包含ASCII字符
    ascii_chars = ['(', ')', ':', ',']
    print("\n检查ASCII字符:")
    for char in ascii_chars:
        if char in fixed_code:
            print(f"✅ 包含ASCII字符: {char}")
        else:
            print(f"❌ 不包含ASCII字符: {char}")
    
    print("\n" + "=" * 50)
    print("✅ Unicode字符修复调试完成！")

if __name__ == "__main__":
    test_unicode_debug() 