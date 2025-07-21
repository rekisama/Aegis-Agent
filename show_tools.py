#!/usr/bin/env python3
"""
展示 Aegis Agent 系统中可用的工具
"""

import asyncio
from python.agent.core import Agent

async def show_available_tools():
    """展示当前可用的工具"""
    print("🛡️ Aegis Agent - 可用工具列表")
    print("=" * 50)
    
    # 创建智能体实例
    agent = Agent()
    
    print(f"🤖 智能体名称: {agent.config.name}")
    print(f"🆔 智能体ID: {agent.agent_id}")
    print(f"🔧 工具数量: {len(agent.tools)}")
    print()
    
    # 显示每个工具的详细信息
    for tool_name, tool in agent.tools.items():
        print(f"📦 工具: {tool_name}")
        print(f"   📝 描述: {tool.description}")
        print(f"   🔧 类型: {tool.__class__.__name__}")
        
        # 显示工具特定信息
        if tool_name == "search":
            print(f"   🌐 搜索引擎: {list(tool.search_engines.keys())}")
            print(f"   ⏱️ 超时时间: {tool.timeout}秒")
            print(f"   📊 最大结果数: {tool.max_results}")
            
        elif tool_name == "terminal":
            print(f"   📁 工作目录: {tool.working_directory}")
            print(f"   ⏱️ 超时时间: {tool.timeout}秒")
            print(f"   ✅ 安全命令: {len(tool.safe_commands)}个")
            print(f"   ❌ 危险命令: {len(tool.dangerous_commands)}个")
            
        elif tool_name == "code":
            print(f"   ⏱️ 最大执行时间: {tool.max_execution_time}秒")
            print(f"   📏 最大输出大小: {tool.max_output_size}字符")
            print(f"   ✅ 安全模块: {len(tool.safe_modules)}个")
            print(f"   ❌ 危险模块: {len(tool.dangerous_modules)}个")
        
        print()
    
    print("=" * 50)
    print("💡 工具使用示例:")
    print()
    print("🔍 搜索工具:")
    print("   - 搜索最近保险新闻")
    print("   - 查找Python教程")
    print("   - 查询天气信息")
    print()
    print("💻 终端工具:")
    print("   - 查看当前目录")
    print("   - 列出文件")
    print("   - 检查Python版本")
    print()
    print("🐍 代码工具:")
    print("   - 执行Python计算")
    print("   - 生成数据分析")
    print("   - 创建文件操作")
    print()
    print("🤖 智能任务执行:")
    print("   - 系统会自动分析任务意图")
    print("   - 选择合适的工具组合")
    print("   - 生成综合结果报告")

if __name__ == "__main__":
    asyncio.run(show_available_tools()) 