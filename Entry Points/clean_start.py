#!/usr/bin/env python3
"""
clean_start.py
--------------
Clean startup script for the LinkedIn Profile Optimizer that initializes
dependencies with proper warnings suppression.
"""

import os
import sys
import warnings

# Add paths for the new folder structure
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
core_modules_path = os.path.join(parent_dir, "Core Modules")
sys.path.insert(0, current_dir)
sys.path.insert(0, core_modules_path)

def clean_startup():
    """Initialize the application with clean, suppressed warnings."""
    
    # Suppress dependency warnings globally
    from utils.warnings_handler import initialize_dependencies, print_clean_startup_message
    initialize_dependencies()
    
    # Test imports to trigger any one-time loading
    try:
        print("🔄 Loading AI and NLP components...")
        
        # This will load models silently if they haven't been loaded yet
        from analyzer.keyword_extractor import extract_skills_from_text
        from analyzer.similarity_scorer import semantic_similarity_score
        from ai_rewriter.rewriter import _call_groq
        
        # Quick test to ensure everything works
        test_result = extract_skills_from_text("Python developer with React experience")
        
        print_clean_startup_message()
        return True
        
    except Exception as e:
        print(f"⚠️  Warning during startup: {e}")
        print("   Application will still work with reduced functionality.")
        return False

if __name__ == "__main__":
    success = clean_startup()
    if success:
        print("✅ Ready to run: python -m streamlit run app.py")
    else:
        print("⚠️  Some issues detected, but you can still try running the app.")