"""
LinkedIn Profile Optimizer - Quick Start
========================================

Use this script to quickly start the application, bypassing dependency checks.
"""

import subprocess
import sys

def main():
    print("🚀 LinkedIn Profile Optimizer - Quick Start")
    print("=" * 50)
    print()
    print("💡 TIP: Use 'Manual Input' mode for best results!")
    print("   Avoids Chrome/ChromeDriver compatibility issues")
    print()
    print("⚠️  Note: This will start the app even if some ML dependencies have issues.")
    print("   The app will use fallback modes for incompatible libraries.")
    print()
    
    choice = input("🚀 Start the application? (y/n): ").lower().strip()
    if choice in ['y', 'yes']:
        print("\n🚀 Starting LinkedIn Profile Optimizer...")
        print("💡 Remember: Choose 'Manual Input' to avoid browser issues!")
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        except KeyboardInterrupt:
            print("\n👋 Application stopped")
    else:
        print("👋 To start manually, run: streamlit run app.py")

if __name__ == "__main__":
    main()