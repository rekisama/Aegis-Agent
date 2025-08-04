#!/usr/bin/env python3
"""
Web服务器智能启动脚本（只监控项目代码，不监控虚拟环境）
"""

import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    print("🚀 启动Web服务器（智能监控模式）...")
    print("📝 访问地址: http://localhost:8000")
    print("👀 只监控项目代码目录，忽略虚拟环境")
    print("🔧 按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 定义要监控的目录（只监控项目代码，不监控虚拟环境和动态工具目录）
    reload_dirs = [
        str(Path(project_root) / "web"),
        str(Path(project_root) / "python" / "agent"),
        str(Path(project_root) / "python" / "tools" / "base.py"),
        str(Path(project_root) / "python" / "tools" / "code.py"),
        str(Path(project_root) / "python" / "tools" / "terminal.py"),
        str(Path(project_root) / "python" / "tools" / "search.py"),
        str(Path(project_root) / "python" / "tools" / "web_reader.py"),
        str(Path(project_root) / "python" / "llm"),
        str(Path(project_root) / "python" / "utils"),
        str(Path(project_root) / "examples"),
    ]
    
    # 启动服务器
    uvicorn.run(
        "web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=reload_dirs,  # 只监控指定目录
        log_level="info"
    ) 