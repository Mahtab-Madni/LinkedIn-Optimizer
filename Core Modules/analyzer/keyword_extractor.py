import re
import warnings
from collections import Counter
from typing import List, Dict

# Suppress warnings early in the module
warnings.filterwarnings("ignore", category=UserWarning, module="confection")
warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality.*")

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# ── Lazy-load spaCy model ─────────────────────────────────────────
nlp = None
_spacy_initialized = False

def _get_spacy():
    """Lazy-load spaCy model to avoid import issues with Python 3.14+."""
    global nlp, _spacy_initialized
    
    if _spacy_initialized:
        return nlp
    
    _spacy_initialized = True
    
    # Check Python version for Pydantic v1 compatibility
    import sys
    if sys.version_info >= (3, 14):
        if not hasattr(_get_spacy, '_warned'):
            print("ℹ️  Python 3.14+ detected: spaCy unavailable due to Pydantic v1 compatibility")
            print("   Using fallback NLP mode (full functionality still available)")
            _get_spacy._warned = True
        nlp = None
        return nlp
    
    try:
        import spacy
        
        # Suppress spaCy warnings during model loading
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                nlp = spacy.load("en_core_web_sm")
            except (OSError, IOError):
                nlp = spacy.blank("en")
                # Only print this once, quietly
                if not hasattr(_get_spacy, '_model_warned'):
                    print("ℹ️  Using basic spaCy model (en_core_web_sm not found)")
                    _get_spacy._model_warned = True
                    
    except Exception as e:
        # Handle Pydantic compatibility errors specifically
        if "unable to infer type" in str(e) or "ConfigError" in str(e):
            if not hasattr(_get_spacy, '_warned'):
                print("ℹ️  spaCy unavailable (Pydantic v1 compatibility issue)")
                print("   Using fallback NLP mode (full functionality still available)")
                _get_spacy._warned = True
        else:
            if not hasattr(_get_spacy, '_warned'):
                print(f"ℹ️  spaCy unavailable, using fallback NLP mode")
                _get_spacy._warned = True
        nlp = None
    
    return nlp


# ── Curated tech & professional skill vocabulary ─────────────────────────────
TECH_SKILLS = {
    # Programming
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "r", "scala", "php", "ruby", "matlab",
    # Web
    "react", "vue", "angular", "node.js", "django", "flask", "fastapi",
    "next.js", "html", "css", "rest", "graphql", "webpack",
    # Data & ML
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "spark", "hadoop", "airflow", "mlflow", "hugging face", "transformers",
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd",
    "jenkins", "github actions", "linux", "bash",
    # Data
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "snowflake", "bigquery", "databricks", "tableau", "power bi",
    # Soft skills
    "leadership", "communication", "problem solving", "agile", "scrum",
    "project management", "stakeholder management", "mentoring", "collaboration",
    # Business
    "product management", "strategy", "analytics", "kpis", "roadmap",
    "cross-functional", "go-to-market", "revenue growth", "cost optimization",
}

# Action verbs that signal strong bullet points
POWER_VERBS = {
    "led", "built", "designed", "architected", "developed", "launched",
    "optimized", "reduced", "increased", "improved", "managed", "delivered",
    "scaled", "automated", "implemented", "established", "drove", "achieved",
    "spearheaded", "orchestrated", "transformed", "generated", "saved",
    "deployed", "migrated", "integrated", "mentored", "collaborated",
}


def _clean_text(text: str) -> str:
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s\.\+\#]", " ", text)
    return text.lower().strip()


def extract_skills_from_text(text: str) -> List[str]:
    """Extract tech skills and keywords from free text."""
    cleaned = _clean_text(text)
    found = set()

    # 1. Direct match against curated vocab
    for skill in TECH_SKILLS:
        if skill in cleaned:
            found.add(skill)

    # 2. Try spaCy NER — catch ORGs, products, technologies (if available)
    try:
        nlp = _get_spacy()
        if nlp is not None:
            try:
                doc = nlp(text[:50000])  # spaCy limit
                for ent in doc.ents:
                    if ent.label_ in ("ORG", "PRODUCT", "WORK_OF_ART"):
                        token = ent.text.lower().strip()
                        if len(token) > 2 and not token.isdigit():
                            found.add(token)

                # 3. Noun chunks — multi-word skill phrases
                for chunk in doc.noun_chunks:
                    phrase = chunk.text.lower().strip()
                    if phrase in TECH_SKILLS:
                        found.add(phrase)
            except Exception as e:
                print(f"⚠️  spaCy processing failed: {e}. Using basic keyword matching.")
    except Exception as e:
        print(f"⚠️  spaCy initialization failed: {e}. Using basic keyword matching.")
    
    # Fallback: Enhanced regex-based skill extraction
    words = re.findall(r'\b\w+(?:\.\w+)*\b', cleaned)  # Handle things like "node.js"
    for word in words:
        if word in TECH_SKILLS:
            found.add(word)
    
    # Also check for multi-word skills in the text
    for skill in TECH_SKILLS:
        if len(skill.split()) > 1 and skill in cleaned:
            found.add(skill)

    return sorted(found)


