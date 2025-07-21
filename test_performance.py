#!/usr/bin/env python3
"""
Performance Test Script for Aegis Agent
Tests system performance and response times.
"""

import asyncio
import time
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from python.agent.core import Agent
from python.tools.terminal import TerminalTool
from python.memory.memory_manager import MemoryManager
from python.utils.config_types import AgentConfig
from python.llm.deepseek_client import DeepSeekClient


async def test_agent_creation_performance():
    """Test agent creation performance."""
    print("🧪 Testing Agent Creation Performance...")
    
    start_time = time.time()
    agent = Agent()
    creation_time = time.time() - start_time
    
    print(f"✅ Agent created in {creation_time:.3f} seconds")
    return creation_time < 2.0  # Should be under 2 seconds


async def test_tool_execution_performance():
    """Test tool execution performance."""
    print("\n🧪 Testing Tool Execution Performance...")
    
    terminal_tool = TerminalTool()
    
    # Test terminal command execution
    start_time = time.time()
    result = await terminal_tool.execute(command="echo 'test'")
    execution_time = time.time() - start_time
    
    print(f"✅ Terminal command executed in {execution_time:.3f} seconds")
    return execution_time < 5.0  # Should be under 5 seconds


async def test_memory_operations_performance():
    """Test memory operations performance."""
    print("\n🧪 Testing Memory Operations Performance...")
    
    config = AgentConfig()
    memory = MemoryManager(config)
    
    # Test knowledge storage
    start_time = time.time()
    await memory.store_knowledge(
        "performance_test",
        "This is a performance test entry",
        source="test",
        confidence=0.9
    )
    storage_time = time.time() - start_time
    
    print(f"✅ Knowledge storage completed in {storage_time:.3f} seconds")
    
    # Test knowledge retrieval
    start_time = time.time()
    knowledge = await memory.get_knowledge("performance_test")
    retrieval_time = time.time() - start_time
    
    print(f"✅ Knowledge retrieval completed in {retrieval_time:.3f} seconds")
    
    return storage_time < 1.0 and retrieval_time < 1.0


async def test_deepseek_response_performance():
    """Test DeepSeek response performance."""
    print("\n🧪 Testing DeepSeek Response Performance...")
    
    async with DeepSeekClient() as client:
        start_time = time.time()
        result = await client.generate_response(
            prompt="Say hello in one word",
            temperature=0.7,
            max_tokens=10
        )
        response_time = time.time() - start_time
        
        if result["success"]:
            print(f"✅ DeepSeek response received in {response_time:.3f} seconds")
            return response_time < 10.0  # Should be under 10 seconds
        else:
            print(f"❌ DeepSeek response failed: {result.get('error', 'Unknown error')}")
            return False


async def test_concurrent_operations():
    """Test concurrent operations performance."""
    print("\n🧪 Testing Concurrent Operations...")
    
    async def create_agent():
        return Agent()
    
    async def execute_task(agent):
        return await agent.execute_task("Simple test task")
    
    # Test concurrent agent creation
    start_time = time.time()
    agents = await asyncio.gather(*[create_agent() for _ in range(3)])
    creation_time = time.time() - start_time
    
    print(f"✅ Created {len(agents)} agents concurrently in {creation_time:.3f} seconds")
    
    # Test concurrent task execution
    start_time = time.time()
    results = await asyncio.gather(*[execute_task(agent) for agent in agents])
    execution_time = time.time() - start_time
    
    print(f"✅ Executed {len(results)} tasks concurrently in {execution_time:.3f} seconds")
    
    return creation_time < 5.0 and execution_time < 15.0


async def test_memory_stress():
    """Test memory system under stress."""
    print("\n🧪 Testing Memory Stress...")
    
    config = AgentConfig()
    memory = MemoryManager(config)
    
    # Store multiple knowledge entries
    start_time = time.time()
    tasks = []
    for i in range(10):
        task = memory.store_knowledge(
            f"stress_test_{i}",
            f"This is stress test entry {i}",
            source="stress_test",
            confidence=0.8
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    storage_time = time.time() - start_time
    
    print(f"✅ Stored 10 knowledge entries in {storage_time:.3f} seconds")
    
    # Retrieve all entries
    start_time = time.time()
    tasks = []
    for i in range(10):
        task = memory.get_knowledge(f"stress_test_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    retrieval_time = time.time() - start_time
    
    successful_retrievals = sum(1 for r in results if r is not None)
    print(f"✅ Retrieved {successful_retrievals}/10 entries in {retrieval_time:.3f} seconds")
    
    return storage_time < 5.0 and retrieval_time < 5.0 and successful_retrievals >= 8


async def main():
    """Run all performance tests."""
    print("🚀 Aegis Agent Performance Tests")
    print("=" * 50)
    
    tests = [
        ("Agent Creation", test_agent_creation_performance),
        ("Tool Execution", test_tool_execution_performance),
        ("Memory Operations", test_memory_operations_performance),
        ("DeepSeek Response", test_deepseek_response_performance),
        ("Concurrent Operations", test_concurrent_operations),
        ("Memory Stress", test_memory_stress),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} performance test passed!")
            else:
                print(f"❌ {test_name} performance test failed!")
        except Exception as e:
            print(f"❌ {test_name} performance test error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Performance Test Results:")
    print("=" * 30)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} performance tests passed")
    
    if passed == total:
        print("🎉 All performance tests passed! Aegis Agent is performing well.")
        return True
    else:
        print("⚠️  Some performance tests failed. Consider optimization.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 