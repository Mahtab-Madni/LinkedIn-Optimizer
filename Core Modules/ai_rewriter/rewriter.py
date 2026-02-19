import json
import os
from pathlib import Path
from typing import Generator, List
from groq import Groq
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / "Data & Configuration" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    possible_paths = [
        Path(__file__).parent.parent.parent / "Data & Configuration" / ".env",
        Path(__file__).parent.parent / ".env", 
        Path(".env")
    ]
    for path in possible_paths:
        if path.exists():
            load_dotenv(path)
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                break

# Initialize client only if API key is available
client = None
if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"Warning: Could not initialize Groq client: {e}")
elif not api_key:
    print("Warning: GROQ_API_KEY not found. AI features will be disabled until API key is configured.")
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a world-class LinkedIn profile optimizer and career coach.
You write punchy, keyword-rich, human-sounding LinkedIn content that:
- Passes ATS systems (includes relevant keywords naturally)
- Tells a compelling career story
- Uses metrics and quantified achievements wherever possible
- Sounds authentic — NOT generic or robotic
- Follows LinkedIn best practices for each section

Never use em-dashes (—) excessively. Never start every bullet with "Led" or "Managed".
Vary your language. Be specific. Be human."""


def _call_groq(prompt: str, max_tokens: int = 800) -> str:
    """Standard (non-streaming) Groq call."""
    if not client:
        return "❌ AI feature unavailable: GROQ_API_KEY not configured. Please set your API key in Streamlit Cloud secrets or environment variables."
    
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.7,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error connecting to AI service: {str(e)}"


def _stream_groq(prompt: str, max_tokens: int = 800) -> Generator[str, None, None]:
    """Streaming Groq call — yields text chunks."""
    if not client:
        yield "❌ AI feature unavailable: GROQ_API_KEY not configured. Please set your API key in Streamlit Cloud secrets or environment variables."
        return
    
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.7,
            stream=True,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta
    except Exception as e:
        yield f"❌ Error connecting to AI service: {str(e)}"


def rewrite_headline(
    current_headline: str,
    current_role: str,
    target_role: str,
    top_keywords: List[str],
    user_skills: List[str],
    stream: bool = False,
): 
    keywords_str = ", ".join(top_keywords[:12])
    skills_str = ", ".join(user_skills[:8])

    prompt = f"""Rewrite this LinkedIn headline for someone whose current status is "{current_role}" targeting the role of "{target_role}".

CURRENT ROLE/STATUS: {current_role}
TARGET ROLE: {target_role}
CURRENT HEADLINE: {current_headline or "(empty)"}

USER'S KEY SKILLS: {skills_str}
HIGH-VALUE KEYWORDS FOR THIS ROLE: {keywords_str}

CONTEXT-AWARE REQUIREMENTS:
- Maximum 220 characters (LinkedIn limit)
- Include 2-3 of the high-value keywords naturally
- Adjust tone and approach based on current status:
  * Students/Recent Graduates: Focus on potential, learning, and relevant projects/internships
  * Career Changers: Highlight transferable skills and enthusiasm for new field
  * Experienced Professionals: Emphasize expertise, achievements, and leadership
- Clearly states what they do/aspire to do and the value they bring
- Optionally includes a short unique differentiator
- Do NOT use phrases like "Passionate about" or "Results-driven"
- Output ONLY the headline text, nothing else"""

    if stream:
        return _stream_groq(prompt, max_tokens=100)
    return _call_groq(prompt, max_tokens=100)


def rewrite_about(
    current_about: str,
    current_role: str,
    target_role: str,
    top_keywords: List[str],
    missing_skills: List[str],
    user_skills: List[str],
    experience_titles: List[str],
    stream: bool = False,
):
    """Rewrite the About / Summary section."""
    keywords_str = ", ".join(top_keywords[:15])
    missing_str = ", ".join(missing_skills[:8])
    skills_str = ", ".join(user_skills[:10])
    exp_str = ", ".join(experience_titles[:4])

    prompt = f"""Rewrite this LinkedIn About section for someone whose current status is "{current_role}" targeting "{target_role}".

CURRENT ROLE/STATUS: {current_role}
TARGET ROLE: {target_role}
CURRENT ABOUT: {current_about or "(empty — write from scratch based on context)"}

USER'S SKILLS: {skills_str}
PAST ROLES: {exp_str}
TOP KEYWORDS TO INCLUDE: {keywords_str}
MISSING SKILLS TO WEAVE IN (if genuinely applicable): {missing_str}

CONTEXT-AWARE REQUIREMENTS:
- 150-250 words (ideal LinkedIn about length)
- Adapt narrative arc based on current status:
  * Students/Recent Graduates: Focus on academic projects, internships, eagerness to apply knowledge
  * Career Changers: Highlight transferable skills, reasons for transition, commitment to new field
  * Experienced Professionals: Emphasize track record, leadership, strategic impact
