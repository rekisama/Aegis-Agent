# 🛡️ WAgent (Aegis Agent)

A powerful AI agent framework with persistent memory, multi-agent collaboration, and dynamic tool creation capabilities.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 🌟 Features

### 🤖 Core Capabilities
- **Intelligent Task Execution**: Automatically analyze and execute complex tasks
- **Persistent Memory**: Long-term memory and context preservation
- **Multi-Agent Collaboration**: Master-slave agent architecture with task delegation
- **Dynamic Tool Creation**: LLM-driven tool generation and optimization
- **Real-time Communication**: Efficient communication mechanism between agents

### 🛠️ Built-in Tools
- **Terminal Operations**: System command execution and file operations
- **Web Search**: Tavily search and general web scraping
- **Code Execution**: Secure code execution environment
- **Dynamic Tools**: Intelligent text analysis, data visualization, code quality inspection, etc.

### 🔧 Advanced Features
- **Adaptive Learning**: Learn and improve from task execution
- **Self-evolution**: Automatically optimize tools and strategies
- **Security Validation**: Multi-layer security checks and validation
- **Modular Architecture**: Extensible tool and component system

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
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

### Basic Usage

1. **Start the Agent**
```bash
python main.py
```

2. **Interactive Mode**
```
🛡️  Aegis Agent > task Help me analyze the code quality of this project
```

3. **Check Status**
```
🛡️  Aegis Agent > status
```

### Example Script

```python
from python.agent.core import Agent
from python.utils.env_manager import env_manager

# Initialize agent
agent = Agent()

# Execute task
result = await agent.execute_task("Analyze the quality of Python files in current directory")
print(result)
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file and configure the following variables:

```env
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Tavily Search API Configuration
TAVILY_API_KEY=your_tavily_api_key_here
TAVILY_SEARCH_DEPTH=basic
TAVILY_INCLUDE_IMAGES=false
TAVILY_INCLUDE_ANSWER=true

# Agent Configuration
AGENT_NAME=Aegis Agent
AGENT_MODEL=deepseek-chat
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=4000

# Memory Configuration
MEMORY_ENABLED=true
MEMORY_RETENTION_DAYS=30
MEMORY_MAX_SIZE=10000

# Tools Configuration
TOOLS_ENABLED=true
TERMINAL_TIMEOUT=30
SEARCH_TIMEOUT=10
CODE_TIMEOUT=30
```

### Getting API Keys

1. **DeepSeek API**: Visit [DeepSeek Platform](https://platform.deepseek.com/) to register and get API key
2. **Tavily API**: Visit [Tavily](https://tavily.com/) to register and get API key

## 📖 Usage Guide

### Command Line Interface

After starting, you can use the following commands:

- `task <description>` - Execute a task
- `status` - Show agent status
- `memory` - Show memory statistics
- `tools` - List available tools
- `create <name>` - Create subordinate agent
- `help` - Show help
- `quit` - Exit

### Programming Interface

```python
from python.agent.core import Agent

# Create agent instance
agent = Agent()

# Execute task
result = await agent.execute_task("Help me write a Python function to calculate Fibonacci sequence")

# Create subordinate agent
subordinate = agent.create_subordinate("Data Analysis Assistant")

# Add custom tool
from python.tools.base import BaseTool
agent.add_tool("custom_tool", CustomTool())
```

## 🔧 Tool System

### Built-in Tools

| Tool | Function | Status |
|------|----------|--------|
| `terminal` | System command execution | ✅ |
| `search` | Web search | ✅ |
| `tavily_search` | Tavily search | ✅ |
| `code` | Code execution | ✅ |

### Dynamic Tools

The system supports LLM-driven dynamic tool creation:

- **Text Analysis**: Sentiment analysis, text summarization
- **Data Processing**: Data cleaning, statistical analysis, visualization
- **Code Quality**: Code quality analysis, security checks
- **Smart Calculation**: Mathematical calculations, unit conversion

### Creating Custom Tools

```python
from python.tools.base import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="Custom tool description",
            parameters={
                "param1": {"type": "string", "description": "Parameter 1"}
            }
        )
    
    async def execute(self, **kwargs):
        # Tool implementation logic
        return {"result": "Execution result"}
```

## 🏗️ Architecture

```
WAgent/
├── python/
│   ├── agent/           # Agent core
│   ├── tools/           # Tool system
│   ├── memory/          # Memory management
│   ├── communication/   # Communication system
│   ├── llm/            # LLM client
│   └── utils/          # Utility functions
├── prompts/            # Prompt templates
├── examples/           # Example code
├── tests/             # Test files
└── docs/              # Documentation
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_basic.py

# Run performance tests
pytest test_performance.py
```

## 🤝 Contributing

We welcome all forms of contributions!

### Contribution Steps

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Environment Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Code formatting
black python/
flake8 python/
mypy python/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [DeepSeek](https://platform.deepseek.com/) - Providing powerful LLM API
- [Tavily](https://tavily.com/) - Providing intelligent search services
- All contributors and users

## 📞 Support

- 📧 Email: [your-email@example.com]
- 🐛 Issue Report: [GitHub Issues](https://github.com/rekisama/Aegis-Agent/issues)
- 📖 Documentation: [Project Wiki](https://github.com/rekisama/Aegis-Agent/wiki)

---

**⭐ If this project helps you, please give us a star!** 