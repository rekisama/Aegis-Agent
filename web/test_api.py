#!/usr/bin/env python3
"""
Aegis Agent API测试脚本
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"

async def test_api():
    """测试API功能"""
    async with aiohttp.ClientSession() as session:
        print("🧪 开始API测试...")
        print("=" * 50)
        
        # 测试健康检查
        print("\n1. 测试健康检查")
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                data = await response.json()
                print(f"✅ 健康检查: {data}")
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
        
        # 测试系统状态
        print("\n2. 测试系统状态")
        try:
            async with session.get(f"{BASE_URL}/api/status") as response:
                data = await response.json()
                print(f"✅ 系统状态: {data}")
        except Exception as e:
            print(f"❌ 系统状态失败: {e}")
        
        # 测试获取工具列表
        print("\n3. 测试获取工具列表")
        try:
            async with session.get(f"{BASE_URL}/api/tools") as response:
                data = await response.json()
                print(f"✅ 工具列表: 找到 {data.get('count', 0)} 个工具")
                for tool in data.get('tools', [])[:5]:  # 只显示前5个
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")
        
        # 测试获取配置
        print("\n4. 测试获取配置")
        try:
            async with session.get(f"{BASE_URL}/api/config") as response:
                data = await response.json()
                print(f"✅ 当前配置: {data}")
        except Exception as e:
            print(f"❌ 获取配置失败: {e}")
        
        # 测试聊天功能
        print("\n5. 测试聊天功能")
        try:
            chat_data = {
                "message": "你好，请介绍一下你的功能"
            }
            async with session.post(f"{BASE_URL}/api/chat", json=chat_data) as response:
                data = await response.json()
                if data.get('success'):
                    print(f"✅ 聊天成功")
                    print(f"   响应: {data.get('response', '')[:100]}...")
                    print(f"   执行时间: {data.get('execution_time', 0)}ms")
                    print(f"   使用工具: {data.get('tools_used', [])}")
                else:
                    print(f"❌ 聊天失败: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 聊天测试失败: {e}")
        
        # 测试工具执行
        print("\n6. 测试工具执行")
        try:
            tool_data = {
                "tool_name": "enhanced_terminal",
                "parameters": {
                    "command": "echo 'Hello from API test'",
                    "auto_fix": True,
                    "auto_install": True
                }
            }
            async with session.post(f"{BASE_URL}/api/execute_tool", json=tool_data) as response:
                data = await response.json()
                if data.get('success'):
                    print(f"✅ 工具执行成功")
                    print(f"   输出: {data.get('data', {}).get('stdout', '')}")
                else:
                    print(f"❌ 工具执行失败: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 工具执行测试失败: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API测试完成!")

async def test_websocket():
    """测试WebSocket功能"""
    import websockets
    
    print("\n🔌 测试WebSocket连接...")
    try:
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 发送聊天消息
            message = {
                "type": "chat",
                "message": "通过WebSocket发送的消息"
            }
            await websocket.send(json.dumps(message))
            print("📤 消息已发送")
            
            # 接收响应
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 收到响应: {data.get('type', 'unknown')}")
            
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")

async def main():
    """主函数"""
    print("🚀 Aegis Agent API测试")
    print("请确保Web服务器正在运行 (python web/start_server.py)")
    print()
    
    # 测试HTTP API
    await test_api()
    
    # 测试WebSocket
    await test_websocket()

if __name__ == "__main__":
    asyncio.run(main()) 
 