- Start with a strong hook appropriate for their career stage — NOT "I am a..."
- Paragraph 1: Who they are + what they bring (context-appropriate, 2-3 sentences)
- Paragraph 2: Key achievements/projects/relevant experience with metrics when possible
- Paragraph 3: What they're looking for / what excites them about the target role
- End with a subtle CTA appropriate to their status (e.g., "Open to connecting with...")
- Include keywords naturally — do NOT keyword-stuff
- Sound authentic and human, not like a generic template
- Output ONLY the About text, no labels or headers"""

    if stream:
        return _stream_groq(prompt, max_tokens=400)
    return _call_groq(prompt, max_tokens=400)


def rewrite_experience_bullets(
    job_title: str,
    company: str,
    current_description: str,
    current_role: str,
    target_role: str,
    top_keywords: List[str],
    stream: bool = False,
):
    """Rewrite experience bullets for a single role."""
    keywords_str = ", ".join(top_keywords[:10])

    prompt = f"""Rewrite the LinkedIn experience description for this role to better target "{target_role}". The person's current status is "{current_role}".

ROLE: {job_title} at {company}
CURRENT STATUS: {current_role}
TARGET ROLE: {target_role}
CURRENT DESCRIPTION: {current_description or "(no description provided — infer typical responsibilities for this role)"}

TOP KEYWORDS TO INCLUDE: {keywords_str}

CONTEXT-AWARE REQUIREMENTS:
- Write 3-5 bullet points (use • as bullet character)
- Each bullet: Action Verb + What you did + Measurable Impact
- Format: "• [Strong verb] [specific action] resulting in [metric/outcome]"
- Adapt approach based on their current status:
  * Students/Recent Graduates: Focus on learning, projects, contributions despite limited experience
  * Career Changers: Highlight transferable skills and relevance to target role
  * Experienced Professionals: Emphasize leadership, strategic impact, and advanced responsibilities
- If no metrics exist in the original, add realistic placeholder metrics like "[X%]" or "[number]"
- Include 2-3 of the keywords naturally
- Vary the action verbs — no two bullets should start the same way
- Output ONLY the bullet points, no labels"""

    if stream:
        return _stream_groq(prompt, max_tokens=300)
    return _call_groq(prompt, max_tokens=300)


def generate_skills_recommendations(
    current_skills: List[str],
    missing_skills: List[str],
    target_role: str,
) -> str:
    """Suggest which skills to add to the Skills section."""
    current_str = ", ".join(current_skills[:15])
    missing_str = ", ".join(missing_skills[:15])

    prompt = f"""A LinkedIn user targeting "{target_role}" has these skills listed:
CURRENT: {current_str}

These skills appear in top {target_role} profiles but are missing:
MISSING: {missing_str}

Give a brief, actionable recommendation:
1. Which 5 missing skills they should IMMEDIATELY add (if they have them)
2. Which 3 skills they should LEARN next (with a 1-line reason each)
3. Any current skills they should REWORD to match industry terminology

Be specific and practical. Keep it under 200 words."""

    return _call_groq(prompt, max_tokens=350)


def generate_optimization_summary(
    scores: dict,
    gap: dict,
    target_role: str,
) -> str:
    """Generate an executive summary of the optimization results."""
    prompt = f"""Write a brief, encouraging executive summary of a LinkedIn profile optimization for someone targeting "{target_role}".

SCORES:
- Overall score: {scores['overall']}/100
- Semantic match to top profiles: {scores['semantic_similarity']}%
- Skill coverage: {scores['skill_coverage']}%
- Headline: {scores['headline_score']}/15
- About section: {scores['about_score']}/15
- Experience: {scores['experience_score']}/15

GAPS FOUND:
- Missing skills: {', '.join(gap['missing_skills'][:8])}
- Missing power verbs: {', '.join(gap['missing_power_verbs'][:5])}
- Has quantified metrics: {gap['has_quantified_metrics']}

Write 3-4 sentences:
1. Current state assessment (honest but encouraging)
2. Top 2 things that will make the biggest impact
3. What the optimized profile achieves

Tone: Professional, direct, like a career coach. Output ONLY the summary paragraph."""

    return _call_groq(prompt, max_tokens=200)


def rewrite_full_profile(
    user_profile: dict,
    target_role: str,
    top_analysis: dict,
    gap: dict,
) -> dict:
    """
    Rewrite all sections of a profile in one call.
    Returns dict with all rewritten sections.
    """
    top_keywords  = top_analysis.get("top_keywords", [])
    top_skills    = top_analysis.get("top_skills", [])
    missing       = gap.get("missing_skills", [])
    user_skills   = gap.get("present_skills", [])
    exp_titles    = [e.get("title", "") for e in user_profile.get("experience", [])]
    current_role  = user_profile.get("current_role", "")

    results = {}

    # 1. Headline
    results["headline"] = rewrite_headline(
        user_profile.get("headline", ""),
        current_role,
        target_role, top_keywords, user_skills,
    )

    # 2. About
    results["about"] = rewrite_about(
        user_profile.get("about", ""),
        current_role,
        target_role, top_keywords, missing, user_skills, exp_titles,
    )

    # 3. Experience bullets (up to 3 roles)
    results["experience"] = []
    for exp in user_profile.get("experience", [])[:3]:
        rewritten_bullets = rewrite_experience_bullets(
            exp.get("title", ""),
            exp.get("company", ""),
            exp.get("description", ""),
            current_role,
            target_role,
            top_keywords,
        )
        results["experience"].append({
            "title": exp.get("title", ""),
            "company": exp.get("company", ""),
            "original": exp.get("description", ""),
            "rewritten": rewritten_bullets,
        })

    # 4. Skills recommendations
    results["skills_recommendations"] = generate_skills_recommendations(
        user_profile.get("skills", []),
        missing,
        target_role,
    )

    # 5. Summary
    return results
