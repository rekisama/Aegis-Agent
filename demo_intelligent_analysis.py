#!/usr/bin/env python3
"""
演示 Aegis Agent 的智能意图分析和工具选择流程
"""

import asyncio
import json
from python.agent.core import Agent

async def demo_intelligent_analysis():
    """演示智能意图分析流程"""
    print("🛡️ Aegis Agent - 智能意图分析演示")
    print("=" * 60)
    
    # 创建智能体实例
    agent = Agent()
    
    # 演示任务
    demo_tasks = [
        "搜索最近保险新闻",
        "查看当前目录文件",
        "计算斐波那契数列前10项",
        "分析Python项目结构"
    ]
    
    for i, task in enumerate(demo_tasks, 1):
        print(f"\n🔍 演示 {i}: {task}")
        print("-" * 40)
        
        try:
            # 执行任务
            result = await agent.execute_task(task)
            
            # 显示结果
            print(f"✅ 任务完成!")
            print(f"📋 结果: {result['result'][:200]}...")
            
            # 显示元数据（工具使用情况）
            if 'metadata' in result and 'tool_plan' in result['metadata']:
                plan = result['metadata']['tool_plan']
                print(f"🤖 执行计划: {plan.get('description', 'N/A')}")
                
                if 'steps' in plan:
                    print("🔧 使用的工具:")
                    for step in plan['steps']:
                        print(f"   - {step['tool']}: {step.get('reason', 'N/A')}")
            
        except Exception as e:
            print(f"❌ 任务执行失败: {e}")
        
        print()

async def demo_tool_selection_process():
    """演示工具选择过程"""
    print("\n🔬 工具选择过程详解")
    print("=" * 60)
    
    agent = Agent()
    task = "搜索最近保险新闻"
    
    print(f"📝 任务: {task}")
    print()
    
    # 步骤1: 任务分析
    print("1️⃣ 任务分析阶段")
    print("   - 使用DeepSeek API分析任务复杂度")
    print("   - 确定是否需要委托给子智能体")
    print("   - 评估所需工具类型")
    print()
    
    # 步骤2: 工具选择
    print("2️⃣ 智能工具选择")
    print("   - LLM分析任务意图")
    print("   - 从可用工具中选择合适的工具")
    print("   - 生成执行计划")
    print()
    
    # 步骤3: 工具执行
    print("3️⃣ 工具执行阶段")
    print("   - 按计划执行选定的工具")
    print("   - 收集工具执行结果")
    print("   - 处理成功和失败的工具")
    print()
    
    # 步骤4: 结果合成
    print("4️⃣ 结果合成阶段")
    print("   - LLM分析所有工具结果")
    print("   - 生成综合响应")
    print("   - 格式化最终输出")
    print()
    
    # 实际演示
    print("🎯 实际执行演示:")
    try:
        result = await agent.execute_task(task)
        print(f"✅ 最终结果: {result['result'][:300]}...")
    except Exception as e:
        print(f"❌ 执行失败: {e}")

async def demo_llm_prompts():
    """演示LLM提示词"""
    print("\n📝 LLM提示词示例")
    print("=" * 60)
    
    # 工具选择提示词
    tool_selection_prompt = """You are an intelligent task planner for an AI agent. 

Available tools: ['terminal', 'search', 'code']

For each task, analyze what tools are needed and create a step-by-step execution plan.

Respond in JSON format:
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

Be specific and practical. For search tasks, extract the search query from the task description."""
    
    print("🔧 工具选择提示词:")
    print(tool_selection_prompt)
    print()
    
    # 结果合成提示词
    result_synthesis_prompt = """You are an AI assistant that synthesizes results from multiple tools into a coherent response.

Your task is to take the outputs from various tools and create a comprehensive, well-formatted response that directly answers the user's original question.

Format the response clearly and include relevant information from all successful tool executions."""
    
    print("📊 结果合成提示词:")
    print(result_synthesis_prompt)

if __name__ == "__main__":
    print("🚀 启动智能意图分析演示...")
    asyncio.run(demo_intelligent_analysis())
    asyncio.run(demo_tool_selection_process())
    asyncio.run(demo_llm_prompts()) 