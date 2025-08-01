"""
Terminal Tool
执行 Shell 命令的工具
"""

import asyncio
import logging
import subprocess
import shlex
from typing import Dict, Any, Optional

import sys
from pathlib import Path
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from python.tools.base import BaseTool, ToolResult


class TerminalTool(BaseTool):
    """执行 Shell 命令的工具"""
    
    def __init__(self):
        super().__init__("terminal", "执行 Shell 命令")
        self.command_history = []
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行 Shell 命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            cwd: 工作目录
            shell: 是否使用shell模式
            
        Returns:
            ToolResult with command output
        """
        try:
            command = kwargs.get("command", "")
            timeout = kwargs.get("timeout", 30)
            cwd = kwargs.get("cwd", None)
            shell = kwargs.get("shell", False)
            
            if not command:
                return ToolResult(
                    success=False,
                    data=None,
                    error="No command provided",
                    metadata={"tool_type": "terminal"}
                )
            
            # 记录命令历史
            self.command_history.append({
                "command": command,
                "timestamp": self.created_at.isoformat()
            })
            
            logging.info(f"Executing terminal command: {command}")
            
            # 执行命令
            try:
                if shell:
                    # 使用shell模式
                    process = await asyncio.create_subprocess_shell(
                        command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=cwd
                    )
                else:
                    # 解析命令参数
                    args = shlex.split(command)
                    process = await asyncio.create_subprocess_exec(
                        *args,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=cwd
                    )
            except NotImplementedError:
                # Windows系统上的兼容性处理
                logging.warning("asyncio subprocess not supported, falling back to synchronous execution")
                return await self._execute_sync(command, timeout, cwd, shell)
            
            # 等待命令完成
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            # 获取返回码
            return_code = process.returncode
            
            # 解码输出
            stdout_text = stdout.decode('utf-8', errors='ignore')
            stderr_text = stderr.decode('utf-8', errors='ignore')
            
            result_data = {
                "command": command,
                "return_code": return_code,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "success": return_code == 0,
                "command_history_length": len(self.command_history)
            }
            
            if return_code == 0:
                logging.info(f"Command executed successfully: {command}")
                return ToolResult(
                    success=True,
                    data=result_data,
                    metadata={
                        "tool_type": "terminal",
                        "command": command,
                        "return_code": return_code
                    }
                )
            else:
                error_message = f"Command failed with return code {return_code}"
                if stderr_text:
                    error_message += f"\nError output: {stderr_text}"
                
                logging.warning(f"Command failed with return code {return_code}: {command}")
                logging.warning(f"Error output: {stderr_text}")
                
                return ToolResult(
                    success=False,
                    data=result_data,
                    error=error_message,
                    metadata={
                        "tool_type": "terminal",
                        "command": command,
                        "return_code": return_code,
                        "stderr": stderr_text
                    }
                )
                
        except asyncio.TimeoutError:
            logging.error(f"Command timed out after {timeout}s: {command}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Command timed out after {timeout} seconds",
                metadata={"tool_type": "terminal", "timeout": True}
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"Command execution failed: {e}")
            logging.error(f"详细错误信息: {error_details}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Command execution failed: {str(e)}",
                metadata={"tool_type": "terminal", "error_details": error_details}
            )
    
    async def _execute_sync(self, command: str, timeout: int, cwd: Optional[str], shell: bool) -> ToolResult:
        """同步执行命令（Windows兼容性备选方案）"""
        try:
            import subprocess
            import threading
            import time
            
            # 使用同步subprocess
            if shell:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    text=True
                )
            else:
                args = shlex.split(command)
                process = subprocess.Popen(
                    args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    text=True
                )
            
            # 等待命令完成，带超时
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Command timed out after {timeout} seconds",
                    metadata={"tool_type": "terminal", "timeout": True, "sync_execution": True}
                )
            
            result_data = {
                "command": command,
                "return_code": return_code,
                "stdout": stdout,
                "stderr": stderr,
                "success": return_code == 0,
                "command_history_length": len(self.command_history),
                "sync_execution": True
            }
            
            if return_code == 0:
                logging.info(f"Command executed successfully (sync): {command}")
                return ToolResult(
                    success=True,
                    data=result_data,
                    metadata={
                        "tool_type": "terminal",
                        "command": command,
                        "return_code": return_code,
                        "sync_execution": True
                    }
                )
            else:
                error_message = f"Command failed with return code {return_code}"
                if stderr:
                    error_message += f"\nError output: {stderr}"
                
                logging.warning(f"Command failed with return code {return_code} (sync): {command}")
                logging.warning(f"Error output: {stderr}")
                
                return ToolResult(
                    success=False,
                    data=result_data,
                    error=error_message,
                    metadata={
                        "tool_type": "terminal",
                        "command": command,
                        "return_code": return_code,
                        "stderr": stderr,
                        "sync_execution": True
                    }
                )
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"Sync command execution failed: {e}")
            logging.error(f"详细错误信息: {error_details}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Sync command execution failed: {str(e)}",
                metadata={"tool_type": "terminal", "error_details": error_details, "sync_execution": True}
            )
    
    def get_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        info = super().get_info()
        info.update({
            "command_history_length": len(self.command_history),
            "supported_shells": ["bash", "cmd", "powershell"],
            "max_timeout": 300
        })
        return info
    
    def clear_history(self):
        """清空命令历史"""
        self.command_history.clear()
        logging.info("Terminal command history cleared") 
    
    def get_history(self) -> list:
        """获取命令历史"""
        return self.command_history.copy() 