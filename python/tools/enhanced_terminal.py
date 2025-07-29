"""
Enhanced Terminal Tool
增强的终端工具，具有错误分析和自动修复功能
"""

import asyncio
import logging
import subprocess
import shlex
import re
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

import sys
from pathlib import Path
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from python.tools.base import BaseTool, ToolResult


class ErrorType(Enum):
    """错误类型枚举"""
    MODULE_NOT_FOUND = "module_not_found"
    COMMAND_NOT_FOUND = "command_not_found"
    PERMISSION_DENIED = "permission_denied"
    CONNECTION_ERROR = "connection_error"
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    UNKNOWN = "unknown"


class ErrorAnalyzer:
    """错误分析器"""
    
    # 错误模式匹配
    ERROR_PATTERNS = {
        ErrorType.MODULE_NOT_FOUND: [
            r"No module named '([^']+)'",
            r"ModuleNotFoundError: No module named '([^']+)'",
            r"ImportError: No module named '([^']+)'"
        ],
        ErrorType.COMMAND_NOT_FOUND: [
            r"command not found",
            r"bash: ([^:]+): command not found",
            r"zsh: command not found: ([^\s]+)"
        ],
        ErrorType.PERMISSION_DENIED: [
            r"Permission denied",
            r"EACCES",
            r"Access denied"
        ],
        ErrorType.CONNECTION_ERROR: [
            r"Connection refused",
            r"Connection timed out",
            r"Network is unreachable",
            r"远程计算机拒绝网络连接"
        ],
        ErrorType.SYNTAX_ERROR: [
            r"SyntaxError:",
            r"IndentationError:",
            r"NameError:",
            r"TypeError:"
        ],
        ErrorType.RUNTIME_ERROR: [
            r"RuntimeError:",
            r"ValueError:",
            r"KeyError:",
            r"IndexError:"
        ]
    }
    
    @classmethod
    def analyze_error(cls, stderr: str, stdout: str = "") -> Dict[str, Any]:
        """分析错误信息"""
        error_info = {
            "error_type": ErrorType.UNKNOWN,
            "error_message": stderr.strip(),
            "missing_module": None,
            "missing_command": None,
            "suggested_fix": None,
            "confidence": 0.0
        }
        
        # 检查各种错误类型
        for error_type, patterns in cls.ERROR_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, stderr, re.IGNORECASE)
                if match:
                    error_info["error_type"] = error_type
                    error_info["confidence"] = 0.9
                    
                    # 提取具体信息
                    if error_type == ErrorType.MODULE_NOT_FOUND:
                        error_info["missing_module"] = match.group(1)
                        error_info["suggested_fix"] = f"pip install {match.group(1)}"
                    elif error_type == ErrorType.COMMAND_NOT_FOUND:
                        if len(match.groups()) > 0:
                            error_info["missing_command"] = match.group(1)
                            error_info["suggested_fix"] = f"安装 {match.group(1)} 命令"
                        else:
                            error_info["suggested_fix"] = "检查命令是否正确安装"
                    elif error_type == ErrorType.PERMISSION_DENIED:
                        error_info["suggested_fix"] = "使用 sudo 或检查文件权限"
                    elif error_type == ErrorType.CONNECTION_ERROR:
                        error_info["suggested_fix"] = "检查网络连接和服务器状态"
                    elif error_type == ErrorType.SYNTAX_ERROR:
                        error_info["suggested_fix"] = "检查代码语法错误"
                    elif error_type == ErrorType.RUNTIME_ERROR:
                        error_info["suggested_fix"] = "检查运行时错误"
                    
                    break
        
        return error_info


