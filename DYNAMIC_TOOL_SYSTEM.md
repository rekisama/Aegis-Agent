# 动态工具创建系统

Aegis Agent的动态工具创建系统允许Agent在运行时自动创建、管理和使用自定义工具，实现真正的自我进化能力。

## 功能特性

### 🚀 核心功能
- **自动工具创建**: Agent能够分析任务需求并自动创建新工具
- **安全验证**: 使用LLM验证工具代码的安全性
- **实时监控**: 文件系统监控支持热加载工具
- **Web管理界面**: 完整的Web界面用于工具管理
- **统计跟踪**: 工具使用统计和成功率跟踪

### 🛡️ 安全机制
- **代码安全检查**: 检测危险操作（文件系统、网络、系统调用等）
- **参数验证**: 验证工具参数的类型和范围
- **沙箱执行**: 在隔离环境中执行动态代码
- **LLM验证**: 使用大语言模型验证工具规范

### 📊 管理功能
- **工具创建**: 通过Web界面或API创建新工具
- **工具列表**: 查看所有动态工具及其统计信息
- **工具测试**: 在线测试工具功能
- **工具删除**: 安全删除不需要的工具

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent Core    │    │ Dynamic Tool    │    │   Web Interface │
│                 │    │   Creator       │    │                 │
│ - 任务分析      │◄──►│ - 工具创建      │◄──►│ - 工具管理      │
│ - 工具执行      │    │ - 安全验证      │    │ - 创建表单      │
│ - 结果生成      │    │ - 文件监控      │    │ - 工具列表      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tool Files    │    │   Metadata      │    │   API Endpoints │
│                 │    │                 │    │                 │
│ - Python代码    │    │ - JSON配置      │    │ - REST API      │
│ - 工具类        │    │ - 统计信息      │    │ - WebSocket     │
│ - 元数据        │    │ - 使用记录      │    │ - 实时通知      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动Web服务器

```bash
python web/start_server.py
```

访问 http://localhost:8000 查看Web界面。

### 3. 运行演示

```bash
python examples/dynamic_tool_creation_demo.py
```

## 使用方法

### 通过Web界面创建工具

1. 打开Web界面，点击侧边栏的"工具管理"按钮
2. 填写工具信息：
   - **工具名称**: 例如 `calculator`
   - **工具描述**: 描述工具的功能
   - **Python代码**: 实现工具功能的代码
   - **参数定义**: JSON格式的参数说明
3. 点击"创建工具"按钮

### 通过API创建工具

```python
import requests

tool_spec = {
    "name": "calculator",
    "description": "简单计算器",
    "code": """
def calculate(a, b, operation):
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        return a / b if b != 0 else 'Error: Division by zero'
    else:
        return 'Error: Unknown operation'

result = calculate(a, b, operation)
""",
    "parameters": {
        "a": "第一个数字",
        "b": "第二个数字",
        "operation": "操作类型 (add/subtract/multiply/divide)"
    }
}

response = requests.post('http://localhost:8000/api/tools/create', json=tool_spec)
print(response.json())
```

### 通过Agent自动创建

Agent会在执行任务时自动分析是否需要创建新工具：

```python
from python.agent.core import Agent

agent = Agent()
result = await agent.execute_task("帮我创建一个工具，可以计算斐波那契数列的第n项")
```

## API参考

### 工具管理API

#### 创建工具
```http
POST /api/tools/create
Content-Type: application/json

{
    "name": "tool_name",
    "description": "工具描述",
    "code": "Python代码",
    "parameters": {
        "param1": "参数描述"
    }
}
```

#### 获取工具列表
```http
GET /api/tools/dynamic
```

#### 删除工具
```http
DELETE /api/tools/dynamic/{tool_name}
```

#### 测试工具
```http
POST /api/tools/dynamic/{tool_name}/test
Content-Type: application/json

{
    "param1": "value1",
    "param2": "value2"
}
```

#### 获取工具信息
```http
GET /api/tools/dynamic/{tool_name}/info
```

## 工具代码规范

### 基本结构

