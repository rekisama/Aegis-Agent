# Aegis Agent Web界面

基于FastAPI的智能Agent Web界面，提供直观的图形化操作界面。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r ../requirements.txt
```

### 2. 启动Web服务器

```bash
# 方法1: 使用启动脚本
python web/start_server.py

# 方法2: 直接使用uvicorn
uvicorn web.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问界面

- **主页**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 📱 界面功能

### 主要功能

1. **智能聊天**
   - 与Agent进行自然语言对话
   - 支持实时WebSocket通信
   - 显示执行时间和使用的工具

2. **工具管理**
   - 查看所有可用工具
   - 直接执行特定工具
   - 实时工具状态监控

3. **配置管理**
   - 调整模型参数（温度、最大令牌数）
   - 选择不同的AI模型
   - 启用/禁用自动修复和自动安装

4. **系统监控**
   - 实时连接状态
   - Agent初始化状态
   - 系统版本信息

### 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│                    Aegis Agent Web界面                           │
├─────────────────────────────────┬───────────────────────────┤
│                                 │                           │
│        聊天区域                 │        侧边栏             │
│                                 │                           │
│  ┌─────────────────────────────┐ │ ┌─────────────────────┐ │
│  │ 用户消息                    │ │ │ 配置面板            │ │
│  └─────────────────────────────┘ │ └─────────────────────┘ │
│                                 │                           │
│  ┌─────────────────────────────┐ │ ┌─────────────────────┐ │
│  │ Agent响应                   │ │ │ 工具面板            │ │
│  └─────────────────────────────┘ │ └─────────────────────┘ │
│                                 │                           │
│  ┌─────────────────────────────┐ │ ┌─────────────────────┐ │
│  │ 输入框 + 发送按钮           │ │ │ 系统状态            │ │
│  └─────────────────────────────┘ │ └─────────────────────┘ │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

## 🔧 API接口

### REST API

#### 1. 系统状态
```http
GET /api/status
```

#### 2. 获取工具列表
```http
GET /api/tools
```

#### 3. 聊天对话
```http
POST /api/chat
Content-Type: application/json

{
    "message": "你好，请介绍一下你的功能"
}
```

#### 4. 执行工具
```http
POST /api/execute_tool
Content-Type: application/json

{
    "tool_name": "enhanced_terminal",
    "parameters": {
        "command": "echo 'Hello World'",
        "auto_fix": true,
        "auto_install": true
    }
}
```

#### 5. 更新配置
```http
POST /api/config
Content-Type: application/json

{
    "model_name": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 2000,
    "auto_fix": true,
    "auto_install": true
}
```

### WebSocket API

#### 连接
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

#### 发送聊天消息
```javascript
ws.send(JSON.stringify({
    type: 'chat',
    message: '你好'
}));
```

#### 发送工具执行请求
```javascript
ws.send(JSON.stringify({
    type: 'tool_execution',
    tool_name: 'enhanced_terminal',
    parameters: {
        command: 'echo "Hello"',
        auto_fix: true
    }
}));
```

## 🧪 测试

### 运行API测试
```bash
python web/test_api.py
```

### 手动测试
```bash
# 健康检查
curl http://localhost:8000/health

# 获取系统状态
curl http://localhost:8000/api/status

# 获取工具列表
curl http://localhost:8000/api/tools

# 发送聊天消息
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

## 🎨 界面特性

### 响应式设计
- 支持桌面和移动设备
- 自适应布局
- 触摸友好的界面

### 实时通信
- WebSocket实时连接
- 打字指示器
- 连接状态监控

### 美观的UI
- 现代化设计
- 渐变背景
- 动画效果
- 图标支持

### 功能丰富
- 消息历史记录
- 工具执行详情
- 错误处理和显示
- 配置管理

## 🔍 故障排除

### 常见问题

1. **服务器无法启动**
   ```bash
   # 检查端口是否被占用
   netstat -an | grep 8000
   
   # 检查依赖是否安装
   pip list | grep fastapi
   ```

2. **Agent初始化失败**
   - 检查配置文件
   - 确认API密钥设置
   - 查看日志输出

3. **WebSocket连接失败**
   - 检查防火墙设置
   - 确认服务器正在运行
   - 查看浏览器控制台错误

4. **工具执行失败**
   - 检查工具是否正确注册
   - 确认权限设置
   - 查看详细错误信息

### 日志查看
```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 📊 性能监控

### 监控指标
- 响应时间
- 并发连接数
- 错误率
- 资源使用情况

### 健康检查
```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查Agent状态
curl http://localhost:8000/api/status
```

## 🔐 安全考虑

### 生产环境部署
1. 使用HTTPS
2. 配置CORS策略
3. 添加身份验证
4. 限制请求频率
5. 日志审计

### 安全配置
```python
# 在main.py中配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📝 开发指南

### 添加新功能
1. 在`main.py`中添加新的路由
2. 更新HTML模板
3. 添加JavaScript处理逻辑
4. 编写测试用例

### 自定义样式
- 修改`templates/index.html`中的CSS
- 添加新的CSS类
- 调整颜色和布局

### 扩展API
- 在`main.py`中添加新的端点
- 定义Pydantic模型
- 添加错误处理
- 编写文档

## 🎉 总结

Aegis Agent Web界面提供了：

- ✅ **直观的用户界面** - 易于使用的图形化界面
- ✅ **实时通信** - WebSocket支持实时交互
- ✅ **完整的API** - RESTful API和WebSocket API
- ✅ **工具管理** - 可视化的工具执行和监控
- ✅ **配置管理** - 动态调整Agent参数
- ✅ **系统监控** - 实时状态监控和健康检查
- ✅ **响应式设计** - 支持各种设备
- ✅ **美观界面** - 现代化UI设计

这个Web界面让用户可以方便地与智能Agent进行交互，无需命令行操作，大大提升了用户体验。 
 