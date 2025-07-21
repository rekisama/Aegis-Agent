#!/usr/bin/env python3
"""
测试编码修复
验证代码执行工具是否能正确处理中文字符
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from python.tools.code import CodeExecutionTool

async def test_chinese_character_counting():
    """测试中文字符计数"""
    print("🧪 测试中文字符计数功能")
    print("=" * 50)
    
    # 创建代码执行工具
    code_tool = CodeExecutionTool()
    
    # 测试用例
    test_cases = [
        {
            "name": "简单中文字符计数",
            "code": """
text = "阿门阿前一棵葡萄树"
count = len(text)
print(f"字符数量: {count}")
print(f"字符列表: {list(text)}")
""",
            "expected": "字符数量: 9"
        },
        {
            "name": "混合字符计数",
            "code": """
text = "Hello世界123"
chinese_count = sum(1 for char in text if ord(char) > 127)
total_count = len(text)
print(f"总字符数: {total_count}")
print(f"中文字符数: {chinese_count}")
print(f"英文字符数: {total_count - chinese_count}")
""",
            "expected": "中文字符数: 2"
        },
        {
            "name": "复杂字符串分析",
            "code": """
def analyze_text(text):
    total = len(text)
    chinese = sum(1 for char in text if ord(char) > 127)
    english = sum(1 for char in text if ord(char) <= 127 and char.isalpha())
    digits = sum(1 for char in text if char.isdigit())
    spaces = sum(1 for char in text if char.isspace())
    
    return {
        "total": total,
        "chinese": chinese,
        "english": english,
        "digits": digits,
        "spaces": spaces
    }

text = "阿门阿前一棵葡萄树 ABC 123"
result = analyze_text(text)
print(f"分析结果: {result}")
""",
            "expected": "分析结果"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            result = await code_tool.execute(code=test_case["code"])
            
            if result.success:
                print("✅ 执行成功")
                print(f"输出: {result.data.get('stdout', '')}")
                if result.data.get('stderr'):
                    print(f"错误: {result.data.get('stderr', '')}")
            else:
                print("❌ 执行失败")
                print(f"错误: {result.error}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
        
        print()

async def test_encoding_handling():
    """测试编码处理"""
    print("\n🔤 测试编码处理")
    print("=" * 50)
    
    code_tool = CodeExecutionTool()
    
    # 测试包含中文字符的代码
    chinese_code = """
# 测试中文字符处理
text = "你好世界"
print(f"文本: {text}")
print(f"长度: {len(text)}")
print(f"编码: {text.encode('utf-8')}")
"""
    
    try:
        result = await code_tool.execute(code=chinese_code)
        
        if result.success:
            print("✅ 中文字符处理成功")
            print(f"输出: {result.data.get('stdout', '')}")
        else:
            print("❌ 中文字符处理失败")
            print(f"错误: {result.error}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

async def test_original_task():
    """测试原始任务"""
    print("\n🎯 测试原始任务")
    print("=" * 50)
    
    code_tool = CodeExecutionTool()
    
    # 原始任务的代码
    original_code = """
text = "阿门阿前一棵葡萄树"
count = len(text)
print(f"这句话有 {count} 个字")
print("字符列表:")
for i, char in enumerate(text, 1):
    print(f"{i}. {char}")
"""
    
    try:
        result = await code_tool.execute(code=original_code)
        
        if result.success:
            print("✅ 原始任务执行成功")
            print(f"输出: {result.data.get('stdout', '')}")
        else:
            print("❌ 原始任务执行失败")
            print(f"错误: {result.error}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    print("🚀 开始编码修复测试...")
    asyncio.run(test_chinese_character_counting())
    asyncio.run(test_encoding_handling())
    asyncio.run(test_original_task())
    print("\n✅ 测试完成！") 