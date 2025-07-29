"""
Configuration Management for Aegis Agent
Handles loading and saving agent configurations.
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .config_types import AgentConfig


def load_config(config_path: str = None) -> AgentConfig:
    """
    Load configuration from file or return default configuration.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        AgentConfig: Loaded configuration
    """
    if not config_path:
        return AgentConfig()
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"⚠️  Configuration file not found: {config_path}")
        print("Using default configuration.")
        return AgentConfig()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() == '.json':
                config_data = json.load(f)
            elif config_file.suffix.lower() in ['.yml', '.yaml']:
                config_data = yaml.safe_load(f)
            else:
                print(f"⚠️  Unsupported configuration file format: {config_file.suffix}")
                return AgentConfig()
        
        # Convert to AgentConfig
        return AgentConfig(**config_data)
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        print("Using default configuration.")
        return AgentConfig()


def save_config(config: AgentConfig, config_path: str) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: AgentConfig to save
        config_path: Path to save configuration
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert AgentConfig to dict
        config_data = {
            "name": config.name,
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "memory_enabled": config.memory_enabled,
            "hierarchical_enabled": config.hierarchical_enabled,
            "tools_enabled": config.tools_enabled,
            "report_frequency": config.report_frequency,
            "require_approval": config.require_approval,
            "memory_retention_days": config.memory_retention_days,
            "max_memory_size": config.max_memory_size
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            if config_file.suffix.lower() == '.json':
                json.dump(config_data, f, indent=2)
            elif config_file.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(config_data, f, default_flow_style=False)
            else:
                print(f"⚠️  Unsupported configuration file format: {config_file.suffix}")
                return False
        
        print(f"✅ Configuration saved to: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False


def create_default_config(config_path: str = "config/agent_zero.json") -> bool:
    """
    Create a default configuration file.
    
    Args:
        config_path: Path to save default configuration
        
    Returns:
        bool: True if successful, False otherwise
    """
    default_config = AgentConfig()
    return save_config(default_config, config_path)


def get_config_examples() -> Dict[str, Dict]:
    """
    Get example configurations for different use cases.
    
    Returns:
        Dict: Example configurations
    """
    return {
        "basic": {
            "name": "Aegis Agent",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 4000,
            "memory_enabled": True,
            "hierarchical_enabled": True,
            "tools_enabled": True,
            "report_frequency": 5,
            "require_approval": False,
            "memory_retention_days": 30,
            "max_memory_size": 10000
        },
        "conservative": {
            "name": "Conservative Agent",
            "model": "gpt-4",
            "temperature": 0.3,
            "max_tokens": 2000,
            "memory_enabled": True,
            "hierarchical_enabled": False,
            "tools_enabled": True,
            "report_frequency": 3,
            "require_approval": True,
            "memory_retention_days": 7,
            "max_memory_size": 5000
        },
        "experimental": {
            "name": "Experimental Agent",
            "model": "gpt-4",
            "temperature": 0.9,
            "max_tokens": 8000,
            "memory_enabled": True,
            "hierarchical_enabled": True,
            "tools_enabled": True,
            "report_frequency": 10,
            "require_approval": False,
            "memory_retention_days": 60,
            "max_memory_size": 20000
        }
    }


def validate_config(config: AgentConfig) -> Dict[str, Any]:
    """
    Validate a configuration and return validation results.
    
    Args:
        config: AgentConfig to validate
        
    Returns:
        Dict: Validation results
    """
    issues = []
    warnings = []
    
    # Check required fields
    if not config.name:
        issues.append("Agent name is required")
    
    if not config.model:
        issues.append("Model is required")
    
    # Check value ranges
    if config.temperature < 0 or config.temperature > 2:
        issues.append("Temperature must be between 0 and 2")
    
    if config.max_tokens < 1 or config.max_tokens > 100000:
        issues.append("Max tokens must be between 1 and 100000")
    
    if config.memory_retention_days < 1:
        warnings.append("Memory retention days should be at least 1")
    
    if config.max_memory_size < 1000:
        warnings.append("Max memory size should be at least 1000")
    
    if config.report_frequency < 1:
        warnings.append("Report frequency should be at least 1")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


def print_config_info(config: AgentConfig):
    """
    Print configuration information in a readable format.
    
    Args:
        config: AgentConfig to display
    """
    print("\n📋 Agent Configuration:")
    print(f"  Name: {config.name}")
    print(f"  Model: {config.model}")
    print(f"  Temperature: {config.temperature}")
    print(f"  Max Tokens: {config.max_tokens}")
    print(f"  Memory Enabled: {config.memory_enabled}")
    print(f"  Hierarchical Enabled: {config.hierarchical_enabled}")
    print(f"  Tools Enabled: {config.tools_enabled}")
    print(f"  Report Frequency: {config.report_frequency}")
    print(f"  Require Approval: {config.require_approval}")
    print(f"  Memory Retention: {config.memory_retention_days} days")
    print(f"  Max Memory Size: {config.max_memory_size}")
    
    # Validate and show issues
    validation = validate_config(config)
    if validation["issues"]:
        print("\n❌ Configuration Issues:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
    
    if validation["warnings"]:
        print("\n⚠️  Configuration Warnings:")
        for warning in validation["warnings"]:
            print(f"  - {warning}")
    
    if validation["valid"] and not validation["warnings"]:
        print("\n✅ Configuration is valid!") 