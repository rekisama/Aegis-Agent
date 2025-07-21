#!/usr/bin/env python3
"""
简化的 Tavily 测试
"""

import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_tavily():
    """测试Tavily API"""
    print("🔍 测试 Tavily API")
    print("=" * 30)
    
    # 检查API密钥
    api_key = os.getenv("TAVILY_API_KEY")
    print(f"🔑 API密钥: {'已设置' if api_key else '未设置'}")
    
    if not api_key:
        print("❌ Tavily API密钥未设置")
        return
    
    try:
        from tavily import TavilyClient
        
        # 创建客户端
        client = TavilyClient(api_key=api_key)
        print("✅ Tavily客户端创建成功")
        
        # 测试搜索
        print("🔍 执行搜索测试...")
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.search(
                query="最近保险新闻",
                search_depth="basic",
                max_results=3
            )
        )
        
        print("✅ 搜索成功!")
        print(f"📊 找到 {len(response.get('results', []))} 个结果")
        
        if response.get('answer'):
            print(f"🤖 AI回答: {response['answer']}")
        
        # 显示前3个结果
        for i, result in enumerate(response.get('results', [])[:3], 1):
            print(f"\n📄 结果 {i}:")
            print(f"   标题: {result.get('title', 'N/A')}")
            print(f"   链接: {result.get('url', 'N/A')}")
            print(f"   内容: {result.get('content', 'N/A')[:100]}...")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tavily()) 