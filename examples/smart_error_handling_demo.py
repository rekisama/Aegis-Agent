#!/usr/bin/env python3
"""
智能错误处理系统演示
展示如何自动分析错误并执行修复操作
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from python.agent.error_handler import ErrorHandlerAgent
from python.tools.enhanced_terminal import EnhancedTerminalTool, ErrorAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demo_basic_error_analysis():
    """演示基本错误分析"""
    print("🔍 基本错误分析演示")
    print("=" * 50)
    
    # 模拟各种错误场景
    error_scenarios = [
        {
            "name": "Python模块缺失",
            "command": "python -c 'import requests; print(\"requests found\")'",
            "expected_error": "ModuleNotFoundError: No module named 'requests'"
        },
        {
            "name": "系统命令缺失",
            "command": "tree --version",
            "expected_error": "bash: tree: command not found"
        },
        {
            "name": "权限问题",
            "command": "touch /root/test_file",
            "expected_error": "Permission denied"
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\n📋 场景: {scenario['name']}")
        print(f"命令: {scenario['command']}")
        
        # 分析错误
        analysis = ErrorAnalyzer.analyze_error(scenario['expected_error'])
        
        print(f"错误分析:")
        print(f"  类型: {analysis['error_type'].value}")
        print(f"  置信度: {analysis['confidence']}")
        print(f"  修复建议: {analysis['suggested_fix']}")
        
        if analysis['missing_module']:
            print(f"  缺失模块: {analysis['missing_module']}")
        if analysis['missing_command']:
            print(f"  缺失命令: {analysis['missing_command']}")

async def demo_enhanced_terminal():
    """演示增强终端工具"""
    print("\n🔧 增强终端工具演示")
    print("=" * 50)
    
    terminal = EnhancedTerminalTool()
    
    # 测试成功命令
    print("\n1. 成功命令测试:")
    result = await terminal.execute(command="echo 'Hello from enhanced terminal'")
    print(f"  成功: {result.success}")
    if result.success:
        print(f"  输出: {result.data['stdout'].strip()}")
    
    # 测试失败命令
    print("\n2. 失败命令测试:")
    result = await terminal.execute(command="nonexistent_command")
    print(f"  成功: {result.success}")
    if not result.success:
        print(f"  错误: {result.error}")
        if result.data and 'error_analysis' in result.data:
            analysis = result.data['error_analysis']
            print(f"  错误类型: {analysis['error_type'].value}")
            print(f"  修复建议: {analysis['suggested_fix']}")

async def demo_auto_fix_scenarios():
    """演示自动修复场景"""
    print("\n🛠️ 自动修复场景演示")
    print("=" * 50)
    
    agent = ErrorHandlerAgent()
    
    scenarios = [
        {
            "name": "自动安装Python模块",
            "command": "python -c 'import pandas; print(\"pandas imported successfully\")'",
            "description": "尝试导入pandas模块，如果不存在会自动安装"
        },
        {
            "name": "权限问题自动修复",
            "command": "mkdir /tmp/test_dir_$(date +%s)",
            "description": "创建临时目录，演示权限处理"
        },
        {
            "name": "系统命令检查",
            "command": "which git && git --version",
            "description": "检查git命令是否可用"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 场景: {scenario['name']}")
        print(f"描述: {scenario['description']}")
        print(f"命令: {scenario['command']}")
        
        result = await agent.execute_with_auto_fix(
            command=scenario['command'],
            max_attempts=3
        )
        
        print(f"结果:")
        print(f"  最终成功: {result['success']}")
        print(f"  尝试次数: {result['attempts']}")
        print(f"  自动修复次数: {result['auto_fixes_applied']}")
        
        if result['success']:
            print("  ✅ 任务成功完成")
        else:
            print(f"  ❌ 最终错误: {result.get('final_error', 'Unknown error')}")

async def demo_error_handler_agent():
    """演示错误处理代理"""
    print("\n🤖 错误处理代理演示")
    print("=" * 50)
    
    agent = ErrorHandlerAgent()
    
    # 模拟一个复杂的错误处理流程
    print("\n1. 复杂错误处理流程:")
    
    # 尝试运行一个需要多个依赖的Python脚本
    test_script = '''
import requests
import pandas as pd
import matplotlib.pyplot as plt

# 获取数据
response = requests.get('https://api.github.com/users/octocat')
data = response.json()

# 创建DataFrame
df = pd.DataFrame([data])

# 绘制图表
plt.figure(figsize=(10, 6))
plt.bar(df.columns, df.iloc[0])
plt.title('GitHub User Data')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('github_user_data.png')
print("图表已保存为 github_user_data.png")
'''
    
    # 将脚本写入临时文件
    script_path = "/tmp/test_script.py"
    with open(script_path, 'w') as f:
        f.write(test_script)
    
    print(f"创建测试脚本: {script_path}")
    print("脚本内容包含多个可能缺失的依赖")
    
    # 执行脚本
    result = await agent.execute_with_auto_fix(
        command=f"python {script_path}",
        max_attempts=5
    )
    
    print(f"\n执行结果:")
    print(f"  最终成功: {result['success']}")
    print(f"  尝试次数: {result['attempts']}")
    print(f"  自动修复次数: {result['auto_fixes_applied']}")
    
    # 显示错误摘要
    print(f"\n2. 错误处理摘要:")
    summary = agent.get_error_summary()
    print(f"  总错误数: {summary['total_errors']}")
    print(f"  总修复数: {summary['total_fixes']}")
    print(f"  成功修复数: {summary['successful_fixes']}")
    print(f"  错误类型: {summary['error_types']}")

async def demo_interactive_error_handling():
    """演示交互式错误处理"""
    print("\n💬 交互式错误处理演示")
    print("=" * 50)
    
    agent = ErrorHandlerAgent()
    
    print("\n模拟用户交互式错误处理:")
    print("1. 用户运行命令")
    print("2. 命令失败，系统分析错误")
    print("3. 系统生成修复建议")
    print("4. 用户确认后执行修复")
    print("5. 重新尝试原始命令")
    
    # 模拟一个需要用户确认的修复场景
    command = "sudo apt update && sudo apt install -y tree"
    
    print(f"\n📋 示例命令: {command}")
    print("这个命令可能需要用户确认sudo权限")
    
    # 执行命令
    result = await agent.execute_with_auto_fix(
        command=command,
        max_attempts=2
    )
    
    print(f"\n执行结果:")
    print(f"  成功: {result['success']}")
    print(f"  尝试次数: {result['attempts']}")
    
    if not result['success']:
        print(f"  失败原因: {result.get('final_error', 'Unknown')}")
        print("  注意: 某些命令可能需要用户交互确认")

async def main():
    """主演示函数"""
    print("🚀 智能错误处理系统演示")
    print("=" * 60)
    print("本演示展示如何自动分析错误并执行修复操作")
    print()
    
    try:
        # 基本错误分析
        await demo_basic_error_analysis()
        
        # 增强终端工具
        await demo_enhanced_terminal()
        
        # 自动修复场景
        await demo_auto_fix_scenarios()
        
        # 错误处理代理
        await demo_error_handler_agent()
        
        # 交互式错误处理
        await demo_interactive_error_handling()
        
        print("\n✅ 演示完成")
        print("\n📝 总结:")
        print("1. 系统能够自动识别常见错误类型")
        print("2. 提供针对性的修复建议")
        print("3. 自动执行修复操作")
        print("4. 支持重试机制")
        print("5. 记录错误和修复历史")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        logging.exception("演示失败")

if __name__ == "__main__":
    asyncio.run(main()) 