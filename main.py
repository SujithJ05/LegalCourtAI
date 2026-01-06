"""Main entry point for command-line trial execution."""
from core.trial_manager import TrialManager
from utils.logger import setup_logger
import config


logger = setup_logger(__name__)


def main():
    """Run a trial from the command line."""
    case_facts = """The plaintiff, a small bakery named "Sweet Delights," alleges that the defendant, "Reliable Shipping Co.," breached a contract for the refrigerated transport of a large wedding cake. The contract stipulated delivery by 10:00 AM on Saturday for a wedding at noon. The cake was picked up on Friday evening. However, the defendant's refrigerated truck broke down en route, and a replacement vehicle did not arrive until 2:00 PM on Saturday, four hours late. By this time, the wedding ceremony was over, and the client had to arrange for an emergency, much simpler cake from a local supermarket. "Sweet Delights" claims financial loss due to the full refund they had to provide to their client for the wedding cake, loss of reputation, and the cost of the ingredients for the undelivered cake.
    Defendant's possible private knowledge: The breakdown was due to a sudden, unexpected engine part failure despite recent standard maintenance. They immediately dispatched their closest available replacement truck, but it was 2 hours away. The contract has a clause: 'Liability for delays due to unforeseeable mechanical failure is limited to 25% of the contract value.' Sweet Delights was offered this 25% but refused."""

    print("=" * 70)
    print("VIRTUAL COURT AI - COMMAND LINE INTERFACE")
    print("=" * 70)
    print(f"Model: {config.OLLAMA_MODEL}")
    print(f"Ollama URL: {config.OLLAMA_BASE_URL}")
    print(f"LLM Timeout: {config.LLM_TIMEOUT_SECONDS}s")
    print(f"Max Retries: {config.LLM_MAX_RETRIES}")
    print("\nIMPORTANT: Ensure Ollama is running and you have pulled the model.")
    print(f"Run: ollama pull {config.OLLAMA_MODEL}")
    print("=" * 70)
    print()
    
    try:
        logger.info("Starting command-line trial execution")
        manager = TrialManager(case_facts=case_facts)
        manager.run_trial_step_by_step()
        
        # Export trial results
        export_path = "trial_output.json"
        if manager.export_to_json(export_path):
            print(f"\nTrial results exported to: {export_path}")
            logger.info(f"Trial exported to {export_path}")
        
        print(f"\nTotal statements: {len(manager.conversation_history)}")
        print(f"Errors encountered: {manager.error_count}")
        print(f"Trial completed: {manager.completed}")
        
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nError: {e}")
    except Exception as e:
        logger.error(f"Fatal error during trial: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        print("Check logs/app.log for details")


if __name__ == "__main__":
    main()