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
            
            if capture_output:
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8'
                )
                stdout_str = result.stdout
                stderr_str = result.stderr
                return_code = result.returncode
            else:
                result = subprocess.run(
                    [sys.executable, temp_file],
                    timeout=timeout,
                    encoding='utf-8'
                )
                stdout_str = ""
                stderr_str = ""
                return_code = result.returncode
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Limit output size
            if len(stdout_str) > self.max_output_size:
                stdout_str = stdout_str[:self.max_output_size] + "... (truncated)"
            
            if len(stderr_str) > self.max_output_size:
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