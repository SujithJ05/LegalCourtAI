"""Trial store - In-memory storage for active trials with expiry management."""
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from core.trial_manager import TrialManager
import config
from utils.logger import setup_logger


logger = setup_logger(__name__)


_lock = threading.Lock()
_trials: Dict[str, dict] = {}  # trial_id -> {manager, created_at, last_accessed}
_stats_cache = {'total_active': 0, 'last_update': None}  # Cache for statistics


def create_trial_id() -> str:
    """Generate a unique trial ID."""
    trial_id = uuid.uuid4().hex
    logger.debug(f"Created new trial ID: {trial_id}")
    return trial_id


def put(trial_id: str, manager: TrialManager) -> None:
    """Store a trial manager instance."""
    with _lock:
        now = datetime.now()
        _trials[trial_id] = {
            'manager': manager,
            'created_at': now,
            'last_accessed': now
        }
        _stats_cache['last_update'] = None  # Invalidate cache
        logger.debug(f"Trial {trial_id} stored")


def get(trial_id: str) -> Optional[TrialManager]:
    """Retrieve a trial manager instance."""
    with _lock:
        if trial_id not in _trials:
            logger.debug(f"Trial {trial_id} not found")
            return None
        
        trial_data = _trials[trial_id]
        
        # Check if trial has expired
        created_at = trial_data['created_at']
        max_age = timedelta(hours=config.MAX_TRIAL_DURATION_HOURS)
        
        if datetime.now() - created_at > max_age:
            logger.info(f"Trial {trial_id} expired, removing")
            del _trials[trial_id]
            return None
        
        # Update last accessed time
        trial_data['last_accessed'] = datetime.now()
        logger.debug(f"Trial {trial_id} accessed")
        
        return trial_data['manager']


def delete(trial_id: str) -> None:
    """Delete a specific trial."""
    with _lock:
        if trial_id in _trials:
            del _trials[trial_id]
            _stats_cache['last_update'] = None  # Invalidate cache
            logger.info(f"Trial {trial_id} deleted")
        else:
            logger.debug(f"Trial {trial_id} not found for deletion")


def clear() -> None:
    """Clear all trials."""
    with _lock:
        count = len(_trials)
        _trials.clear()
        _stats_cache['last_update'] = None  # Invalidate cache
        logger.info(f"Cleared {count} trials from store")


def cleanup_expired() -> int:
    """Remove expired trials and return count of removed trials."""
    with _lock:
        now = datetime.now()
        max_age = timedelta(hours=config.MAX_TRIAL_DURATION_HOURS)
        cutoff_time = now - max_age
        
        expired_ids = [
            trial_id for trial_id, data in _trials.items()
            if data['created_at'] < cutoff_time
        ]
        
        for trial_id in expired_ids:
            del _trials[trial_id]
        
        if expired_ids:
            _stats_cache['last_update'] = None  # Invalidate cache
            logger.info(f"Cleaned up {len(expired_ids)} expired trials")
        
        return len(expired_ids)


def get_active_count() -> int:
    """Get count of active trials."""
    with _lock:
        return len(_trials)


def get_all_ids() -> List[str]:
    """Get all active trial IDs."""
    with _lock:
        return list(_trials.keys())


def get_statistics() -> Dict[str, any]:
    """Get store statistics with caching for better performance."""
    with _lock:
        # Return cached stats if available and recent (within 5 seconds)
        if _stats_cache['last_update']:
            cache_age = (datetime.now() - _stats_cache['last_update']).total_seconds()
            if cache_age < 5:
                logger.debug("Returning cached statistics")
                return _stats_cache['data']
        
        # Calculate fresh statistics
        now = datetime.now()
        active_trials = []
        
        for trial_id, data in _trials.items():
            manager = data['manager']
            active_trials.append({
                'id': trial_id,
                'age_seconds': (now - data['created_at']).total_seconds(),
                'statement_count': len(manager.conversation_history),
                'phase': manager.current_phase,
                'completed': manager.completed
            })
        
        result = {
            'total_active': len(active_trials),
            'trials': active_trials
        }
        
        # Update cache
        _stats_cache['data'] = result
        _stats_cache['last_update'] = now
        logger.debug("Statistics calculated and cached")
        
        return result
