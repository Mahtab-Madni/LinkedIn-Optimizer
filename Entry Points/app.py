"""
app.py  —  LinkedIn Profile Optimizer
Main Streamlit UI
"""

import streamlit as st
import json
import sys
import os

# Add paths for the new folder structure
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
core_modules_path = os.path.join(parent_dir, "Core Modules")
sys.path.insert(0, current_dir)
sys.path.insert(0, core_modules_path)

# Suppress dependency warnings early
from utils.warnings_handler import initialize_dependencies, print_clean_startup_message

# Initialize with clean startup  
initialize_dependencies()

from analyzer.keyword_extractor  import analyze_profile, analyze_top_profiles, profile_to_full_text
from analyzer.similarity_scorer  import keyword_gap_analysis, compute_overall_score
from ai_rewriter.rewriter        import (
    rewrite_headline, rewrite_about, rewrite_experience_bullets,
    generate_skills_recommendations, generate_optimization_summary,
    rewrite_full_profile,
)
from scrapper.linkedin_scraper    import parse_manual_profile

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LinkedIn Optimizer · AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium Styling ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cabinet+Grotesk:wght@400;500;700;800&family=Lora:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #f8f7f4;
    --surface:  #ffffff;
    --navy:     #0f172a;
    --indigo:   #6366f1;
    --indigo2:  #4f46e5;
    --green:    #10b981;
    --red:      #ef4444;
    --gold:     #f59e0b;
    --muted:    #64748b;
    --border:   #e2e8f0;
    --card:     #ffffff;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
    color: var(--navy) !important;
}

[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

h1, h2, h3 { font-family: 'Cabinet Grotesk', sans-serif !important; font-weight: 800 !important; }

.stButton > button {
    background: var(--indigo) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.6rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: var(--indigo2) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 20px !important;
    padding: 0 10px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'Cabinet Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 12px 20px !important;
    margin: 0 5px !important;
    border-radius: 8px 8px 0 0 !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    color: var(--indigo) !important;
    border-bottom: 2px solid var(--indigo) !important;
    background: transparent !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Cabinet Grotesk', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
    color: var(--navy) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

.stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--surface) !important;
}
.stTextInput input {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

/* Custom components */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #312e81 100%);
    border-radius: 20px;
    padding: 2.5rem 2.8rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: white;
    line-height: 1.1;
    margin-bottom: 0.4rem;
}
.hero-sub {
    font-family: 'Lora', serif;
    font-style: italic;
    color: #a5b4fc;
    font-size: 1.1rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.3);
    border: 1px solid rgba(165,180,252,0.4);
    color: #c7d2fe;
    border-radius: 20px;
    padding: 0.25rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin: 0.6rem 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.card-accent { border-left: 4px solid var(--indigo); }
.card-green  { border-left: 4px solid var(--green);  }
.card-red    { border-left: 4px solid var(--red);    }
.card-gold   { border-left: 4px solid var(--gold);   }

.section-header {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--indigo);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    margin-top: 0.2rem;
}

.score-ring {
    font-family: 'Cabinet Grotesk', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    line-height: 1;
}

.before-after {
    display: grid;
    gap: 1rem;
}
.before-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 1rem;
    font-size: 0.88rem;
    line-height: 1.6;
}
.after-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
    padding: 1rem;
    font-size: 0.88rem;
    line-height: 1.6;
}

