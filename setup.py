"""Setup script for Legal Court AI."""
import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"➤ {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"  ✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {description} failed: {e}")
        if e.stderr:
            print(f"    Error: {e.stderr}")
        return False


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"✗ Python 3.10+ required, found {version.major}.{version.minor}.{version.micro}")
        return False


def create_env_file():
    """Create .env file from .env.example if it doesn't exist."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return True
    
    if env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✓ Created .env file from .env.example")
        return True
    else:
        print("✗ .env.example not found")
        return False


def create_directories():
    """Create necessary directories."""
    directories = ["logs", "exports"]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        print(f"✓ Directory '{directory}' ready")
    
    return True


def main():
    """Main setup function."""
    print_header("LEGAL COURT AI - SETUP")
    
    print("This script will set up your Legal Court AI environment.\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    print("\n[1/5] Configuration")
    if not create_env_file():
        print("⚠ Warning: You'll need to create a .env file manually")
    
    # Install dependencies
    print("\n[2/5] Installing Python Dependencies")
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing packages"
    ):
        print("⚠ Warning: Some packages may not have installed correctly")
    
    # Create directories
    print("\n[3/5] Creating Directories")
    create_directories()
    
    # Check Ollama
    print("\n[4/5] Checking Ollama Installation")
    ollama_check = run_command("ollama --version", "Checking Ollama")
    
    if ollama_check:
        print("\n[5/5] Checking Ollama Models")
        result = subprocess.run(
            "ollama list",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("  Available models:")
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                if line.strip():
                    print(f"    • {line.split()[0]}")
        
        print("\n  Recommended: ollama pull mistral")
    else:
        print("  ✗ Ollama not found")
        print("  ℹ Install from: https://ollama.ai/download")
    
    # Final instructions
    print_header("SETUP COMPLETE")
    
    print("Next steps:\n")
    print("1. Make sure Ollama is running:")
    print("   ollama serve\n")
    print("2. Pull a model (if not already done):")
    print("   ollama pull mistral\n")
    print("3. Start the application:")
    print("   python run.py")
    print("   or")
    print("   python app.py\n")
    print("4. Open your browser:")
    print("   http://localhost:5000\n")
    print("For more information, see README.md and QUICKSTART.md")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nSetup failed with error: {e}")
        sys.exit(1)
