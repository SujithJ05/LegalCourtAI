from agents.base_agent import Agent
from utils.llm import run_ollama

class DefendantAgent(Agent):
    def __init__(self, model_name: str = "tinyllama"):
        super().__init__(name="DefendantAgent", role="Advocate for the Defendant", model_name=model_name)

    def generate_opening_statement(self, case_facts: str, history: list) -> str | None:
        action = "Generate Defense Opening Statement"
        plaintiff_opening = ""
        if history and history[0]['speaker'] == "PlaintiffAgent":
            plaintiff_opening = history[0]['statement']
        
        specific_input_text = f"The plaintiff has made their opening statement: \"{plaintiff_opening if plaintiff_opening else 'Not yet heard or available.'}\". Now, present your opening statement. Acknowledge the plaintiff's claims if appropriate, but focus on outlining your defense, any counterclaims, and why the defendant should not be held liable or why damages should be mitigated."

        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history, # Pass relevant history
            specific_input=specific_input_text
        )
        return run_ollama(prompt_text, model=self.model_name)

    def respond_to_argument(self, case_facts: str, history: list, plaintiff_argument: str) -> str | None:
        action = "Respond to Plaintiff's Argument / Cross-Examine"
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input=f"The plaintiff has presented the argument: \"{plaintiff_argument}\". Analyze this argument. Identify weaknesses, inconsistencies, or alternative interpretations. Formulate a response or cross-examination questions to challenge it."
        )
        return run_ollama(prompt_text, model=self.model_name)
    
    def present_defense_argument(self, case_facts: str, history: list, argument_focus: str) -> str | None:
        action = "Present Defense Argument/Evidence Point"
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input=f"Present a key defense argument or piece of evidence related to: {argument_focus}. This should counter the plaintiff's claims or support your defense theory."
        )
        return run_ollama(prompt_text, model=self.model_name)

    def generate_closing_argument(self, case_facts: str, history: list) -> str | None:
        action = "Generate Defense Closing Argument"
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input="Summarize your key defense points, highlight how the evidence (or lack thereof from the plaintiff) supports your position, address major plaintiff arguments, and strongly argue why the defendant is not liable or why damages should be limited/denied."
        )
        return run_ollama(prompt_text, model=self.model_name)