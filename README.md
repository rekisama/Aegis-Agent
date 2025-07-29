#  Aegis Agent

![Aegis Agent](pic/P3RE_Aigis_art.png)

AI代理框架，具备智能任务执行、持久化记忆和动态工具管理能力。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![状态](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

##  特性

###  核心功能
- **智能任务执行**: 自动分析和执行复杂任务
- **持久化记忆**: 长期记忆和上下文保持
- **动态工具管理**: JSON驱动的工具注册和管理
- **实时Web界面**: 现代化Web界面
- **对话保存**: 本地存储对话历史，支持多对话管理

###  内置工具
- **代码执行**: 安全的Python代码运行环境
- **终端操作**: 系统命令执行和文件操作
- **网络搜索**: SearXNG搜索引擎集成
- **文件操作**: 文件读写和内容分析
- **数据可视化**: 智能数据分析和图表生成

###  高级特性
- **WebSocket通信**: 实时双向通信
- **模块化架构**: 可扩展的工具和组件系统
- **安全验证**: 多层安全检查和验证
- **响应式设计**: 支持桌面和移动设备

##  目录

- [安装](#安装)
- [快速开始](#快速开始)
- [Web界面](#web界面)
- [配置](#配置)
- [API文档](#api文档)
- [工具系统](#工具系统)


##  安装

### 系统要求
- Python 3.8+
- Git
- 网络连接（用于API调用）

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/rekisama/Aegis-Agent.git
cd Aegis-Agent
```

2. **创建虚拟环境**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，填入你的API密钥
```

##  快速开始

### 命令行模式

1. **启动代理**
```bash
python main.py
```

2. **交互模式**
```
Aegis Agent > 帮我计算2的100次方
```

### Web界面模式

1. **启动Web服务器**
```bash
python web/start_server.py
```

2. **访问Web界面**
打开浏览器访问 `http://localhost:8000`

3. **开始对话**
- 在输入框中输入任务
- 实时查看执行过程
- 自动保存对话历史

##  Web界面

### 界面特性
- **实时执行**: 显示Agent的实时执行过程
- **对话管理**: 自动保存和加载对话历史
- **响应式设计**: 支持桌面和移动设备
- **键盘快捷键**: Enter发送，Shift+Enter换行

### 功能演示
1. **任务执行**: 输入"计算2的100次方"查看实时执行过程
2. **代码分析**: 输入"分析这个Python代码的性能"
3. **数据可视化**: 输入"生成一个销售数据的柱状图"
4. **文件操作**: 输入"读取并分析这个CSV文件"

##  配置

### 环境变量

创建 `.env` 文件并配置以下变量：

```env
# LLM API配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 工具配置
SEARXNG_URL=https://searxng.example.com
SEARXNG_API_KEY=your_searxng_api_key

# 系统配置
LOG_LEVEL=INFO
MEMORY_ENABLED=true
```

### 工具配置

工具配置存储在 `python/tools/` 目录下的JSON文件中：

```json
{
  "name": "code",
  "description": "执行Python代码",
  "parameters": {
    "code": {
      "type": "string",
      "description": "要执行的Python代码"
    }
  }
}
```

##  API文档

### WebSocket API

#### 连接
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

#### 发送消息
```javascript
ws.send(JSON.stringify({
  type: 'chat',
  message: '你的任务描述'
}));
```

#### 接收消息
```javascript
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  switch(data.type) {
    case 'task_completed':
      console.log('任务完成:', data.result);
      break;
    case 'execution_log':
      console.log('执行日志:', data.message);
      break;
  }
};
```

### HTTP API

#### 发送任务
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算2的100次方"}'
```

##  工具系统

### 内置工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `code` | 执行Python代码 | `code`: 代码字符串 |
| `terminal` | 执行系统命令 | `command`: 命令字符串 |
| `search` | 网络搜索 | `query`: 搜索查询 |
| `file_reader` | 读取文件内容 | `file_path`: 文件路径 |

### 动态工具

系统支持动态加载和注册工具：

```python
from python.tools.base import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "自定义工具"
    
    async def execute(self, **kwargs):
        # 工具执行逻辑
        return ToolResult(success=True, data={"result": "执行结果"})
```

##  开发

### 项目结构
```
Aegis-Agent/
├── python/
│   ├── agent/          # 代理核心
│   ├── tools/          # 工具系统
│   ├── llm/           # LLM客户端
│   ├── memory/        # 记忆管理
│   └── utils/         # 工具函数
├── web/               # Web界面
│   ├── templates/     # HTML模板
│   └── main.py        # FastAPI应用
├── examples/          # 示例脚本
└── tests/            # 测试文件
```

### 添加新工具

1. **创建工具类**
```python
# python/tools/custom_tool.py
from .base import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "自定义工具描述"
    
    async def execute(self, **kwargs):
        # 实现工具逻辑
        return ToolResult(success=True, data={"result": "结果"})
```

2. **注册工具**
```json
// python/tools/custom_tool_metadata.json
{
  "name": "custom_tool",
  "description": "自定义工具描述",
  "parameters": {
    "param1": {
      "type": "string",
      "description": "参数描述"
    }
  }
}
```

### 运行测试
```bash
python -m pytest tests/
```


### 开发环境设置
```bash
git clone https://github.com/rekisama/Aegis-Agent.git
cd Aegis-Agent
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

