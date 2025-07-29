"""
Dynamic Tool System Usage Example
演示如何使用动态工具系统的完整流程
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.tools.tool_adapter import register_builtin_tools, register_dynamic_tools, tool_registry_adapter
from python.tools.hot_swap_manager import hot_swap_manager
from python.agent.core import Agent


async def demo_basic_usage():
    """演示基本用法：注册工具并获取实例"""
    print("🔧 Demo: Basic Tool Registration and Usage")
    print("=" * 50)
    
    # 1. 注册工具
    register_builtin_tools()
    register_dynamic_tools()
    
    print("✅ Tools registered")
    
    # 2. 获取工具实例
    available_tools = tool_registry_adapter.list_available_tools()
    print(f"📋 Available tools: {available_tools}")
    
    # 3. 使用工具
    if "hello_world" in available_tools:
        hello_tool = tool_registry_adapter.get_tool_instance("hello_world")
        if hello_tool:
            result = await hello_tool.execute(name="Alice", language="zh")
            print(f"🌍 HelloWorld result: {result.data['greeting']}")
        else:
            print("❌ HelloWorld tool not available")
    
    if "mock_tool" in available_tools:
        mock_tool = tool_registry_adapter.get_tool_instance("mock_tool")
        if mock_tool:
            result = await mock_tool.execute(operation="success")
            print(f"🎭 MockTool result: {result.data['message']}")
        else:
            print("❌ MockTool not available")
    
    return True


async def demo_agent_integration():
    """演示Agent集成"""
    print("\n🤖 Demo: Agent Integration")
    print("=" * 50)
    
    # 创建Agent
    agent = Agent()
    print(f"✅ Agent created with {len(agent.tools)} tools")
    
    # 测试任务执行
    test_tasks = [
        "使用hello_world工具向张三问好",
        "使用mock_tool执行一个随机操作",
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


async def demo_hot_swap():
    """演示热插拔功能"""
    print("\n🔄 Demo: Hot Swap Functionality")
    print("=" * 50)
    
    # 启动文件监控
    hot_swap_manager.start_monitoring()
    print("✅ File monitoring started")
    
    # 添加事件处理器
    events = []
    
    def on_tool_event(event):
        events.append(event)
        print(f"   🔄 Tool event: {event.event_type} - {event.tool_name}")
    
    hot_swap_manager.add_event_handler(on_tool_event)
    
    # 测试热重载
    print("\n   Testing hot reload...")
    success = hot_swap_manager.hot_reload_tool("hello_world")
    print(f"   {'✅' if success else '❌'} Hot reload: {success}")
    
    # 测试热卸载
    print("\n   Testing hot unload...")
    success = hot_swap_manager.hot_unload_tool("mock_tool")
    print(f"   {'✅' if success else '❌'} Hot unload: {success}")
    
    # 测试热加载
    print("\n   Testing hot load...")
    from python.tools.dynamic.dynamic_mock_tool import MockTool
    success = hot_swap_manager.hot_load_tool("mock_tool", MockTool)
    print(f"   {'✅' if success else '❌'} Hot load: {success}")
    
    # 显示工具状态
    print("\n📊 Tool Status:")
    tool_status = hot_swap_manager.list_tool_status()
    for tool_name, status in tool_status.items():
        status_icon = "🟢" if status['loaded'] else "🔴"
        print(f"   {status_icon} {tool_name}: {'Loaded' if status['loaded'] else 'Not loaded'}")
    
    # 停止监控
    hot_swap_manager.stop_monitoring()
    print("\n✅ File monitoring stopped")
    
    return len(events) > 0


async def demo_custom_tool_creation():
    """演示自定义工具创建"""
    print("\n🛠️ Demo: Custom Tool Creation")
    print("=" * 50)
    
    # 1. 创建自定义工具
    from python.tools.base import BaseTool, ToolResult
    
    class CustomCalculatorTool(BaseTool):
        """自定义计算器工具"""
        
        def __init__(self):
            super().__init__("custom_calculator", "A custom calculator tool")
        
        async def execute(self, **kwargs) -> ToolResult:
            try:
                operation = kwargs.get("operation", "add")
                a = kwargs.get("a", 0)
                b = kwargs.get("b", 0)
                
                if operation == "add":
                    result = a + b
                elif operation == "subtract":
                    result = a - b
                elif operation == "multiply":
                    result = a * b
                elif operation == "divide":
                    if b == 0:
                        raise ValueError("Division by zero")
                    result = a / b
                else:
                    raise ValueError(f"Unknown operation: {operation}")
                
                return ToolResult(
                    success=True,
                    data={
                        "operation": operation,
                        "a": a,
                        "b": b,
                        "result": result
                    },
                    metadata={"tool_type": "custom_calculator"}
                )
                
            except Exception as e:
                return ToolResult(
                    success=False,
                    data=None,
                    error=str(e),
                    metadata={"tool_type": "custom_calculator"}
                )
    
    # 2. 注册自定义工具
    tool_registry_adapter.register_tool_class("custom_calculator", CustomCalculatorTool, "custom")
    print("✅ Custom calculator tool registered")
    
    # 3. 使用自定义工具
    calc_tool = tool_registry_adapter.get_tool_instance("custom_calculator")
    
    if calc_tool:
        test_cases = [
            {"operation": "add", "a": 5, "b": 3},
            {"operation": "multiply", "a": 4, "b": 7},
            {"operation": "divide", "a": 10, "b": 2},
            {"operation": "divide", "a": 10, "b": 0},  # 错误测试
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {test_case}")
            result = await calc_tool.execute(**test_case)
            
            if result.success:
                print(f"   ✅ Result: {result.data['result']}")
            else:
                print(f"   ❌ Error: {result.error}")
    else:
        print("❌ Custom calculator tool not available")
    
    return True


async def demo_plugin_management():
    """演示插件管理功能"""
    print("\n⚙️ Demo: Plugin Management")
    print("=" * 50)
    
    from python.tools.plugin_manager import plugin_manager
    
    # 列出所有插件
    all_plugins = plugin_manager.list_available_plugins()
    print(f"📦 Available plugins: {all_plugins}")
    
    # 测试插件状态
    for plugin_name in all_plugins:
        if plugin_name not in ["hot_swap"]:  # 不操作热插拔插件
            status = plugin_manager.get_plugin_status(plugin_name)
            print(f"   📊 {plugin_name}: {status.value if status else 'Unknown'}")
    
    return True


async def main():
    """主演示函数"""
    print("🚀 Dynamic Tool System Usage Demo")
    print("=" * 60)
    
    try:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 运行所有演示
        demos = [
            ("Basic Usage", demo_basic_usage),
            ("Agent Integration", demo_agent_integration),
            ("Hot Swap", demo_hot_swap),
            ("Custom Tool Creation", demo_custom_tool_creation),
            ("Plugin Management", demo_plugin_management),
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
            print("🎉 All demos passed! Dynamic tool system is working correctly.")
        else:
            print("⚠️ Some demos failed. Please check the logs for details.")
        
        # 清理
        hot_swap_manager.cleanup()
        
    except Exception as e:
        print(f"❌ Demo suite failed: {e}")
        logging.error(f"Demo suite error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 