class Agent:
    def __init__(self, name: str, role: str, model_name: str = "tinyllama"):
        self.name = name
        self.role = role
        self.model_name = model_name

    def think(self, prompt_details: dict) -> str | None:
        """
        Generic think method.
        prompt_details should contain all necessary info to construct the prompt.
        Example: {'action': 'opening_statement', 'case_facts': '...', 'history': []}
        """
        raise NotImplementedError("You must override the think() method or specific action methods.")

    def _construct_prompt(self, action: str, case_facts: str, history: list, specific_input: str = "") -> str:
        """Helper to build a common prompt structure."""
        history_str = "\n".join([f"{msg['speaker']}: {msg['statement']}" for msg in history[-5:]]) # Last 5 for brevity

        prompt = f"You are {self.name}, an expert {self.role}.\n"
        prompt += f"Current Action: {action.replace('_', ' ').title()}\n"
        prompt += f"Case Facts:\n{case_facts}\n\n"
        if history_str:
            prompt += f"Recent Conversation History (last 5 turns):\n{history_str}\n\n"
        if specific_input:
            prompt += f"Specific Input/Focus for this turn:\n{specific_input}\n\n"
        
        prompt += "Your response should be concise, in character, and directly address the current action. "
        prompt += "Maintain a professional legal tone appropriate for your role.\n"
        prompt += "Response:"
        return prompt