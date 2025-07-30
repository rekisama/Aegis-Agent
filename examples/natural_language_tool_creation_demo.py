#!/usr/bin/env python3
"""
自然语言工具创建演示
演示Agent如何通过自然语言识别任务需求并自动创建新工具
"""

import asyncio
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 添加项目根目录到Python路径
import sys
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from python.agent.core import Agent
from python.utils.config import load_config


async def demo_natural_language_tool_creation():
    """演示自然语言工具创建功能"""
    
    print("🤖 自然语言工具创建演示")
    print("=" * 50)
    
    # 初始化Agent
    config = load_config()
    agent = Agent(config)
    
    print(f"✅ Agent初始化完成")
    print(f"📋 当前可用工具: {list(agent.tools.keys())}")
    print()
    

    
    # 演示任务2：使用新创建的工具
    print("🎯 演示任务2: 使用新创建的图片处理工具")
    task2 = "使用图片处理工具调整一张图片的亮度为1.2倍"
    
    print(f"📝 任务描述: {task2}")
    print("⏳ Agent正在执行任务...")
    
    result2 = await agent.execute_task(task2)
    
    print(f"✅ 任务2执行完成")
    print(f"📊 结果: {result2.get('result', '无结果')}")
    print()
    
    # 演示任务3：另一个需要新工具的任务
    print("🎯 演示任务3: 创建数据分析工具")
    task3 = "我需要一个工具来分析CSV文件，计算平均值、中位数和标准差"
    
    print(f"📝 任务描述: {task3}")
    print("⏳ Agent正在分析任务需求...")
    
    result3 = await agent.execute_task(task3)
    
    print(f"✅ 任务3执行完成")
    print(f"📊 结果: {result3.get('result', '无结果')}")
    print()
    
    # 显示最终的工具列表
    print("📋 最终工具列表:")
    for name, tool in agent.tools.items():
        print(f"  - {name}: {tool.description}")
    
    print()
    print("🎉 演示完成！")


async def demo_web_interface():
    """演示Web界面中的自然语言工具创建"""
    
    print("🌐 Web界面自然语言工具创建演示")
    print("=" * 50)
    
    print("1. 启动Web服务器:")
    print("   python web/start_server.py")
    print()
    
    print("2. 访问 http://localhost:8000")
    print()
    
    print("3. 在聊天界面中输入以下任务:")
    print("   - '我需要一个工具来计算复利'")
    print("   - '创建一个工具来生成随机密码'")
    print("   - '我需要一个工具来验证邮箱格式'")
    print()
    
    print("4. Agent会自动:")
    print("   - 分析任务需求")
    print("   - 判断是否需要新工具")
    print("   - 创建相应的工具")
    print("   - 执行任务")
    print()
    
    print("5. 在工具管理界面查看:")
    print("   - 内置工具列表")
    print("   - 动态创建的工具")
    print("   - 工具使用统计")
    print()


async def demo_advanced_features():
    """演示高级功能"""
    
    print("🚀 高级功能演示")
    print("=" * 50)
    
    print("1. 智能工具识别:")
    print("   - Agent会分析任务描述")
    print("   - 检查现有工具是否满足需求")
    print("   - 自动决定是否需要创建新工具")
    print()
    
    print("2. 安全验证:")
    print("   - LLM验证工具代码安全性")
    print("   - 检查是否包含危险操作")
    print("   - 确保工具功能合理")
    print()
    
    print("3. 实时工具发现:")
    print("   - 文件系统监控")
    print("   - 自动加载新工具")
    print("   - 热更新支持")
    print()
    
    print("4. 工具管理:")
    print("   - Web界面管理")
    print("   - 工具统计信息")
    print("   - 测试和删除功能")
    print()


if __name__ == "__main__":
    print("🎯 自然语言工具创建系统演示")
    print("=" * 60)
    print()
    
    # 运行演示
    asyncio.run(demo_natural_language_tool_creation())
    print()
    
    demo_web_interface()
    print()
    
    demo_advanced_features()
    print()
    
    print("📚 使用说明:")
    print("1. 直接向Agent描述你的需求")
    print("2. Agent会自动分析是否需要新工具")
    print("3. 如果需要，Agent会创建相应的工具")
    print("4. 新工具会立即可用")
    print("5. 可以在Web界面中管理所有工具")
    print()
    
    print("💡 示例任务:")
    print("- '我需要一个工具来计算BMI指数'")
    print("- '创建一个工具来生成二维码'")
    print("- '我需要一个工具来解析JSON数据'")
    print("- '创建一个工具来验证身份证号码'")
    print()
    
    print("🎉 系统已准备就绪！开始体验智能工具创建吧！") 