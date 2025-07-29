#!/usr/bin/env python3
"""
WebSocket连接测试脚本
"""

import asyncio
import websockets
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

async def test_websocket():
    """测试WebSocket连接和消息处理"""
    uri = "ws://localhost:8000/ws"
    
    try:
        print("🔌 连接到WebSocket服务器...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 测试1: 发送聊天消息
            print("\n📝 测试1: 发送聊天消息")
            chat_message = {
                "type": "chat",
                "message": "你好，请介绍一下你自己"
            }
            
            await websocket.send(json.dumps(chat_message))
            print(f"📤 发送消息: {chat_message}")
            
            # 接收响应
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"📥 收到响应: {response_data}")
            
            # 测试2: 发送工具执行消息
            print("\n🔧 测试2: 发送工具执行消息")
            tool_message = {
                "type": "tool_execution",
                "tool_name": "terminal",
                "parameters": {
                    "command": "echo 'Hello from WebSocket test'",
                    "timeout": 10
                }
            }
            
            await websocket.send(json.dumps(tool_message))
            print(f"📤 发送工具消息: {tool_message}")
            
            # 接收响应
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"📥 收到工具响应: {response_data}")
            
            # 测试3: 发送无效消息类型
            print("\n❌ 测试3: 发送无效消息类型")
            invalid_message = {
                "type": "invalid_type",
                "message": "This should return an error"
            }
            
            await websocket.send(json.dumps(invalid_message))
            print(f"📤 发送无效消息: {invalid_message}")
            
            # 接收响应
            response = await websocket.recv()
            response_data = json.loads(response)
            print(f"📥 收到错误响应: {response_data}")
            
            print("\n✅ 所有测试完成")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ 无法连接到WebSocket服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")

async def test_http_api():
    """测试HTTP API"""
    import aiohttp
    
    print("\n🌐 测试HTTP API...")
    
    async with aiohttp.ClientSession() as session:
        # 测试健康检查
        print("🔍 测试健康检查...")
        async with session.get("http://localhost:8000/health") as response:
            data = await response.json()
            print(f"健康检查响应: {data}")
        
        # 测试状态API
        print("\n📊 测试状态API...")
        async with session.get("http://localhost:8000/api/status") as response:
            data = await response.json()
            print(f"状态API响应: {data}")
        
        # 测试工具列表API
        print("\n🔧 测试工具列表API...")
        async with session.get("http://localhost:8000/api/tools") as response:
            data = await response.json()
            print(f"工具列表响应: {data}")
        
        # 测试聊天API
        print("\n💬 测试聊天API...")
        chat_data = {"message": "你好，请简单介绍一下你的功能"}
        async with session.post("http://localhost:8000/api/chat", json=chat_data) as response:
            data = await response.json()
            print(f"聊天API响应: {data}")

async def main():
    """主测试函数"""
    print("🧪 开始WebSocket和HTTP API测试")
    print("=" * 50)
    
    # 测试HTTP API
    await test_http_api()
    
    # 测试WebSocket
    await test_websocket()
    
    print("\n🎉 所有测试完成")

if __name__ == "__main__":
    asyncio.run(main()) 
 
 
 