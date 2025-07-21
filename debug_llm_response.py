#!/usr/bin/env python3
"""
调试LLM响应
"""

import asyncio
import json
from python.llm.deepseek_client import DeepSeekClient

async def debug_llm_response():
    """调试LLM响应"""
    print("🔍 调试LLM响应")
    print("=" * 40)
    
    system_prompt = """You are an intelligent task planner for an AI agent. 

Available tools: ['terminal', 'search', 'code']

For each task, analyze what tools are needed and create a step-by-step execution plan.

IMPORTANT: Respond ONLY with valid JSON, no additional text.

JSON format:
{
    "description": "Brief description of the execution plan",
    "steps": [
        {
            "tool": "tool_name",
            "parameters": {"param1": "value1", "param2": "value2"},
            "reason": "Why this tool is needed"
        }
    ]
}

Tool parameters:
- search: {"query": "search term", "max_results": 5}
- terminal: {"command": "system command"}
- code: {"code": "python code to execute"}

Examples:
For "搜索最近保险新闻":
{
    "description": "Search for recent insurance news",
    "steps": [
        {
            "tool": "search",
            "parameters": {"query": "最近保险新闻", "max_results": 5},
            "reason": "Need to search for recent insurance news"
        }
    ]
}

For "查看当前目录文件":
{
    "description": "List files in current directory",
    "steps": [
        {
            "tool": "terminal",
            "parameters": {"command": "dir"},
            "reason": "Need to list files in current directory"
        }
    ]
}

Be specific and practical. For search tasks, extract the search query from the task description."""

    prompt = "Task: 查看当前目录文件\n\nTask Analysis: {'complexity': 'simple', 'requires_delegation': False, 'required_tools': [], 'estimated_duration': 'short'}\n\nCreate an execution plan:"
    
    try:
        async with DeepSeekClient() as llm_client:
            result = await llm_client.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=800
            )
            
            print(f"✅ LLM响应成功: {result['success']}")
            print(f"📝 响应内容:")
            print("-" * 40)
            print(result['content'])
            print("-" * 40)
            
            # 尝试解析JSON
            try:
                parsed = json.loads(result['content'])
                print(f"✅ JSON解析成功!")
                print(f"📋 解析结果: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"🔍 尝试清理响应...")
                
                # 尝试清理响应
                content = result['content'].strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                print(f"🧹 清理后的内容:")
                print(content)
                
                try:
                    parsed = json.loads(content)
                    print(f"✅ 清理后JSON解析成功!")
                except json.JSONDecodeError as e2:
                    print(f"❌ 清理后仍然解析失败: {e2}")
                    
    except Exception as e:
        print(f"❌ LLM请求失败: {e}")

if __name__ == "__main__":
    asyncio.run(debug_llm_response()) 