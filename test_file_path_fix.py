#!/usr/bin/env python3
"""
测试文件路径修复功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from python.agent.core import Agent
from python.utils.config import load_config

async def test_file_path_fix():
    """测试文件路径修复功能"""
    
    # 初始化agent
    config = load_config()
    agent = Agent(config)
    
    # 模拟一个文件路径错误的代码
    original_code = """
from PIL import Image, ImageEnhance

def adjust_contrast(image_path, factor):
    img = Image.open(image_path)
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)

adjusted_img = adjust_contrast('input.jpg', 1.5)
adjusted_img.save('output.jpg')
"""
    
    error_message = "FileNotFoundError: [Errno 2] No such file or directory: 'input.jpg'"
    
    print("测试文件路径修复功能...")
    print(f"原始代码:\n{original_code}")
    print(f"错误信息: {error_message}")
    print("-" * 50)
    
    # 调用自动修复功能
    result = await agent._auto_fix_code_error(original_code, error_message)
    
    if result["success"]:
        print("修复成功！")
        print(f"修复后的代码:\n{result['fixed_code']}")
    else:
        print("修复失败！")
        print(f"错误: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_file_path_fix()) 