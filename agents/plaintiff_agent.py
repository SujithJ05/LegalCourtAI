from agents.base_agent import Agent
from utils.llm import run_ollama

class PlaintiffAgent(Agent):
    def __init__(self, model_name: str = "tinyllama"):
        super().__init__(name="PlaintiffAgent", role="Advocate for the Plaintiff", model_name=model_name)

    def generate_opening_statement(self, case_facts: str) -> str | None:
        action = "Generate Opening Statement"
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=[], # No history for initial opening
            specific_input="Outline the key claims, the alleged breach, the damages sought, and why the plaintiff should prevail."
        )
        return run_ollama(prompt_text, model=self.model_name)

    def present_argument(self, case_facts: str, history: list, argument_focus: str) -> str | None:
        action = "Present Argument/Evidence Point"
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input=f"Present a key argument or piece of evidence related to: {argument_focus}. Connect it back to the opening statement and the damages sought."
        )
        return run_ollama(prompt_text, model=self.model_name)

    def generate_rebuttal(self, case_facts: str, history: list, target_statement: str) -> str | None:
        action = "Generate Rebuttal"
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input=f"The opposing counsel stated: \"{target_statement}\". Craft a rebuttal to counter this specific point, highlighting weaknesses or misinterpretations."
        )
        return run_ollama(prompt_text, model=self.model_name)

    def generate_closing_argument(self, case_facts: str, history: list) -> str | None:
        action = "Generate Closing Argument"
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input="Summarize your key arguments, reiterate how the evidence supports your claims, address any major counter-arguments, and strongly appeal for a favorable verdict based on the facts and law presented."
        )
        return run_ollama(prompt_text, model=self.model_name)