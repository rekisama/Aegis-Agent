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
                logging.warning(f"Command failed with return code {return_code}: {command}")
                return ToolResult(
                    success=False,
                    data=result_data,
                    error=f"Command failed with return code {return_code}",
                    metadata={
                        "tool_type": "terminal",
                        "command": command,
                        "return_code": return_code
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
            logging.error(f"Command execution failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Command execution failed: {str(e)}",
                metadata={"tool_type": "terminal"}
            )