def extract_keywords_tfidf(texts: List[str], top_n: int = 30) -> List[str]:
    """
    Use TF-IDF across a corpus of texts to find the most
    important / distinguishing keywords.
    """
    if not texts or all(not t.strip() for t in texts):
        return []

    cleaned = [_clean_text(t) for t in texts]

    vectorizer = TfidfVectorizer(
        max_features=200,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
    )
    try:
        tfidf_matrix = vectorizer.fit_transform(cleaned)
    except ValueError:
        return []

    feature_names = vectorizer.get_feature_names_out()
    mean_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    top_indices = mean_scores.argsort()[::-1][:top_n]
    return [feature_names[i] for i in top_indices]


def extract_power_verbs(text: str) -> List[str]:
    """Find which power action verbs are used in experience bullets."""
    words = set(_clean_text(text).split())
    return sorted(words & POWER_VERBS)


def profile_to_full_text(profile: dict) -> str:
    """Flatten a profile dict into a single text blob for analysis."""
    if not isinstance(profile, dict):
        print(f"❌ Warning: profile_to_full_text received non-dict: {type(profile)}")
        return ""
    
    parts = [
        profile.get("headline", ""),
        profile.get("about", ""),
    ]
    
    # Handle experience with defensive programming
    experience = profile.get("experience", [])
    if not isinstance(experience, list):
        print(f"❌ Warning: experience field is not a list: {type(experience)}")
        experience = []
    
    for exp in experience:
        if isinstance(exp, dict):
            parts.extend([
                exp.get("title", ""),
                exp.get("company", ""),
                exp.get("description", ""),
            ])
        else:
            print(f"❌ Warning: experience entry is not a dict: {type(exp)}")
    
    # Handle skills with defensive programming  
    skills = profile.get("skills", [])
    if not isinstance(skills, list):
        print(f"❌ Warning: skills field is not a list: {type(skills)}")
        skills = []
    
    parts.extend(str(skill) for skill in skills if skill)
    
    return " ".join(str(p) for p in parts if p)


def extract_metrics(text: str) -> List[str]:
    """Extract quantified achievements (numbers + context)."""
    # Patterns: 40%, $2M, 3x, 50K users, 2 years
    pattern = r'\b(\d+(?:\.\d+)?(?:%|x|k|m|b|\+)?)\s*\w{0,20}'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[:10]


def analyze_profile(profile: dict) -> Dict:
    """
    Full analysis of a single profile.
    Returns skills, keywords, power verbs, metrics found.
    """
    if not isinstance(profile, dict):
        print(f"❌ Error: analyze_profile received non-dict: {type(profile)}")
        return {
            "skills": [],
            "tfidf_keywords": [],
            "power_verbs": [],
            "metrics": [],
            "headline_length": 0,
            "about_length": 0,
            "experience_count": 0,
            "skills_count": 0,
        }
    
    try:
        full_text = profile_to_full_text(profile)
        
        # Defensive handling of profile fields
        headline = profile.get("headline", "")
        about = profile.get("about", "")
        experience = profile.get("experience", [])
        skills = profile.get("skills", [])
        
        # Ensure they're the right types
        if not isinstance(headline, str):
            headline = str(headline) if headline else ""
        if not isinstance(about, str):
            about = str(about) if about else ""
        if not isinstance(experience, list):
            experience = []
        if not isinstance(skills, list):
            skills = []

        return {
            "skills": extract_skills_from_text(full_text),
            "tfidf_keywords": extract_keywords_tfidf([full_text], top_n=25) if full_text else [],
            "power_verbs": extract_power_verbs(full_text),
            "metrics": extract_metrics(full_text),
            "headline_length": len(headline.split()),
            "about_length": len(about.split()),
            "experience_count": len(experience),
            "skills_count": len(skills),
        }
        
    except Exception as e:
        print(f"❌ Error in analyze_profile: {str(e)}")
        return {
            "skills": [],
            "tfidf_keywords": [],
            "power_verbs": [],
            "metrics": [],
            "headline_length": 0,
            "about_length": 0,
            "experience_count": 0,
            "skills_count": 0,
        }


def analyze_top_profiles(profiles: List[dict]) -> Dict:
    """
    Analyze a collection of top profiles to find common patterns.
    Returns aggregated insights.
    """
    all_skills = Counter()
    all_keywords = Counter()
    all_verbs = Counter()
    all_texts = []

    for p in profiles:
        full_text = profile_to_full_text(p)
        all_texts.append(full_text)
        analysis = analyze_profile(p)
        all_skills.update(analysis["skills"])
        all_verbs.update(analysis["power_verbs"])

    # TF-IDF across all top profiles
    corpus_keywords = extract_keywords_tfidf(all_texts, top_n=40)
    for kw in corpus_keywords:
        all_keywords[kw] += 1

    avg_headline_len = np.mean([
        len(p.get("headline", "").split()) for p in profiles
    ]) if profiles else 0

    avg_about_len = np.mean([
        len(p.get("about", "").split()) for p in profiles
    ]) if profiles else 0

    return {
        "top_skills": [s for s, _ in all_skills.most_common(25)],
        "top_keywords": corpus_keywords[:25],
        "top_verbs": [v for v, _ in all_verbs.most_common(15)],
        "avg_headline_length": round(avg_headline_len, 1),
        "avg_about_length": round(avg_about_len, 1),
        "profile_count": len(profiles),
    }
