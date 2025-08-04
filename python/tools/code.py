"""
Code Execution Tool for Aegis Agent
Provides safe code execution capabilities for agents.
"""

import asyncio
import subprocess
import tempfile
import os
import logging
import json
import ast
from typing import Dict, List, Optional, Any
from pathlib import Path
import sys

try:
    from .base import BaseTool, ToolResult
except ImportError:
    from python.tools.base import BaseTool, ToolResult


class CodeExecutionTool(BaseTool):
    """
    Tool for executing code safely.
    
    Features:
    - Python code execution in sandbox
    - File creation and manipulation
    - Code analysis and validation
    - Safe execution environment
    """
    
    def __init__(self):
        super().__init__("code", "Execute Python code safely (also known as codeexecution)")
        self.safe_modules = {
            "os", "sys", "json", "datetime", "math", "random", "re",
            "pathlib", "tempfile", "shutil", "glob", "fnmatch"
        }
        self.dangerous_modules = {
            "subprocess", "eval", "exec", "compile", "__import__"
        }
        self.execution_history: List[Dict] = []
        
        # Load timeout from environment
        try:
            from ..utils.env_manager import env_manager
            tools_config = env_manager.get_tools_config()
            self.max_execution_time = tools_config.get("code_timeout", 30)
        except ImportError:
            # Fallback to default value
            self.max_execution_time = 30
        self.max_output_size = 10000
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute Python code safely."""
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        timeout = kwargs.get("timeout", self.max_execution_time)
        capture_output = kwargs.get("capture_output", True)
        
        if not code:
            return ToolResult(
                success=False,
                data=None,
                error="No code provided",
                metadata={"tool_type": "code"}
            )
        
        if language.lower() != "python":
            return ToolResult(
                success=False,
                data=None,
                error=f"Language '{language}' not supported. Only Python is supported.",
                metadata={"tool_type": "code"}
            )
        
        try:
            # 修复代码中的Unicode字符问题
            fixed_code = self._fix_unicode_characters(code)
            if fixed_code != code:
                logging.info("修复了代码中的Unicode字符问题")
                code = fixed_code
            
            # Validate code safety
            if not self._is_safe_code(code):
                return ToolResult(
                    success=False,
                    data=None,
                    error="Code contains potentially dangerous operations",
                    metadata={"tool_type": "code", "blocked": True}
                )
            
            # Execute the code
            result = await self._execute_python_code(code, timeout, capture_output)
            
            # Store in history
            self.execution_history.append({
                "code": code,
                "timestamp": asyncio.get_event_loop().time(),
                "success": result.success,
                "output": result.data if result.success else result.error
            })
            
            return result
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Code execution failed: {str(e)}",
                metadata={"tool_type": "code"}
            )
    
    def _is_safe_code(self, code: str) -> bool:
        """Check if the code is safe to execute."""
        try:
            # Parse the code to analyze it
            tree = ast.parse(code)
            
            # Check for dangerous operations
            for node in ast.walk(tree):
                # Check for function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in self.dangerous_modules:
                            return False
                
                # Check for imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.dangerous_modules:
                            return False
                
                if isinstance(node, ast.ImportFrom):
                    if node.module in self.dangerous_modules:
                        return False
                
                # Check for eval/exec calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["eval", "exec", "compile"]:
                            return False
            
            return True
            
        except SyntaxError:
            return False
        except Exception:
            return False
    
    async def _execute_python_code(self, code: str, timeout: int, capture_output: bool) -> ToolResult:
        """Execute Python code in a safe environment."""
        start_time = asyncio.get_event_loop().time()
        
        # Create a temporary file for the code with UTF-8 encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            # Add encoding declaration for Python files with non-ASCII content
            if any(ord(char) > 127 for char in code):
                f.write("# -*- coding: utf-8 -*-\n")
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute the code using subprocess.run instead of asyncio.create_subprocess_exec
            # This is more compatible with Windows
            import subprocess
            import locale
            
            # 检测系统编码
            system_encoding = locale.getpreferredencoding()
            logging.info(f"System encoding: {system_encoding}")
            
            # 设置环境变量以确保正确的编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            if capture_output:
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='replace',
                    env=env
                )
                stdout_str = result.stdout
                stderr_str = result.stderr
                return_code = result.returncode
            else:
                result = subprocess.run(
                    [sys.executable, temp_file],
                    timeout=timeout,
                    encoding='utf-8',
                    errors='replace',
                    env=env
                )
                stdout_str = ""
                stderr_str = ""
                return_code = result.returncode
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # 处理输出编码问题
            if stdout_str:
                # 尝试修复编码问题
                try:
                    # 如果输出包含乱码，尝试重新编码
                    if 'ͼ' in stdout_str or 'Ƭ' in stdout_str:
                        logging.warning("检测到可能的编码问题，尝试修复...")
                        # 尝试不同的编码方式
                        if hasattr(result, '_stdout') and result._stdout:
                            try:
                                stdout_str = result._stdout.decode('utf-8', errors='replace')
                            except:
                                stdout_str = result._stdout.decode('gbk', errors='replace')
                except Exception as e:
                    logging.error(f"编码修复失败: {e}")
            
            if stderr_str:
                # 处理错误输出的编码问题
                try:
                    if 'ͼ' in stderr_str or 'Ƭ' in stderr_str:
                        logging.warning("检测到错误输出中的编码问题，尝试修复...")
                        if hasattr(result, '_stderr') and result._stderr:
                            try:
                                stderr_str = result._stderr.decode('utf-8', errors='replace')
                            except:
                                stderr_str = result._stderr.decode('gbk', errors='replace')
                except Exception as e:
                    logging.error(f"错误输出编码修复失败: {e}")
            
            # Limit output size
            if stdout_str and len(stdout_str) > self.max_output_size:
                stdout_str = stdout_str[:self.max_output_size] + "... (truncated)"
            
            if stderr_str and len(stderr_str) > self.max_output_size:
                stderr_str = stderr_str[:self.max_output_size] + "... (truncated)"
            
            if return_code == 0:
                return ToolResult(
                    success=True,
                    data={
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                        "return_code": return_code,
                        "code": code
                    },
                    execution_time=execution_time,
                    metadata={"tool_type": "code"}
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Code execution failed with return code {return_code}: {stderr_str}",
                    execution_time=execution_time,
                    metadata={"tool_type": "code", "return_code": return_code}
                )
                
        except subprocess.TimeoutExpired:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error=f"Code execution timed out after {timeout} seconds",
                execution_time=timeout,
                metadata={"tool_type": "code", "timeout": True}
            )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Code execution error: {str(e)}"
            if not str(e):
                error_msg = f"Code execution error: Unknown exception of type {type(e).__name__}"
            
            # 添加详细的错误信息
            import traceback
            error_details = traceback.format_exc()
            error_msg += f"\nDetails: {error_details}"
            
            return ToolResult(
                success=False,
                data=None,
                error=error_msg,
                execution_time=execution_time,
                metadata={"tool_type": "code", "exception_type": type(e).__name__}
            )
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass
    
    async def create_file(self, filename: str, content: str, file_type: str = "text") -> ToolResult:
        """Create a file with the specified content."""
        try:
            # Validate filename
            if not self._is_safe_filename(filename):
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Filename '{filename}' is not safe",
                    metadata={"tool_type": "code"}
                )
            
            # Create the file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ToolResult(
                success=True,
                data={
                    "filename": filename,
                    "size": len(content),
                    "file_type": file_type
                },
                metadata={"tool_type": "code", "action": "file_created"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to create file: {str(e)}",
                metadata={"tool_type": "code"}
            )
    
    async def read_file(self, filename: str) -> ToolResult:
        """Read the contents of a file."""
        try:
            if not os.path.exists(filename):
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"File '{filename}' does not exist",
                    metadata={"tool_type": "code"}
                )
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                data={
                    "filename": filename,
                    "content": content,
                    "size": len(content)
                },
                metadata={"tool_type": "code", "action": "file_read"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to read file: {str(e)}",
                metadata={"tool_type": "code"}
            )
    
    def _is_safe_filename(self, filename: str) -> bool:
        """Check if a filename is safe to use."""
        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        
        # Check for dangerous extensions
        dangerous_extensions = {".exe", ".bat", ".cmd", ".com", ".pif", ".scr"}
        if any(filename.lower().endswith(ext) for ext in dangerous_extensions):
            return False
        
        return True
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent code execution history."""
        return self.execution_history[-limit:] if self.execution_history else []
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history.clear()
        logging.info("Code execution history cleared")
    
    def get_safe_modules(self) -> List[str]:
        """Get list of safe modules."""
        return list(self.safe_modules)
    
    def get_dangerous_modules(self) -> List[str]:
        """Get list of dangerous modules."""
        return list(self.dangerous_modules)
    
    def _fix_unicode_characters(self, code: str) -> str:
        """修复代码中的Unicode字符问题"""
        if not code:
            return code
        
        # 检测并修复常见的Unicode字符问题
        unicode_fixes = [
            (chr(0xFF0C), ','),  # 全角逗号 -> 半角逗号
            (chr(0xFF1A), ':'),  # 全角冒号 -> 半角冒号
            (chr(0xFF08), '('),  # 全角左括号 -> 半角左括号
            (chr(0xFF09), ')'),  # 全角右括号 -> 半角右括号
            (chr(0xFF3B), '['),  # 全角左方括号 -> 半角左方括号
            (chr(0xFF3D), ']'),  # 全角右方括号 -> 半角右方括号
            (chr(0xFF02), '"'),  # 全角双引号 -> 半角双引号
            (chr(0xFF07), "'"),  # 全角单引号 -> 半角单引号
            (chr(0x2026), '...'), # 省略号 -> 三个点
            (chr(0x2014), '-'),  # 全角破折号 -> 半角连字符
            (chr(0x2013), '-'),  # 全角连字符 -> 半角连字符
        ]
        
        fixed_code = code
        for unicode_char, ascii_char in unicode_fixes:
            fixed_code = fixed_code.replace(unicode_char, ascii_char)
        
        # 如果检测到Unicode字符问题，记录日志
        if any(unicode_char in code for unicode_char, _ in unicode_fixes):
            logging.warning(f"检测到Unicode字符问题，已尝试修复代码")
        
        return fixed_code 