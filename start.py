"""Quick start script for Legal Court AI."""
import os
import sys
import subprocess


def main():
    """Quick start the application."""
    print("\n" + "="*70)
    print("LEGAL COURT AI - QUICK START".center(70))
    print("="*70 + "\n")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating from .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✓ .env file created\n")
        else:
            print("✗ .env.example not found!")
            return
    
    # Check if Ollama is running
    print("Checking Ollama status...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            print(f"✓ Ollama is running")
            print(f"  Available models: {', '.join(models) if models else 'None'}\n")
            
            if not models:
                print("⚠️  No models found. Recommend running:")
                print("   ollama pull mistral\n")
        else:
            print("⚠️  Ollama responded but with unexpected status\n")
    except:
        print("✗ Ollama is not running or not accessible")
        print("  Please start Ollama with: ollama serve\n")
        
        response = input("Start app anyway? (y/n): ").lower()
        if response != 'y':
            return
    
    # Start the application
    print("\nStarting Legal Court AI...")
    print("Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    try:
        from app import create_app
        app = create_app()
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Check logs/app.log for details")


if __name__ == '__main__':
    main()
