#!/usr/bin/env python3
"""
Basic tests for Aegis Agent
Tests core functionality of the agent system.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from python.agent.core import Agent, AgentConfig
from python.tools.base import BaseTool, ToolResult
from python.memory.memory_manager import MemoryManager


class TestAgent:
    """Test cases for the Agent class."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        config = AgentConfig(
            name="Test Agent",
            memory_enabled=True,
            hierarchical_enabled=True,
            tools_enabled=True
        )
        return Agent(config)
    
    def test_agent_creation(self, agent):
        """Test that agent can be created successfully."""
        assert agent is not None
        assert agent.config.name == "Test Agent"
        assert agent.agent_id is not None
        assert len(agent.agent_id) > 0
    
    def test_agent_status(self, agent):
        """Test agent status reporting."""
        status = agent.get_status()
        assert "name" in status
        assert "agent_id" in status
        assert "task_count" in status
        assert status["name"] == "Test Agent"
        assert status["task_count"] == 0
    
    def test_tools_initialization(self, agent):
        """Test that default tools are initialized."""
        assert "terminal" in agent.tools
        assert "search" in agent.tools
        assert "code" in agent.tools
        assert len(agent.tools) >= 3
    
    def test_subordinate_creation(self, agent):
        """Test creating subordinate agents."""
        subordinate = agent.create_subordinate("Helper Agent")
        assert subordinate is not None
        assert subordinate.config.name == "Helper Agent"
        assert subordinate.superior == agent
        assert len(agent.subordinates) == 1
    
    @pytest.mark.asyncio
    async def test_task_execution(self, agent):
        """Test basic task execution."""
        result = await agent.execute_task("Test task")
        assert result is not None
        assert "status" in result
        assert result["status"] == "completed"
        assert agent.task_count == 1


class TestMemoryManager:
    """Test cases for the MemoryManager class."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create a test memory manager."""
        config = AgentConfig()
        return MemoryManager(config)
    
    def test_memory_creation(self, memory_manager):
        """Test that memory manager can be created."""
        assert memory_manager is not None
        assert memory_manager.config is not None
    
    def test_memory_stats(self, memory_manager):
        """Test memory statistics."""
        stats = memory_manager.get_memory_stats()
        assert "task_memories" in stats
        assert "solution_patterns" in stats
        assert "knowledge_entries" in stats
        assert "memory_enabled" in stats
    
    @pytest.mark.asyncio
    async def test_knowledge_storage(self, memory_manager):
        """Test storing and retrieving knowledge."""
        # Store knowledge
        await memory_manager.store_knowledge(
            "test_topic",
            "Test knowledge content",
            source="test",
            confidence=0.8
        )
        
        # Retrieve knowledge
        knowledge = await memory_manager.get_knowledge("test_topic")
        assert knowledge is not None
        assert knowledge["content"] == "Test knowledge content"
        assert knowledge["source"] == "test"
        assert knowledge["confidence"] == 0.8
    
    @pytest.mark.asyncio
    async def test_solution_pattern_storage(self, memory_manager):
        """Test storing and retrieving solution patterns."""
        # Store pattern
        await memory_manager.store_solution_pattern(
            "test_pattern",
            "Test pattern description",
            ["terminal", "code"],
            0.9
        )
        
        # Retrieve patterns
        patterns = await memory_manager.get_solution_patterns()
        assert len(patterns) >= 1
        
        # Find our pattern
        test_pattern = None
        for pattern in patterns:
            if pattern["pattern_name"] == "test_pattern":
                test_pattern = pattern
                break
        
        assert test_pattern is not None
        assert test_pattern["pattern_description"] == "Test pattern description"
        assert test_pattern["tools_used"] == ["terminal", "code"]
        assert test_pattern["success_rate"] == 0.9


class TestTools:
    """Test cases for the tool system."""
    
    def test_tool_result_creation(self):
        """Test ToolResult creation."""
        result = ToolResult(
            success=True,
            data={"test": "data"},
            execution_time=1.5
        )
        assert result.success is True
        assert result.data["test"] == "data"
        assert result.execution_time == 1.5
        assert result.error is None
    
    def test_base_tool_creation(self):
        """Test creating a basic tool."""
        class TestTool(BaseTool):
            async def execute(self, **kwargs):
                return ToolResult(
                    success=True,
                    data={"message": "Test tool executed"},
                    metadata={"tool_type": "test"}
                )
        
        tool = TestTool("test_tool", "A test tool")
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert tool.usage_count == 0
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test tool execution."""
        class TestTool(BaseTool):
            async def execute(self, **kwargs):
                self._update_usage_stats(True)
                return ToolResult(
                    success=True,
                    data={"message": "Test tool executed"},
                    metadata={"tool_type": "test"}
                )
        
        tool = TestTool("test_tool", "A test tool")
        result = await tool.execute(test_param="value")
        
        assert result.success is True
        assert result.data["message"] == "Test tool executed"
        assert tool.usage_count == 1
        assert tool.success_count == 1


class TestConfiguration:
    """Test cases for configuration management."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = AgentConfig()
        assert config.name == "Aegis Agent"
        assert config.memory_enabled is True
        assert config.hierarchical_enabled is True
        assert config.tools_enabled is True
    
    def test_custom_config(self):
        """Test custom configuration creation."""
        config = AgentConfig(
            name="Custom Agent",
            memory_enabled=False,
            hierarchical_enabled=False,
            tools_enabled=False
        )
        assert config.name == "Custom Agent"
        assert config.memory_enabled is False
        assert config.hierarchical_enabled is False
        assert config.tools_enabled is False


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 