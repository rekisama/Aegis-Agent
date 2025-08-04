#!/usr/bin/env python3
"""
测试改进后的错误修复机制
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from python.agent.core import Agent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_syntax_error_fix():
    """测试语法错误修复"""
    print("🧪 测试语法错误修复")
    print("=" * 50)
    
    # 创建一个有语法错误的工具规范
    tool_spec = {
        "name": "test_syntax_fix",
        "description": "测试语法错误修复",
        "code": '''
import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path

def apply_fisheye(input_path, output_path, strength=0.5):
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param strength: 鱼眼效果强度
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    
    # 读取图片
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError("无法读取图片文件")
    
    return f"鱼眼效果处理完成，保存至: {output_path}"
''',
        "parameters": {}
    }
    
    # 创建Agent实例
    agent = Agent()
    
    print("📝 原始代码（包含语法错误）:")
    print(tool_spec["code"])
    print("\n" + "="*50)
    
    # 尝试创建工具
    print("🛠️ 尝试创建工具...")
    result = await agent.create_new_tool(tool_spec)
    
    print(f"\n📊 创建结果:")
    print(f"  成功: {result.get('success', False)}")
    if result.get('success'):
        print(f"  工具名称: {result.get('tool_name')}")
        print(f"  消息: {result.get('message')}")
    else:
        print(f"  错误: {result.get('error')}")
        if 'details' in result:
            print(f"  详细信息: {result['details'][:200]}...")

async def test_import_error_fix():
    """测试导入错误修复"""
    print("\n🧪 测试导入错误修复")
    print("=" * 50)
    
    # 创建一个有导入错误的工具规范
    tool_spec = {
        "name": "test_import_fix",
        "description": "测试导入错误修复",
        "code": '''
def test_function():
    import nonexistent_module
    return "test"
''',
        "parameters": {}
    }
    
    # 创建Agent实例
    agent = Agent()
    
    print("📝 原始代码（包含导入错误）:")
    print(tool_spec["code"])
    print("\n" + "="*50)
    
    # 尝试创建工具
    print("🛠️ 尝试创建工具...")
    result = await agent.create_new_tool(tool_spec)
    
    print(f"\n📊 创建结果:")
    print(f"  成功: {result.get('success', False)}")
    if result.get('success'):
        print(f"  工具名称: {result.get('tool_name')}")
        print(f"  消息: {result.get('message')}")
    else:
        print(f"  错误: {result.get('error')}")

async def test_unicode_error_fix():
    """测试Unicode字符错误修复"""
    print("\n🧪 测试Unicode字符错误修复")
    print("=" * 50)
    
    # 创建一个有Unicode字符错误的工具规范
    tool_spec = {
        "name": "test_unicode_fix",
        "description": "测试Unicode字符错误修复",
        "code": '''
def test_function():
    # 这是一个包含全角标点符号的注释：，。！？
    print("测试Unicode字符修复")
    return "success"
''',
        "parameters": {}
    }
    
    # 创建Agent实例
    agent = Agent()
    
    print("📝 原始代码（包含Unicode字符错误）:")
    print(tool_spec["code"])
    print("\n" + "="*50)
    
    # 尝试创建工具
    print("🛠️ 尝试创建工具...")
    result = await agent.create_new_tool(tool_spec)
    
    print(f"\n📊 创建结果:")
    print(f"  成功: {result.get('success', False)}")
    if result.get('success'):
        print(f"  工具名称: {result.get('tool_name')}")
        print(f"  消息: {result.get('message')}")
    else:
        print(f"  错误: {result.get('error')}")

async def main():
    """主测试函数"""
    print("🚀 错误修复机制改进测试")
    print("=" * 60)
    print("本测试验证改进后的错误识别和修复机制")
    print()
    
    try:
        # 测试语法错误修复
        await test_syntax_error_fix()
        
        # 测试导入错误修复
        await test_import_error_fix()
        
        # 测试Unicode字符错误修复
        await test_unicode_error_fix()
        
        print("\n✅ 测试完成")
        print("\n📝 总结:")
        print("1. 改进的错误识别机制")
        print("2. 更精确的语法错误检测")
        print("3. 更详细的错误上下文信息")
        print("4. 更有效的LLM修复提示词")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        logging.exception("测试失败")

if __name__ == "__main__":
    asyncio.run(main()) 