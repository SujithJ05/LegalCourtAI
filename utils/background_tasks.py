"""Background tasks for maintenance and cleanup."""
import threading
import time
from datetime import datetime

from core.trial_store import cleanup_expired
from utils.logger import setup_logger


logger = setup_logger(__name__)


class BackgroundTaskManager:
    """Manages background tasks like cleanup and health checks."""
    
    def __init__(self, cleanup_interval_seconds: int = 3600):
        """
        Initialize background task manager.
        
        Args:
            cleanup_interval_seconds: How often to run cleanup (default: 1 hour)
        """
        self.cleanup_interval = cleanup_interval_seconds
        self.running = False
        self.thread = None
        
    def start(self):
        """Start background tasks."""
        if self.running:
            logger.warning("Background tasks already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._run_tasks, daemon=True)
        self.thread.start()
        logger.info("Background tasks started")
        
    def stop(self):
        """Stop background tasks."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Background tasks stopped")
        
    def _run_tasks(self):
        """Main loop for background tasks."""
        logger.info("Background task loop started")
        
        while self.running:
            try:
                # Run cleanup
                expired_count = cleanup_expired()
                if expired_count > 0:
                    logger.info(f"Background cleanup removed {expired_count} expired trials")
                
                # Sleep until next interval
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error in background task: {e}", exc_info=True)
                time.sleep(60)  # Wait a minute before retrying


# Global instance
_task_manager = None


def start_background_tasks(cleanup_interval: int = 3600):
    """
    Start background tasks globally.
    
    Args:
        cleanup_interval: Seconds between cleanup runs
    """
    global _task_manager
    
    if _task_manager is None:
        _task_manager = BackgroundTaskManager(cleanup_interval)
        _task_manager.start()


def stop_background_tasks():
    """Stop background tasks globally."""
    global _task_manager
    
    if _task_manager:
        _task_manager.stop()
        _task_manager = None
