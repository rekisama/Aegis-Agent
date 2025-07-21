#!/usr/bin/env python3
"""
Basic Usage Example for Aegis Agent
Demonstrates how to create and use an agent for simple tasks.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.agent.core import Agent, AgentConfig


async def basic_example():
    """Basic example of using Aegis Agent."""
    print("🛡️  Aegis Agent - Basic Usage Example")
    print("=" * 50)
    
    # Create an agent with custom configuration
    config = AgentConfig(
        name="Example Agent",
        memory_enabled=True,
        hierarchical_enabled=True,
        tools_enabled=True
    )
    
    agent = Agent(config)
    
    print(f"✅ Created agent: {agent.config.name}")
    print(f"📊 Agent ID: {agent.agent_id}")
    
    # Execute a simple task
    print("\n🔄 Executing task: 'Show current directory structure'")
    try:
        result = await agent.execute_task("Show current directory structure")
        print(f"✅ Task completed: {result}")
    except Exception as e:
        print(f"❌ Task failed: {e}")
    
    # Show agent status
    print("\n📊 Agent Status:")
    status = agent.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Show memory statistics
    print("\n🧠 Memory Statistics:")
    memory_stats = agent.memory.get_memory_stats()
    for key, value in memory_stats.items():
        print(f"  {key}: {value}")
    
    # Create a subordinate agent
    print("\n👥 Creating subordinate agent...")
    try:
        subordinate = agent.create_subordinate("Helper Agent")
        print(f"✅ Created subordinate: {subordinate.config.name}")
        print(f"   ID: {subordinate.agent_id}")
    except Exception as e:
        print(f"❌ Failed to create subordinate: {e}")
    
    print("\n🎉 Basic example completed!")


async def tool_usage_example():
    """Example of using different tools."""
    print("\n🛠️  Tool Usage Example")
    print("=" * 50)
    
    agent = Agent()
    
    # Terminal tool example
    print("\n📟 Using Terminal Tool:")
    terminal_tool = agent.get_tool("terminal")
    if terminal_tool:
        result = await terminal_tool.execute(command="pwd")
        if result.success:
            print(f"✅ Current directory: {result.data['stdout']}")
        else:
            print(f"❌ Terminal command failed: {result.error}")
    
    # Code tool example
    print("\n🐍 Using Code Tool:")
    code_tool = agent.get_tool("code")
    if code_tool:
        python_code = """
import os
import json

# Get current directory info
current_dir = os.getcwd()
files = os.listdir(current_dir)

result = {
    "directory": current_dir,
    "files": files[:5],  # Show first 5 files
    "total_files": len(files)
}

print(json.dumps(result, indent=2))
"""
        result = await code_tool.execute(code=python_code)
        if result.success:
            print("✅ Code executed successfully!")
            print(f"Output: {result.data['stdout']}")
        else:
            print(f"❌ Code execution failed: {result.error}")
    
    print("\n🎉 Tool usage example completed!")


async def memory_example():
    """Example of using the memory system."""
    print("\n🧠 Memory System Example")
    print("=" * 50)
    
    agent = Agent()
    
    # Store some knowledge
    print("\n💾 Storing knowledge...")
    await agent.memory.store_knowledge(
        "python_best_practices",
        "Use type hints, write docstrings, follow PEP 8, and use virtual environments.",
        source="example",
        confidence=0.9
    )
    
    # Store a solution pattern
    print("📝 Storing solution pattern...")
    await agent.memory.store_solution_pattern(
        "file_analysis",
        "Analyze files in a directory using os.listdir and pathlib",
        ["terminal", "code"],
        1.0
    )
    
    # Retrieve knowledge
    print("\n🔍 Retrieving knowledge...")
    knowledge = await agent.memory.get_knowledge("python_best_practices")
    if knowledge:
        print(f"✅ Found knowledge: {knowledge['content']}")
    else:
        print("❌ Knowledge not found")
    
    # Get solution patterns
    print("\n🔍 Retrieving solution patterns...")
    patterns = await agent.memory.get_solution_patterns()
    print(f"✅ Found {len(patterns)} solution patterns")
    for pattern in patterns:
        print(f"  - {pattern['pattern_name']}: {pattern['pattern_description']}")
    
    print("\n🎉 Memory system example completed!")


async def main():
    """Run all examples."""
    print("🚀 Aegis Agent Examples")
    print("=" * 50)
    
    try:
        await basic_example()
        await tool_usage_example()
        await memory_example()
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 