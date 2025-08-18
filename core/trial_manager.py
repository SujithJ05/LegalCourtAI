from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent

class TrialManager:
    def __init__(self, case_facts: str, model_name: str = "tinyllama"):
        self.case_facts = case_facts
        self.model_name = model_name
        self.plaintiff = PlaintiffAgent(model_name)
        self.defendant = DefendantAgent(model_name)
        self.judge = JudgeAgent(model_name)
        self.conversation_history = []
        self.current_phase = ""

    def _log_statement(self, speaker_name: str, statement: str | None, action_description: str = ""):
        if statement:
            print(f"\n--- {speaker_name} ({action_description}) ---")
            print(statement)
            self.conversation_history.append({"speaker": speaker_name, "statement": statement})
        else:
            print(f"\n--- {speaker_name} FAILED to respond for {action_description} ---")
            self.conversation_history.append({"speaker": speaker_name, "statement": "[Failed to respond]"})
        print("-" * 50)

    def run_trial_step_by_step(self):
        # --- Phase 1: Opening Statements ---
        self.current_phase = "Opening Statements"
        print(f"\n\n=== {self.current_phase.upper()} ===")

        # Judge's initial remarks (optional, can be done first)
        # stmt = self.judge.provide_opening_remarks_or_guidance(self.case_facts, self.conversation_history)
        # self._log_statement(self.judge.name, stmt, "Initial Remarks")
        # if not stmt: return

        # Plaintiff Opening
        stmt = self.plaintiff.generate_opening_statement(self.case_facts)
        self._log_statement(self.plaintiff.name, stmt, "Plaintiff's Opening Statement")
        if not stmt: return # End trial if critical step fails

        # Defendant Opening
        stmt = self.defendant.generate_opening_statement(self.case_facts, self.conversation_history)
        self._log_statement(self.defendant.name, stmt, "Defendant's Opening Statement")
        if not stmt: return

        # Judge comments on openings
        stmt = self.judge.provide_opening_remarks_or_guidance(self.case_facts, self.conversation_history) # Re-using for post-opening comments
        self._log_statement(self.judge.name, stmt, "Judge's Comments on Openings")
        if not stmt: return

        # --- Phase 2: Plaintiff's Case ---
        self.current_phase = "Plaintiff's Case"
        print(f"\n\n=== {self.current_phase.upper()} ===")
        
        # Judge directs Plaintiff
        stmt = self.judge.manage_turn(self.case_facts, self.conversation_history, "Plaintiff to present their first argument.")
        self._log_statement(self.judge.name, stmt, "Directing Plaintiff")
        if not stmt: return
        
        # Plaintiff Argument 1
        plaintiff_arg1_focus = "the defendant's failure to deliver on time as per the contract"
        plaintiff_arg1 = self.plaintiff.present_argument(self.case_facts, self.conversation_history, plaintiff_arg1_focus)
        self._log_statement(self.plaintiff.name, plaintiff_arg1, f"Plaintiff's Argument on: {plaintiff_arg1_focus}")
        if not plaintiff_arg1: return

        # Defendant Responds to Argument 1
        stmt = self.judge.manage_turn(self.case_facts, self.conversation_history, "Defendant to respond or cross-examine.")
        self._log_statement(self.judge.name, stmt, "Directing Defendant")
        if not stmt: return

        defendant_resp_arg1 = self.defendant.respond_to_argument(self.case_facts, self.conversation_history, plaintiff_arg1)
        self._log_statement(self.defendant.name, defendant_resp_arg1, "Defendant's Response/Cross")
        if not defendant_resp_arg1: return

        # Plaintiff Rebuttal (optional, or for a second argument)
        # stmt = self.judge.manage_turn(self.case_facts, self.conversation_history, "Plaintiff for any brief rebuttal on this point.")
        # self._log_statement(self.judge.name, stmt, "Directing Plaintiff for Rebuttal")
        # if not stmt: return
        # plaintiff_rebuttal1 = self.plaintiff.generate_rebuttal(self.case_facts, self.conversation_history, defendant_resp_arg1)
        # self._log_statement(self.plaintiff.name, plaintiff_rebuttal1, "Plaintiff's Rebuttal")
        # if not plaintiff_rebuttal1: return # Non-critical, can continue

        # --- Phase 3: Defendant's Case (Simplified for this example) ---
        self.current_phase = "Defendant's Case"
        print(f"\n\n=== {self.current_phase.upper()} ===")
        stmt = self.judge.manage_turn(self.case_facts, self.conversation_history, "Defendant to present their primary defense argument.")
        self._log_statement(self.judge.name, stmt, "Directing Defendant")
        if not stmt: return

        defendant_arg1_focus = "unforeseeable circumstances or mitigation of damages" # Defendant needs to argue this
        defendant_arg1 = self.defendant.present_defense_argument(self.case_facts, self.conversation_history, defendant_arg1_focus)
        self._log_statement(self.defendant.name, defendant_arg1, f"Defendant's Argument on: {defendant_arg1_focus}")
        # Not returning on failure for non-critical path for now

        # --- Phase 4: Closing Arguments ---
        self.current_phase = "Closing Arguments"
        print(f"\n\n=== {self.current_phase.upper()} ===")
        stmt = self.judge.manage_turn(self.case_facts, self.conversation_history, "Plaintiff for Closing Arguments.")
        self._log_statement(self.judge.name, stmt, "Directing Plaintiff for Closing")
        if not stmt: return

        plaintiff_closing = self.plaintiff.generate_closing_argument(self.case_facts, self.conversation_history)
        self._log_statement(self.plaintiff.name, plaintiff_closing, "Plaintiff's Closing Argument")
        if not plaintiff_closing: return

        stmt = self.judge.manage_turn(self.case_facts, self.conversation_history, "Defendant for Closing Arguments.")
        self._log_statement(self.judge.name, stmt, "Directing Defendant for Closing")
        if not stmt: return

        defendant_closing = self.defendant.generate_closing_argument(self.case_facts, self.conversation_history)
        self._log_statement(self.defendant.name, defendant_closing, "Defendant's Closing Argument")
        if not defendant_closing: return

        # --- Phase 5: Verdict ---
        self.current_phase = "Verdict"
        print(f"\n\n=== {self.current_phase.upper()} ===")
        stmt = self.judge.manage_turn(self.case_facts, self.conversation_history, "Judge to deliver a summary and verdict based on the arguments.")
        self._log_statement(self.judge.name, stmt, "Directing Judge for Verdict")
        if not stmt: return
        
        verdict = self.judge.deliver_verdict_summary(self.case_facts, self.conversation_history)
        self._log_statement(self.judge.name, verdict, "Judge's Verdict Summary")

        print("\n\n--- TRIAL CONCLUDED ---")