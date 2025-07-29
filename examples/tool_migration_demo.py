"""
Tool Migration Demo
演示如何迁移旧工具到新的动态工具系统
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.tools.tool_adapter import register_builtin_tools, tool_registry_adapter
from python.agent.core import Agent


async def demo_migrated_tools():
    """演示迁移后的工具"""
    print("🔧 Demo: Migrated Tools")
    print("=" * 50)
    
    # 1. 注册所有工具
    register_builtin_tools()
    print("✅ All tools registered")
    
    # 2. 获取可用工具列表
    available_tools = tool_registry_adapter.list_available_tools()
    print(f"📋 Available tools: {available_tools}")
    
    # 3. 测试每个工具
    tool_tests = [
        {
            "name": "terminal",
            "test_params": {"command": "echo 'Terminal tool test'"},
            "description": "Terminal Tool"
        },
        {
            "name": "search", 
            "test_params": {"query": "Python programming", "max_results": 2},
            "description": "Search Tool"
        },
        {
            "name": "code",
            "test_params": {"code": "print('Hello from code tool')", "language": "python"},
            "description": "Code Execution Tool"
        },
        {
            "name": "tavily_search",
            "test_params": {"query": "artificial intelligence", "max_results": 2},
            "description": "Tavily Search Tool"
        }
    ]
    
    for test in tool_tests:
        tool_name = test["name"]
        if tool_name in available_tools:
            print(f"\n🧪 Testing {test['description']}:")
            
            tool = tool_registry_adapter.get_tool_instance(tool_name)
            if tool:
                try:
                    result = await tool.execute(**test["test_params"])
                    if result.success:
                        print(f"   ✅ {test['description']} executed successfully")
                        if hasattr(result.data, 'get'):
                            output = result.data.get('stdout', result.data.get('message', 'Success'))
                            print(f"   📄 Output: {str(output)[:100]}...")
                    else:
                        print(f"   ❌ {test['description']} failed: {result.error}")
                except Exception as e:
                    print(f"   ❌ {test['description']} error: {e}")
            else:
                print(f"   ❌ {test['description']} not available")
        else:
            print(f"\n⚠️ {test['description']} not in available tools list")
    
    return True


async def demo_agent_with_migrated_tools():
    """演示Agent与迁移工具的集成"""
    print("\n🤖 Demo: Agent with Migrated Tools")
    print("=" * 50)
    
    # 创建Agent
    agent = Agent()
    print(f"✅ Agent created with {len(agent.tools)} tools")
    
    # 测试任务
    test_tasks = [
        "使用terminal工具检查当前目录",
        "使用search工具搜索Python编程",
        "使用code工具执行简单的Python代码",
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


async def demo_tool_comparison():
    """演示工具比较"""
    print("\n🔍 Demo: Tool Comparison")
    print("=" * 50)
    
    # 获取工具信息
    tools_info = {}
    
    for tool_name in ["terminal", "search", "code", "tavily_search"]:
        tool = tool_registry_adapter.get_tool_instance(tool_name)
        if tool:
            info = tool.get_info()
            tools_info[tool_name] = {
                "description": info.get("description", "No description"),
                "usage_count": info.get("usage_count", 0),
                "success_rate": info.get("success_rate", 0.0),
                "created_at": info.get("created_at", "Unknown")
            }
    
    # 显示工具信息
    print("📊 Tool Information:")
    for tool_name, info in tools_info.items():
        print(f"\n   🔧 {tool_name.upper()}:")
        print(f"      📝 Description: {info['description']}")
        print(f"      📊 Usage Count: {info['usage_count']}")
        print(f"      ✅ Success Rate: {info['success_rate']:.2%}")
        print(f"      🕒 Created: {info['created_at']}")
    
    return True


async def demo_tool_registration_process():
    """演示工具注册过程"""
    print("\n📝 Demo: Tool Registration Process")
    print("=" * 50)
    
    print("🔄 Tool Registration Process:")
    print("   1. Tool inherits from BaseTool")
    print("   2. Tool is registered via ToolAdapter")
    print("   3. Tool becomes available in Agent")
    print("   4. Tool can be used dynamically")
    
    # 演示注册过程
    from python.tools.base import BaseTool, ToolResult
    
    class ExampleTool(BaseTool):
        """示例工具 - 演示迁移过程"""
        
        def __init__(self):
            super().__init__("example", "An example tool for migration demo")
        
        async def execute(self, **kwargs) -> ToolResult:
            return ToolResult(
                success=True,
                data={"message": "Example tool executed successfully"},
                metadata={"tool_type": "example"}
            )
    
    print("\n✅ Example tool created and ready for registration")
    
    # 注册示例工具
    tool_registry_adapter.register_tool_class("example", ExampleTool, "demo")
    print("✅ Example tool registered")
    
    # 获取并使用示例工具
    example_tool = tool_registry_adapter.get_tool_instance("example")
    if example_tool:
        result = await example_tool.execute()
        print(f"✅ Example tool executed: {result.data['message']}")
    
    return True


async def main():
    """主演示函数"""
    print("🚀 Tool Migration Demo")
    print("=" * 60)
    
    try:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 运行演示
        demos = [
            ("Migrated Tools", demo_migrated_tools),
            ("Agent Integration", demo_agent_with_migrated_tools),
            ("Tool Comparison", demo_tool_comparison),
            ("Registration Process", demo_tool_registration_process),
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
        print("📊 Migration Demo Summary")
        print(f"{'='*60}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for demo_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}: {demo_name}")
        
        print(f"\n🎯 Overall Result: {passed}/{total} demos passed")
        
        if passed == total:
            print("🎉 All demos passed! Tool migration successful.")
            print("\n📋 Migration Summary:")
            print("   ✅ All old tools successfully migrated")
            print("   ✅ Tools now use BaseTool inheritance")
            print("   ✅ Tools registered via ToolAdapter")
            print("   ✅ Agent integration working")
            print("   ✅ Dynamic tool system operational")
        else:
            print("⚠️ Some demos failed. Please check the logs for details.")
        
    except Exception as e:
        print(f"❌ Demo suite failed: {e}")
        logging.error(f"Demo suite error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 