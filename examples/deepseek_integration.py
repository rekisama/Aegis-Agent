#!/usr/bin/env python3
"""
DeepSeek Integration Example for Aegis Agent
Demonstrates how to use DeepSeek API with the agent system.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.llm.deepseek_client import DeepSeekClient
from python.utils.env_manager import env_manager


async def test_deepseek_client():
    """Test the DeepSeek client functionality."""
    print("🤖 DeepSeek API Integration Test")
    print("=" * 50)
    
    # Print configuration
    deepseek_config = env_manager.get_deepseek_config()
    print(f"📋 Configuration:")
    print(f"  Model: {deepseek_config['model']}")
    print(f"  Base URL: {deepseek_config['api_base_url']}")
    print(f"  API Key: {'*' * 10 if deepseek_config['api_key'] else 'Not set'}")
    
    if not deepseek_config['api_key']:
        print("❌ DeepSeek API key not found in environment variables!")
        return False
    
    try:
        async with DeepSeekClient() as client:
            print("\n🔄 Testing basic response generation...")
            
            # Test basic response
            result = await client.generate_response(
                prompt="Hello! Can you tell me a short joke?",
                temperature=0.7,
                max_tokens=100
            )
            
            if result["success"]:
                print("✅ Basic response test passed!")
                print(f"Response: {result['content']}")
            else:
                print(f"❌ Basic response test failed: {result['error']}")
                return False
            
            # Test task analysis
            print("\n🔄 Testing task analysis...")
            analysis_result = await client.analyze_task(
                "Create a Python script to scrape a website"
            )
            
            if analysis_result["success"]:
                print("✅ Task analysis test passed!")
                analysis = analysis_result["analysis"]
                print(f"Complexity: {analysis.get('complexity', 'unknown')}")
                print(f"Requires delegation: {analysis.get('requires_delegation', False)}")
                print(f"Required tools: {analysis.get('required_tools', [])}")
            else:
                print(f"❌ Task analysis test failed: {analysis_result['error']}")
            
            # Test code generation
            print("\n🔄 Testing code generation...")
            code_result = await client.generate_code(
                "A function to calculate fibonacci numbers",
                "python"
            )
            
            if code_result["success"]:
                print("✅ Code generation test passed!")
                print("Generated code:")
                print(code_result["content"])
            else:
                print(f"❌ Code generation test failed: {code_result['error']}")
            
            # Test text summarization
            print("\n🔄 Testing text summarization...")
            text_to_summarize = """
            Artificial Intelligence (AI) is a branch of computer science that aims to create 
            intelligent machines that work and react like humans. Some of the activities 
            computers with artificial intelligence are designed for include speech recognition, 
            learning, planning, and problem solving. AI has been used in various applications 
            including medical diagnosis, stock trading, robot control, law, scientific discovery 
            and toys. However, some people fear that AI might replace human workers in the future.
            """
            
            summary_result = await client.summarize_text(text_to_summarize, 100)
            
            if summary_result["success"]:
                print("✅ Text summarization test passed!")
                print(f"Summary: {summary_result['content']}")
            else:
                print(f"❌ Text summarization test failed: {summary_result['error']}")
            
            # Show conversation summary
            print("\n📊 Conversation Summary:")
            summary = client.get_conversation_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
            
            return True
            
    except Exception as e:
        print(f"❌ DeepSeek client test failed: {e}")
        return False


async def test_agent_with_deepseek():
    """Test agent with DeepSeek integration."""
    print("\n🤖 Testing Agent with DeepSeek Integration")
    print("=" * 50)
    
    from python.agent.core import Agent
    
    try:
        # Create agent (will use DeepSeek for task analysis)
        agent = Agent()
        
        print(f"✅ Agent created: {agent.config.name}")
        print(f"📊 Using model: {agent.config.model}")
        
        # Test task execution with LLM analysis
        print("\n🔄 Testing task execution with LLM analysis...")
        result = await agent.execute_task("Create a simple web scraper")
        
        if result:
            print("✅ Task execution with LLM analysis passed!")
            print(f"Result: {result}")
        else:
            print("❌ Task execution failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent with DeepSeek test failed: {e}")
        return False


async def main():
    """Run all DeepSeek integration tests."""
    print("🚀 DeepSeek Integration Tests")
    print("=" * 50)
    
    # Test environment configuration
    print("\n📋 Environment Configuration:")
    env_manager.print_config_summary()
    
    # Validate environment
    validation = env_manager.validate_required_vars()
    if not all(validation.values()):
        print("❌ Environment validation failed!")
        return
    
    # Run tests
    tests = [
        ("DeepSeek Client", test_deepseek_client),
        ("Agent with DeepSeek", test_agent_with_deepseek)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
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
        print("🎉 All tests passed! DeepSeek integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and API key.")


if __name__ == "__main__":
    asyncio.run(main()) 