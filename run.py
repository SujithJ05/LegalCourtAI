"""
Run the Legal Court AI Flask application.

This is the entry point for the web application.
"""
from app import create_app
from utils.logger import setup_logger
import config


logger = setup_logger(__name__)


if __name__ == '__main__':
    app = create_app()
    
    logger.info(f"Starting Flask application on port 5000")
    logger.info(f"Using model: {config.OLLAMA_MODEL}")
    logger.info(f"Debug mode: {config.DEBUG}")
    
    print("\n" + "=" * 70)
    print("VIRTUAL COURT AI - WEB APPLICATION")
    print("=" * 70)
    print(f"Application running at: http://localhost:5000")
    print(f"Model: {config.OLLAMA_MODEL}")
    print(f"Debug Mode: {config.DEBUG}")
    print(f"Log File: {config.LOG_FILE}")
    print("=" * 70)
    print("\nPress CTRL+C to stop the server\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.DEBUG
    )
