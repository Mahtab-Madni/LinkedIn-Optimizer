import os
import sys
import warnings
from contextlib import contextmanager

def suppress_dependency_warnings():
    
    # Suppress specific warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="confection")
    warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
    warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")
    warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")
    warnings.filterwarnings("ignore", category=UserWarning, module="torch")
    warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality.*")
    warnings.filterwarnings("ignore", message=".*You are sending unauthenticated requests.*")
    warnings.filterwarnings("ignore", message=".*UNEXPECTED.*")
    
    # Suppress HuggingFace Hub warnings about authentication
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    
    # Redirect some verbose outputs to reduce noise
    try:
        # Check if we're in non-interactive mode (like Streamlit)
        is_not_tty = hasattr(sys.stdout, 'isatty') and not sys.stdout.isatty()
    except (ValueError, OSError, AttributeError):
        # Handle case where stdout is closed, redirected, or unavailable
        is_not_tty = True  # Assume non-interactive when we can't determine TTY status
    
    if is_not_tty:
        # Only suppress in non-interactive mode (like when running via Streamlit)
        warnings.simplefilter("ignore")

@contextmanager
def suppress_stdout():
    """Context manager to temporarily suppress stdout (for noisy library loading)."""
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def initialize_dependencies():
    """Initialize dependencies with proper warning suppression."""
    suppress_dependency_warnings()
    
    # Try to pre-import problematic modules with warnings suppressed
    try:
        with suppress_stdout():
            import sentence_transformers
            # Let it load models silently on first import
    except ImportError:
        pass
    
    # Don't try to import spaCy if we're on Python 3.14+ due to Pydantic v1 issues
    import sys
    python_version = sys.version_info
    if python_version >= (3, 14):
        try:
            print("ℹ️  Python 3.14+ detected, skipping spaCy initialization (Pydantic v1 compatibility)")
        except (ValueError, OSError):
            # Silently skip print if stdout is closed (e.g., in Streamlit)
            pass
    else:
        try:
            # Suppress spaCy warnings
            import spacy
            # Disable spaCy logging that causes warnings
            spacy.util.set_data_path(spacy.util.get_data_path())
        except Exception:
            # Silently skip spaCy if there are issues
            pass

def print_clean_startup_message():
    """Print a clean startup message after suppressing warnings."""
    try:
        print("🚀 LinkedIn Profile Optimizer")
        print("   ✅ Dependencies loaded successfully")
        print("   🤖 AI-powered PDF extraction ready")
        print("   📊 Profile analysis tools active")
        print()
    except (ValueError, OSError):
        # Silently skip print if stdout is closed (e.g., in Streamlit)
        pass

# Initialize warnings suppression when this module is imported
suppress_dependency_warnings()