.tag {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 600;
    margin: 0.18rem;
}
.tag-red    { background: #fee2e2; color: #dc2626; }
.tag-green  { background: #d1fae5; color: #059669; }
.tag-indigo { background: #e0e7ff; color: #4338ca; }
.tag-gold   { background: #fef3c7; color: #d97706; }

.streaming-box {
    background: #f8faff;
    border: 1px solid #c7d2fe;
    border-radius: 12px;
    padding: 1.2rem;
    font-family: 'Lora', serif;
    font-size: 0.95rem;
    line-height: 1.8;
    min-height: 60px;
}

.step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: var(--indigo);
    color: white;
    border-radius: 50%;
    font-size: 0.8rem;
    font-weight: 700;
    margin-right: 0.5rem;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ──────────────────────────────────────────────────────────
def generate_ai_enhanced_benchmarks(target_role: str) -> list:
    """Generate AI-enhanced benchmark profiles based on target role."""
    role_benchmarks = {
        "data scientist": {
            "skills": ["Python", "Machine Learning", "SQL", "TensorFlow", "PyTorch", "Statistics", "A/B Testing", "AWS", "Docker", "Git"],
            "experience_desc": "Built end-to-end ML pipelines processing 10M+ daily events. Improved model accuracy by 25% using advanced feature engineering. Led cross-functional team of 5 data professionals. Deployed models serving 100K+ predictions/day.",
            "about_template": "Passionate Data Scientist with 5+ years building ML solutions at scale. Expert in deep learning, statistical modeling, and big data analytics. Proven track record of delivering business impact through data-driven insights and production ML systems."
        },
        "software engineer": {
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redis", "Git"],
            "experience_desc": "Architected microservices handling 1M+ requests/day. Reduced API latency by 60% through optimization. Led migration to cloud-native architecture. Mentored 3 junior engineers and established coding standards.",
            "about_template": "Senior Software Engineer with expertise in full-stack development and cloud architecture. 6+ years building scalable web applications and distributed systems. Passionate about clean code, performance optimization, and technical leadership."
        },
        "product manager": {
            "skills": ["Product Strategy", "User Research", "Analytics", "A/B Testing", "Roadmapping", "Agile", "SQL", "Figma", "JIRA", "Stakeholder Management"],
            "experience_desc": "Launched 3 major features driving 40% user engagement increase. Led cross-functional teams of 12 engineers and designers. Conducted 50+ user interviews and validated product-market fit. Grew revenue by $2M through data-driven product decisions.",
            "about_template": "Strategic Product Manager with 4+ years driving product growth and user satisfaction. Expert in data analysis, user research, and go-to-market strategy. Proven ability to translate business objectives into successful product outcomes."
        }
    }
    
    # Get role-specific data or use generic template
    role_key = target_role.lower().replace(" ", " ").strip()
    role_data = None
    for key in role_benchmarks:
        if key in role_key or role_key in key:
            role_data = role_benchmarks[key]
            break
    
    if not role_data:
        # Generic template for unknown roles
        role_data = {
            "skills": ["Leadership", "Communication", "Project Management", "Analytics", "Strategy", "Problem Solving"],
            "experience_desc": f"Led high-impact initiatives in {target_role} role. Delivered measurable business results through strategic planning and execution. Collaborated with cross-functional teams to drive organizational success.",
            "about_template": f"Experienced {target_role} with proven track record of success. Expert in strategic thinking, stakeholder management, and delivering results in fast-paced environments."
        }
    
    return [{
        "url": "ai_enhanced_benchmark",
        "name": f"AI-Enhanced {target_role} Benchmark",
        "headline": f"Senior {target_role} | {role_data['skills'][0]} Expert | 5+ Years Experience",
        "about": role_data["about_template"],
        "experience": [{
            "title": f"Senior {target_role}",
            "company": "Leading Tech Company",
            "description": role_data["experience_desc"]
        }],
        "skills": role_data["skills"],
        "education": [],
        "certifications": []
    }]

# ── Session State ─────────────────────────────────────────────────────────────
for key in ["user_profile", "top_profiles", "user_analysis", "top_analysis",
            "gap", "scores", "rewritten", "optimization_done"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "optimization_done" not in st.session_state:
    st.session_state.optimization_done = False


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⬡ LinkedIn Optimizer")
    st.markdown("---")
    
    # Mode Selection
    st.markdown('<p style="color:#94a3b8;font-size:0.8rem;">CHOOSE YOUR MODE</p>', unsafe_allow_html=True)
    optimization_mode = st.radio(
        "Select optimization approach",
        ["🤖 AI Enhancement Mode", "📊 Benchmark Comparison Mode"],
        help="AI Mode: Get recommendations based on target role analysis. Benchmark Mode: Compare against specific top profiles.",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown('<p style="color:#94a3b8;font-size:0.8rem;">STEP 1 — YOUR PROFILE</p>', unsafe_allow_html=True)

    input_mode = st.radio(
        "Input method",
        ["✏️ Manual Input (Recommended)", "📄 Upload LinkedIn PDF", "⚙️ LinkedIn URL (May have Chrome issues)"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    
    # Conditional Step 2 based on mode
    if "AI Enhancement" in optimization_mode:
        st.markdown('<p style="color:#94a3b8;font-size:0.8rem;">STEP 2 — TARGET ROLE FOCUS</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#1e293b;padding:1rem;border-radius:8px;margin-bottom:1rem;">
            <div style="color:#10b981;font-weight:600;margin-bottom:0.5rem;">🤖 AI Enhancement Mode</div>
            <div style="color:#e2e8f0;font-size:0.85rem;">Get personalized recommendations based on your target role. AI analyzes industry trends and best practices.</div>
        </div>
        """, unsafe_allow_html=True)
        
        bench_texts = []  # No benchmark profiles needed in AI mode
        uploaded_benchmark_files = []  # Initialize for consistency
        benchmark_input_method = "N/A"  # Not applicable in AI mode
        
    else:  # Benchmark Comparison Mode
        st.markdown('<p style="color:#94a3b8;font-size:0.8rem;">STEP 2 — BENCHMARK PROFILES</p>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#1e293b;padding:1rem;border-radius:8px;margin-bottom:1rem;">
            <div style="color:#6366f1;font-weight:600;margin-bottom:0.5rem;">📊 Benchmark Comparison Mode</div>
            <div style="color:#e2e8f0;font-size:0.85rem;">Upload PDF profiles of top performers in your target role or paste as text.</div>
        </div>
        """, unsafe_allow_html=True)
        
        benchmark_input_method = st.radio(
            "Benchmark input method",
            ["📄 Upload PDF Profiles", "📝 Paste Text Profiles"],
            help="Upload: More accurate extraction. Text: Quick manual input."
        )
        
        bench_texts = []
        uploaded_benchmark_files = []
        
        if "Upload PDF" in benchmark_input_method:
            st.caption("Upload 2-3 LinkedIn PDF profiles of top performers")
            
            for i in range(1, 4):
                uploaded_file = st.file_uploader(
                    f"Benchmark Profile {i} PDF",
                    type=['pdf'],
                    key=f"bench_pdf_{i}",
                    help="Download from LinkedIn: Profile → More → Save to PDF"
                )
                if uploaded_file:
                    uploaded_benchmark_files.append(uploaded_file)
                    
        else:  # Text input
            st.caption("Paste 2–3 top LinkedIn profiles for your target role (as plain text)")
            for i in range(1, 4):
                t = st.text_area(f"Benchmark Profile {i}", height=80, key=f"bench_{i}",
                                 placeholder=f"Paste profile {i} text here…")
                if t.strip():
                    bench_texts.append(t.strip())

    st.markdown("---")
    st.caption("Powered by Groq · Llama 3.3 70B · spaCy · sentence-transformers")


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">⬡ AI-Powered · Free to Use</div>
    <div class="hero-title">LinkedIn Profile<br>Optimizer</div>
    <div class="hero-sub">Two optimization modes: AI-enhanced recommendations or benchmark comparison with PDF uploads</div>
</div>
""", unsafe_allow_html=True)


# ── Input Section ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown('<div class="section-header">Your Profile Details</div>', unsafe_allow_html=True)

    if "Manual" in input_mode:
        name        = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
        current_role = st.text_input("Current Role/Status", placeholder="e.g. Student, Software Engineer, Career Changer, Recent Graduate")
        target_role = st.text_input("Target Role", placeholder="e.g. Data Scientist, Backend Engineer, Product Manager")
        headline    = st.text_input("Current Headline", placeholder="e.g. Software Engineer at XYZ | Python | AWS")
        about       = st.text_area("About Section", height=130,
                                   placeholder="Paste your current About/Summary section here…")
        experience  = st.text_area("Experience (paste all roles)", height=160,
                                   placeholder="Software Engineer at Google\nBuilt microservices...\n\nData Analyst at Infosys\nAnalyzed datasets...")
        skills_raw  = st.text_input("Skills (comma separated)",
                                    placeholder="Python, SQL, Machine Learning, AWS, Docker…")
        use_ai_parsing = True  # Default for manual mode
    elif "PDF" in input_mode:
        st.markdown("""
        <div class="card card-green">
            <strong>📄 Upload LinkedIn PDF Profile</strong><br><br>
            <strong>How to get your LinkedIn PDF:</strong>
            <ol style="margin:0.5rem 0 0 1.2rem;">
                <li>Go to your LinkedIn profile</li>
                <li>Click "More" button → "Save to PDF"</li>
                <li>Download the PDF file</li>
                <li>Upload it below</li>
            </ol>
            <strong>💡 Benefits:</strong> Quick setup, preserves formatting, includes all sections
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your LinkedIn PDF file", 
            type=['pdf'],
            help="Download your profile PDF from LinkedIn: Profile → More → Save to PDF"
        )
        
        # AI parsing option
        use_ai_parsing = st.checkbox(
            "🤖 Use AI-powered extraction (Recommended)",
            value=True,
            help="Uses advanced AI to extract profile information more accurately. Falls back to basic parsing if AI is unavailable."
        )
        
        current_role = st.text_input("Current Role/Status", placeholder="e.g. Student, Software Engineer, Career Changer, Recent Graduate")
        target_role = st.text_input("Target Role", placeholder="e.g. Data Scientist, Backend Engineer, Product Manager")
        
        # Initialize variables for PDF mode
        name = headline = about = experience = skills_raw = ""
    else:
        st.markdown("""
        <div class="card card-gold">
            <strong>⚠️ URL Scraping Requirements & Common Issues</strong><br><br>
            <strong>Requirements:</strong> Chrome browser + ChromeDriver versions must match<br>
            <strong>Common Issue:</strong> Chrome/ChromeDriver version mismatch (like the error you just saw)<br><br>
            <strong>💡 Recommendation:</strong> Use <strong>Manual Input</strong> instead - it's:
            <ul style="margin:0.5rem 0 0 1.2rem;">
                <li>✅ More reliable (no browser issues)</li>
                <li>✅ Faster setup</li>  
                <li>✅ Same great results</li>
                <li>✅ No Chrome version conflicts</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        profile_url = st.text_input("LinkedIn Profile URL", placeholder="https://linkedin.com/in/username")
        li_email    = st.text_input("LinkedIn Email", type="default")
        li_pass     = st.text_input("LinkedIn Password", type="password")
        current_role = st.text_input("Current Role/Status", placeholder="e.g. Student, Software Engineer, Career Changer, Recent Graduate")
        target_role = st.text_input("Target Role", placeholder="e.g. Data Scientist")
        name = headline = about = experience = skills_raw = ""
        use_ai_parsing = True  # Default for URL mode

with col_right:
    st.markdown('<div class="section-header">How It Works</div>', unsafe_allow_html=True)
    
    # Show different steps based on the selected mode
    if "optimization_mode" in locals() and "AI Enhancement" in optimization_mode:
        steps = [
            ("01", "Choose AI Enhancement Mode"),
            ("02", "Enter your profile (manual, PDF, or URL)"),
            ("03", "Specify your target role"),
            ("04", "AI analyzes industry trends & best practices"),
            ("05", "Get personalized recommendations & rewrite"),
        ]
    else:
        steps = [
            ("01", "Choose Benchmark Comparison Mode"),
            ("02", "Upload your profile (manual, PDF, or URL)"),
            ("03", "Upload benchmark PDFs or paste text"),
            ("04", "AI compares & identifies gaps"),
            ("05", "Download optimized profile report"),
        ]
    
    for num, desc in steps:
        st.markdown(f"""
        <div class="card" style="padding:0.8rem 1rem;margin:0.3rem 0;">
            <span class="step-badge">{num}</span>
            <span style="font-size:0.88rem;">{desc}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">What Gets Analyzed</div>', unsafe_allow_html=True)
    features = ["Semantic similarity to top profiles", "Skill & keyword gap detection",
                "Power verb usage scoring", "Quantified metrics check",
                "Section-by-section quality score", "AI-powered recommendations"]
    for f in features:
        st.markdown(f'<span class="tag tag-indigo">✓ {f}</span>', unsafe_allow_html=True)


# ── Optimize Button ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    run_btn = st.button("⚡ Analyze & Optimize My Profile", use_container_width=True)

st.markdown("---")


# ── MAIN ANALYSIS PIPELINE ────────────────────────────────────────────────────
if run_btn:
    if not target_role:
        st.error("Please enter a target role.")
        st.stop()
    
    if not current_role:
        st.error("Please enter your current role or status (e.g., 'Student', 'Software Engineer', 'Recent Graduate').")
        st.stop()

    # Build user profile
    if "Manual" in input_mode:
        if not name and not headline and not about:
            st.error("Please fill in at least your name, headline, and about section.")
            st.stop()
        user_profile = parse_manual_profile(name, current_role, headline, about, experience, skills_raw)
    elif "PDF" in input_mode:
        if uploaded_file is None:
            st.error("Please upload your LinkedIn PDF file.")
            st.stop()
        try:
            if use_ai_parsing:
                from scrapper.linkedin_scraper import parse_linkedin_pdf_with_ai
                with st.spinner("🤖 AI-powered PDF parsing in progress..."):
                    user_profile = parse_linkedin_pdf_with_ai(uploaded_file)
                    
                # Override current_role with user input if provided
                if current_role:
                    user_profile["current_role"] = current_role
                elif not user_profile.get("current_role"):
                    user_profile["current_role"] = "Professional"  # Default fallback
            else:
                from scrapper.linkedin_scraper import parse_linkedin_pdf
                with st.spinner("📄 Basic PDF parsing in progress..."):
                    user_profile = parse_linkedin_pdf(uploaded_file)
                
            # Override current_role with user input if provided
            if current_role:
                user_profile["current_role"] = current_role
            elif not user_profile.get("current_role"):
                user_profile["current_role"] = "Professional"  # Default fallback
                
            # Show extracted information for user verification
            parsing_method = "AI-powered" if use_ai_parsing else "Basic"
            st.success(f"✅ PDF parsed successfully using {parsing_method} extraction!")
            with st.expander("📋 Extracted Profile Information", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {user_profile.get('name', 'Not found')}")
                    st.write(f"**Current Role:** {user_profile.get('current_role', 'Not found')}")
                    st.write(f"**Headline:** {user_profile.get('headline', 'Not found')}")
                    st.write(f"**Location:** {user_profile.get('location', 'Not found')}")
                with col2:
                    st.write(f"**Skills:** {len(user_profile.get('skills', []))} found")
                    st.write(f"**Experience:** {len(user_profile.get('experience', []))} roles found")
                    st.write(f"**Education:** {len(user_profile.get('education', []))} entries found")
                
                if user_profile.get('about'):
                    st.write(f"**About:** {user_profile['about'][:200]}...")
                
                # Show additional details for AI parsing
                if use_ai_parsing and user_profile.get('url') == 'pdf_upload_ai':
                    if user_profile.get('experience'):
                        st.write("**📋 Experience Extracted:**")
                        for i, exp in enumerate(user_profile['experience'][:3], 1):
                            st.write(f"{i}. {exp.get('title', 'N/A')} at {exp.get('company', 'N/A')} ({exp.get('duration', 'N/A')})")
                    
                    if user_profile.get('education'):
                        st.write("**🎓 Education Extracted:**")
                        for edu in user_profile['education'][:2]:
                            degree_info = f"{edu.get('degree', '')} {edu.get('field', '')}".strip()
                            st.write(f"• {edu.get('school', 'N/A')} - {degree_info or 'N/A'}")
                    
                    if user_profile.get('certifications'):
                        st.write(f"**🏆 Certifications:** {', '.join(user_profile['certifications'][:5])}")
                    
        except Exception as e:
            st.error(f"❌ **PDF parsing failed:** {e}")
            st.info("💡 **Try Manual Input mode** if PDF parsing doesn't work properly!")
            st.stop()
    else:
        try:
            from scrapper.linkedin_scraper import scrape_profile
            user_profile = scrape_profile(profile_url, li_email, li_pass)
            
            # Add current_role to scraped profile
            if current_role:
                user_profile["current_role"] = current_role
            elif not user_profile.get("current_role"):
                user_profile["current_role"] = "Professional"  # Default fallback
        except Exception as e:
            error_msg = str(e)
            
            # Provide specific guidance for common Chrome/ChromeDriver issues
            if "Chrome" in error_msg or "ChromeDriver" in error_msg or "session not created" in error_msg:
                st.error("🔧 **Chrome/ChromeDriver Version Mismatch**")
                st.markdown("""
                **Quick Fix Options:**
                1. **👈 Switch to Manual Input** (recommended - works perfectly!)
                2. Update Chrome: `chrome://settings/help`
                3. Update ChromeDriver: `pip install --upgrade undetected-chromedriver`
                
                💡 **Manual input works just as well and avoids browser compatibility issues!**
                """)
            else:
                st.error(f"❌ **Scraping failed:** {error_msg}")
                st.info("💡 **Try Manual Input mode** - it's more reliable and works perfectly for profile optimization!")
            
            st.stop()

    # Build benchmark profiles based on mode
    top_profiles = []
    
    if "AI Enhancement" in optimization_mode:
        # AI Enhancement Mode: Use synthetic role-specific benchmarks
        top_profiles = generate_ai_enhanced_benchmarks(target_role)
        
    else:
        # Benchmark Comparison Mode: Process uploaded PDFs or text
        if "Upload PDF" in benchmark_input_method and uploaded_benchmark_files:
            # Process uploaded PDF benchmark files
            for i, pdf_file in enumerate(uploaded_benchmark_files):
                try:
                    with st.spinner(f"Processing benchmark PDF {i+1}..."):
                        if use_ai_parsing:  # Use same AI parsing setting as main profile
                            from scrapper.linkedin_scraper import parse_linkedin_pdf_with_ai
                            benchmark_profile = parse_linkedin_pdf_with_ai(pdf_file)
                        else:
                            from scrapper.linkedin_scraper import parse_linkedin_pdf
                            benchmark_profile = parse_linkedin_pdf(pdf_file)
                        
                        benchmark_profile["url"] = f"benchmark_pdf_{i}"
                        benchmark_profile["name"] = benchmark_profile.get("name") or f"Benchmark {i+1}"
                        top_profiles.append(benchmark_profile)
                        
                except Exception as e:
                    st.warning(f"Failed to parse benchmark PDF {i+1}: {e}")
                    continue
                    
        elif bench_texts:
            # Process pasted text benchmarks
            for i, bt in enumerate(bench_texts):
                top_profiles.append({
                    "url": f"benchmark_text_{i}",
                    "name": f"Benchmark {i+1}",
                    "headline": bt[:200],
                    "about": bt,
                    "experience": [],
                    "skills": [],
                })
        
        # If no benchmarks provided in benchmark mode, use synthetic ones
        if not top_profiles:
            st.warning("No benchmark profiles provided. Using AI-generated benchmarks.")
            top_profiles = generate_ai_enhanced_benchmarks(target_role)

    st.session_state.user_profile = user_profile
    st.session_state.top_profiles = top_profiles

    # ── Run analysis pipeline ──────────────────────────────────────────────
    progress = st.progress(0, text="Analyzing your profile…")

    user_analysis = analyze_profile(user_profile)
    progress.progress(15, text="Analyzing benchmark profiles…")

    top_analysis  = analyze_top_profiles(top_profiles)
    progress.progress(30, text="Computing keyword gaps…")

    gap = keyword_gap_analysis(user_profile, top_analysis)
    progress.progress(45, text="Scoring your profile…")

    scores = compute_overall_score(user_profile, top_profiles, top_analysis, gap)
    
    # Debug: Check if scoring worked
    if scores:
        st.write(f"✅ Profile scoring successful. Overall score: {scores.get('total', 'unknown')}")
    else:
        st.error("❌ Profile scoring failed")
        
    progress.progress(60, text="AI rewriting headline…")

    # Stream headline
    st.session_state.user_analysis = user_analysis
    st.session_state.top_analysis  = top_analysis
    st.session_state.gap            = gap
    st.session_state.scores         = scores

    # Full rewrite (non-streaming for pipeline)
    try:
        st.write("🔄 Starting AI profile rewrite...")
        rewritten = rewrite_full_profile(user_profile, target_role, top_analysis, gap)
        
        if rewritten and isinstance(rewritten, dict):
            st.write(f"✅ AI rewrite successful. Generated {len(rewritten)} sections:")
            for section_name, content in rewritten.items():
                if content and not content.startswith("❌"):
                    st.write(f"  - {section_name}: {len(str(content))} chars")
                else:
                    st.write(f"  - ❌ {section_name}: {content}")
        else:
            st.error(f"❌ AI rewrite failed. Result: {rewritten}")
            
    except Exception as e:
        st.error(f"❌ Error during AI rewrite: {str(e)}")
        st.exception(e)
        rewritten = {}
    progress.progress(95, text="Generating optimization summary…")

    opt_summary = generate_optimization_summary(scores, gap, target_role)
    rewritten["summary"] = opt_summary
    rewritten["target_role"] = target_role

    st.session_state.rewritten         = rewritten
    st.session_state.optimization_mode = optimization_mode
    st.session_state.optimization_done = True
    progress.progress(100, text="Done!")
    progress.empty()
    st.rerun()


# ── RESULTS ───────────────────────────────────────────────────────────────────
if st.session_state.optimization_done and st.session_state.scores:
    scores   = st.session_state.scores
    gap      = st.session_state.gap
    rewritten = st.session_state.rewritten
    user_profile = st.session_state.user_profile
    top_analysis = st.session_state.top_analysis
    target_role  = rewritten.get("target_role", "")

    tabs = st.tabs([
        "📊 Score & Summary",
        "🏷️ Headline",
        "📝 About Section",
        "💼 Experience",
        "🔍 Skill Gaps",
        "📥 Export",
    ])

    # ── TAB 1: Score ─────────────────────────────────────────────────────────
    with tabs[0]:
        overall = scores["overall"]
        color   = "#10b981" if overall >= 70 else "#f59e0b" if overall >= 50 else "#ef4444"
        grade   = "A" if overall >= 80 else "B" if overall >= 65 else "C" if overall >= 50 else "D"

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Overall Score", f"{overall:.0f}/100")
        m2.metric("Grade", grade)
        m3.metric("Semantic Match", f"{scores['semantic_similarity']:.0f}%")
        m4.metric("Skill Coverage", f"{scores['skill_coverage']:.0f}%")
        m5.metric("Missing Skills", len(gap.get("missing_skills", [])))

        st.markdown("<br>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<div class="section-header">Score Breakdown</div>', unsafe_allow_html=True)
            for label, pts in scores.get("breakdown", {}).items():
                max_pts_str = label.split("(")[1].replace("pts)", "") if "(" in label else "100"
                max_pts = int(max_pts_str)
                pct = pts / max_pts
                bar_color = "#10b981" if pct >= 0.7 else "#f59e0b" if pct >= 0.4 else "#ef4444"
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;font-size:0.82rem;font-weight:600;margin-bottom:3px;">
                        <span>{label}</span>
                        <span style="color:{bar_color};">{pts:.0f}/{max_pts}</span>
                    </div>
                    <div style="background:#e2e8f0;border-radius:4px;height:8px;overflow:hidden;">
                        <div style="width:{pct*100:.0f}%;height:100%;background:{bar_color};border-radius:4px;transition:width 0.5s;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-header">AI Assessment</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card card-accent">
                <div style="font-size:0.9rem;line-height:1.8;font-family:'Lora',serif;font-style:italic;">
                    {rewritten.get("summary", "Analysis complete.")}
                </div>
            </div>""", unsafe_allow_html=True)

    # ── TAB 2: Headline ───────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown('<div class="section-header">AI-Optimized Headline</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card card-red"><b style="color:#dc2626;font-size:0.8rem;">BEFORE</b><br><br>' +
                        (user_profile.get("headline") or "<i>No headline</i>") + '</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card card-green"><b style="color:#059669;font-size:0.8rem;">AFTER — OPTIMIZED</b><br><br>' +
                        (rewritten.get("headline") or "") + '</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">Regenerate with Custom Tweaks</div>', unsafe_allow_html=True)
        custom_note = st.text_input("Any specific notes? (e.g. 'emphasize leadership', 'mention open-source')",
                                    key="hl_custom")
        if st.button("↻ Regenerate Headline", key="regen_hl"):
            placeholder = st.empty()
            full = ""
            extra = f" Additional requirement: {custom_note}" if custom_note else ""
            
            # Debug info
            st.write("🔍 Debug Info:")
            st.write(f"- Current role: {user_profile.get('current_role', 'None')}")
            st.write(f"- Target role: {target_role}")
            st.write(f"- Top keywords available: {len(top_analysis.get('top_keywords', []))}")
            st.write(f"- Present skills available: {len(gap.get('present_skills', []))}")
            
            try:
                with st.spinner("🤖 Generating optimized headline..."):
                    for chunk in rewrite_headline(
                        user_profile.get("headline", ""), 
                        user_profile.get("current_role", ""), 
                        target_role,
                        top_analysis.get("top_keywords", []),
                        gap.get("present_skills", []), stream=True,
                    ):
                        full += chunk
                        placeholder.markdown(f'<div class="streaming-box">{full}▌</div>', unsafe_allow_html=True)
                placeholder.markdown(f'<div class="streaming-box">{full}</div>', unsafe_allow_html=True)
                st.session_state.rewritten["headline"] = full
                
                if not full or "❌" in full:
                    st.error(f"AI function returned: {full}")
                    
            except Exception as e:
                st.error(f"❌ Error generating headline: {str(e)}")
                st.exception(e)

    # ── TAB 3: About ──────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="section-header">AI-Optimized About Section</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Before**")
            st.markdown(f'<div class="before-box">{user_profile.get("about") or "<i>No about section</i>"}</div>',
                        unsafe_allow_html=True)
        with col2:
            st.markdown("**After — Optimized**")
            st.markdown(f'<div class="after-box">{rewritten.get("about") or ""}</div>',
                        unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↻ Regenerate About Section", key="regen_about"):
            exp_titles = [e.get("title", "") for e in user_profile.get("experience", [])]
            placeholder = st.empty()
            full = ""
            
            # Debug info
            st.write("🔍 Debug Info:")
            st.write(f"- Current about length: {len(user_profile.get('about', ''))}")
            st.write(f"- Experience titles: {len(exp_titles)}")
            st.write(f"- Missing skills: {len(gap.get('missing_skills', []))}")
            st.write(f"- Present skills: {len(gap.get('present_skills', []))}")
            
            try:
                with st.spinner("🤖 Generating optimized about section..."):
                    for chunk in rewrite_about(
                        user_profile.get("about", ""), 
                        user_profile.get("current_role", ""), 
                        target_role,
                        top_analysis.get("top_keywords", []),
                        gap.get("missing_skills", []),
                        gap.get("present_skills", []),
                        exp_titles, stream=True,
                    ):
                        full += chunk
                        placeholder.markdown(f'<div class="streaming-box">{full}▌</div>', unsafe_allow_html=True)
                placeholder.markdown(f'<div class="streaming-box">{full}</div>', unsafe_allow_html=True)
                st.session_state.rewritten["about"] = full
                
                if not full or "❌" in full:
                    st.error(f"AI function returned: {full}")
                    
            except Exception as e:
                st.error(f"❌ Error generating about section: {str(e)}")
                st.exception(e)
            st.session_state.rewritten["about"] = full

    # ── TAB 4: Experience ─────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown('<div class="section-header">AI-Optimized Experience Bullets</div>', unsafe_allow_html=True)
        exp_list = rewritten.get("experience", [])

        if not exp_list:
            st.info("No experience entries found. Add your experience in the input form.")
        else:
            for i, exp in enumerate(exp_list):
                with st.expander(f"💼 {exp.get('title', 'Role')} @ {exp.get('company', 'Company')}", expanded=(i == 0)):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Original**")
                        st.markdown(f'<div class="before-box">{exp.get("original") or "<i>No description</i>"}</div>',
                                    unsafe_allow_html=True)
                    with c2:
                        st.markdown("**Optimized**")
                        st.markdown(f'<div class="after-box">{exp.get("rewritten") or ""}</div>',
                                    unsafe_allow_html=True)

                    if st.button(f"↻ Regenerate bullets", key=f"regen_exp_{i}"):
                        placeholder = st.empty()
                        full = ""
                        for chunk in rewrite_experience_bullets(
                            exp.get("title", ""), exp.get("company", ""),
                            exp.get("original", ""), 
                            user_profile.get("current_role", ""),
                            target_role,
                            top_analysis.get("top_keywords", []), stream=True,
                        ):
                            full += chunk
                            placeholder.markdown(f'<div class="streaming-box">{full}▌</div>', unsafe_allow_html=True)
                        placeholder.markdown(f'<div class="streaming-box">{full}</div>', unsafe_allow_html=True)
                        st.session_state.rewritten["experience"][i]["rewritten"] = full

    # ── TAB 5: Skill Gaps ─────────────────────────────────────────────────────
    with tabs[4]:
        # Check if AI Enhancement mode was selected
        selected_mode = st.session_state.get("optimization_mode", "")
        is_ai_mode = "AI Enhancement" in selected_mode
        
        if is_ai_mode:
            st.markdown('<div class="section-header">🤖 AI-Recommended Skills Focus</div>', unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**✅ Your Current Skills**")
                st.markdown('<div class="card card-green">' +
                    "".join(f'<span class="tag tag-green">{s}</span>' for s in gap.get("present_skills", [])[:15]) +
                    "</div>", unsafe_allow_html=True)

            with col_b:
                st.markdown("**🎯 AI-Recommended Target Skills**")
                st.markdown('<div class="card card-accent">' +
                    "".join(f'<span class="tag tag-indigo">{s}</span>' for s in gap.get("missing_skills", [])[:15]) +
                    "</div>", unsafe_allow_html=True)
                    
        else:
            st.markdown('<div class="section-header">Keyword & Skills Gap Analysis</div>', unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**❌ Missing Skills — Add These**")
                st.markdown('<div class="card card-red">' +
                    "".join(f'<span class="tag tag-red">{s}</span>' for s in gap.get("missing_skills", [])[:15]) +
                    "</div>", unsafe_allow_html=True)

                st.markdown("</br>**⚠️ Missing Power Verbs**")
                st.markdown('<div class="card card-gold">' +
                    "".join(f'<span class="tag tag-gold">{v}</span>' for v in gap.get("missing_power_verbs", [])) +
                    "</div>", unsafe_allow_html=True)

            with col_b:
                st.markdown("**✅ Skills You Already Have**")
                st.markdown('<div class="card card-green">' +
                    "".join(f'<span class="tag tag-green">{s}</span>' for s in gap.get("present_skills", [])[:15]) +
                    "</div>", unsafe_allow_html=True)

                st.markdown("</br>**📊 Top Keywords in Target Role Profiles**")
                st.markdown('<div class="card card-accent">' +
                    "".join(f'<span class="tag tag-indigo">{k}</span>' for k in st.session_state.top_analysis.get("top_keywords", [])[:20]) +
                    "</div>", unsafe_allow_html=True)

        st.markdown("</br>")
        st.markdown('<div class="section-header">AI Skills Recommendations</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card card-accent" style="font-size:0.9rem;line-height:1.8;">{rewritten.get("skills_recommendations", "")}</div>',
                    unsafe_allow_html=True)

        metrics_ok = gap.get("has_quantified_metrics", False)
        st.markdown(f"""
        <div class="card {'card-green' if metrics_ok else 'card-red'}" style="margin-top:1rem;">
            {'✅ <b>Quantified metrics found</b> in your profile — great for ATS and recruiters.' if metrics_ok
             else '⚠️ <b>No quantified metrics detected.</b> Add specific numbers (%, $, users, time saved) to every experience bullet. This single change can 2× your response rate.'}
        </div>""", unsafe_allow_html=True)

    # ── TAB 6: Export ─────────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown('<div class="section-header">Export Your Optimized Profile</div>', unsafe_allow_html=True)

        # Text export (always works)
        report_text = f"""LINKEDIN PROFILE OPTIMIZATION REPORT
=====================================
Name: {user_profile.get("name", "")}
Target Role: {target_role}
Overall Score: {scores["overall"]:.0f}/100

AI ASSESSMENT
-------------
{rewritten.get("summary", "")}

OPTIMIZED HEADLINE
------------------
{rewritten.get("headline", "")}

OPTIMIZED ABOUT SECTION
------------------------
{rewritten.get("about", "")}

OPTIMIZED EXPERIENCE
---------------------
"""
        for exp in rewritten.get("experience", []):
            report_text += f"\n{exp.get('title','')} @ {exp.get('company','')}\n"
            report_text += exp.get("rewritten", "") + "\n"

        report_text += f"""
SKILLS RECOMMENDATIONS
-----------------------
{rewritten.get("skills_recommendations", "")}

MISSING SKILLS TO ADD
----------------------
{', '.join(gap.get("missing_skills", []))}

SCORE BREAKDOWN
---------------
"""
        for label, pts in scores.get("breakdown", {}).items():
            report_text += f"  {label}: {pts:.0f}\n"

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
            st.markdown("**📄 Text Report**")
            st.markdown("Download all optimized sections as a plain text file, ready to copy-paste into LinkedIn.")
            st.download_button(
                "📥 Download .txt Report",
                data=report_text,
                file_name=f"linkedin_optimized_{user_profile.get('name','profile').replace(' ','_').lower()}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card card-green">', unsafe_allow_html=True)
            st.markdown("**📊 PDF Report**")
            st.markdown("Formatted PDF with before/after comparisons, score bars, and action items.")
            if st.button("⚡ Generate PDF Report", use_container_width=True, key="gen_pdf"):
                try:
                    from exporter.pdf_report import generate_pdf_report
                    with st.spinner("Generating PDF…"):
                        pdf_path = generate_pdf_report(
                            user_profile, rewritten, scores, gap, top_analysis, target_role
                        )
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "📥 Download PDF",
                            data=f.read(),
                            file_name=f"linkedin_report_{user_profile.get('name','').replace(' ','_').lower()}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}. Install fpdf2: pip install fpdf2")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>")
        st.markdown('<div class="section-header">Raw JSON Data</div>', unsafe_allow_html=True)
        with st.expander("View full analysis JSON"):
            st.json({
                "scores": scores,
                "gap": gap,
                "rewritten_sections": {
                    "headline": rewritten.get("headline"),
                    "about": rewritten.get("about"),
                },
                "top_analysis": st.session_state.top_analysis,
            })

elif not st.session_state.optimization_done:
    st.markdown("""
    <div class="card" style="text-align:center;padding:3rem;border:2px dashed #c7d2fe;background:#f8f9ff;">
        <div style="font-size:2.5rem;margin-bottom:1rem;">⬡</div>
        <div style="font-size:1.1rem;font-weight:700;color:#4338ca;margin-bottom:0.5rem;">
            Fill in your profile details above and click Optimize
        </div>
        <div style="font-size:0.88rem;color:#64748b;">
            Results include: optimized headline · rewritten about · improved experience bullets ·
            skill gap report · PDF export
        </div>
    </div>
    """, unsafe_allow_html=True)
