#!/usr/bin/env python3
"""
测试Unicode字符修复功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_unicode_fix():
    """测试Unicode字符修复功能"""
    
    # 导入Agent类
    from python.agent.core import Agent
    
    # 创建Agent实例
    agent = Agent()
    
    # 测试用例：包含Unicode字符的代码
    test_code = '''def test_function（param1，param2）:
    """
    测试函数
    :param param1: 参数1
    :param param2: 参数2，如果为None则不保存
    """
    result = param1 + param2
    return result'''
    
    print("🧪 测试Unicode字符修复功能")
    print("=" * 50)
    
    print(f"原始代码:")
    print(test_code)
    print("\n" + "-" * 50)
    
    # 修复Unicode字符
    fixed_code = agent._fix_unicode_characters(test_code)
    
    print(f"修复后代码:")
    print(fixed_code)
    print("\n" + "-" * 50)
    
    # 检查是否修复了Unicode字符
    unicode_chars = ['（', '）', '：', '，']
    fixed_chars = ['(', ')', ':', ',']
    
    print("检查修复结果:")
    for unicode_char, fixed_char in zip(unicode_chars, fixed_chars):
        if unicode_char in test_code:
            print(f"❌ 原始代码包含: {unicode_char}")
        else:
            print(f"✅ 原始代码不包含: {unicode_char}")
            
        if unicode_char in fixed_code:
            print(f"❌ 修复后代码仍包含: {unicode_char}")
        else:
            print(f"✅ 修复后代码不包含: {unicode_char}")
            
        if fixed_char in fixed_code:
            print(f"✅ 修复后代码包含: {fixed_char}")
        else:
            print(f"❌ 修复后代码不包含: {fixed_char}")
        print()
    
    # 测试模板字符串修复
    print("测试模板字符串修复:")
    template = '''def test_function（param1，param2）:
    """
    测试函数
    :param param1: 参数1
    :param param2: 参数2，如果为None则不保存
    """
    result = param1 + param2
    return result'''
    
    fixed_template = agent._fix_unicode_characters(template)
    print(f"模板修复前: {template}")
    print(f"模板修复后: {fixed_template}")
    
    print("\n" + "=" * 50)
    print("✅ Unicode字符修复功能测试完成！")

if __name__ == "__main__":
    test_unicode_fix() 