"""
Dynamic Tool System Demo
Demonstrates the new dynamic tool loading and hot-plugging capabilities.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.tools.plugin_manager import plugin_manager
from python.tools.tool_adapter import tool_registry_adapter, register_builtin_tools, register_dynamic_tools
from python.tools.hot_swap_manager import hot_swap_manager
from python.agent.core import Agent


async def demo_dynamic_tool_system():
    """Demonstrate the dynamic tool system capabilities."""
    
    print("🛡️ Dynamic Tool System Demo")
    print("=" * 50)
    
    # 1. Initialize the system
    print("\n1. Initializing dynamic tool system...")
    
    # Register built-in and dynamic tools
    register_builtin_tools()
    register_dynamic_tools()
    
    print(f"✅ Discovered plugins: {plugin_manager.list_available_plugins()}")
    print(f"✅ Loaded tools: {plugin_manager.list_plugins()}")
    
    # 2. Show tool status
    print("\n2. Tool Status:")
    for tool_name in plugin_manager.list_available_plugins():
        status = plugin_manager.get_plugin_status(tool_name)
        plugin_info = plugin_manager.get_plugin_info(tool_name)
        print(f"   📦 {tool_name}: {status.value}")
        if plugin_info:
            print(f"      📝 {plugin_info.description}")
    
    # 3. Demonstrate hot-swapping
    print("\n3. Hot-swapping demonstration:")
    
    # Start monitoring
    hot_swap_manager.start_monitoring()
    print("   🔍 Started file monitoring")
    
    # Add event handler
    def on_tool_event(event):
        print(f"   🔄 Tool event: {event.event_type} - {event.tool_name}")
    
    hot_swap_manager.add_event_handler(on_tool_event)
    
    # 4. Test tool execution
    print("\n4. Testing tool execution:")
    
    # Create agent with new tool system
    agent = Agent()
    
    # Test a simple task
    result = await agent.execute_task("列出当前目录的文件")
    print(f"   ✅ Task result: {result.get('status', 'unknown')}")
    
    # 5. Show available tools
    print("\n5. Available tools:")
    tools = agent.tools
    for tool_name, tool in tools.items():
        print(f"   🔧 {tool_name}: {tool.description}")
    
    # 6. Demonstrate plugin management
    print("\n6. Plugin management:")
    
    # Enable/disable plugins
    for plugin_name in plugin_manager.list_available_plugins():
        if plugin_name != "hot_swap":  # Don't disable the hot swap plugin
            plugin_manager.disable_plugin(plugin_name)
            print(f"   ⚠️ Disabled plugin: {plugin_name}")
    
    # Re-enable plugins
    for plugin_name in plugin_manager.list_available_plugins():
        if plugin_name != "hot_swap":
            plugin_manager.enable_plugin(plugin_name)
            print(f"   ✅ Re-enabled plugin: {plugin_name}")
    
    # 7. Show hot swap capabilities
    print("\n7. Hot swap capabilities:")
    
    # Get tool status
    tool_status = hot_swap_manager.list_tool_status()
    for tool_name, status in tool_status.items():
        print(f"   📊 {tool_name}: {'🟢 Loaded' if status['loaded'] else '🔴 Not loaded'}")
    
    # 8. Cleanup
    print("\n8. Cleanup:")
    hot_swap_manager.stop_monitoring()
    plugin_manager.cleanup()
    print("   🧹 Cleanup completed")
    
    print("\n✅ Dynamic tool system demo completed!")


async def demo_tool_creation():
    """Demonstrate dynamic tool creation."""
    
    print("\n🛠️ Dynamic Tool Creation Demo")
    print("=" * 40)
    
    # Create a simple dynamic tool
    from python.tools.base import BaseTool, ToolResult
    
    class DemoCalculatorTool(BaseTool):
        """A simple calculator tool for demonstration."""
        
        def __init__(self):
            super().__init__("demo_calculator", "Simple calculator for demonstration")
        
        async def execute(self, **kwargs) -> ToolResult:
            operation = kwargs.get("operation", "add")
            a = kwargs.get("a", 0)
            b = kwargs.get("b", 0)
            
            try:
                if operation == "add":
                    result = a + b
                elif operation == "subtract":
                    result = a - b
                elif operation == "multiply":
                    result = a * b
                elif operation == "divide":
                    result = a / b if b != 0 else "Error: Division by zero"
                else:
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"Unknown operation: {operation}"
                    )
                
                return ToolResult(
                    success=True,
                    data={"result": result, "operation": operation, "a": a, "b": b}
                )
                
            except Exception as e:
                return ToolResult(
                    success=False,
                    data=None,
                    error=str(e)
                )
    
    # Register the demo tool
    tool_registry_adapter.register_tool_class("demo_calculator", DemoCalculatorTool, "dynamic")
    
    print("✅ Created and registered demo calculator tool")
    
    # Test the tool
    tool_instance = plugin_manager.loaded_tools.get("demo_calculator")
    if tool_instance:
        result = await tool_instance.execute(operation="add", a=5, b=3)
        print(f"✅ Test calculation: 5 + 3 = {result.data.get('result')}")
    
    # Cleanup
    tool_registry_adapter.unregister_tool_class("demo_calculator")
    print("✅ Cleaned up demo tool")


async def main():
    """Main demo function."""
    try:
        await demo_dynamic_tool_system()
        await demo_tool_creation()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logging.error(f"Demo error: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the demo
    asyncio.run(main()) 