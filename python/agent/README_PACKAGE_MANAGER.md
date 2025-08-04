# 包管理器说明

## 问题背景

Agent在执行任务时，如果检测到缺少必要的Python包，会自动尝试安装。但是使用terminal工具执行`pip install`命令会触发uvicorn的WatchFiles机制，导致服务器自动重启，影响任务执行的连续性。

## 解决方案

### 1. 专用包管理器

创建了专门的`PackageManager`类来处理包安装，避免使用terminal工具：

```python
from python.agent.package_manager import PackageManager

# 创建包管理器
package_manager = PackageManager()

# 安装包
result = await package_manager.install_package("opencv-python")
```

### 2. 优势

- ✅ **避免服务器重启**：直接使用subprocess，不触发WatchFiles
- ✅ **异步执行**：支持异步操作，不阻塞主线程
- ✅ **错误处理**：完善的错误处理和超时机制
- ✅ **包缓存**：维护已安装包列表，避免重复安装
- ✅ **可配置**：支持启用/禁用自动安装功能

### 3. 使用方式

#### 基本使用
```python
# 创建包管理器
package_manager = PackageManager()

# 安装单个包
result = await package_manager.install_package("pillow")

# 批量安装包
result = await package_manager.install_packages(["opencv-python", "numpy"])
```

#### 配置自动安装
```python
# 禁用自动安装
package_manager = PackageManager(auto_install_enabled=False)

# 动态启用/禁用
package_manager.set_auto_install_enabled(True)
```

#### 检查包状态
```python
# 检查包是否已安装
if package_manager.is_package_installed("opencv-python"):
    print("包已安装")

# 获取已安装包列表
installed = package_manager.get_installed_packages()
```

### 4. 集成到Agent

包管理器已经集成到以下组件中：

1. **Agent Core** (`python/agent/core.py`)
   - `_try_install_missing_package` 方法

2. **Error Handler** (`python/agent/error_handler.py`)
   - `_fix_missing_module` 方法

3. **Enhanced Terminal** (`python/tools/enhanced_terminal.py`)
   - `_fix_missing_module` 方法

### 5. 配置选项

可以通过环境变量或配置文件控制包管理器的行为：

```python
# 环境变量
AUTO_INSTALL_PACKAGES=true  # 启用自动安装
AUTO_INSTALL_PACKAGES=false # 禁用自动安装

# 或在代码中设置
package_manager = PackageManager(auto_install_enabled=False)
```

### 6. 错误处理

包管理器会处理以下错误情况：

- **安装超时**：默认5分钟超时
- **网络错误**：pip网络连接失败
- **权限错误**：没有安装权限
- **包不存在**：指定的包不存在
- **依赖冲突**：包依赖冲突

### 7. 日志记录

包管理器会记录详细的安装日志：

```
INFO - 开始安装包: opencv-python
INFO - 包 opencv-python 安装成功
ERROR - 包 invalid-package 安装失败: No matching distribution found
```

## 注意事项

1. **权限要求**：包安装需要适当的权限
2. **网络连接**：需要网络连接来下载包
3. **磁盘空间**：确保有足够的磁盘空间
4. **虚拟环境**：确保在正确的虚拟环境中安装

## 故障排除

### 常见问题

1. **安装失败**
   - 检查网络连接
   - 检查pip源配置
   - 检查权限设置

2. **超时错误**
   - 增加超时时间
   - 检查网络速度
   - 使用国内镜像源

3. **依赖冲突**
   - 检查现有包版本
   - 使用虚拟环境
   - 手动解决依赖

### 调试模式

启用详细日志来调试安装问题：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

package_manager = PackageManager()
result = await package_manager.install_package("package-name")
``` 