class AutoFixer:
    """自动修复器"""
    
    @staticmethod
    async def generate_fix_suggestion(error_info: Dict[str, Any], context: str = "") -> str:
        """生成修复建议"""
        error_type = error_info["error_type"]
        error_message = error_info["error_message"]
        
        # 根据错误类型生成修复建议
        if error_type == ErrorType.MODULE_NOT_FOUND:
            module = error_info["missing_module"]
            if module:
                return f"需要安装缺失的模块。建议执行：\npip install {module}"
        
        elif error_type == ErrorType.COMMAND_NOT_FOUND:
            command = error_info["missing_command"]
            if command:
                return f"命令 '{command}' 未找到。建议：\n1. 检查命令是否正确安装\n2. 使用包管理器安装：sudo apt install {command} (Ubuntu) 或 brew install {command} (macOS)"
        
        elif error_type == ErrorType.PERMISSION_DENIED:
            return "权限被拒绝。建议：\n1. 使用 sudo 运行命令\n2. 检查文件/目录权限\n3. 更改文件权限：chmod +x <filename>"
        
        elif error_type == ErrorType.CONNECTION_ERROR:
            return "网络连接错误。建议：\n1. 检查网络连接\n2. 检查服务器是否运行\n3. 检查防火墙设置"
        
        elif error_type == ErrorType.SYNTAX_ERROR:
            return "语法错误。建议：\n1. 检查代码语法\n2. 使用 linter 工具检查\n3. 查看错误行号并修复"
        
        elif error_type == ErrorType.RUNTIME_ERROR:
            return "运行时错误。建议：\n1. 检查变量类型和值\n2. 添加异常处理\n3. 调试代码逻辑"
        
        return f"未知错误：{error_message}\n建议检查命令和参数是否正确"
    
    @staticmethod
    async def execute_fix_command(fix_command: str, context: str = "") -> Dict[str, Any]:
        """执行修复命令"""
        try:
            logging.info(f"🔧 执行修复命令: {fix_command}")
            
            # 执行修复命令
            process = await asyncio.create_subprocess_shell(
                fix_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60  # 修复命令可能需要更长时间
            )
            
            return_code = process.returncode
            stdout_text = stdout.decode('utf-8', errors='ignore')
            stderr_text = stderr.decode('utf-8', errors='ignore')
            
            if return_code == 0:
                logging.info(f"✅ 修复命令执行成功: {fix_command}")
                return {
                    "success": True,
                    "command": fix_command,
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "return_code": return_code
                }
            else:
                logging.warning(f"❌ 修复命令执行失败: {fix_command}")
                return {
                    "success": False,
                    "command": fix_command,
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "return_code": return_code,
                    "error": f"修复命令失败，返回码: {return_code}"
                }
                
        except asyncio.TimeoutError:
            logging.error(f"⏰ 修复命令超时: {fix_command}")
            return {
                "success": False,
                "command": fix_command,
                "error": "修复命令执行超时"
            }
        except Exception as e:
            logging.error(f"❌ 修复命令执行异常: {e}")
            return {
                "success": False,
                "command": fix_command,
                "error": f"修复命令执行异常: {str(e)}"
            }


