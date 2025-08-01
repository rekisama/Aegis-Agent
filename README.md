# Aegis Agent - 智能AI代理系统

<div align="center">
  <img src="pic/P3RE_Aigis_art.png" alt="Aegis Agent" width="200" height="auto">
</div>

Aegis Agent是一个先进的AI代理框架，具备智能任务执行、动态工具创建、智能错误处理和自动修复能力。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![状态](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 🚀 核心特性

### 🧠 智能错误处理
- **自动错误分析**: LLM驱动的错误诊断和修复建议
- **智能代码修复**: 自动修复Python代码中的常见错误（如缺少导入）
- **工具代码自修复**: 动态工具执行失败时自动修复工具代码
- **任务重分析**: 基于错误上下文重新分析和规划任务执行

### 🔧 动态工具系统
- **自然语言工具创建**: 用自然语言描述即可创建新工具
- **LLM工具规范验证**: 智能验证工具代码的安全性和完整性
- **工具代码自动更新**: 支持运行时更新和修复工具代码
- **工具链管理**: 支持工具链的创建和执行

### 🛡️ 安全验证机制
- **多层安全检查**: LLM验证 + 本地关键词检测
- **危险操作拦截**: 自动检测和阻止危险代码执行
- **参数完整性验证**: 确保工具参数定义完整
- **功能合理性检查**: 验证工具功能的合理性

### 💾 持久化记忆
- **长期记忆**: 跨会话的记忆保持
- **上下文管理**: 智能上下文切换和保持
- **对话历史**: 自动保存和加载对话历史

### 🌐 现代化Web界面
- **实时WebSocket通信**: 实时双向通信
- **响应式设计**: 支持桌面和移动设备
- **实时执行监控**: 显示Agent的实时执行过程
- **文件上传支持**: 支持文件上传和处理

## 📋 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [核心功能](#核心功能)
- [Web界面](#web界面)
- [配置](#配置)
- [API文档](#api文档)
- [工具系统](#工具系统)
- [开发指南](#开发指南)

## 🛠️ 安装

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

## 🚀 快速开始

### 命令行模式

1. **启动代理**
```bash
python main.py
```

2. **交互模式**
```
Aegis Agent > 帮我计算2的100次方
Aegis Agent > 创建一个工具来读取网页标题
Aegis Agent > 修复这个Python代码中的错误
```

### Web界面模式

1. **启动Web服务器**
```bash
python web/start_server.py
```

2. **访问Web界面**
打开浏览器访问 `http://localhost:8000`

3. **开始智能对话**
- 在输入框中输入任务
- 实时查看执行过程和错误处理
- 自动保存对话历史

## 🧠 核心功能

### 智能错误处理

Aegis Agent具备强大的错误处理能力：

```python
# 自动修复代码错误
Aegis Agent > 执行这段代码：import re; print(re.findall(r'\d+', 'abc123def456'))

# 系统会自动检测并修复错误
# 如果缺少导入，会自动添加
# 如果语法错误，会自动修复
```

### 动态工具创建

用自然语言创建新工具：

```python
# 创建网页标题读取工具
Aegis Agent > 创建一个工具来读取网页的标题

# 系统会：
# 1. 分析需求
# 2. 生成工具代码
# 3. 验证安全性
# 4. 注册工具
# 5. 提供使用示例
```

### 工具规范验证

系统使用LLM验证工具规范：

- **代码安全性检查**: 检测危险操作（eval, exec, os.system等）
- **参数完整性验证**: 确保工具参数定义完整
- **功能合理性检查**: 验证工具功能的合理性
- **命名规范性检查**: 确保命名符合Python规范

### 自动代码修复

当工具执行失败时，系统会：

1. **分析错误**: 使用LLM分析错误原因
2. **生成修复**: 自动生成修复代码
3. **更新工具**: 自动更新工具代码
4. **重新执行**: 使用修复后的代码重新执行

## 🌐 Web界面

### 界面特性
- **实时执行监控**: 显示Agent的实时执行过程
- **错误处理可视化**: 实时显示错误分析和修复过程
- **工具创建界面**: 可视化工具创建和验证过程
- **对话管理**: 自动保存和加载对话历史
- **文件上传**: 支持文件上传和处理

### 功能演示
1. **智能任务执行**: 输入复杂任务，观看智能分析和执行
2. **动态工具创建**: 用自然语言描述需求，自动创建工具
3. **错误自动修复**: 故意输入错误代码，观察自动修复过程
4. **工具链执行**: 创建和执行复杂的工具链

## ⚙️ 配置

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
AUTO_FIX_ENABLED=true
MAX_RETRIES=3
```

### 错误处理配置

```python
# 在代码中配置错误处理参数
agent.set_auto_fix_enabled(True)  # 启用自动修复
agent.set_max_retries(3)          # 设置最大重试次数
agent.set_verbose_logging(True)    # 启用详细日志
```

## 📚 API文档

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
    case 'error_analysis':
      console.log('错误分析:', data.analysis);
      break;
    case 'auto_fix_applied':
      console.log('自动修复:', data.fix);
      break;
  }
};
```

### HTTP API

#### 创建工具
```bash
curl -X POST http://localhost:8000/api/create_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "web_title_reader",
    "description": "读取网页标题的工具",
    "code": "import requests\nfrom bs4 import BeautifulSoup\n\ndef get_title(url):\n    response = requests.get(url)\n    soup = BeautifulSoup(response.text, 'html.parser')\n    return soup.title.string",
    "parameters": {"url": "网页URL"}
  }'
```

#### 执行工具
```bash
curl -X POST http://localhost:8000/api/execute_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "web_title_reader",
    "parameters": {"url": "https://example.com"}
  }'
```

## 🔧 工具系统

### 内置工具

| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `code` | 执行Python代码（带自动修复） | `code`: 代码字符串 |
| `terminal` | 执行系统命令 | `command`: 命令字符串 |
| `search` | 网络搜索 | `query`: 搜索查询 |
| `file_reader` | 读取文件内容 | `file_path`: 文件路径 |
| `web_reader` | 网页内容读取 | `url`: 网页URL |

### 动态工具

系统支持动态创建和管理工具：

```python
# 创建动态工具
tool_spec = {
    "name": "data_analyzer",
    "description": "数据分析工具",
    "code": """
import pandas as pd
import matplotlib.pyplot as plt

def analyze_data(file_path):
    df = pd.read_csv(file_path)
    summary = df.describe()
    return summary.to_dict()
    """,
    "parameters": {"file_path": "CSV文件路径"}
}

# 系统会自动验证和注册工具
```

### 工具验证流程

1. **LLM验证**: 使用大语言模型分析代码质量和安全性
2. **本地安全检查**: 快速检测危险关键词
3. **参数验证**: 确保参数定义完整
4. **功能验证**: 验证工具功能的合理性

## 🛠️ 开发指南

### 项目结构
```
Aegis Agent/
├── python/
│   ├── agent/              # 代理核心
│   │   ├── smart_error_core.py    # 智能错误处理核心
│   │   ├── error_handler.py       # 错误处理代理
│   │   ├── dynamic_tool_creator.py # 动态工具创建器
│   │   └── enhanced_tool_manager.py # 增强工具管理器
│   ├── tools/              # 工具系统
│   │   ├── dynamic/        # 动态工具目录
│   │   ├── enhanced_terminal.py   # 增强终端工具
│   │   └── web_reader.py   # 网页读取工具
│   ├── llm/               # LLM客户端
│   ├── memory/            # 记忆管理
│   └── utils/             # 工具函数
├── web/                   # Web界面
│   ├── templates/         # HTML模板
│   └── main.py           # FastAPI应用
├── examples/              # 示例脚本
└── tests/                # 测试文件
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

### 错误处理开发

```python
# 自定义错误处理器
from python.agent.error_handler import ErrorHandlerAgent

class CustomErrorHandler(ErrorHandlerAgent):
    async def handle_custom_error(self, error_context):
        # 自定义错误处理逻辑
        pass
```

### 运行测试
```bash
python -m pytest tests/
```

## 📝 更新日志

### v2.0.0 (当前版本)
- ✨ 新增智能错误处理系统
- ✨ 新增动态工具创建功能
- ✨ 新增LLM工具规范验证
- ✨ 新增自动代码修复功能
- ✨ 新增工具代码自修复能力
- ✨ 新增任务重分析功能
- 🔧 优化Web界面和用户体验
- 🛡️ 增强安全验证机制

### v1.0.0
- 🎉 初始版本发布
- ✨ 基础AI代理功能
- ✨ Web界面
- ✨ 基础工具系统

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">
  <strong>Aegis Agent - 让AI代理更智能，让错误处理更优雅</strong>
</div>

