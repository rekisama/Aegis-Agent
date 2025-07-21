# 🛡️ Aegis Agent

一个强大的AI代理框架，具备持久化记忆、多代理协作和动态工具创建能力。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![状态](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 🌟 特性

### 🤖 核心功能
- **智能任务执行**: 自动分析和执行复杂任务
- **持久化记忆**: 长期记忆和上下文保持
- **多代理协作**: 主从代理架构，支持任务委派
- **动态工具创建**: LLM驱动的工具生成和优化
- **实时通信**: 代理间高效通信机制

### 🛠️ 内置工具
- **终端操作**: 系统命令执行和文件操作
- **网络搜索**: Tavily搜索和通用网络爬取
- **代码执行**: 安全的代码运行环境
- **动态工具**: 智能文本分析、数据可视化、代码质量检查等

### 🔧 高级特性
- **自适应学习**: 从任务执行中学习和改进
- **自我进化**: 自动优化工具和策略
- **安全验证**: 多层安全检查和验证
- **模块化架构**: 可扩展的工具和组件系统

## 📋 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [配置](#配置)
- [使用指南](#使用指南)
- [API文档](#api文档)
- [工具系统](#工具系统)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 🚀 安装

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

## ⚡ 快速开始

### 基本使用

1. **启动代理**
```bash
python main.py
```

2. **交互模式**
```
🛡️  Aegis Agent > task 帮我分析这个项目的代码质量
```

3. **查看状态**
```
🛡️  Aegis Agent > status
```

### 示例脚本

```python
from python.agent.core import Agent
from python.utils.env_manager import env_manager

# 初始化代理
agent = Agent()

# 执行任务
result = await agent.execute_task("分析当前目录的Python文件质量")
print(result)
```

## ⚙️ 配置

### 环境变量

创建 `.env` 文件并配置以下变量：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Tavily搜索API配置
TAVILY_API_KEY=your_tavily_api_key_here
TAVILY_SEARCH_DEPTH=basic
TAVILY_INCLUDE_IMAGES=false
TAVILY_INCLUDE_ANSWER=true

# 代理配置
AGENT_NAME=Aegis Agent
AGENT_MODEL=deepseek-chat
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=4000

# 记忆配置
MEMORY_ENABLED=true
MEMORY_RETENTION_DAYS=30
MEMORY_MAX_SIZE=10000

# 工具配置
TOOLS_ENABLED=true
TERMINAL_TIMEOUT=30
SEARCH_TIMEOUT=10
CODE_TIMEOUT=30
```

### 获取API密钥

1. **DeepSeek API**: 访问 [DeepSeek官网](https://platform.deepseek.com/) 注册并获取API密钥
2. **Tavily API**: 访问 [Tavily官网](https://tavily.com/) 注册并获取API密钥

## 📖 使用指南

### 命令行界面

启动后，你可以使用以下命令：

- `task <描述>` - 执行任务
- `status` - 显示代理状态
- `memory` - 显示记忆统计
- `tools` - 列出可用工具
- `create <名称>` - 创建从属代理
- `help` - 显示帮助
- `quit` - 退出

### 编程接口

```python
from python.agent.core import Agent

# 创建代理实例
agent = Agent()

# 执行任务
result = await agent.execute_task("帮我写一个Python函数来计算斐波那契数列")

# 创建从属代理
subordinate = agent.create_subordinate("数据分析助手")

# 添加自定义工具
from python.tools.base import BaseTool
agent.add_tool("custom_tool", CustomTool())
```

## 🔧 工具系统

### 内置工具

| 工具 | 功能 | 状态 |
|------|------|------|
| `terminal` | 系统命令执行 | ✅ |
| `search` | 网络搜索 | ✅ |
| `tavily_search` | Tavily搜索 | ✅ |
| `code` | 代码执行 | ✅ |

### 动态工具

系统支持LLM驱动的动态工具创建：

- **文本分析**: 情感分析、文本摘要
- **数据处理**: 数据清洗、统计分析、可视化
- **代码质量**: 代码质量分析、安全检查
- **智能计算**: 数学计算、单位转换

### 创建自定义工具

```python
from python.tools.base import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="自定义工具描述",
            parameters={
                "param1": {"type": "string", "description": "参数1"}
            }
        )
    
    async def execute(self, **kwargs):
        # 工具实现逻辑
        return {"result": "执行结果"}
```

## 🏗️ 架构

```
WAgent/
├── python/
│   ├── agent/           # 代理核心
│   ├── tools/           # 工具系统
│   ├── memory/          # 记忆管理
│   ├── communication/   # 通信系统
│   ├── llm/            # LLM客户端
│   └── utils/          # 工具函数
├── prompts/            # 提示词模板
├── examples/           # 示例代码
├── tests/             # 测试文件
└── docs/              # 文档
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_basic.py

# 运行性能测试
pytest test_performance.py
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献步骤

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8 mypy

# 代码格式化
black python/
flake8 python/
mypy python/
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [DeepSeek](https://platform.deepseek.com/) - 提供强大的LLM API
- [Tavily](https://tavily.com/) - 提供智能搜索服务
- 所有贡献者和用户
