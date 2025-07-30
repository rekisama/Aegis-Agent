#!/usr/bin/env python3
"""
Web Server for Aegis Agent
Provides a web interface for interacting with the agent.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("应用程序启动中...")
    logging.info("应用程序启动中...")
    await initialize_agent()
    print("应用程序启动完成")
    logging.info("应用程序启动完成")
    yield
    # 关闭时执行
    print("应用程序关闭中...")
    logging.info("应用程序关闭中...")

app = FastAPI(lifespan=lifespan)

# Global variables
agent = None
active_connections: List[WebSocket] = []

class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
    
    async def add_connection(self, websocket: WebSocket):
        self.connections.append(websocket)
    
    async def remove_connection(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)
    
    async def broadcast_log(self, message: str, level: str = "info"):
        """向所有连接的客户端广播日志消息"""
        for connection in self.connections:
            try:
                await connection.send_json({
                    "type": "execution_log",
                    "message": message,
                    "level": level
                })
            except Exception as e:
                logging.error(f"Failed to send log to connection: {e}")
                # 移除失效的连接
                if connection in self.connections:
                    self.connections.remove(connection)

# 创建WebSocket管理器实例
websocket_manager = WebSocketManager()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)
logger = logging.getLogger(__name__)

# 确保日志立即输出
for handler in logging.root.handlers:
    handler.setLevel(logging.INFO)
    if isinstance(handler, logging.StreamHandler):
        handler.setStream(sys.stdout)

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Mount static files (if directory exists)
static_dir = Path("web/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class WebAgentConfig(BaseModel):
    model_name: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000
    auto_fix: bool = True
    auto_install: bool = True

# Pydantic models for tool management
class ToolCreationRequest(BaseModel):
    name: str
    description: str
    code: str
    parameters: Dict[str, Any] = {}

class ToolDeletionRequest(BaseModel):
    tool_name: str

async def initialize_agent():
    """Initialize the agent."""
    global agent
    try:
        from python.agent.core import Agent
        from python.utils.config_types import AgentConfig
        
        # Load environment variables
        from python.utils.env_manager import env_manager
        env_manager._load_env()
        
        # Create agent configuration
        config = AgentConfig(
            name="Aegis Agent",
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=4000,
            memory_enabled=True,
            hierarchical_enabled=False,  # 禁用委派功能
            tools_enabled=True,
            report_frequency=5,
            require_approval=False,
            memory_retention_days=30,
            max_memory_size=10000
        )
        
        # Initialize agent
        agent = Agent(config)
        
        logging.info("Agent initialized successfully with 4 tools")
        logging.info(f"Agent config: {config}")
        
    except Exception as e:
        logging.error(f"Failed to initialize agent: {e}")
        raise

# 删除旧的startup事件，现在使用lifespan
# @app.on_event("startup")
# async def startup_event():
#     """Initialize agent on startup."""
#     await initialize_agent()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    """Get agent status."""
    if not agent:
        return {"status": "not_initialized"}
    
    return {
        "status": "initialized",
        "agent_info": agent.get_status(),
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/tools")
async def get_tools():
    """Get available tools."""
    if not agent:
        return {"error": "Agent not initialized"}
    
    tools_info = []
    for name, tool in agent.tools.items():
        tools_info.append({
            "name": name,
            "description": tool.description,
            "usage_count": getattr(tool, 'usage_count', 0),
            "type": "builtin"  # 标记为内置工具
        })
    
    return {"tools": tools_info}

@app.get("/api/tools/all")
async def get_all_tools():
    """Get all tools including builtin and dynamic tools."""
    if not agent:
        return {"error": "Agent not initialized"}
    
    try:
        # 获取内置工具
        builtin_tools = []
        for name, tool in agent.tools.items():
            builtin_tools.append({
                "name": name,
                "description": tool.description,
                "usage_count": getattr(tool, 'usage_count', 0),
                "type": "builtin",
                "category": getattr(tool, 'category', 'utility')
            })
        
        # 获取动态工具
        dynamic_tools = []
        if hasattr(agent, 'dynamic_tool_creator'):
            dynamic_stats = agent.dynamic_tool_creator.get_tool_statistics()
            for tool_info in dynamic_stats.get('tools', []):
                dynamic_tools.append({
                    "name": tool_info['name'],
                    "description": tool_info['description'],
                    "usage_count": tool_info['usage_count'],
                    "success_rate": tool_info['success_rate'],
                    "type": "dynamic",
                    "category": "dynamic",
                    "created_at": tool_info['created_at']
                })
        
        return {
            "success": True,
            "data": {
                "builtin_tools": builtin_tools,
                "dynamic_tools": dynamic_tools,
                "total_builtin": len(builtin_tools),
                "total_dynamic": len(dynamic_tools),
                "total_tools": len(builtin_tools) + len(dynamic_tools)
            }
        }
    except Exception as e:
        logging.error(f"Failed to get all tools: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/chat")
async def chat(request: ChatMessage):
    """Handle chat requests."""
    if not agent:
        return {"error": "Agent not initialized"}
    
    try:
        result = await agent.execute_task(request.message)
        return {
            "success": True,
            "result": result.get("result", ""),
            "metadata": result.get("metadata", {})
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/execute_tool")
async def execute_tool(request: ToolExecutionRequest):
    """Execute a specific tool."""
    if not agent:
        return {"error": "Agent not initialized"}
    
    try:
        tool = agent.get_tool(request.tool_name)
        if not tool:
            return {"error": f"Tool {request.tool_name} not found"}
        
        result = await tool.execute(**request.parameters)
        return {
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "metadata": result.metadata
        }
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/config")
async def update_config(config: WebAgentConfig):
    """Update agent configuration."""
    if not agent:
        return {"error": "Agent not initialized"}
    
    try:
        # Update agent configuration
        agent.config.model = config.model_name
        agent.config.temperature = config.temperature
        agent.config.max_tokens = config.max_tokens
        
        return {"success": True, "message": "Configuration updated"}
    except Exception as e:
        logger.error(f"Config update error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/config")
async def get_config():
    """Get current agent configuration."""
    if not agent:
        return {"error": "Agent not initialized"}
    
    return {
        "model_name": agent.config.model,
        "temperature": agent.config.temperature,
        "max_tokens": agent.config.max_tokens,
        "memory_enabled": agent.config.memory_enabled,
        "tools_enabled": agent.config.tools_enabled
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    # 强制刷新输出
    import sys
    sys.stdout.flush()
    
    # 使用多种方式输出日志
    print("新的WebSocket连接请求")
    print("新的WebSocket连接请求", file=sys.stderr)
    logging.info(f"新的WebSocket连接请求")
    
    # 强制刷新日志
    for handler in logging.root.handlers:
        if hasattr(handler, 'flush'):
            handler.flush()
    
    await websocket.accept()
    await websocket_manager.add_connection(websocket)
    print(f"WebSocket连接已建立，当前连接数: {len(websocket_manager.connections)}")
    print(f"WebSocket连接已建立，当前连接数: {len(websocket_manager.connections)}", file=sys.stderr)
    logging.info(f"WebSocket连接已建立，当前连接数: {len(websocket_manager.connections)}")
    
    try:
        while True:
            print(f"等待WebSocket消息...")
            print(f"等待WebSocket消息...", file=sys.stderr)
            logging.info(f"等待WebSocket消息...")
            data = await websocket.receive_text()
            print(f"收到WebSocket原始数据: {data[:100]}...")
            print(f"收到WebSocket原始数据: {data[:100]}...", file=sys.stderr)
            logging.info(f"收到WebSocket原始数据: {data[:100]}...")
            message = json.loads(data)
            print(f"收到WebSocket消息: {message.get('type', 'unknown')}")
            print(f"收到WebSocket消息: {message.get('type', 'unknown')}", file=sys.stderr)
            logging.info(f"收到WebSocket消息: {message.get('type', 'unknown')}")
            
            response = await handle_websocket_chat(message, websocket)
            print(f"发送WebSocket响应: {response}")
            print(f"发送WebSocket响应: {response}", file=sys.stderr)
            logging.info(f"发送WebSocket响应: {response}")
            
            if response:
                await websocket.send_json(response)
                
    except WebSocketDisconnect:
        await websocket_manager.remove_connection(websocket)
        print(f"WebSocket连接断开，当前连接数: {len(websocket_manager.connections)}")
        print(f"WebSocket连接断开，当前连接数: {len(websocket_manager.connections)}", file=sys.stderr)
        logging.info(f"WebSocket连接断开，当前连接数: {len(websocket_manager.connections)}")
    except Exception as e:
        print(f"WebSocket错误: {e}")
        print(f"WebSocket错误: {e}", file=sys.stderr)
        logging.error(f"WebSocket错误: {e}")
        import traceback
        traceback.print_exc()
        await websocket_manager.remove_connection(websocket)

async def handle_websocket_chat(message: Dict[str, Any], websocket: WebSocket):
    """处理WebSocket聊天消息"""
    try:
        if not agent:
            return {
                "type": "error",
                "message": "Agent未初始化"
            }
        
        user_message = message.get("message", "")
        if not user_message:
            return {
                "type": "error",
                "message": "消息为空"
            }
        
        # 发送开始执行的消息
        await websocket.send_json({
            "type": "execution_log",
            "message": f"开始处理任务: {user_message}",
            "level": "info"
        })
        
        # 执行任务
        logging.info(f"WebSocket收到任务: {user_message}")
        logging.info(f"开始执行任务...")
        
        # 发送任务分析开始的消息
        await websocket.send_json({
            "type": "execution_log",
            "message": "开始分析任务...",
            "level": "info"
        })
        
        result = await agent.execute_task(user_message)
        
        # 发送任务完成的消息
        await websocket.send_json({
            "type": "execution_log",
            "message": "任务执行完成",
            "level": "info"
        })
        
        logging.info(f"任务执行完成")
        
        # 发送任务完成消息 - 确保结果是可序列化的
        task_result = result.get('result', '')
        
        # 处理ToolResult对象
        if hasattr(task_result, 'data'):
            # 如果是ToolResult对象，提取其数据
            if isinstance(task_result.data, dict) and 'stdout' in task_result.data:
                # 如果是code工具的结果，提取stdout
                task_result = task_result.data['stdout']
            else:
                task_result = str(task_result.data)
        elif isinstance(task_result, dict) and 'stdout' in task_result:
            # 如果已经是字典格式，提取stdout
            task_result = task_result['stdout']
        else:
            task_result = str(task_result)
        
        await websocket.send_json({
            "type": "task_completed",
            "result": task_result,
            "metadata": {
                "execution_method": result.get('metadata', {}).get('execution_method', 'unknown'),
                "tool_results": result.get('metadata', {}).get('tool_results', [])
            }
        })
        
        # 返回成功响应
        return {
            "type": "success",
            "message": "任务执行完成"
        }
        
    except Exception as e:
        logger.error(f"WebSocket chat error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "type": "error",
            "message": str(e)
        }

async def handle_websocket_tool_execution(message: Dict[str, Any], websocket: WebSocket):
    """处理WebSocket工具执行消息"""
    try:
        if not agent:
            return {
                "type": "error",
                "message": "Agent not initialized"
            }
        
        tool_name = message.get("tool_name", "")
        parameters = message.get("parameters", {})
        
        tool = agent.get_tool(tool_name)
        if not tool:
            return {
                "type": "error",
                "message": f"Tool {tool_name} not found"
            }
        
        result = await tool.execute(**parameters)
        
        return {
            "type": "tool_response",
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "metadata": result.metadata,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"WebSocket tool execution error: {e}")
        return {
            "type": "error",
            "message": str(e)
        }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/favicon.ico")
async def favicon():
    """Handle favicon requests."""
    return {"status": "not_found"}

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """Test page for debugging."""
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/test_ws", response_class=HTMLResponse)
async def websocket_test_page(request: Request):
    """WebSocket test page."""
    return templates.TemplateResponse("websocket_test.html", {"request": request}) 

@app.get("/simple_test", response_class=HTMLResponse)
async def simple_test_page(request: Request):
    """简单的WebSocket测试页面"""
    with open("web/templates/simple_test.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read()) 

@app.get("/test_connection")
async def test_connection():
    """测试连接"""
    print("🔍 测试连接被调用")
    logging.info("🔍 测试连接被调用")
    return {"message": "服务器连接正常"} 

# Tool management API endpoints
@app.post("/api/tools/create")
async def create_tool(request: ToolCreationRequest):
    """创建新工具"""
    try:
        if not agent:
            return {"success": False, "error": "Agent not initialized"}
        
        tool_spec = {
            "name": request.name,
            "description": request.description,
            "code": request.code,
            "parameters": request.parameters
        }
        
        result = await agent.create_new_tool(tool_spec)
        return result
        
    except Exception as e:
        logging.error(f"Failed to create tool: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/tools/dynamic")
async def list_dynamic_tools():
    """获取动态工具列表"""
    try:
        if not agent:
            return {"success": False, "error": "Agent not initialized"}
        
        stats = agent.dynamic_tool_creator.get_tool_statistics()
        return {"success": True, "data": stats}
        
    except Exception as e:
        logging.error(f"Failed to list dynamic tools: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/api/tools/dynamic/{tool_name}")
async def delete_dynamic_tool(tool_name: str):
    """删除动态工具"""
    try:
        if not agent:
            return {"success": False, "error": "Agent not initialized"}
        
        success = agent.dynamic_tool_creator.delete_tool(tool_name)
        
        if success:
            # 从agent工具列表中移除
            if tool_name in agent.tools:
                del agent.tools[tool_name]
            
            # 重新加载系统提示词
            agent.system_prompt = agent._load_system_prompt()
        
        return {"success": success}
        
    except Exception as e:
        logging.error(f"Failed to delete dynamic tool: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/tools/dynamic/{tool_name}/info")
async def get_dynamic_tool_info(tool_name: str):
    """获取动态工具详细信息"""
    try:
        if not agent:
            return {"success": False, "error": "Agent not initialized"}
        
        tool_info = agent.dynamic_tool_creator.get_tool_info(tool_name)
        
        if tool_info:
            return {"success": True, "data": {
                "name": tool_info.name,
                "description": tool_info.description,
                "parameters": tool_info.parameters,
                "usage_count": tool_info.usage_count,
                "success_rate": tool_info.success_rate,
                "created_at": tool_info.created_at
            }}
        else:
            return {"success": False, "error": "Tool not found"}
            
    except Exception as e:
        logging.error(f"Failed to get tool info: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/tools/dynamic/{tool_name}/test")
async def test_dynamic_tool(tool_name: str, parameters: Dict[str, Any]):
    """测试动态工具"""
    try:
        if not agent:
            return {"success": False, "error": "Agent not initialized"}
        
        tool = agent.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": "Tool not found"}
        
        # 执行工具
        result = await tool.execute(**parameters)
        
        return {
            "success": result.success,
            "data": result.data,
            "error": result.error
        }
        
    except Exception as e:
        logging.error(f"Failed to test tool: {e}")
        return {"success": False, "error": str(e)} 


