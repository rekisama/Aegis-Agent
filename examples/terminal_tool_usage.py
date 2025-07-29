"""
Terminal Tool Usage Example
演示如何使用终端工具的完整流程
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.tools.tool_adapter import register_builtin_tools, tool_registry_adapter
from python.tools.terminal import TerminalTool


async def demo_terminal_tool():
    """演示终端工具的使用"""
    print("🔧 Demo: Terminal Tool Usage")
    print("=" * 50)
    
    # 1. 注册工具
    register_builtin_tools()
    print("✅ Tools registered")
    
    # 2. 获取终端工具实例
    terminal_tool = tool_registry_adapter.get_tool_instance("terminal")
    
    if not terminal_tool:
        print("❌ Terminal tool not available")
        return False
    
    print("✅ Terminal tool loaded")
    
    # 3. 测试不同的命令
    test_commands = [
        {"command": "echo Hello World", "description": "Basic echo command"},
        {"command": "pwd", "description": "Show current directory"},
        {"command": "ls -la", "description": "List files with details"},
        {"command": "python --version", "description": "Check Python version"},
        {"command": "invalid_command", "description": "Test error handling"},
    ]
    
    for i, test_case in enumerate(test_commands, 1):
        print(f"\n   Test {i}: {test_case['description']}")
        print(f"   Command: {test_case['command']}")
        
        result = await terminal_tool.execute(
            command=test_case['command'],
            timeout=10
        )
        
        if result.success:
            print(f"   ✅ Success (return code: {result.data['return_code']})")
            print(f"   📄 Output: {result.data['stdout'][:100]}...")
            if result.data['stderr']:
                print(f"   ⚠️  Errors: {result.data['stderr'][:100]}...")
        else:
            print(f"   ❌ Failed: {result.error}")
    
    # 4. 显示工具信息
    tool_info = terminal_tool.get_info()
    print(f"\n📋 Tool Info:")
    print(f"   Usage count: {tool_info['usage_count']}")
    print(f"   Success rate: {tool_info['success_rate']:.2%}")
    print(f"   Command history length: {tool_info['command_history_length']}")
    
    return True


async def demo_direct_usage():
    """演示直接使用终端工具"""
    print("\n🛠️ Demo: Direct Terminal Tool Usage")
    print("=" * 50)
    
    # 直接创建终端工具实例
    terminal_tool = TerminalTool()
    print("✅ Terminal tool created directly")
    
    # 执行命令
    result = await terminal_tool.execute(command="echo 'Direct usage test'")
    
    if result.success:
        print(f"✅ Direct usage successful: {result.data['stdout'].strip()}")
    else:
        print(f"❌ Direct usage failed: {result.error}")
    
    return True


async def demo_agent_with_terminal():
    """演示Agent与终端工具的集成"""
    print("\n🤖 Demo: Agent with Terminal Tool")
    print("=" * 50)
    
    # 创建Agent
    from python.agent.core import Agent
    agent = Agent()
    
    # 手动添加终端工具
    terminal_tool = TerminalTool()
    agent.tools["terminal"] = terminal_tool
    
    print(f"✅ Agent created with {len(agent.tools)} tools")
    
    # 测试任务
    test_tasks = [
        "使用terminal工具列出当前目录的文件",
        "使用terminal工具检查Python版本",
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n   Task {i}: {task}")
        
        try:
            result = await agent.execute_task(task)
            print(f"   ✅ Status: {result.get('status')}")
            
            if result.get('status') == 'completed':
                print(f"   📄 Result: {result.get('result', '')[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return True


async def main():
    """主演示函数"""
    print("🚀 Terminal Tool Usage Demo")
    print("=" * 60)
    
    try:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 运行演示
        demos = [
            ("Terminal Tool Usage", demo_terminal_tool),
            ("Direct Usage", demo_direct_usage),
            ("Agent Integration", demo_agent_with_terminal),
        ]
        
        results = {}
        
        for demo_name, demo_func in demos:
            print(f"\n{'='*60}")
            print(f"🎬 Running: {demo_name}")
            print(f"{'='*60}")
            
            try:
                result = await demo_func()
                results[demo_name] = result
                print(f"✅ {demo_name}: PASSED")
            except Exception as e:
                print(f"❌ {demo_name}: FAILED - {e}")
                results[demo_name] = False
                logging.error(f"Demo {demo_name} failed: {e}")
        
        # 总结
        print(f"\n{'='*60}")
        print("📊 Demo Summary")
        print(f"{'='*60}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for demo_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}: {demo_name}")
        
        print(f"\n🎯 Overall Result: {passed}/{total} demos passed")
        
        if passed == total:
            print("🎉 All demos passed! Terminal tool is working correctly.")
        else:
            print("⚠️ Some demos failed. Please check the logs for details.")
        
    except Exception as e:
        print(f"❌ Demo suite failed: {e}")
        logging.error(f"Demo suite error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 