class EnhancedTerminalTool(BaseTool):
    """增强的终端工具，具有错误分析和自动修复功能"""
    
    def __init__(self):
        super().__init__("enhanced_terminal", "执行 Shell 命令并自动分析错误")
        self.command_history = []
        self.error_history = []
        self.auto_fix_enabled = True
        self.auto_install_enabled = True
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行 Shell 命令并分析错误
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            cwd: 工作目录
            shell: 是否使用shell模式
            auto_fix: 是否启用自动修复
            auto_install: 是否启用自动安装
            max_retries: 最大重试次数
            
        Returns:
            ToolResult with command output and error analysis
        """
        try:
            command = kwargs.get("command", "")
            timeout = kwargs.get("timeout", 30)
            cwd = kwargs.get("cwd", None)
            shell = kwargs.get("shell", False)
            auto_fix = kwargs.get("auto_fix", self.auto_fix_enabled)
            auto_install = kwargs.get("auto_install", self.auto_install_enabled)
            max_retries = kwargs.get("max_retries", 3)
            
            if not command:
                return ToolResult(
                    success=False,
                    data=None,
                    error="No command provided",
                    metadata={"tool_type": "enhanced_terminal"}
                )
            
            # 记录命令历史
            self.command_history.append({
                "command": command,
                "timestamp": self.created_at.isoformat()
            })
            
            logging.info(f"Executing enhanced terminal command: {command}")
            
            # 执行命令并分析结果
            result = await self._execute_with_analysis(
                command, timeout, cwd, shell, auto_fix, auto_install, max_retries
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Enhanced terminal execution failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Execution failed: {str(e)}",
                metadata={"tool_type": "enhanced_terminal"}
            )
    
    async def _execute_with_analysis(
        self, 
        command: str, 
        timeout: int, 
        cwd: Optional[str], 
        shell: bool,
        auto_fix: bool,
        auto_install: bool,
        max_retries: int
    ) -> ToolResult:
        """执行命令并分析错误"""
        
        for attempt in range(max_retries):
            # 执行命令
            stdout, stderr, return_code = await self._run_command(
                command, timeout, cwd, shell
            )
            
            # 如果命令成功，直接返回
            if return_code == 0:
                return ToolResult(
                    success=True,
                    data={
                        "command": command,
                        "return_code": return_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "attempt": attempt + 1,
                        "error_analysis": None,
                        "auto_fix_applied": False
                    },
                    metadata={"tool_type": "enhanced_terminal", "attempts": attempt + 1}
                )
            
            # 分析错误
            error_analysis = ErrorAnalyzer.analyze_error(stderr, stdout)
            
            # 记录错误历史
            self.error_history.append({
                "command": command,
                "error_analysis": error_analysis,
                "attempt": attempt + 1,
                "timestamp": self.created_at.isoformat()
            })
            
            # 如果启用自动修复且错误置信度高
            if auto_fix and error_analysis["confidence"] > 0.5:
                fix_result = await self._attempt_auto_fix(error_analysis, command, auto_install)
                
                # 如果自动修复成功，重新尝试原始命令
                if fix_result["success"]:
                    logging.info(f"🔄 自动修复成功，重新尝试原始命令")
                    retry_stdout, retry_stderr, retry_return_code = await self._run_command(
                        command, timeout, cwd, shell
                    )
                    
                    if retry_return_code == 0:
                        return ToolResult(
                            success=True,
                            data={
                                "command": command,
                                "return_code": retry_return_code,
                                "stdout": retry_stdout,
                                "stderr": retry_stderr,
                                "attempt": attempt + 1,
                                "error_analysis": error_analysis,
                                "auto_fix_applied": True,
                                "fix_result": fix_result
                            },
                            metadata={"tool_type": "enhanced_terminal", "attempts": attempt + 1}
                        )
                    else:
                        logging.warning(f"⚠️ 自动修复后重试仍然失败")
            
            # 如果是最后一次尝试，返回错误分析
            if attempt == max_retries - 1:
                return ToolResult(
                    success=False,
                    data={
                        "command": command,
                        "return_code": return_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "attempt": attempt + 1,
                        "error_analysis": error_analysis,
                        "auto_fix_applied": False
                    },
                    error=f"Command failed after {max_retries} attempts",
                    metadata={"tool_type": "enhanced_terminal", "attempts": max_retries}
                )
            
            # 如果不是自动修复模式，直接返回错误
            if not auto_fix:
                return ToolResult(
                    success=False,
                    data={
                        "command": command,
                        "return_code": return_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "attempt": attempt + 1,
                        "error_analysis": error_analysis,
                        "auto_fix_applied": False
                    },
                    error=f"Command failed with return code {return_code}",
                    metadata={"tool_type": "enhanced_terminal", "attempts": attempt + 1}
                )
        
        # 如果所有尝试都失败
        return ToolResult(
            success=False,
            data=None,
            error=f"Command failed after {max_retries} attempts",
            metadata={"tool_type": "enhanced_terminal", "attempts": max_retries}
        )
    
    async def _attempt_auto_fix(
        self, 
        error_analysis: Dict[str, Any], 
        original_command: str,
        auto_install: bool
    ) -> Dict[str, Any]:
        """尝试自动修复"""
        
        error_type = error_analysis["error_type"]
        
        # 根据错误类型执行相应的修复操作
        if error_type == ErrorType.MODULE_NOT_FOUND and auto_install:
            return await self._fix_missing_module(error_analysis)
        elif error_type == ErrorType.COMMAND_NOT_FOUND and auto_install:
            return await self._fix_missing_command(error_analysis)
        elif error_type == ErrorType.PERMISSION_DENIED:
            return await self._fix_permission_issue(original_command)
        elif error_type == ErrorType.CONNECTION_ERROR:
            return await self._fix_connection_issue(error_analysis)
        else:
            return {
                "success": False,
                "reason": f"Unsupported error type or auto_install disabled: {error_type.value}",
                "suggestion": error_analysis.get("suggested_fix", "请手动修复")
            }
    
    async def _fix_missing_module(self, error_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """修复缺失模块"""
        missing_module = error_analysis.get("missing_module")
        if not missing_module:
            return {"success": False, "reason": "No missing module identified"}
        
        # 尝试安装模块
        install_command = f"pip install {missing_module}"
        logging.info(f"📦 自动安装缺失模块: {install_command}")
        
        fix_result = await AutoFixer.execute_fix_command(install_command)
        
        if fix_result["success"]:
            logging.info(f"✅ 模块安装成功: {missing_module}")
            return {
                "success": True,
                "fix_type": "module_install",
                "module": missing_module,
                "command": install_command,
                "details": fix_result
            }
        else:
            logging.error(f"❌ 模块安装失败: {missing_module}")
            return {
                "success": False,
                "fix_type": "module_install",
                "module": missing_module,
                "command": install_command,
                "error": fix_result.get("error", "Unknown error"),
                "details": fix_result
            }
    
    async def _fix_missing_command(self, error_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """修复缺失命令"""
        missing_command = error_analysis.get("missing_command")
        if not missing_command:
            return {"success": False, "reason": "No missing command identified"}
        
        # 尝试使用包管理器安装命令
        install_commands = [
            f"sudo apt install {missing_command}",  # Ubuntu/Debian
            f"brew install {missing_command}",      # macOS
            f"yum install {missing_command}",       # CentOS/RHEL
        ]
        
        for install_command in install_commands:
            logging.info(f"📦 尝试安装命令: {install_command}")
            fix_result = await AutoFixer.execute_fix_command(install_command)
            
            if fix_result["success"]:
                logging.info(f"✅ 命令安装成功: {missing_command}")
                return {
                    "success": True,
                    "fix_type": "command_install",
                    "command": missing_command,
                    "install_command": install_command,
                    "details": fix_result
                }
        
        logging.error(f"❌ 所有安装尝试都失败: {missing_command}")
        return {
            "success": False,
            "fix_type": "command_install",
            "command": missing_command,
            "tried_commands": install_commands,
            "reason": "All package manager installation attempts failed"
        }
    
    async def _fix_permission_issue(self, original_command: str) -> Dict[str, Any]:
        """修复权限问题"""
        # 尝试使用sudo重新执行命令
        sudo_command = f"sudo {original_command}"
        logging.info(f"🔐 尝试使用sudo执行: {sudo_command}")
        
        fix_result = await AutoFixer.execute_fix_command(sudo_command)
        
        if fix_result["success"]:
            logging.info(f"✅ 权限问题修复成功")
            return {
                "success": True,
                "fix_type": "permission_fix",
                "original_command": original_command,
                "sudo_command": sudo_command,
                "details": fix_result
            }
        else:
            logging.warning(f"⚠️ 权限修复失败")
            return {
                "success": False,
                "fix_type": "permission_fix",
                "original_command": original_command,
                "sudo_command": sudo_command,
                "error": fix_result.get("error", "Unknown error"),
                "details": fix_result
            }
    
    async def _fix_connection_issue(self, error_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """修复连接问题"""
        # 对于连接问题，通常需要手动干预
        logging.warning(f"🌐 连接问题需要手动干预")
        return {
            "success": False,
            "fix_type": "connection_fix",
            "reason": "Connection issues require manual intervention",
            "suggestions": [
                "检查网络连接",
                "检查服务器状态",
                "检查防火墙设置",
                "检查DNS配置"
            ]
        }
    
    async def _run_command(
        self, 
        command: str, 
        timeout: int, 
        cwd: Optional[str], 
        shell: bool
    ) -> Tuple[str, str, int]:
        """运行命令并返回结果"""
        
        if shell:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
        else:
            args = shlex.split(command)
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        
        return (
            stdout.decode('utf-8', errors='ignore'),
            stderr.decode('utf-8', errors='ignore'),
            process.returncode
        )
    
    def get_error_history(self) -> List[Dict]:
        """获取错误历史"""
        return self.error_history
    
    def clear_error_history(self):
        """清除错误历史"""
        self.error_history.clear()
    
    def get_info(self) -> Dict[str, Any]:
        """获取工具信息"""
        return {
            "name": self.name,
            "description": self.description,
            "command_history_count": len(self.command_history),
            "error_history_count": len(self.error_history),
            "auto_fix_enabled": self.auto_fix_enabled,
            "auto_install_enabled": self.auto_install_enabled
        } 