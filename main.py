#!/usr/bin/env python3
"""
Agent Zero - Main Entry Point
A general-purpose personal assistant with persistent memory and multi-agent cooperation.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from python.agent.core import Agent, AgentConfig
from python.tools.base import ToolBuilder
from python.utils.config import load_config


class AegisAgentCLI:
    """
    Command-line interface for Agent Zero.
    """
    
    def __init__(self):
        self.agent = None
        self.config = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agent_zero.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    async def initialize_agent(self, config_path: str = None):
        """Initialize the main agent."""
        try:
            # Load environment configuration
            from python.utils.env_manager import env_manager
            
            # Print configuration summary
            env_manager.print_config_summary()
            
            # Validate required environment variables
            validation = env_manager.validate_required_vars()
            if not all(validation.values()):
                print("❌ Some required environment variables are missing!")
                return False
            
            # Create the main agent (will use environment config)
            self.agent = Agent()
            
            logging.info(f"Aegis Agent initialized: {self.agent.config.name}")
            print(f"🛡️  Aegis Agent ({self.agent.config.name}) is ready!")
            print(f"📊 Using model: {self.agent.config.model}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize agent: {e}")
            print(f"❌ Failed to initialize Aegis Agent: {e}")
            return False
    
    async def run_interactive_mode(self):
        """Run the agent in interactive mode."""
        if not self.agent:
            print("❌ Agent not initialized. Please initialize first.")
            return
        
        print("\n" + "="*50)
        print("🛡️  Aegis Agent Interactive Mode")
        print("="*50)
        print("Commands:")
        print("  task <description>  - Execute a task")
        print("  status              - Show agent status")
        print("  memory              - Show memory statistics")
        print("  tools               - List available tools")
        print("  create <name>       - Create a subordinate agent")
        print("  help                - Show this help")
        print("  quit                - Exit")
        print("="*50)
        
        while True:
            try:
                user_input = input("\n🛡️  Aegis Agent > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "quit":
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == "help":
                    self.show_help()
                
                elif user_input.lower() == "status":
                    await self.show_status()
                
                elif user_input.lower() == "memory":
                    await self.show_memory_stats()
                
                elif user_input.lower() == "tools":
                    await self.show_tools()
                
                elif user_input.lower().startswith("create "):
                    agent_name = user_input[7:].strip()
                    await self.create_subordinate(agent_name)
                
                elif user_input.lower().startswith("task "):
                    task_description = user_input[5:].strip()
                    await self.execute_task(task_description)
                
                else:
                    # Treat as a task
                    await self.execute_task(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logging.error(f"Error in interactive mode: {e}")
                print(f"❌ Error: {e}")
    
    async def execute_task(self, task_description: str):
        """Execute a task."""
        if not self.agent:
            print("❌ Agent not initialized.")
            return
        
        print(f"🔄 Executing task: {task_description}")
        
        try:
            result = await self.agent.execute_task(task_description)
            
            if result.get("status") == "completed":
                print("✅ Task completed successfully!")
                if "result" in result:
                    print(f"📋 Result: {result['result']}")
            else:
                print("❌ Task failed!")
                if "error" in result:
                    print(f"💥 Error: {result['error']}")
                    
        except Exception as e:
            logging.error(f"Task execution failed: {e}")
            print(f"❌ Task execution failed: {e}")
    
    async def show_status(self):
        """Show agent status."""
        if not self.agent:
            print("❌ Agent not initialized.")
            return
        
        status = self.agent.get_status()
        
        print("\n📊 Agent Status:")
        print(f"  Name: {status['name']}")
        print(f"  ID: {status['agent_id']}")
        print(f"  Tasks Completed: {status['task_count']}")
        print(f"  Subordinates: {status['subordinates_count']}")
        print(f"  Tools Available: {status['tools_count']}")
        print(f"  Memory Enabled: {status['memory_enabled']}")
        print(f"  Created: {status['created_at']}")
        
        if self.agent.current_task:
            print(f"  Current Task: {self.agent.current_task['description']}")
    
    async def show_memory_stats(self):
        """Show memory statistics."""
        if not self.agent:
            print("❌ Agent not initialized.")
            return
        
        stats = self.agent.memory.get_memory_stats()
        
        print("\n🧠 Memory Statistics:")
        print(f"  Task Memories: {stats.get('task_memories', 0)}")
        print(f"  Solution Patterns: {stats.get('solution_patterns', 0)}")
        print(f"  Knowledge Entries: {stats.get('knowledge_entries', 0)}")
        print(f"  Database Size: {stats.get('database_size_bytes', 0)} bytes")
        print(f"  Memory Enabled: {stats.get('memory_enabled', False)}")
    
    async def show_tools(self):
        """Show available tools."""
        if not self.agent:
            print("❌ Agent not initialized.")
            return
        
        print("\n🛠️  Available Tools:")
        for tool_name, tool in self.agent.tools.items():
            info = tool.get_info()
            print(f"  📦 {tool_name}: {info['description']}")
            print(f"      Usage: {info['usage_count']}, Success Rate: {info['success_rate']:.2%}")
    
    async def create_subordinate(self, name: str):
        """Create a subordinate agent."""
        if not self.agent:
            print("❌ Agent not initialized.")
            return
        
        try:
            subordinate = self.agent.create_subordinate(name)
            print(f"✅ Created subordinate agent: {name}")
            print(f"   ID: {subordinate.agent_id}")
            
        except Exception as e:
            logging.error(f"Failed to create subordinate: {e}")
            print(f"❌ Failed to create subordinate: {e}")
    
    def show_help(self):
        """Show help information."""
        print("\n📖 Aegis Agent Help:")
        print("  task <description>  - Execute a task")
        print("  status              - Show agent status")
        print("  memory              - Show memory statistics")
        print("  tools               - List available tools")
        print("  create <name>       - Create a subordinate agent")
        print("  help                - Show this help")
        print("  quit                - Exit")
        print("\n💡 You can also just type your task directly!")


async def main():
    """Main entry point."""
    cli = AegisAgentCLI()
    
    # Initialize agent
    success = await cli.initialize_agent()
    if not success:
        return
    
    # Run interactive mode
    await cli.run_interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"❌ Application error: {e}")
        sys.exit(1) 