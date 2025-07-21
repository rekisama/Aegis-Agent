"""
Terminal Tool for Agent Zero
Allows agents to execute terminal commands safely.
"""

import asyncio
import subprocess
import logging
import os
import tempfile
from typing import Dict, List, Optional
from pathlib import Path

from .base import BaseTool, ToolResult


class TerminalTool(BaseTool):
    """
    Tool for executing terminal commands.
    
    Features:
    - Safe command execution
    - Working directory management
    - Output capture and parsing
    - Command history tracking
    """
    
    def __init__(self):
        super().__init__("terminal", "Execute terminal commands safely")
        self.working_directory = os.getcwd()
        self.command_history: List[Dict] = []
        
        # Load timeout from environment
        from ..utils.env_manager import env_manager
        tools_config = env_manager.get_tools_config()
        self.timeout = tools_config.get("terminal_timeout", 30)
        
        self.safe_commands = {
            "ls", "dir", "pwd", "cd", "echo", "cat", "head", "tail",
            "grep", "find", "which", "where", "type", "help", "man",
            "python", "pip", "git", "npm", "node", "curl", "wget"
        }
        self.dangerous_commands = {
            "rm", "del", "format", "fdisk", "dd", "shutdown", "reboot",
            "kill", "killall", "sudo", "su", "chmod", "chown"
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute a terminal command."""
        command = kwargs.get("command", "")
        working_dir = kwargs.get("working_dir", self.working_directory)
        timeout = kwargs.get("timeout", 30)
        capture_output = kwargs.get("capture_output", True)
        
        if not command:
            return ToolResult(
                success=False,
                data=None,
                error="No command provided",
                metadata={"tool_type": "terminal"}
            )
        
        # Check if command is safe
        if not self._is_safe_command(command):
            return ToolResult(
                success=False,
                data=None,
                error=f"Command '{command}' is not allowed for security reasons",
                metadata={"tool_type": "terminal", "blocked": True}
            )
        
        try:
            # Execute the command
            result = await self._execute_command(command, working_dir, timeout, capture_output)
            
            # Store in history
            self.command_history.append({
                "command": command,
                "working_dir": working_dir,
                "timestamp": asyncio.get_event_loop().time(),
                "success": result.success,
                "output": result.data if result.success else result.error
            })
            
            return result
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Command execution failed: {str(e)}",
                metadata={"tool_type": "terminal"}
            )
    
    async def _execute_command(self, command: str, working_dir: str, 
                             timeout: int, capture_output: bool) -> ToolResult:
        """Execute a command with the given parameters."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create process
            if capture_output:
                process = await asyncio.create_subprocess_exec(
                    *command.split(),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=working_dir
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *command.split(),
                    cwd=working_dir
                )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Command timed out after {timeout} seconds",
                    execution_time=timeout,
                    metadata={"tool_type": "terminal", "timeout": True}
                )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if process.returncode == 0:
                return ToolResult(
                    success=True,
                    data={
                        "stdout": stdout.decode() if stdout else "",
                        "stderr": stderr.decode() if stderr else "",
                        "return_code": process.returncode,
                        "command": command,
                        "working_dir": working_dir
                    },
                    execution_time=execution_time,
                    metadata={"tool_type": "terminal"}
                )
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Command failed with return code {process.returncode}: {stderr.decode() if stderr else 'Unknown error'}",
                    execution_time=execution_time,
                    metadata={"tool_type": "terminal", "return_code": process.returncode}
                )
                
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data=None,
                error=f"Command execution error: {str(e)}",
                execution_time=execution_time,
                metadata={"tool_type": "terminal"}
            )
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if a command is safe to execute."""
        # Split command and get the first part (the actual command)
        parts = command.split()
        if not parts:
            return False
        
        cmd = parts[0].lower()
        
        # Check if it's in the dangerous list
        if cmd in self.dangerous_commands:
            return False
        
        # Check if it's in the safe list
        if cmd in self.safe_commands:
            return True
        
        # Allow some commands with specific patterns
        safe_patterns = [
            "python -c", "python -m", "pip install", "pip list",
            "git status", "git log", "git show", "git diff",
            "npm list", "npm view", "node -e"
        ]
        
        for pattern in safe_patterns:
            if command.lower().startswith(pattern):
                return True
        
        # By default, be conservative
        return False
    
    def change_working_directory(self, new_dir: str) -> bool:
        """Change the working directory for future commands."""
        try:
            if os.path.exists(new_dir) and os.path.isdir(new_dir):
                self.working_directory = os.path.abspath(new_dir)
                logging.info(f"Changed working directory to: {self.working_directory}")
                return True
            else:
                logging.error(f"Directory does not exist: {new_dir}")
                return False
        except Exception as e:
            logging.error(f"Failed to change working directory: {e}")
            return False
    
    def get_working_directory(self) -> str:
        """Get the current working directory."""
        return self.working_directory
    
    def get_command_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history."""
        return self.command_history[-limit:] if self.command_history else []
    
    def clear_history(self):
        """Clear command history."""
        self.command_history.clear()
        logging.info("Terminal command history cleared") 