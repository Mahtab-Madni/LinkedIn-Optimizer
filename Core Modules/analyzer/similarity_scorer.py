import numpy as np
import warnings
from typing import List, Dict

# Suppress transformer warnings early
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", message=".*You are sending unauthenticated requests.*")

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .keyword_extractor import (
    profile_to_full_text,
    extract_skills_from_text,
    extract_power_verbs,
    extract_metrics,
    TECH_SKILLS,
)


# Load model once (cached after first call)
_model = None

def _get_model():
    global _model
    if _model is None and TRANSFORMERS_AVAILABLE:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Suppress all stdout during model loading to avoid progress bars and logs
            import os
            import sys
            with open(os.devnull, 'w') as devnull:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                try:
                    sys.stdout = devnull
                    sys.stderr = devnull
                    _model = SentenceTransformer("all-MiniLM-L6-v2")
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
    return _model


def _embed(texts: List[str]) -> np.ndarray:
    """Embed a list of texts into vectors."""
    model = _get_model()
    if model is None:
        # Fallback: simple bag-of-words overlap
        return None
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)


def semantic_similarity_score(user_text: str, benchmark_texts: List[str]) -> float:
    """
    Compute mean cosine similarity between user profile
    and a list of benchmark (top) profiles.
    Returns score 0-100.
    """
    if not benchmark_texts:
        return 0.0

    embeddings = _embed([user_text] + benchmark_texts)

    if embeddings is None:
        # Fallback: keyword overlap ratio
        user_words = set(user_text.lower().split())
        scores = []
        for bt in benchmark_texts:
            bench_words = set(bt.lower().split())
            overlap = len(user_words & bench_words)
            union = len(user_words | bench_words)
            scores.append(overlap / union if union > 0 else 0)
        return round(np.mean(scores) * 100, 1)

    user_vec = embeddings[0:1]
    bench_vecs = embeddings[1:]
    sims = cosine_similarity(user_vec, bench_vecs)[0]
    return round(float(np.mean(sims)) * 100, 1)


def keyword_gap_analysis(user_profile: dict, top_profile_analysis: dict) -> Dict:
    """
    Compare user's skills/keywords against top profiles.
    Returns missing skills, missing keywords, and coverage scores.
    """
    try:
        if not isinstance(user_profile, dict):
            print(f"❌ Error: user_profile is not a dict: {type(user_profile)}")
            return {
                "missing_skills": [],
                "present_skills": [],
                "skill_coverage_pct": 0,
                "missing_keywords": [],
                "missing_power_verbs": [],
                "present_power_verbs": [],
                "has_quantified_metrics": False,
                "metrics_found": [],
            }
            
        if not isinstance(top_profile_analysis, dict):
            print(f"❌ Error: top_profile_analysis is not a dict: {type(top_profile_analysis)}")
            return {
                "missing_skills": [],
                "present_skills": [],
                "skill_coverage_pct": 0,
                "missing_keywords": [],
                "missing_power_verbs": [],
                "present_power_verbs": [],
                "has_quantified_metrics": False,
                "metrics_found": [],
            }
        
        user_text = profile_to_full_text(user_profile)
        user_skills = set(extract_skills_from_text(user_text))
        user_keywords = set(user_text.lower().split()) if user_text else set()

        top_skills = set(top_profile_analysis.get("top_skills", []))
        top_keywords = set(top_profile_analysis.get("top_keywords", []))
        top_verbs = set(top_profile_analysis.get("top_verbs", []))

        # Skills gap
        missing_skills = sorted(top_skills - user_skills) if top_skills and user_skills else list(top_skills)
        present_skills = sorted(top_skills & user_skills) if top_skills and user_skills else []
        skill_coverage = round(len(present_skills) / len(top_skills) * 100, 1) if top_skills else 0

        # Keyword gap
        missing_keywords = [kw for kw in top_keywords if kw not in user_keywords][:15] if top_keywords and user_keywords else []

        # Verb gap
        user_verbs = set(extract_power_verbs(user_text)) if user_text else set()
        missing_verbs = sorted(top_verbs - user_verbs)[:8] if top_verbs and user_verbs else []
        present_verbs = sorted(top_verbs & user_verbs) if top_verbs and user_verbs else []

        # Metrics check
        user_metrics = extract_metrics(user_text) if user_text else []
        has_metrics = len(user_metrics) > 0

        return {
            "missing_skills": missing_skills[:15],
            "present_skills": present_skills[:15],
            "skill_coverage_pct": skill_coverage,
            "missing_keywords": missing_keywords,
            "missing_power_verbs": missing_verbs,
            "present_power_verbs": present_verbs,
            "has_quantified_metrics": has_metrics,
            "metrics_found": user_metrics[:5],
        }
        
    except Exception as e:
        print(f"❌ Error in keyword_gap_analysis: {str(e)}")
        return {
            "missing_skills": [],
            "present_skills": [],
            "skill_coverage_pct": 0,
            "missing_keywords": [],
            "missing_power_verbs": [],
            "present_power_verbs": [],
            "has_quantified_metrics": False,
            "metrics_found": [],
        }


