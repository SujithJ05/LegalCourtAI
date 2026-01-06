"""Flask application for Virtual Court AI."""
from flask import Flask, jsonify, render_template, request, session, send_file
from datetime import datetime
import json
import os

import config
from core.trial_manager import TrialManager
from core.trial_store import (
    create_trial_id, get as get_trial, put as put_trial, 
    delete as delete_trial, cleanup_expired, get_statistics
)
from utils.validators import validate_case_facts, sanitize_input
from utils.logger import setup_logger
from utils.health import check_ollama_health, get_system_status
from utils.background_tasks import start_background_tasks, stop_background_tasks
from utils.templates import list_templates, get_template
import atexit


logger = setup_logger(__name__)


def get_active_trial(trial_id: str):
    """Helper to get active trial with error handling."""
    if not trial_id:
        return None, jsonify({"error": "Trial not started. Please start a new trial."}), 400
    
    trial_manager = get_trial(trial_id)
    if not trial_manager:
        return None, jsonify({"error": "Trial state expired. Please start a new trial."}), 400
    
    return trial_manager, None, None


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Start background tasks
    start_background_tasks(cleanup_interval=3600)  # Run every hour
    atexit.register(stop_background_tasks)
    
    logger.info(f"Starting Legal Court AI application with model: {config.OLLAMA_MODEL}")

    @app.route('/')
    def index():
        """Serves the main HTML page."""
        # Cleanup expired trials on page load
        expired_count = cleanup_expired()
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired trials")
        
        return render_template('index.html')

    @app.route('/start_trial', methods=['POST'])
    def start_trial():
        """Initializes a new trial."""
        try:
            data = request.get_json(silent=True) or {}
            case_facts = sanitize_input(data.get('case_facts', ''))

            # Validate case facts
            is_valid, error_message = validate_case_facts(case_facts)
            if not is_valid:
                logger.warning(f"Invalid case facts: {error_message}")
                return jsonify({"error": error_message}), 400

            # Create trial manager
            trial_manager = TrialManager(case_facts=case_facts)
            trial_id = create_trial_id()
            put_trial(trial_id, trial_manager)
            
            # Store in session
            session.permanent = True
            session['trial_id'] = trial_id
            session['current_step_index'] = -1
            session['started_at'] = datetime.now().isoformat()

            logger.info(f"New trial {trial_id} started with {len(case_facts)} chars of case facts")
            return jsonify({
                "message": "Trial initialized. Click 'Next Statement' to proceed.",
                "trial_id": trial_id
            })
            
        except Exception as e:
            logger.error(f"Error starting trial: {e}", exc_info=True)
            return jsonify({"error": "Failed to initialize trial. Please try again."}), 500

    @app.route('/next_statement', methods=['POST'])
    def next_statement():
        """Gets the next statement in the trial sequence."""
        try:
            trial_id = session.get('trial_id')
            trial_manager, error_response, status_code = get_active_trial(trial_id)
            if error_response:
                logger.warning(f"Next statement requested for invalid trial: {trial_id}")
                return error_response, status_code

            current_step_index = session.get('current_step_index', -1)
            current_step_index += 1

            all_steps = [step for phase in trial_manager.trial_flow['phases'] for step in phase['steps']]

            if current_step_index >= len(all_steps):
                trial_manager.completed = True
                put_trial(trial_id, trial_manager)
                logger.info(f"Trial {trial_id} concluded")
                return jsonify({
                    "speaker": "System",
                    "statement": "Trial concluded. All steps completed.",
                    "is_final": True
                })

            step_info = all_steps[current_step_index]
            logger.debug(f"Executing step {current_step_index + 1}/{len(all_steps)} for trial {trial_id}")

            # Execute step
            agent_name = step_info.get("agent")
            action = step_info.get("action")
            args_def = step_info.get("args", [])
            description = step_info.get("description", "")

            agent = getattr(trial_manager, agent_name.lower().replace("agent", ""), None)
            if not agent:
                logger.error(f"Unknown agent: {agent_name}")
                return jsonify({"error": f"Unknown agent: {agent_name}"}), 500

            method = getattr(agent, action, None)
            if not method:
                logger.error(f"Unknown action: {action} for agent: {agent_name}")
                return jsonify({"error": f"Unknown action: {action} for agent: {agent_name}"}), 500

            resolved_args = []
            for arg in args_def:
                if arg == "case_facts":
                    resolved_args.append(trial_manager.case_facts)
                elif arg == "history":
                    resolved_args.append(trial_manager.conversation_history)
                elif arg == "last_statement":
                    resolved_args.append(
                        trial_manager.conversation_history[-1]['statement'] 
                        if trial_manager.conversation_history else ""
                    )
                else:
                    resolved_args.append(arg)

            # Execute the action
            statement = method(*resolved_args)

            if statement:
                trial_manager.conversation_history.append({
                    "speaker": agent.name,
                    "statement": statement,
                    "timestamp": datetime.now().isoformat(),
                    "action": description
                })
                response_data = {
                    "speaker": agent.name,
                    "statement": statement,
                    "is_final": False,
                    "description": description
                }
                logger.debug(f"Statement generated successfully for {agent.name}")
            else:
                failed_statement = f"[Agent {agent.name} failed to generate a response for: {description}]"
                trial_manager.conversation_history.append({
                    "speaker": agent.name,
                    "statement": failed_statement,
                    "timestamp": datetime.now().isoformat(),
                    "action": description,
                    "error": True
                })
                response_data = {
                    "speaker": agent.name,
                    "statement": failed_statement,
                    "is_final": False,
                    "description": description
                }
                logger.warning(f"Agent {agent.name} failed to generate response")

            if current_step_index == len(all_steps) - 1:
                response_data["is_final"] = True
                response_data["statement"] += "\n\n--- TRIAL CONCLUDED ---"
                trial_manager.completed = True
                logger.info(f"Trial {trial_id} reached final step")

            put_trial(trial_id, trial_manager)
            session['current_step_index'] = current_step_index

            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error processing next statement: {e}", exc_info=True)
            return jsonify({"error": "An error occurred processing the statement."}), 500

    @app.route('/export_trial', methods=['GET'])
    def export_trial():
        """Export current trial to JSON."""
        try:
            trial_id = session.get('trial_id')
            trial_manager, error_response, status_code = get_active_trial(trial_id)
            if error_response:
                return error_response, status_code

            trial_data = trial_manager.export_to_dict()
            
            # Create exports directory if it doesn't exist
            os.makedirs('exports', exist_ok=True)
            filename = f"trial_{trial_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join('exports', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(trial_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Trial {trial_id} exported to {filepath}")
            return send_file(filepath, as_attachment=True, download_name=filename)
            
        except Exception as e:
            logger.error(f"Error exporting trial: {e}", exc_info=True)
            return jsonify({"error": "Failed to export trial."}), 500

    @app.route('/statistics', methods=['GET'])
    def statistics():
        """Get current system statistics."""
        try:
            stats = get_statistics()
            stats['model'] = config.OLLAMA_MODEL
            stats['max_trial_hours'] = config.MAX_TRIAL_DURATION_HOURS
            return jsonify(stats)
        except Exception as e:
            logger.error(f"Error getting statistics: {e}", exc_info=True)
            return jsonify({"error": "Failed to retrieve statistics."}), 500

    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint for monitoring."""
        try:
            status = get_system_status()
            status_code = 200 if status['system']['status'] == 'operational' else 503
            return jsonify(status), status_code
        except Exception as e:
            logger.error(f"Error in health check: {e}", exc_info=True)
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 503

    @app.route('/available_models', methods=['GET'])
    def available_models():
        """Get list of available Ollama models."""
        try:
            health = check_ollama_health()
            if health.get('ollama_running'):
                return jsonify({
                    "models": health.get('models_available', []),
                    "current_model": config.OLLAMA_MODEL
                })
            else:
                return jsonify({
                    "error": "Ollama is not running",
                    "models": []
                }), 503
        except Exception as e:
            logger.error(f"Error getting available models: {e}", exc_info=True)
            return jsonify({"error": "Failed to retrieve models."}), 500

    @app.route('/reset_trial', methods=['POST'])
    def reset_trial():
        """Reset current trial and start fresh."""
        try:
            trial_id = session.get('trial_id')
            if trial_id:
                delete_trial(trial_id)
                logger.info(f"Trial {trial_id} reset by user")
            
            session.clear()
            return jsonify({"message": "Trial reset successfully."})
        except Exception as e:
            logger.error(f"Error resetting trial: {e}", exc_info=True)
            return jsonify({"error": "Failed to reset trial."}), 500

    @app.route('/templates', methods=['GET'])
    def get_templates():
        """Get list of available trial templates."""
        try:
            templates = list_templates()
            return jsonify({"templates": templates})
        except Exception as e:
            logger.error(f"Error getting templates: {e}", exc_info=True)
            return jsonify({"error": "Failed to retrieve templates."}), 500

    @app.route('/templates/<template_id>', methods=['GET'])
    def get_template_detail(template_id):
        """Get details of a specific template."""
        try:
            template = get_template(template_id)
            if template:
                return jsonify(template)
            else:
                return jsonify({"error": "Template not found"}), 404
        except Exception as e:
            logger.error(f"Error getting template {template_id}: {e}", exc_info=True)
            return jsonify({"error": "Failed to retrieve template."}), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)