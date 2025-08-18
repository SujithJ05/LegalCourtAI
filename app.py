from flask import Flask, render_template, request, jsonify
from core.trial_manager import TrialManager # Ensure this import path is correct
import os # For choosing model based on environment variable if desired

app = Flask(__name__)

# Global variable to hold the trial manager instance.
# For a real multi-user app, this would need to be session-based or use a database.
current_trial_manager = None
current_trial_steps = []
current_step_index = -1

# --- CHOOSE YOUR OLLAMA MODEL ---
# You can set this via an environment variable or hardcode it.
# Example: OLLAMA_MODEL=tinyllama python app.py
DEFAULT_MODEL = "tinyllama" # Fallback if env var not set
SELECTED_MODEL = os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
print(f"--- Web App: Using Ollama model: {SELECTED_MODEL} ---")
print(f"--- Ensure 'ollama' is running and '{SELECTED_MODEL}' is pulled. ---")


def initialize_trial_steps(case_facts_str: str):
    """Defines the sequence of actions in the trial."""
    global current_trial_manager, current_trial_steps, current_step_index
    
    current_trial_manager = TrialManager(case_facts=case_facts_str, model_name=SELECTED_MODEL)
    tm = current_trial_manager # Alias for brevity

    current_trial_steps = [
        # Phase 1: Opening Statements
        {"speaker_method": tm.plaintiff.generate_opening_statement, "args": [tm.case_facts], "desc": "Plaintiff's Opening Statement"},
        {"speaker_method": tm.defendant.generate_opening_statement, "args": [tm.case_facts, lambda: tm.conversation_history], "desc": "Defendant's Opening Statement"},
        {"speaker_method": tm.judge.provide_opening_remarks_or_guidance, "args": [tm.case_facts, lambda: tm.conversation_history], "desc": "Judge's Comments on Openings"},
        
        # Phase 2: Plaintiff's Case
        {"speaker_method": tm.judge.manage_turn, "args": [tm.case_facts, lambda: tm.conversation_history, "Plaintiff to present their first argument."], "desc": "Judge Directs Plaintiff"},
        {"speaker_method": tm.plaintiff.present_argument, "args": [tm.case_facts, lambda: tm.conversation_history, "the defendant's failure to deliver on time as per the contract"], "desc": "Plaintiff's Argument on Late Delivery"},
        {"speaker_method": tm.judge.manage_turn, "args": [tm.case_facts, lambda: tm.conversation_history, "Defendant to respond or cross-examine."], "desc": "Judge Directs Defendant"},
        {"speaker_method": tm.defendant.respond_to_argument, "args": [tm.case_facts, lambda: tm.conversation_history, lambda: tm.conversation_history[-1]['statement'] if tm.conversation_history else ""], "desc": "Defendant's Response/Cross"},
        
        # Phase 3: Defendant's Case (Simplified)
        {"speaker_method": tm.judge.manage_turn, "args": [tm.case_facts, lambda: tm.conversation_history, "Defendant to present their primary defense argument."], "desc": "Judge Directs Defendant for Defense Argument"},
        {"speaker_method": tm.defendant.present_defense_argument, "args": [tm.case_facts, lambda: tm.conversation_history, "unforeseeable circumstances or mitigation of damages, referencing contract clause if applicable"], "desc": "Defendant's Defense Argument"},
        
        # Phase 4: Closing Arguments
        {"speaker_method": tm.judge.manage_turn, "args": [tm.case_facts, lambda: tm.conversation_history, "Plaintiff for Closing Arguments."], "desc": "Judge Directs Plaintiff for Closing"},
        {"speaker_method": tm.plaintiff.generate_closing_argument, "args": [tm.case_facts, lambda: tm.conversation_history], "desc": "Plaintiff's Closing Argument"},
        {"speaker_method": tm.judge.manage_turn, "args": [tm.case_facts, lambda: tm.conversation_history, "Defendant for Closing Arguments."], "desc": "Judge Directs Defendant for Closing"},
        {"speaker_method": tm.defendant.generate_closing_argument, "args": [tm.case_facts, lambda: tm.conversation_history], "desc": "Defendant's Closing Argument"},
        
        # Phase 5: Verdict
        {"speaker_method": tm.judge.manage_turn, "args": [tm.case_facts, lambda: tm.conversation_history, "Judge to deliver a summary and verdict based on the arguments."], "desc": "Judge Directs for Verdict"},
        {"speaker_method": tm.judge.deliver_verdict_summary, "args": [tm.case_facts, lambda: tm.conversation_history], "desc": "Judge's Verdict Summary"},
    ]
    current_step_index = -1


@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/start_trial', methods=['POST'])
def start_trial():
    """Initializes a new trial."""
    global current_trial_manager, current_step_index, current_trial_steps
    data = request.get_json()
    case_facts = data.get('case_facts')

    if not case_facts:
        return jsonify({"error": "Case facts are required."}), 400

    initialize_trial_steps(case_facts)
    current_trial_manager.conversation_history = [] # Clear history for new trial
    
    print(f"New trial started with case facts: {case_facts[:100]}...")
    return jsonify({"message": "Trial initialized. Click 'Next Statement' to proceed."})

@app.route('/next_statement', methods=['POST'])
def next_statement():
    """Gets the next statement in the trial sequence."""
    global current_trial_manager, current_step_index, current_trial_steps

    if not current_trial_manager:
        return jsonify({"error": "Trial not started. Please start a new trial."}), 400

    current_step_index += 1
    if current_step_index >= len(current_trial_steps):
        return jsonify({"speaker": "System", "statement": "Trial concluded. All steps completed.", "is_final": True})

    step_info = current_trial_steps[current_step_index]
    
    # Resolve lambda arguments now
    resolved_args = []
    for arg in step_info["args"]:
        if callable(arg):
            resolved_args.append(arg())
        else:
            resolved_args.append(arg)
            
    # Get the agent's name from the method's __self__ attribute
    agent_instance = step_info["speaker_method"].__self__
    speaker_name = agent_instance.name if hasattr(agent_instance, 'name') else "UnknownAgent"

    print(f"Executing step {current_step_index + 1}/{len(current_trial_steps)}: {speaker_name} - {step_info['desc']}")

    statement = step_info["speaker_method"](*resolved_args)
    
    response_data = {}
    if statement:
        current_trial_manager.conversation_history.append({"speaker": speaker_name, "statement": statement})
        response_data = {"speaker": speaker_name, "statement": statement, "is_final": False, "description": step_info["desc"]}
    else:
        failed_statement = f"[Agent {speaker_name} failed to generate a response for: {step_info['desc']}]"
        current_trial_manager.conversation_history.append({"speaker": speaker_name, "statement": failed_statement})
        response_data = {"speaker": speaker_name, "statement": failed_statement, "is_final": False, "description": step_info["desc"]}

    if current_step_index == len(current_trial_steps) - 1: # If this was the last defined step
        response_data["is_final"] = True
        response_data["statement"] += "\n\n--- TRIAL CONCLUDED ---"

    return jsonify(response_data)

if __name__ == '__main__':
    # Make sure to run ollama serve in a separate terminal if it's not already running
    # And pull the model: ollama pull <SELECTED_MODEL>
    app.run(debug=True, port=5001) # Using port 5001 to avoid conflict if ollama uses 5000