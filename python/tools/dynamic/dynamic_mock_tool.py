"""
Mock Tool for Testing Dynamic Tool Discovery
A mock tool that simulates various operations for testing purposes.
"""

import asyncio
import logging
import time
import random
from typing import Dict, Any, List

import sys
from pathlib import Path
# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from python.tools.base import BaseTool, ToolResult


class MockTool(BaseTool):
    """
    A mock tool for testing dynamic tool discovery and execution.
    
    This tool simulates various operations and can be used to test
    the dynamic loading system with different scenarios.
    """
    
    def __init__(self):
        super().__init__("mock_tool", "A mock tool for testing dynamic tool discovery")
        self.operation_count = 0
        self.simulated_delay = 0.1  # seconds
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the mock tool.
        
        Args:
            operation: Type of operation to simulate ("success", "error", "delay", "random")
            delay: Simulated delay in seconds (optional)
            data: Data to return (optional)
            error_probability: Probability of error (0.0 to 1.0, optional)
            
        Returns:
            ToolResult with mock data
        """
        try:
            operation = kwargs.get("operation", "success")
            delay = kwargs.get("delay", self.simulated_delay)
            data = kwargs.get("data", {})
            error_probability = kwargs.get("error_probability", 0.0)
            
            # Increment operation count
            self.operation_count += 1
            
            # Simulate delay
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Simulate random error
            if random.random() < error_probability:
                raise Exception("Simulated random error")
            
            # Handle different operations
            if operation == "success":
                result_data = {
                    "operation": "success",
                    "message": "Mock operation completed successfully",
                    "data": data,
                    "operation_count": self.operation_count,
                    "timestamp": self.created_at.isoformat()
                }
                
            elif operation == "error":
                raise Exception("Simulated error operation")
                
            elif operation == "delay":
                result_data = {
                    "operation": "delay",
                    "message": f"Mock operation completed after {delay}s delay",
                    "delay": delay,
                    "operation_count": self.operation_count,
                    "timestamp": self.created_at.isoformat()
                }
                
            elif operation == "random":
                random_data = {
                    "number": random.randint(1, 100),
                    "float": random.uniform(0, 1),
                    "choice": random.choice(["apple", "banana", "cherry", "date"]),
                    "list": [random.randint(1, 10) for _ in range(5)]
                }
                result_data = {
                    "operation": "random",
                    "message": "Mock random operation completed",
                    "random_data": random_data,
                    "operation_count": self.operation_count,
                    "timestamp": self.created_at.isoformat()
                }
                
            else:
                result_data = {
                    "operation": "unknown",
                    "message": f"Unknown operation: {operation}",
                    "available_operations": ["success", "error", "delay", "random"],
                    "operation_count": self.operation_count,
                    "timestamp": self.created_at.isoformat()
                }
            
            logging.info(f"MockTool executed: {operation} operation")
            
            return ToolResult(
                success=True,
                data=result_data,
                metadata={
                    "tool_type": "mock_tool",
                    "operation": operation,
                    "operation_count": self.operation_count
                }
            )
            
        except Exception as e:
            logging.error(f"MockTool execution failed: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                metadata={
                    "tool_type": "mock_tool",
                    "operation": kwargs.get("operation", "unknown")
                }
            )
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        info = super().get_info()
        info.update({
            "operation_count": self.operation_count,
            "available_operations": ["success", "error", "delay", "random"],
            "simulated_delay": self.simulated_delay
        })
        return info
    
    def set_simulated_delay(self, delay: float):
        """Set the simulated delay for operations."""
        self.simulated_delay = delay
        logging.info(f"MockTool delay set to {delay}s")
    
    def reset_counters(self):
        """Reset operation counters."""
        self.operation_count = 0
        logging.info("MockTool counters reset") 