"""
Job Terminator - Modular Prompt Templates
Selects specialized prompt templates based on target job portal domain.
"""

from src.prompts.router import prompt_router
from src.prompts.base import BasePromptTemplate

__all__ = ["prompt_router", "BasePromptTemplate"]
