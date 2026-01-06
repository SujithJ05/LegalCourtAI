"""Agent modules for Legal Court AI simulation."""

from agents.base_agent import Agent
from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent

__all__ = ['Agent', 'PlaintiffAgent', 'DefendantAgent', 'JudgeAgent']