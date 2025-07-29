#!/usr/bin/env python3
"""
启动ChatGPT风格的Aegis Agent Web界面
"""

import sys
import uvicorn
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    print("🚀 启动ChatGPT风格的Aegis Agent Web界面")
    print("=" * 50)
    print("📱 访问地址: http://localhost:8000")
    print("📊 API文档: http://localhost:8000/docs")
    print("🔧 健康检查: http://localhost:8000/health")
    print()
    print("✨ 特性:")
    print("  - ChatGPT风格的现代化界面")
    print("  - 实时WebSocket通信")
    print("  - 自动修复和安装功能")
    print("  - 响应式设计")
    print("  - 深色主题")
    print()
    
    try:
        uvicorn.run(
            "web.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 
 
 