"""
Environment Variable Management for Aegis Agent
Handles loading and managing environment variables using python-dotenv.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class EnvManager:
    """
    Manages environment variables for Aegis Agent.
    
    Features:
    - Load environment variables from .env file
    - Provide default values
    - Type conversion for different variable types
    - Validation of required variables
    """
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.loaded = False
        self._load_env()
    
    def _load_env(self):
        """Load environment variables from .env file."""
        env_path = Path(self.env_file)
        
        if env_path.exists():
            load_dotenv(env_path)
            self.loaded = True
        else:
            # Create .env file from example if it doesn't exist
            self._create_env_from_example()
            load_dotenv(env_path)
            self.loaded = True
    
    def _create_env_from_example(self):
        """Create .env file from env.example if it doesn't exist."""
        example_path = Path("env.example")
        env_path = Path(self.env_file)
        
        if example_path.exists() and not env_path.exists():
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Created {self.env_file} from env.example")
    
    def get(self, key: str, default: Any = None, var_type: str = "str") -> Any:
        """
        Get environment variable with type conversion.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            var_type: Type conversion ('str', 'int', 'float', 'bool')
            
        Returns:
            Converted value
        """
        value = os.getenv(key, default)
        
        if value is None:
            return default
        
        # Type conversion
        if var_type == "int":
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        elif var_type == "float":
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        elif var_type == "bool":
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        else:
            return str(value)
    
    def get_deepseek_config(self) -> Dict[str, Any]:
        """Get DeepSeek API configuration."""
        return {
            "api_key": self.get("DEEPSEEK_API_KEY"),
            "api_base_url": self.get("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com/v1"),
            "model": self.get("DEEPSEEK_MODEL", "deepseek-chat")
        }
    
    def get_tavily_config(self) -> Dict[str, Any]:
        """Get Tavily API configuration."""
        return {
            "api_key": self.get("TAVILY_API_KEY"),
            "search_depth": self.get("TAVILY_SEARCH_DEPTH", "basic"),
            "include_images": self.get("TAVILY_INCLUDE_IMAGES", False, "bool"),
            "include_answer": self.get("TAVILY_INCLUDE_ANSWER", True, "bool")
        }
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration from environment."""
        return {
            "name": self.get("AGENT_NAME", "Aegis Agent"),
            "model": self.get("AGENT_MODEL", "deepseek-chat"),
            "temperature": self.get("AGENT_TEMPERATURE", 0.7, "float"),
            "max_tokens": self.get("AGENT_MAX_TOKENS", 4000, "int")
        }
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory configuration from environment."""
        return {
            "enabled": self.get("MEMORY_ENABLED", True, "bool"),
            "retention_days": self.get("MEMORY_RETENTION_DAYS", 30, "int"),
            "max_size": self.get("MEMORY_MAX_SIZE", 10000, "int")
        }
    
    def get_tools_config(self) -> Dict[str, Any]:
        """Get tools configuration from environment."""
        return {
            "enabled": self.get("TOOLS_ENABLED", True, "bool"),
            "terminal_timeout": self.get("TERMINAL_TIMEOUT", 30, "int"),
            "search_timeout": self.get("SEARCH_TIMEOUT", 10, "int"),
            "code_timeout": self.get("CODE_TIMEOUT", 30, "int")
        }
    
    def get_communication_config(self) -> Dict[str, Any]:
        """Get communication configuration from environment."""
        return {
            "hierarchical_enabled": self.get("HIERARCHICAL_ENABLED", True, "bool"),
            "report_frequency": self.get("REPORT_FREQUENCY", 5, "int"),
            "require_approval": self.get("REQUIRE_APPROVAL", False, "bool")
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration from environment."""
        return {
            "level": self.get("LOG_LEVEL", "INFO"),
            "file": self.get("LOG_FILE", "agent_zero.log")
        }
    
    def get_development_config(self) -> Dict[str, Any]:
        """Get development configuration from environment."""
        return {
            "debug": self.get("DEBUG", False, "bool"),
            "test_mode": self.get("TEST_MODE", False, "bool")
        }
    
    def validate_required_vars(self) -> Dict[str, bool]:
        """
        Validate that required environment variables are set.
        
        Returns:
            Dict with validation results
        """
        required_vars = {
            "DEEPSEEK_API_KEY": "DeepSeek API key is required",
            "DEEPSEEK_API_BASE_URL": "DeepSeek API base URL is required"
        }
        
        validation_results = {}
        missing_vars = []
        
        for var, description in required_vars.items():
            value = self.get(var)
            if value is None or value == "":
                missing_vars.append(f"{var}: {description}")
                validation_results[var] = False
            else:
                validation_results[var] = True
        
        if missing_vars:
            print("❌ Missing required environment variables:")
            for var in missing_vars:
                print(f"  - {var}")
            print(f"Please check your {self.env_file} file.")
        
        return validation_results
    
    def print_config_summary(self):
        """Print a summary of the current configuration."""
        print("\n📋 Environment Configuration Summary:")
        print("=" * 50)
        
        # DeepSeek config
        deepseek_config = self.get_deepseek_config()
        print(f"🤖 DeepSeek API:")
        print(f"  Model: {deepseek_config['model']}")
        print(f"  Base URL: {deepseek_config['api_base_url']}")
        print(f"  API Key: {'*' * 10 if deepseek_config['api_key'] else 'Not set'}")
        
        # Agent config
        agent_config = self.get_agent_config()
        print(f"\n🛡️  Aegis Agent Configuration:")
        print(f"  Name: {agent_config['name']}")
        print(f"  Model: {agent_config['model']}")
        print(f"  Temperature: {agent_config['temperature']}")
        print(f"  Max Tokens: {agent_config['max_tokens']}")
        
        # Memory config
        memory_config = self.get_memory_config()
        print(f"\n🧠 Memory Configuration:")
        print(f"  Enabled: {memory_config['enabled']}")
        print(f"  Retention Days: {memory_config['retention_days']}")
        print(f"  Max Size: {memory_config['max_size']}")
        
        # Tools config
        tools_config = self.get_tools_config()
        print(f"\n🛠️  Tools Configuration:")
        print(f"  Enabled: {tools_config['enabled']}")
        print(f"  Terminal Timeout: {tools_config['terminal_timeout']}s")
        print(f"  Search Timeout: {tools_config['search_timeout']}s")
        print(f"  Code Timeout: {tools_config['code_timeout']}s")
        
        # Validation
        validation = self.validate_required_vars()
        if all(validation.values()):
            print(f"\n✅ All required variables are set!")
        else:
            print(f"\n❌ Some required variables are missing!")
        
        print("=" * 50)


# Global environment manager instance
env_manager = EnvManager() 