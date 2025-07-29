"""
Error Handler Agent
智能错误处理代理，自动分析错误并执行修复操作
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

import sys
from pathlib import Path
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from python.tools.base import ToolResult
from python.tools.enhanced_terminal import EnhancedTerminalTool, ErrorAnalyzer, AutoFixer


@dataclass
class ErrorContext:
    """错误上下文"""
    command: str
    stdout: str
    stderr: str
    return_code: int
    error_analysis: Dict[str, Any]
    attempt: int
    max_attempts: int


class ErrorHandlerAgent:
    """错误处理代理"""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.terminal_tool = EnhancedTerminalTool()
        self.error_history = []
        self.fix_history = []
        self.max_auto_fix_attempts = 5
    
    async def handle_command_error(
        self, 
        command: str, 
        stdout: str, 
        stderr: str, 
        return_code: int,
        context: str = ""
    ) -> Dict[str, Any]:
        """处理命令错误"""
        
        # 分析错误
        error_analysis = ErrorAnalyzer.analyze_error(stderr, stdout)
        
        # 创建错误上下文
        error_context = ErrorContext(
            command=command,
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
            error_analysis=error_analysis,
            attempt=1,
            max_attempts=self.max_auto_fix_attempts
        )
        
        # 记录错误
        self.error_history.append({
            "command": command,
            "error_analysis": error_analysis,
            "context": context,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # 生成修复建议
        fix_suggestion = await AutoFixer.generate_fix_suggestion(
            error_analysis, 
            f"Command: {command}\nError: {stderr}\nContext: {context}"
        )
        
        # 尝试自动修复
        if error_analysis["confidence"] > 0.5:
            fix_result = await self._attempt_auto_fix(error_context, fix_suggestion)
            return {
                "error_analysis": error_analysis,
                "fix_suggestion": fix_suggestion,
                "auto_fix_attempted": True,
                "auto_fix_result": fix_result
            }
        else:
            return {
                "error_analysis": error_analysis,
                "fix_suggestion": fix_suggestion,
                "auto_fix_attempted": False,
                "auto_fix_result": None
            }
    
    async def _attempt_auto_fix(
        self, 
        error_context: ErrorContext, 
        fix_suggestion: str
    ) -> Dict[str, Any]:
        """尝试自动修复"""
        
        error_type = error_context.error_analysis["error_type"]
        
        # 根据错误类型执行相应的修复操作
        if error_type.value == "module_not_found":
            return await self._fix_missing_module(error_context)
        elif error_type.value == "command_not_found":
            return await self._fix_missing_command(error_context)
        elif error_type.value == "permission_denied":
            return await self._fix_permission_issue(error_context)
        elif error_type.value == "connection_error":
            return await self._fix_connection_issue(error_context)
        else:
            return {
                "success": False,
                "reason": f"Unsupported error type: {error_type.value}",
                "suggestion": fix_suggestion
            }
    
    async def _fix_missing_module(self, error_context: ErrorContext) -> Dict[str, Any]:
        """修复缺失模块"""
        missing_module = error_context.error_analysis.get("missing_module")
        if not missing_module:
            return {"success": False, "reason": "No missing module identified"}
        
        # 尝试安装模块
        install_command = f"pip install {missing_module}"
        logging.info(f"Attempting to install missing module: {install_command}")
        
        result = await self.terminal_tool.execute(command=install_command)
        
        if result.success:
            # 重新尝试原始命令
            retry_result = await self.terminal_tool.execute(command=error_context.command)
            return {
                "success": retry_result.success,
                "install_success": True,
                "retry_success": retry_result.success,
                "install_command": install_command,
                "retry_output": retry_result.data if retry_result.success else retry_result.error
            }
        else:
            return {
                "success": False,
                "install_success": False,
                "install_error": result.error,
                "install_command": install_command
            }
    
    async def _fix_missing_command(self, error_context: ErrorContext) -> Dict[str, Any]:
        """修复缺失命令"""
        missing_command = error_context.error_analysis.get("missing_command")
        if not missing_command:
            return {"success": False, "reason": "No missing command identified"}
        
        # 尝试使用包管理器安装命令
        install_commands = [
            f"sudo apt install {missing_command}",  # Ubuntu/Debian
            f"brew install {missing_command}",      # macOS
            f"yum install {missing_command}",       # CentOS/RHEL
        ]
        
        for install_command in install_commands:
            logging.info(f"Attempting to install missing command: {install_command}")
            result = await self.terminal_tool.execute(command=install_command)
            
            if result.success:
                # 重新尝试原始命令
                retry_result = await self.terminal_tool.execute(command=error_context.command)
                return {
                    "success": retry_result.success,
                    "install_success": True,
                    "retry_success": retry_result.success,
                    "install_command": install_command,
                    "retry_output": retry_result.data if retry_result.success else retry_result.error
                }
        
        return {
            "success": False,
            "install_success": False,
            "tried_commands": install_commands,
            "reason": "All package manager installation attempts failed"
        }
    
    async def _fix_permission_issue(self, error_context: ErrorContext) -> Dict[str, Any]:
        """修复权限问题"""
        # 尝试使用sudo重新执行命令
        sudo_command = f"sudo {error_context.command}"
        logging.info(f"Attempting to fix permission issue: {sudo_command}")
        
        result = await self.terminal_tool.execute(command=sudo_command)
        
        return {
            "success": result.success,
            "sudo_attempted": True,
            "sudo_command": sudo_command,
            "result": result.data if result.success else result.error
        }
    
    async def _fix_connection_issue(self, error_context: ErrorContext) -> Dict[str, Any]:
        """修复连接问题"""
        # 对于连接问题，通常需要手动干预
        return {
            "success": False,
            "reason": "Connection issues require manual intervention",
            "suggestions": [
                "检查网络连接",
                "检查服务器状态",
                "检查防火墙设置",
                "检查DNS配置"
            ]
        }
    
    async def execute_with_auto_fix(
        self, 
        command: str, 
        max_attempts: int = 3,
        context: str = ""
    ) -> Dict[str, Any]:
        """执行命令并自动修复错误"""
        
        for attempt in range(max_attempts):
            logging.info(f"Executing command (attempt {attempt + 1}): {command}")
            
            # 执行命令
            result = await self.terminal_tool.execute(command=command)
            
            if result.success:
                return {
                    "success": True,
                    "attempts": attempt + 1,
                    "output": result.data,
                    "auto_fixes_applied": len(self.fix_history)
                }
            
            # 处理错误
            error_data = result.data
            if error_data and "error_analysis" in error_data:
                error_handler_result = await self.handle_command_error(
                    command=command,
                    stdout=error_data.get("stdout", ""),
                    stderr=error_data.get("stderr", ""),
                    return_code=error_data.get("return_code", -1),
                    context=context
                )
                
                # 如果自动修复成功，继续下一次尝试
                if (error_handler_result.get("auto_fix_attempted") and 
                    error_handler_result.get("auto_fix_result", {}).get("success")):
                    
                    self.fix_history.append({
                        "command": command,
                        "fix_result": error_handler_result,
                        "attempt": attempt + 1
                    })
                    
                    logging.info(f"Auto-fix applied successfully, retrying command")
                    continue
            
            # 如果所有尝试都失败
            if attempt == max_attempts - 1:
                return {
                    "success": False,
                    "attempts": max_attempts,
                    "final_error": result.error,
                    "error_analysis": error_data.get("error_analysis") if error_data else None,
                    "auto_fixes_applied": len(self.fix_history)
                }
        
        return {
            "success": False,
            "attempts": max_attempts,
            "reason": "Max attempts reached"
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        return {
            "total_errors": len(self.error_history),
            "total_fixes": len(self.fix_history),
            "successful_fixes": len([f for f in self.fix_history if f.get("fix_result", {}).get("success")]),
            "error_types": list(set([e["error_analysis"]["error_type"].value for e in self.error_history]))
        }
    
    def clear_history(self):
        """清除历史记录"""
        self.error_history.clear()
        self.fix_history.clear()
        self.terminal_tool.clear_error_history() 