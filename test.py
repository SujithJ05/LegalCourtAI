import subprocess

def ask_ollama(prompt):
    process = subprocess.Popen(
        ['ollama', 'run', 'mistral'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # Send prompt + EOF
    stdout, stderr = process.communicate(prompt)
    
    if stderr:
        print("Error:", stderr)
    
    return stdout.strip()

prompt = "Hello, how are you?"
response = ask_ollama(prompt)
print("Mistral response:", response)
