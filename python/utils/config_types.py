"""
Configuration types for Aegis Agent.
Separated to avoid circular imports.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentConfig:
    """Configuration for Aegis Agent."""
    name: str = "Aegis Agent"
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 4000
    memory_enabled: bool = True
    hierarchical_enabled: bool = True
    tools_enabled: bool = True
    report_frequency: int = 5
    require_approval: bool = False
    memory_retention_days: int = 30
    max_memory_size: int = 10000 