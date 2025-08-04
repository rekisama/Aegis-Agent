# Web服务器启动方式说明

## 问题背景
当执行 `pip install` 命令时，虚拟环境中的文件发生变化，导致uvicorn的WatchFiles机制检测到变化并自动重启服务器，影响任务执行。

## 解决方案

### 1. 生产环境启动（推荐用于任务执行）
```bash
python web/start_server.py
```
- ✅ 禁用自动重载
- ✅ 避免pip安装时触发重启
- ✅ 适合长时间运行和任务执行
- ❌ 代码修改后需要手动重启

### 2. 开发环境启动（适合代码开发）
```bash
python web/start_server_dev.py
```
- ✅ 启用自动重载
- ✅ 代码修改后自动重启
- ❌ pip安装时可能触发重启

### 3. 智能监控启动（推荐用于开发）
```bash
python web/start_server_smart.py
```
- ✅ 只监控项目代码目录
- ✅ 忽略虚拟环境变化
- ✅ 代码修改后自动重启
- ✅ 避免pip安装时重启

## 使用建议

1. **执行任务时**：使用 `start_server.py`（禁用重载）
2. **开发调试时**：使用 `start_server_smart.py`（智能监控）
3. **需要完整重载时**：使用 `start_server_dev.py`（完整监控）

## 监控目录说明

智能监控模式只监控以下目录：
- `web/` - Web服务器代码
- `python/` - Python代理代码
- `examples/` - 示例代码

不监控：
- `.venv/` - 虚拟环境
- `__pycache__/` - Python缓存
- 其他系统目录 