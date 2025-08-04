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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import shutil
import os

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

# 添加控制台输出
print("Web服务器启动中...")
logging.info("Web服务器启动中...")

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
    attached_files: Optional[List[str]] = None  # List of uploaded file paths

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

class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_size: int
    file_type: str
    upload_time: str

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
        
        logging.info("开始初始化Agent...")
        
        # Initialize agent
        agent = Agent(config)
        
        logging.info("Agent初始化完成，开始检查动态工具...")
        
        # 调试：检查动态工具创建器
        if hasattr(agent, 'dynamic_tool_creator'):
            logging.info(f"动态工具创建器已初始化")
            logging.info(f"动态工具列表: {agent.dynamic_tool_creator.list_dynamic_tools()}")
            logging.info(f"动态工具统计: {agent.dynamic_tool_creator.get_tool_statistics()}")
            
            # 检查Agent的工具列表
            logging.info(f"Agent工具列表: {list(agent.tools.keys())}")
            logging.info(f"Agent工具总数: {len(agent.tools)}")
            
            # 检查是否有动态工具在Agent的工具列表中
            dynamic_tools_in_agent = [name for name in agent.tools.keys() if name in agent.dynamic_tool_creator.list_dynamic_tools()]
            logging.info(f"Agent中的动态工具: {dynamic_tools_in_agent}")
            logging.info(f"Agent中的动态工具数量: {len(dynamic_tools_in_agent)}")
            
            # 详细检查每个工具
            for name, tool in agent.tools.items():
                is_dynamic = name in agent.dynamic_tool_creator.list_dynamic_tools()
                logging.info(f"工具 {name}: {'动态' if is_dynamic else '内置'} - {tool.description}")
        else:
            logging.warning("Agent没有dynamic_tool_creator属性")
        
        logging.info(f"Agent initialized successfully with {len(agent.tools)} tools")
        logging.info(f"Agent config: {config}")
        
    except Exception as e:
        logging.error(f"Failed to initialize agent: {e}")
        import traceback
        traceback.print_exc()
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
        # 获取动态工具列表
        dynamic_tool_names = []
        if hasattr(agent, 'dynamic_tool_creator'):
            dynamic_tool_names = agent.dynamic_tool_creator.list_dynamic_tools()
            logging.info(f"动态工具名称列表: {dynamic_tool_names}")
        
        # 分类工具
        builtin_tools = []
        dynamic_tools = []
        
        for name, tool in agent.tools.items():
            tool_info = {
                "name": name,
                "description": tool.description,
                "usage_count": getattr(tool, 'usage_count', 0),
                "category": getattr(tool, 'category', 'utility')
            }
            
            if name in dynamic_tool_names:
                # 这是动态工具
                tool_info["type"] = "dynamic"
                tool_info["category"] = "dynamic"
                
                # 获取动态工具的额外信息
                if hasattr(agent, 'dynamic_tool_creator'):
                    tool_metadata = agent.dynamic_tool_creator.get_tool_info(name)
                    if tool_metadata:
                        tool_info["success_rate"] = tool_metadata.success_rate
                        tool_info["created_at"] = tool_metadata.created_at
                
                dynamic_tools.append(tool_info)
            else:
                # 这是内置工具
                tool_info["type"] = "builtin"
                builtin_tools.append(tool_info)
        
        logging.info(f"分类结果 - 内置工具: {len(builtin_tools)}, 动态工具: {len(dynamic_tools)}")
        
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
        # Handle file attachments
        message = request.message
        if request.attached_files:
            file_info = []
            for file_path in request.attached_files:
                if Path(file_path).exists():
                    file_size = Path(file_path).stat().st_size
                    file_info.append(f"文件: {Path(file_path).name} ({file_size} bytes)")
            
            if file_info:
                message += f"\n\n附件文件:\n" + "\n".join(file_info)
        
        result = await agent.execute_task(message)
        return {
            "success": True,
            "result": result.get("result", ""),
            "metadata": result.get("metadata", {})
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Chat error: {e}")
        logger.error(f"详细错误信息: {error_details}")
        return {
            "success": False,
            "error": str(e),
            "details": error_details
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
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Tool execution error: {e}")
        logger.error(f"详细错误信息: {error_details}")
        return {
            "success": False,
            "error": str(e),
            "details": error_details
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
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Config update error: {e}")
        logger.error(f"详细错误信息: {error_details}")
        return {
            "success": False,
            "error": str(e),
            "details": error_details
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
        attached_files = message.get("attached_files", [])
        
        if not user_message and not attached_files:
            return {
                "type": "error",
                "message": "消息为空且无附件"
            }
        
        # Handle file attachments
        if attached_files:
            file_info = []
            for file_path in attached_files:
                if Path(file_path).exists():
                    file_size = Path(file_path).stat().st_size
                    file_info.append(f"文件: {Path(file_path).name} ({file_size} bytes)")
            
            if file_info:
                user_message += f"\n\n附件文件:\n" + "\n".join(file_info)
        
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
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"WebSocket chat error: {e}")
        logger.error(f"详细错误信息: {error_details}")
        return {
            "type": "error",
            "message": str(e),
            "details": error_details
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
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"WebSocket tool execution error: {e}")
        logger.error(f"详细错误信息: {error_details}")
        return {
            "type": "error",
            "message": str(e),
            "details": error_details
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

@app.get("/test_download", response_class=HTMLResponse)
async def test_download_page(request: Request):
    """测试下载按钮功能"""
    with open("web/test_download.html", "r", encoding="utf-8") as f:
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
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Failed to create tool: {e}")
        logging.error(f"详细错误信息: {error_details}")
        return {"success": False, "error": str(e), "details": error_details}

@app.get("/api/tools/dynamic")
async def list_dynamic_tools():
    """获取动态工具列表"""
    try:
        if not agent:
            return {"success": False, "error": "Agent not initialized"}
        
        stats = agent.dynamic_tool_creator.get_tool_statistics()
        return {"success": True, "data": stats}
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Failed to list dynamic tools: {e}")
        logging.error(f"详细错误信息: {error_details}")
        return {"success": False, "error": str(e), "details": error_details}

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
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Failed to delete dynamic tool: {e}")
        logging.error(f"详细错误信息: {error_details}")
        return {"success": False, "error": str(e), "details": error_details}

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
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Failed to get tool info: {e}")
        logging.error(f"详细错误信息: {error_details}")
        return {"success": False, "error": str(e), "details": error_details}

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
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"Failed to test tool: {e}")
        logging.error(f"详细错误信息: {error_details}")
        return {"success": False, "error": str(e), "details": error_details} 

# File Upload Endpoints
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the server."""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("web/uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename to prevent conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{timestamp}_{file.filename}" if file.filename else f"{timestamp}_upload"
        
        # Save file
        file_path = upload_dir / unique_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file info
        file_size = file_path.stat().st_size
        file_type = file.content_type or "application/octet-stream"
        
        return FileUploadResponse(
            filename=unique_filename,
            file_path=str(file_path),
            file_size=file_size,
            file_type=file_type,
            upload_time=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"File upload failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"File upload failed: {str(e)}"}
        )

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download a processed file."""
    try:
        upload_dir = Path("web/uploads")
        file_path = upload_dir / filename
        
        if not file_path.exists():
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
        
        # Get file info
        file_size = file_path.stat().st_size
        file_type = "application/octet-stream"
        
        # Determine content type based on file extension
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            file_type = "image/" + filename.split('.')[-1].lower()
        elif filename.lower().endswith('.pdf'):
            file_type = "application/pdf"
        elif filename.lower().endswith(('.txt', '.md')):
            file_type = "text/plain"
        elif filename.lower().endswith(('.json')):
            file_type = "application/json"
        
        # Return file as response
        from fastapi.responses import FileResponse
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=file_type
        )
        
    except Exception as e:
        logging.error(f"File download failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"File download failed: {str(e)}"}
        )

def generate_download_link(filename: str) -> str:
    """Generate a download link for a file."""
    return f"/api/download/{filename}"

@app.get("/api/uploads")
async def list_uploads():
    """List all uploaded files."""
    try:
        upload_dir = Path("web/uploads")
        if not upload_dir.exists():
            return {"files": []}
        
        files = []
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "upload_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "download_link": generate_download_link(file_path.name)
                })
        
        return {"files": files}
        
    except Exception as e:
        logging.error(f"Failed to list uploads: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list uploads: {str(e)}"}
        )

@app.delete("/api/uploads/{filename}")
async def delete_upload(filename: str):
    """Delete an uploaded file."""
    try:
        upload_dir = Path("web/uploads")
        file_path = upload_dir / filename
        
        if not file_path.exists():
            return JSONResponse(
                status_code=404,
                content={"error": "File not found"}
            )
        
        file_path.unlink()
        return {"success": True, "message": "File deleted successfully"}
        
    except Exception as e:
        logging.error(f"Failed to delete file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to delete file: {str(e)}"}
        )