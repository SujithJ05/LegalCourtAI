"""Trial Manager - Orchestrates the entire trial workflow."""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent
import config
from utils.logger import setup_logger


logger = setup_logger(__name__)


# Cache for trial flow JSON to avoid repeated disk I/O
_trial_flow_cache: Dict[str, dict] = {}


class TrialManager:
    """Manages the complete trial workflow and state."""
    
    def __init__(self, case_facts: str, trial_flow_path: str | None = None):
        """Initialize trial manager with case facts and trial flow."""
        self.case_facts = case_facts
        self.model_name = config.OLLAMA_MODEL
        self.plaintiff = PlaintiffAgent(self.model_name)
        self.defendant = DefendantAgent(self.model_name)
        self.judge = JudgeAgent(self.model_name)
        self.conversation_history = []
        self.trial_flow = self._load_trial_flow(trial_flow_path)
        self.current_phase = ""
        self.created_at = datetime.now().isoformat()
        self.completed = False
        self.error_count = 0
        
        logger.info(f"Trial manager initialized with model: {self.model_name}")

    def _load_trial_flow(self, trial_flow_path: str | None) -> dict:
        """Load trial flow configuration from JSON file with caching."""
        if trial_flow_path is None:
            trial_flow_path = str(Path(__file__).resolve().parents[1] / "trial_flow.json")

        # Check cache first
        if trial_flow_path in _trial_flow_cache:
            logger.debug(f"Loaded trial flow from cache for {trial_flow_path}")
            return _trial_flow_cache[trial_flow_path]

        path = Path(trial_flow_path)
        if not path.is_file():
            logger.error(f"trial_flow.json not found at '{path}'")
            raise FileNotFoundError(
                f"trial_flow.json not found at '{path}'. "
                "Pass trial_flow_path explicitly or ensure it exists at the project root."
            )

        try:
            with path.open('r', encoding='utf-8') as f:
                flow = json.load(f)
                _trial_flow_cache[trial_flow_path] = flow  # Cache the loaded flow
                logger.debug(f"Loaded and cached trial flow from {path}")
                return flow
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in trial_flow.json: {e}")
            raise

    def _log_statement(self, speaker_name: str, statement: str | None, action_description: str = ""):
        """Log a statement to console and history (optimized)."""
        timestamp = datetime.now().isoformat()
        
        if statement:
            # Only print to console in main.py, not in web app context
            if hasattr(self, '_console_mode') and self._console_mode:
                print(f"\n--- {speaker_name} ({action_description}) ---")
                print(statement)
                print("-" * 50)
            
            self.conversation_history.append({
                "speaker": speaker_name,
                "statement": statement,
                "timestamp": timestamp,
                "action": action_description
            })
            logger.info(f"{speaker_name} statement logged: {action_description}")
        else:
            error_msg = "[Failed to respond]"
            if hasattr(self, '_console_mode') and self._console_mode:
                print(f"\n--- {speaker_name} FAILED to respond for {action_description} ---")
                print("-" * 50)
            
            self.conversation_history.append({
                "speaker": speaker_name,
                "statement": error_msg,
                "timestamp": timestamp,
                "action": action_description,
                "error": True
            })
            self.error_count += 1
            logger.warning(f"{speaker_name} failed to generate response for: {action_description}")
        
        # Trim history if it gets too long
        if len(self.conversation_history) > config.MAX_HISTORY_LENGTH:
            logger.warning(f"History exceeded max length, trimming oldest entries")
            self.conversation_history = self.conversation_history[-config.MAX_HISTORY_LENGTH:]

    def run_trial_step_by_step(self):
        """Execute the entire trial flow step by step."""
        self._console_mode = True  # Enable console output for main.py usage
        logger.info("Starting trial execution")
        
        try:
            for phase in self.trial_flow.get("phases", []):
                self.current_phase = phase.get("name", "Unknown Phase")
                print(f"\n\n=== {self.current_phase.upper()} ===")
                logger.info(f"Entering phase: {self.current_phase}")
                
                for step in phase.get("steps", []):
                    success = self._execute_step(step)
                    if not success and self.error_count > 3:
                        logger.error("Too many errors, terminating trial")
                        return

            print("\n\n--- TRIAL CONCLUDED ---")
            self.completed = True
            logger.info("Trial completed successfully")
            
        except Exception as e:
            logger.error(f"Fatal error during trial execution: {e}", exc_info=True)
            raise
    
    def _execute_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single trial step."""
        agent_name = step.get("agent")
        action = step.get("action")
        args_def = step.get("args", [])
        description = step.get("description", "")
        
        logger.debug(f"Executing step: {agent_name}.{action}")

        agent = getattr(self, agent_name.lower().replace("agent", ""), None)
        if not agent:
            logger.error(f"Unknown agent: {agent_name}")
            print(f"Unknown agent: {agent_name}")
            return False

        method = getattr(agent, action, None)
        if not method:
            logger.error(f"Unknown action: {action} for agent: {agent_name}")
            print(f"Unknown action: {action} for agent: {agent_name}")
            return False

        resolved_args = self._resolve_args(args_def)
        
        try:
            statement = method(*resolved_args)
            self._log_statement(agent.name, statement, description)
            return statement is not None
        except Exception as e:
            logger.error(f"Error executing {agent_name}.{action}: {e}", exc_info=True)
            self._log_statement(agent.name, None, description)
            return False
    
    def _resolve_args(self, args_def: list) -> list:
        """Resolve argument placeholders to actual values."""
        resolved_args = []
        for arg in args_def:
            if arg == "case_facts":
                resolved_args.append(self.case_facts)
            elif arg == "history":
                resolved_args.append(self.conversation_history)
            elif arg == "last_statement":
                resolved_args.append(
                    self.conversation_history[-1]['statement'] if self.conversation_history else ""
                )
            else:
                resolved_args.append(arg)
        return resolved_args

    def export_to_dict(self) -> Dict[str, Any]:
        """Export trial data to dictionary format."""
        return {
            'case_facts': self.case_facts,
            'model_name': self.model_name,
            'conversation_history': self.conversation_history,
            'trial_flow': self.trial_flow,
            'current_phase': self.current_phase,
            'created_at': self.created_at,
            'completed': self.completed,
            'error_count': self.error_count,
            'total_statements': len(self.conversation_history)
        }
    
    def export_to_json(self, filepath: str) -> bool:
        """Export trial to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.export_to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Trial exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export trial to {filepath}: {e}")
            return False

    def to_dict(self):
        """Alias for export_to_dict for backward compatibility."""
        return self.export_to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrialManager':
        """Restore trial manager from dictionary."""
        manager = cls(data['case_facts'])
        manager.model_name = data.get('model_name', config.OLLAMA_MODEL)
        manager.conversation_history = data.get('conversation_history', [])
        manager.trial_flow = data.get('trial_flow', manager.trial_flow)
        manager.current_phase = data.get('current_phase', '')
        manager.created_at = data.get('created_at', datetime.now().isoformat())
        manager.completed = data.get('completed', False)
        manager.error_count = data.get('error_count', 0)
        
        # Re-create agents
        manager.plaintiff = PlaintiffAgent(manager.model_name)
        manager.defendant = DefendantAgent(manager.model_name)
        manager.judge = JudgeAgent(manager.model_name)
        
        logger.debug("Trial manager restored from dictionary")
        return manager