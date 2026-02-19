import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'streamlit', 'groq', 'scikit-learn', 
        'sentence-transformers', 'pandas', 'numpy', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    # Special handling for spacy (may fail on Python 3.14)
    try:
        import spacy
        print("✅ spaCy is available")
    except ImportError:
        print("⚠️  spaCy is not available (fallback mode will be used)")
        print("   This is likely due to Python 3.14 compatibility issues")
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 Install them with: pip install -r '../Data & Configuration/requirements.txt'")
        return False
    
    print("✅ All core packages are installed")
    return True

def check_env_file():
    """Check if .env file exists and has GROQ_API_KEY."""
    # Look for .env file in Data & Configuration folder
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    env_file = parent_dir / "Data & Configuration" / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Please create a .env file with your GROQ_API_KEY")
        print("   Example: GROQ_API_KEY=your_api_key_here")
        return False
    
    # Read .env file and check for API key
    with open(env_file, 'r') as f:
        content = f.read()
    
    if "GROQ_API_KEY=" not in content or "your_groq_api_key_here" in content:
        print("❌ GROQ_API_KEY not configured in .env file")
        print("🔑 Please set your Groq API key in .env file")
        print("   Get a free key at: https://console.groq.com")
        return False
    
    print("✅ GROQ_API_KEY configured in .env file")
    return True

def check_spacy_model():
    """Check if spaCy English model is available."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy English model is available")
        return True
    except ImportError:
        print("⚠️  spaCy not available (Python 3.14 compatibility issue)")
        print("   The app will use fallback mode (basic functionality)")
        return False
    except OSError:
        print("⚠️  spaCy English model not found")
        print("   The app will use fallback mode (reduced functionality)")
        print("   To install: python -m spacy download en_core_web_sm")
        return False

def main():
    """Main startup function."""
    print("🚀 LinkedIn Profile Optimizer - Startup Check\n")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run checks
    deps_ok = check_dependencies()
    env_ok = check_env_file()
    spacy_ok = check_spacy_model()
    
    print("\n" + "="*50)
    
    if not deps_ok:
        print("❌ Please install missing dependencies first")
        return
    
    if not env_ok:
        print("❌ Please configure your Groq API key first")
        return
    
    # App is ready to run
    print("🎉 Application is ready to run!")
    print("\nTo start the application:")
    print("   streamlit run app.py")
    
    # Ask if user wants to start now
    choice = input("\n🚀 Start the application now? (y/n): ").lower().strip()
    if choice in ['y', 'yes']:
        print("\n🚀 Starting LinkedIn Profile Optimizer...")
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        except KeyboardInterrupt:
            print("\n👋 Application stopped")
    else:
        print("👋 Run 'streamlit run app.py' when you're ready!")

if __name__ == "__main__":
    main()