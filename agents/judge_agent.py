from agents.base_agent import Agent
from utils.llm import run_ollama

class JudgeAgent(Agent):
    def __init__(self, model_name: str = "tinyllama"):
        super().__init__(name="JudgeAgent", role="Presiding Judge", model_name=model_name)

    def provide_opening_remarks_or_guidance(self, case_facts: str, history: list) -> str | None:
        action = "Provide Opening Remarks or Procedural Guidance"
        specific_input = "The trial is about to begin. Briefly outline the expected procedure for opening statements or provide any initial guidance to both counsels. Maintain impartiality."
        if history: # After opening statements
             specific_input = "Both counsels have delivered their opening statements. You may briefly comment on the clarity, ask for immediate clarifications if absolutely necessary, or simply instruct the plaintiff to proceed with their case."
       
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input=specific_input
        )
        return run_ollama(prompt_text, model=self.model_name)

    def manage_turn(self, case_facts: str, history: list, next_expected_action: str) -> str | None:
        action = "Manage Turn / Transition"
        last_speaker = history[-1]['speaker'] if history else "No one"
        last_statement = history[-1]['statement'] if history else "Nothing yet."
        
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input=f"The last statement was from {last_speaker}: \"{last_statement}\". The next expected action is for the {next_expected_action}. Briefly guide the proceedings or call upon the appropriate counsel."
        )
        return run_ollama(prompt_text, model=self.model_name)

    def summarize_and_conclude_phase(self, case_facts: str, history: list, phase_name: str) -> str | None:
        action = f"Summarize and Conclude Phase: {phase_name}"
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input=f"The '{phase_name}' phase has just concluded. Briefly summarize the key developments or arguments presented during this phase before moving to the next."
        )
        return run_ollama(prompt_text, model=self.model_name)

    def deliver_verdict_summary(self, case_facts: str, history: list) -> str | None:
        action = "Deliver Verdict Summary (Based on Arguments)"
        # This is highly simplified. A real verdict requires legal analysis beyond LLM capabilities.
        # We're aiming for a summary based on the "persuasiveness" presented in the mock trial.
        prompt_text = self._construct_prompt(
            action=action,
            case_facts=case_facts,
            history=history,
            specific_input="The trial arguments have concluded. Based *solely* on the arguments and evidence points presented by both sides during this simulated trial (as recorded in the history), provide a brief summary of which side appeared more persuasive on the key issues. This is not a legal judgment but an assessment of the arguments made within this simulation. Conclude with a simulated 'verdict' (e.g., 'In favor of Plaintiff on the grounds of X' or 'In favor of Defendant due to Y')."
        )
        return run_ollama(prompt_text, model=self.model_name)