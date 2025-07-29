#!/usr/bin/env python3
"""
Web服务器启动脚本
"""

import uvicorn
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    print("🚀 启动Web服务器...")
    print("📝 访问地址: http://localhost:8000")
    print("🔧 按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 启动服务器
    uvicorn.run(
        "web.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 