```python
"""
Dynamic Tool: {tool_name}
Auto-generated by Agent
"""

import json
import logging
from typing import Dict, Any
from python.tools.base import BaseTool, ToolResult

class Dynamic{tool_name_capitalized}Tool(BaseTool):
    """Dynamic tool: {tool_name}"""
    
    def __init__(self):
        super().__init__()
        self.name = "{tool_name}"
        self.description = "Dynamic tool created by agent"
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the dynamic tool"""
        try:
            # 参数验证
            validated_params = self._validate_parameters(kwargs)
            
            # 执行动态代码
            result = self._execute_dynamic_code(validated_params)
            
            return ToolResult(
                success=True,
                data={"result": result},
                error=None
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=str(e)
            )
```

### 安全要求

1. **禁止的操作**:
   - `import os`, `import sys`, `import subprocess`
   - `eval()`, `exec()`, `__import__()`
   - 文件系统操作 (`open()`, `file()`)
   - 网络请求
   - 系统命令执行

2. **参数验证**:
   - 检查参数类型
   - 限制字符串长度
   - 限制列表大小
   - 限制字典深度

3. **错误处理**:
   - 捕获所有异常
   - 返回有意义的错误信息
   - 不暴露系统信息

## 文件结构

```
python/
├── agent/
│   ├── core.py                    # Agent核心，包含动态工具创建逻辑
│   └── dynamic_tool_creator.py    # 动态工具创建器
├── tools/
│   └── dynamic/                   # 动态工具目录
│       ├── __init__.py
│       ├── dynamic_hello_world.py # 示例工具
│       └── dynamic_mock_tool.py   # 示例工具
web/
├── main.py                        # Web服务器，包含工具管理API
└── templates/
    └── index.html                 # Web界面，包含工具管理界面
examples/
└── dynamic_tool_creation_demo.py  # 演示脚本
```

## 监控和日志

### 文件系统监控

系统会自动监控 `python/tools/dynamic/` 目录的变化：

- **文件创建**: 自动加载新工具
- **文件修改**: 重新加载工具
- **文件删除**: 从内存中移除工具

### 日志记录

```python
import logging

# 查看工具创建日志
logging.info("Created dynamic tool: calculator")

# 查看工具执行日志
logging.info("Tool calculator executed successfully")

# 查看安全验证日志
logging.warning("Dangerous keyword found in code: import os")
```

### 统计信息

```python
# 获取工具统计
stats = agent.dynamic_tool_creator.get_tool_statistics()
print(stats)
# 输出:
# {
#     "total_dynamic_tools": 3,
#     "total_usage": 15,
#     "average_success_rate": 0.93,
#     "tools": [...]
# }
```

## 故障排除

### 常见问题

1. **工具创建失败**
   - 检查代码语法
   - 验证参数定义
   - 查看安全验证结果

2. **工具执行错误**
   - 检查参数类型
   - 验证代码逻辑
   - 查看错误日志

3. **文件监控不工作**
   - 确保安装了 `watchdog` 包
   - 检查目录权限
   - 查看监控日志

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
agent = Agent(config)
agent.dynamic_tool_creator.debug = True
```

## 扩展开发

### 添加新的工具类型

1. 创建工具类文件
2. 继承 `BaseTool` 类
3. 实现 `execute` 方法
4. 添加安全验证

### 自定义验证规则

```python
def custom_validation_rules(code: str) -> bool:
    # 添加自定义验证逻辑
    dangerous_patterns = [
        r'import\s+os',
        r'import\s+sys',
        r'eval\(',
        r'exec\(',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False
    
    return True
```

### 集成到现有系统

```python
# 在现有的Agent系统中集成
from python.agent.dynamic_tool_creator import DynamicToolCreator

class CustomAgent(Agent):
    def __init__(self):
        super().__init__()
        self.dynamic_tool_creator = DynamicToolCreator()
    
    async def create_custom_tool(self, spec):
        return await self.dynamic_tool_creator.create_tool_from_spec(spec)
```

## 性能优化

### 工具缓存

```python
# 启用工具缓存
agent.dynamic_tool_creator.enable_caching = True
```

### 并行执行

```python
# 并行创建多个工具
import asyncio

async def create_multiple_tools(specs):
    tasks = [agent.create_new_tool(spec) for spec in specs]
    results = await asyncio.gather(*tasks)
    return results
```

## 安全最佳实践

1. **代码审查**: 定期审查动态创建的代码
2. **权限控制**: 限制工具的执行权限
3. **资源限制**: 限制工具的内存和CPU使用
4. **日志审计**: 记录所有工具创建和执行操作
5. **定期更新**: 更新安全验证规则

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。 