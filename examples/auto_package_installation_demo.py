#!/usr/bin/env python3
"""
自动包安装演示
演示Agent如何自动检测缺失的包并安装
"""

import asyncio
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


async def demo_auto_package_installation():
    """演示自动包安装功能"""
    
    print("🤖 自动包安装演示")
    print("=" * 50)
    
    # 初始化Agent
    config = load_config()
    agent = Agent(config)
    
    print(f"✅ Agent初始化完成")
    print(f"📋 当前可用工具: {list(agent.tools.keys())}")
    print()
    
    # 演示任务1：需要Pillow包的任务
    print("🎯 演示任务1: 图片处理（需要Pillow包）")
    task1 = "使用PIL库处理图片，调整亮度为1.2倍"
    
    print(f"📝 任务描述: {task1}")
    print("⏳ Agent正在执行任务...")
    print("💡 预期行为: Agent会检测到PIL模块缺失，自动安装Pillow包")
    print()
    
    result1 = await agent.execute_task(task1)
    
    print(f"✅ 任务1执行完成")
    print(f"📊 结果: {result1.get('result', '无结果')}")
    print()
    
    # 演示任务2：需要requests包的任务
    print("🎯 演示任务2: 网络请求（需要requests包）")
    task2 = "使用requests库获取网页内容"
    
    print(f"📝 任务描述: {task2}")
    print("⏳ Agent正在执行任务...")
    print("💡 预期行为: Agent会检测到requests模块缺失，自动安装requests包")
    print()
    
    result2 = await agent.execute_task(task2)
    
    print(f"✅ 任务2执行完成")
    print(f"📊 结果: {result2.get('result', '无结果')}")
    print()
    
    # 演示任务3：需要numpy包的任务
    print("🎯 演示任务3: 数值计算（需要numpy包）")
    task3 = "使用numpy计算数组的平均值和标准差"
    
    print(f"📝 任务描述: {task3}")
    print("⏳ Agent正在执行任务...")
    print("💡 预期行为: Agent会检测到numpy模块缺失，自动安装numpy包")
    print()
    
    result3 = await agent.execute_task(task3)
    
    print(f"✅ 任务3执行完成")
    print(f"📊 结果: {result3.get('result', '无结果')}")
    print()
    
    print("🎉 演示完成！")


async def demo_web_interface_auto_installation():
    """演示Web界面中的自动包安装"""
    
    print("🌐 Web界面自动包安装演示")
    print("=" * 50)
    
    print("1. 启动Web服务器:")
    print("   python web/start_server.py")
    print()
    
    print("2. 访问 http://localhost:8000")
    print()
    
    print("3. 在聊天界面中输入以下任务:")
    print("   - '使用PIL库处理图片'")
    print("   - '使用requests获取网页内容'")
    print("   - '使用numpy进行数值计算'")
    print()
    
    print("4. Agent会自动:")
    print("   - 检测到缺失的包")
    print("   - 使用终端工具安装包")
    print("   - 重新执行代码")
    print("   - 显示执行结果")
    print()
    
    print("5. 在实时日志中可以看到:")
    print("   - 包安装过程")
    print("   - 代码执行过程")
    print("   - 最终结果")
    print()


def demo_installation_strategies():
    """演示不同的安装策略"""
    
    print("🔧 安装策略演示")
    print("=" * 50)
    
    print("1. 智能包名映射:")
    print("   - PIL → pillow")
    print("   - cv2 → opencv-python")
    print("   - sklearn → scikit-learn")
    print()
    
    print("2. 安装命令选择:")
    print("   - pip install package_name")
    print("   - pip install --user package_name")
    print("   - python -m pip install package_name")
    print()
    
    print("3. 错误处理:")
    print("   - 网络连接失败")
    print("   - 权限不足")
    print("   - 包名不存在")
    print()
    
    print("4. 安装验证:")
    print("   - 检查包是否安装成功")
    print("   - 验证包是否可以导入")
    print("   - 重新执行原始代码")
    print()


if __name__ == "__main__":
    print("🎯 自动包安装系统演示")
    print("=" * 60)
    print()
    
    # 运行演示
    asyncio.run(demo_auto_package_installation())
    print()
    
    demo_web_interface_auto_installation()
    print()
    
    demo_installation_strategies()
    print()
    
    print("📚 功能说明:")
    print("1. Agent会自动检测ModuleNotFoundError")
    print("2. 从错误信息中提取包名")
    print("3. 使用terminal工具安装缺失的包")
    print("4. 重新执行原始代码")
    print("5. 显示最终结果")
    print()
    
    print("💡 支持的包:")
    print("- pillow (PIL)")
    print("- requests")
    print("- numpy")
    print("- pandas")
    print("- matplotlib")
    print("- opencv-python (cv2)")
    print("- scikit-learn (sklearn)")
    print("- 等等...")
    print()
    
    print("🎉 系统已准备就绪！开始体验智能包安装吧！") 