def score_profile_section(section: str, benchmark_avg_length: int, text: str) -> Dict:
    """Score a specific section (headline / about) vs benchmarks."""
    word_count = len(text.split())
    length_score = min(100, (word_count / max(benchmark_avg_length, 1)) * 100)

    has_keywords = len(extract_skills_from_text(text)) > 0
    has_metrics = len(extract_metrics(text)) > 0

    scores = {
        "length_score": round(length_score, 1),
        "has_keywords": has_keywords,
        "has_metrics": has_metrics,
        "word_count": word_count,
        "benchmark_avg_words": benchmark_avg_length,
    }
    return scores


def compute_overall_score(
    user_profile: dict,
    top_profiles: List[dict],
    top_analysis: dict,
    gap: dict,
) -> Dict:
    user_text = profile_to_full_text(user_profile)
    bench_texts = [profile_to_full_text(p) for p in top_profiles]

    # 1. Semantic similarity (30 pts)
    sim_score = semantic_similarity_score(user_text, bench_texts)
    semantic_pts = round(sim_score * 0.30, 1)

    # 2. Skill coverage (25 pts)
    skill_pts = round(gap["skill_coverage_pct"] * 0.25, 1)

    # 3. Headline score (15 pts)
    headline = user_profile.get("headline", "")
    headline_pts = 0
    if len(headline.split()) >= 5:
        headline_pts += 7
    if extract_skills_from_text(headline):
        headline_pts += 8

    # 4. About section (15 pts)
    about = user_profile.get("about", "")
    about_pts = 0
    if len(about.split()) >= 50:
        about_pts += 5
    if len(about.split()) >= 100:
        about_pts += 5
    if extract_metrics(about):
        about_pts += 5

    # 5. Experience bullets (15 pts)
    exp_pts = 0
    for exp in user_profile.get("experience", [])[:3]:
        desc = exp.get("description", "")
        if extract_power_verbs(desc):
            exp_pts += 3
        if extract_metrics(desc):
            exp_pts += 2
    exp_pts = min(15, exp_pts)

    total = round(semantic_pts + skill_pts + headline_pts + about_pts + exp_pts, 1)
    total = min(100, total)

    return {
        "overall": total,
        "semantic_similarity": round(sim_score, 1),
        "skill_coverage": gap["skill_coverage_pct"],
        "headline_score": headline_pts,
        "about_score": about_pts,
        "experience_score": exp_pts,
        "breakdown": {
            "Semantic Match (30pts)": semantic_pts,
            "Skill Coverage (25pts)": skill_pts,
            "Headline Quality (15pts)": headline_pts,
            "About Section (15pts)": about_pts,
            "Experience Bullets (15pts)": exp_pts,
        },
    }
