from core.trial_manager import TrialManager

def main():
    case_facts = """The plaintiff, a small bakery named "Sweet Delights," alleges that the defendant, "Reliable Shipping Co.," breached a contract for the refrigerated transport of a large wedding cake. The contract stipulated delivery by 10:00 AM on Saturday for a wedding at noon. The cake was picked up on Friday evening. However, the defendant's refrigerated truck broke down en route, and a replacement vehicle did not arrive until 2:00 PM on Saturday, four hours late. By this time, the wedding ceremony was over, and the client had to arrange for an emergency, much simpler cake from a local supermarket. "Sweet Delights" claims financial loss due to the full refund they had to provide to their client for the wedding cake, loss of reputation, and the cost of the ingredients for the undelivered cake.
    Defendant's possible private knowledge: The breakdown was due to a sudden, unexpected engine part failure despite recent standard maintenance. They immediately dispatched their closest available replacement truck, but it was 2 hours away. The contract has a clause: 'Liability for delays due to unforeseeable mechanical failure is limited to 25% of the contract value.' Sweet Delights was offered this 25% but refused."""

    # --- CHOOSE YOUR OLLAMA MODEL ---
    # Make sure you have pulled it: ollama pull <model_name>
    # "tinyllama" is recommended for speed and low resource use.
    # "phi-2" might give better quality if tinyllama is too basic.
    # "mistral" for best quality if you have the RAM.
    selected_model = "tinyllama"
    # selected_model = "phi-2"
    # selected_model = "mistral"

    print(f"Starting trial with model: {selected_model}")
    print(f"Ensure 'ollama' is running and you have pulled '{selected_model}'.\n")

    manager = TrialManager(case_facts=case_facts, model_name=selected_model)
    manager.run_trial_step_by_step()

if __name__ == "__main__":
    main()