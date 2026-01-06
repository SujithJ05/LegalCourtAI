"""Health check utilities for monitoring system status."""
from typing import Dict, Any
import requests
from datetime import datetime

import config
from utils.logger import setup_logger


logger = setup_logger(__name__)


def check_ollama_health() -> Dict[str, Any]:
    """
    Check if Ollama is running and accessible.
    
    Returns:
        Dictionary with health status
    """
    try:
        response = requests.get(
            f"{config.OLLAMA_BASE_URL}/api/tags",
            timeout=5
        )
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            # Use generator expression instead of list comprehension for memory efficiency
            model_names = [m['name'] for m in models]  # Keep as list since we need to iterate twice
            
            # Check if configured model is available (use generator here)
            model_available = any(
                config.OLLAMA_MODEL in name 
                for name in model_names
            )
            
            return {
                'status': 'healthy',
                'ollama_running': True,
                'ollama_url': config.OLLAMA_BASE_URL,
                'models_available': model_names,
                'configured_model': config.OLLAMA_MODEL,
                'configured_model_available': model_available,
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'unhealthy',
                'ollama_running': False,
                'error': f'Ollama returned status code {response.status_code}',
                'timestamp': datetime.now().isoformat()
            }
            
    except requests.exceptions.ConnectionError:
        return {
            'status': 'unhealthy',
            'ollama_running': False,
            'error': 'Cannot connect to Ollama. Is it running?',
            'ollama_url': config.OLLAMA_BASE_URL,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return {
            'status': 'unhealthy',
            'ollama_running': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def get_system_status() -> Dict[str, Any]:
    """
    Get comprehensive system status.
    
    Returns:
        System status information
    """
    from core.trial_store import get_statistics
    
    ollama_health = check_ollama_health()
    trial_stats = get_statistics()
    
    return {
        'system': {
            'status': 'operational' if ollama_health['status'] == 'healthy' else 'degraded',
            'timestamp': datetime.now().isoformat()
        },
        'ollama': ollama_health,
        'trials': trial_stats,
        'configuration': {
            'model': config.OLLAMA_MODEL,
            'max_trial_hours': config.MAX_TRIAL_DURATION_HOURS,
            'llm_timeout': config.LLM_TIMEOUT_SECONDS,
            'max_retries': config.LLM_MAX_RETRIES
        }
    }
