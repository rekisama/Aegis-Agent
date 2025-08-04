#!/usr/bin/env python3
"""
Web服务器启动脚本 - 动态工具开发模式
专门用于动态工具开发，排除动态工具目录避免重载
"""

import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🚀 启动Web服务器 - 动态工具开发模式...")
    print("📝 访问地址: http://localhost:8000")
    print("🔧 按 Ctrl+C 停止服务器")
    print("⚠️  此模式已排除动态工具目录，避免工具创建时触发重载")
    print("-" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 启动服务器，排除动态工具目录
    uvicorn.run(
        "web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 启用自动重载
        reload_dirs=[
            str(project_root / "web"),
            str(project_root / "python" / "agent"),
            str(project_root / "python" / "tools"),
            str(project_root / "python" / "llm"),
            str(project_root / "python" / "utils"),
        ],  # 只监视这些目录，排除动态工具目录
        reload_excludes=[
            "python/tools/dynamic/*",  # 排除动态工具目录
            "*.pyc",
            "__pycache__",
            ".git",
            ".venv",
        ],
        log_level="info"
    ) 