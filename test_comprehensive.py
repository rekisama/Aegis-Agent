#!/usr/bin/env python3
"""
Comprehensive Test Script for Aegis Agent
Tests all major components and functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from python.utils.env_manager import env_manager
from python.agent.core import Agent
from python.tools.terminal import TerminalTool
from python.tools.search import SearchTool
from python.tools.code import CodeExecutionTool
from python.memory.memory_manager import MemoryManager
from python.utils.config_types import AgentConfig
from python.llm.deepseek_client import DeepSeekClient


async def test_environment_configuration():
    """Test environment configuration loading."""
    print("🧪 Testing Environment Configuration...")
    
    try:
        # Test environment manager
        agent_config = env_manager.get_agent_config()
        deepseek_config = env_manager.get_deepseek_config()
        memory_config = env_manager.get_memory_config()
        tools_config = env_manager.get_tools_config()
        
        print("✅ Environment configuration loaded successfully")
        print(f"  Agent name: {agent_config['name']}")
        print(f"  Model: {agent_config['model']}")
        print(f"  DeepSeek API key set: {bool(deepseek_config['api_key'])}")
        print(f"  Memory enabled: {memory_config['enabled']}")
        print(f"  Tools enabled: {tools_config['enabled']}")
        
        return True
    except Exception as e:
        print(f"❌ Environment configuration test failed: {e}")
        return False


async def test_agent_creation():
    """Test agent creation and basic functionality."""
    print("\n🧪 Testing Agent Creation...")
    
    try:
        # Create agent
        agent = Agent()
        
        print("✅ Agent created successfully")
        print(f"  Agent ID: {agent.agent_id}")
        print(f"  Agent name: {agent.config.name}")
        print(f"  Tools count: {len(agent.tools)}")
        print(f"  Memory enabled: {agent.config.memory_enabled}")
        
        # Test status
        status = agent.get_status()
        print(f"  Task count: {status['task_count']}")
        print(f"  Subordinates count: {status['subordinates_count']}")
        
        return True
    except Exception as e:
        print(f"❌ Agent creation test failed: {e}")
        return False


async def test_tools():
    """Test tool system."""
    print("\n🧪 Testing Tools...")
    
    try:
        # Test terminal tool
        terminal_tool = TerminalTool()
        print("✅ Terminal tool created")
        
        # Test search tool
        search_tool = SearchTool()
        print("✅ Search tool created")
        
        # Test code tool
        code_tool = CodeExecutionTool()
        print("✅ Code tool created")
        
        # Test tool info
        terminal_info = terminal_tool.get_info()
        print(f"  Terminal tool: {terminal_info['name']} - {terminal_info['description']}")
        
        return True
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False


async def test_memory_system():
    """Test memory system."""
    print("\n🧪 Testing Memory System...")
    
    try:
        # Create memory manager
        config = AgentConfig()
        memory = MemoryManager(config)
        
        print("✅ Memory manager created")
        
        # Test memory stats
        stats = memory.get_memory_stats()
        print(f"  Memory enabled: {stats['memory_enabled']}")
        print(f"  Database size: {stats['database_size_bytes']} bytes")
        
        # Test knowledge storage
        await memory.store_knowledge(
            "test_topic",
            "This is a test knowledge entry",
            source="test",
            confidence=0.9
        )
        print("✅ Knowledge storage test passed")
        
        # Test knowledge retrieval
        knowledge = await memory.get_knowledge("test_topic")
        if knowledge:
            print("✅ Knowledge retrieval test passed")
        else:
            print("❌ Knowledge retrieval test failed")
        
        return True
    except Exception as e:
        print(f"❌ Memory system test failed: {e}")
        return False


async def test_deepseek_integration():
    """Test DeepSeek integration."""
    print("\n🧪 Testing DeepSeek Integration...")
    
    try:
        # Test DeepSeek client creation
        async with DeepSeekClient() as client:
            print("✅ DeepSeek client created")
            
            # Test basic response generation
            result = await client.generate_response(
                prompt="Hello! Can you tell me a short joke?",
                temperature=0.7,
                max_tokens=100
            )
            
            if result["success"]:
                print("✅ DeepSeek response generation test passed")
                print(f"  Response: {result['content'][:50]}...")
            else:
                print(f"❌ DeepSeek response generation failed: {result.get('error', 'Unknown error')}")
                return False
            
            # Test conversation summary
            summary = client.get_conversation_summary()
            print(f"  Conversation messages: {summary['total_messages']}")
        
        return True
    except Exception as e:
        print(f"❌ DeepSeek integration test failed: {e}")
        return False


async def test_task_execution():
    """Test task execution."""
    print("\n🧪 Testing Task Execution...")
    
    try:
        # Create agent
        agent = Agent()
        
        # Execute a simple task
        result = await agent.execute_task("Show current directory structure")
        
        if result and result.get("status") == "completed":
            print("✅ Task execution test passed")
            print(f"  Task result: {result.get('result', 'No result')}")
        else:
            print("❌ Task execution test failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Task execution test failed: {e}")
        return False


async def test_subordinate_creation():
    """Test subordinate agent creation."""
    print("\n🧪 Testing Subordinate Creation...")
    
    try:
        # Create main agent
        agent = Agent()
        
        # Create subordinate
        subordinate = agent.create_subordinate("Test Helper")
        
        print("✅ Subordinate creation test passed")
        print(f"  Subordinate name: {subordinate.config.name}")
        print(f"  Subordinate ID: {subordinate.agent_id}")
        print(f"  Main agent subordinates count: {len(agent.subordinates)}")
        
        return True
    except Exception as e:
        print(f"❌ Subordinate creation test failed: {e}")
        return False


async def main():
    """Run all comprehensive tests."""
    print("🚀 Aegis Agent Comprehensive Tests")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", test_environment_configuration),
        ("Agent Creation", test_agent_creation),
        ("Tools", test_tools),
        ("Memory System", test_memory_system),
        ("DeepSeek Integration", test_deepseek_integration),
        ("Task Execution", test_task_execution),
        ("Subordinate Creation", test_subordinate_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test passed!")
            else:
                print(f"❌ {test_name} test failed!")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Aegis Agent is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration and dependencies.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 