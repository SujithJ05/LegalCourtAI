"""Base agent class with common functionality for all agents."""
from typing import Optional, List, Dict, Any


class Agent:
    """Base class for all trial agents (Plaintiff, Defendant, Judge)."""
    
    def __init__(self, name: str, role: str, model_name: str = "mistral"):
        """
        Initialize an agent.
        
        Args:
            name: Agent's name (e.g., "PlaintiffAgent")
            role: Agent's role description (e.g., "Advocate for the Plaintiff")
            model_name: LLM model name to use
        """
        self.name = name
        self.role = role
        self.model_name = model_name

    def think(self, prompt_details: Dict[str, Any]) -> Optional[str]:
        """
        Generic think method for processing prompts.
        
        Args:
            prompt_details: Dictionary containing action, case_facts, history, etc.
        
        Returns:
            Generated response or None if failed
        
        Raises:
            NotImplementedError: Must be overridden by subclasses
        """
        raise NotImplementedError(
            "You must override the think() method or specific action methods."
        )

    def _construct_prompt(
        self,
        action: str,
        case_facts: str,
        history: List[Dict[str, str]],
        specific_input: str = ""
    ) -> str:
        """
        Build a structured prompt for the LLM.
        
        Args:
            action: Current action being performed
            case_facts: The case facts
            history: Conversation history
            specific_input: Additional context for this specific action
        
        Returns:
            Formatted prompt string
        """
        # Get last 5 entries for brevity and context - optimize by slicing once
        history_len = len(history)
        recent_history = history if history_len <= 5 else history[-5:]
        
        # Pre-build history string to avoid repeated concatenation
        history_parts = [
            f"{msg.get('speaker', 'Unknown')}: {msg.get('statement', '')}"
            for msg in recent_history
        ]
        history_str = "\n".join(history_parts) if history_parts else ""

        # Use list for efficient string building
        prompt_parts = [
            f"You are {self.name}, an expert {self.role}.\n",
            f"Current Action: {action.replace('_', ' ').title()}\n\n",
            f"Case Facts:\n{case_facts}\n\n"
        ]
        
        if history_str:
            prompt_parts.append(f"Recent Conversation History (last 5 turns):\n{history_str}\n\n")
        
        if specific_input:
            prompt_parts.append(f"Specific Input/Focus for this turn:\n{specific_input}\n\n")
        
        prompt_parts.append(
            "Your response should be concise, in character, and directly address "
            "the current action. Maintain a professional legal tone appropriate for "
            "your role.\n\nResponse:"
        )
        
        return "".join(prompt_parts)