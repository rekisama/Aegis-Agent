"""
Agent module for Aegis Agent.
Contains the core agent implementation and related components.
"""

from .core import Agent
from ..utils.config_types import AgentConfig

__all__ = ["Agent", "AgentConfig"] 