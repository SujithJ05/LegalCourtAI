import subprocess

def run_ollama(prompt: str, model: str = 'mistral'):
    try:
        # print(f"\n--- Ollama Prompt for {model} ---\n{prompt}\n---------------------------\n") # For debugging prompts
        process = subprocess.Popen(
            ['ollama', 'run', model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout_data, stderr_data = process.communicate(input=prompt)

        if process.returncode != 0:
            error_message = f"Ollama process error (return code {process.returncode}) for model '{model}':"
            if stdout_data: error_message += f"\nStdout: {stdout_data.strip()}"
            if stderr_data: error_message += f"\nStderr: {stderr_data.strip()}"
            print(error_message)
            return None
        
        # Ollama sometimes prints connection/model info to stderr.
        # We'll print it for debugging if it's not just a success message.
        if stderr_data and "success" not in stderr_data.lower() and "total duration" not in stderr_data.lower():
            print(f"Ollama stderr (informational or error) for model '{model}': {stderr_data.strip()}")

        return stdout_data.strip()

    except FileNotFoundError:
        print("Error: The 'ollama' command was not found. "
              "Please ensure Ollama is installed and in your system's PATH.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while running Ollama with model '{model}': {e}")
        return None