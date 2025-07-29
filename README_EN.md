# 🛡️ Aegis Agent

<div align="center">
  <img src="pic/P3RE_Aigis_art.png" alt="Aegis Agent" width="200" height="auto">
</div>

A powerful AI agent framework with intelligent task execution, persistent memory, and dynamic tool management capabilities.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 🌟 Features

### 🤖 Core Functionality
- **Intelligent Task Execution**: Automatic analysis and execution of complex tasks
- **Persistent Memory**: Long-term memory and context preservation
- **Dynamic Tool Management**: JSON-driven tool registration and management
- **Real-time Web Interface**: Modern ChatGPT-style web interface
- **Conversation Storage**: Local storage for conversation history with multi-conversation management

### 🛠️ Built-in Tools
- **Code Execution**: Secure Python code execution environment
- **Terminal Operations**: System command execution and file operations
- **Web Search**: SearXNG search engine integration
- **File Operations**: File reading, writing, and content analysis
- **Data Visualization**: Intelligent data analysis and chart generation

### 🔧 Advanced Features
- **WebSocket Communication**: Real-time bidirectional communication
- **Modular Architecture**: Extensible tool and component system
- **Security Validation**: Multi-layer security checks and validation
- **Responsive Design**: Support for desktop and mobile devices

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Web Interface](#web-interface)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Tool System](#tool-system)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### System Requirements
- Python 3.8+
- Git
- Internet connection (for API calls)

### Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/rekisama/Aegis-Agent.git
cd Aegis-Agent
```

2. **Create Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
cp env.example .env
# Edit .env file with your API keys
```

## ⚡ Quick Start

### Command Line Mode

1. **Start Agent**
```bash
python main.py
```

2. **Interactive Mode**
```
Aegis Agent > help me calculate 2 to the power of 100
```

### Web Interface Mode

1. **Start Web Server**
```bash
python web/start_server.py
```

2. **Access Web Interface**
Open browser and visit `http://localhost:8000`

3. **Start Conversation**
- Enter tasks in the input box
- View real-time execution process
- Automatically save conversation history

## 🌐 Web Interface

### Interface Features
- **ChatGPT Style**: Modern dark theme interface
- **Real-time Execution**: Display Agent's real-time execution process
- **Conversation Management**: Auto-save and load conversation history
- **Responsive Design**: Support for desktop and mobile devices
- **Keyboard Shortcuts**: Enter to send, Shift+Enter for new line

### Feature Demo
1. **Task Execution**: Enter "calculate 2 to the power of 100" to see real-time execution
2. **Code Analysis**: Enter "analyze the performance of this Python code"
3. **Data Visualization**: Enter "generate a bar chart for sales data"
4. **File Operations**: Enter "read and analyze this CSV file"

## ⚙️ Configuration

### Environment Variables

Create `.env` file and configure the following variables:

```env
# LLM API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# Tool Configuration
SEARXNG_URL=https://searxng.example.com
SEARXNG_API_KEY=your_searxng_api_key

# System Configuration
LOG_LEVEL=INFO
MEMORY_ENABLED=true
```

### Tool Configuration

Tool configurations are stored in JSON files under `python/tools/` directory:

```json
{
  "name": "code",
  "description": "Execute Python code",
  "parameters": {
    "code": {
      "type": "string",
      "description": "Python code to execute"
    }
  }
}
```

## 📚 API Documentation

### WebSocket API

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

#### Send Message
```javascript
ws.send(JSON.stringify({
  type: 'chat',
  message: 'Your task description'
}));
```

#### Receive Messages
```javascript
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  switch(data.type) {
    case 'task_completed':
      console.log('Task completed:', data.result);
      break;
    case 'execution_log':
      console.log('Execution log:', data.message);
      break;
  }
};
```

### HTTP API

#### Send Task
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "calculate 2 to the power of 100"}'
```

## 🛠️ Tool System

### Built-in Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `code` | Execute Python code | `code`: code string |
| `terminal` | Execute system commands | `command`: command string |
| `search` | Web search | `query`: search query |
| `file_reader` | Read file content | `file_path`: file path |

### Dynamic Tools

The system supports dynamic loading and registration of tools:

```python
from python.tools.base import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Custom tool"
    
    async def execute(self, **kwargs):
        # Tool execution logic
        return ToolResult(success=True, data={"result": "execution result"})
```

## 🔧 Development

### Project Structure
```
Aegis-Agent/
├── python/
│   ├── agent/          # Agent core
│   ├── tools/          # Tool system
│   ├── llm/           # LLM client
│   ├── memory/        # Memory management
│   └── utils/         # Utility functions
├── web/               # Web interface
│   ├── templates/     # HTML templates
│   └── main.py        # FastAPI application
├── examples/          # Example scripts
└── tests/            # Test files
```

### Adding New Tools

1. **Create Tool Class**
```python
# python/tools/custom_tool.py
from .base import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "Custom tool description"
    
    async def execute(self, **kwargs):
        # Implement tool logic
        return ToolResult(success=True, data={"result": "result"})
```

2. **Register Tool**
```json
// python/tools/custom_tool_metadata.json
{
  "name": "custom_tool",
  "description": "Custom tool description",
  "parameters": {
    "param1": {
      "type": "string",
      "description": "Parameter description"
    }
  }
}
```

### Running Tests
```bash
python -m pytest tests/
```

## 🤝 Contributing

We welcome all forms of contributions!

### Ways to Contribute
1. **Report Bugs**: Report issues in GitHub Issues
2. **Feature Suggestions**: Propose new features
3. **Code Contributions**: Submit Pull Requests
4. **Documentation Improvements**: Improve documentation and examples

### Development Environment Setup
```bash
git clone https://github.com/rekisama/Aegis-Agent.git
cd Aegis-Agent
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Thanks to all developers and users who have contributed to this project!

---

**Aegis Agent** - Making AI agents smarter, more powerful, and easier to use! 