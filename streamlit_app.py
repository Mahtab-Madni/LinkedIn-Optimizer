import streamlit as st
import json
import sys
import os

# Add paths for Streamlit Cloud deployment (app in root)
current_dir = os.path.dirname(__file__)
core_modules_path = os.path.join(current_dir, "Core Modules")
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
    --emerald:  #10b981;
    --red:      #ef4444;
    --amber:    #f59e0b;
    --slate:    #64748b;
    --radius:   12px;
}

* {
    font-family: 'Cabinet Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main > div {
    padding-top: 2rem;
    background-color: var(--bg);
    border-radius: var(--radius);
}

.stTabs > div > div > div > div {
    padding: 1rem 0;
}

[data-testid="stSidebar"] {
    background: linear-gradient(135deg, var(--navy) 0%, #1e293b 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.metric-card {
    background: var(--surface);
    border: 1px solid #e2e8f0;
    border-radius: var(--radius);
    padding: 1.5rem;
    margin: 0.5rem 0;
    transition: all 0.2s ease;
}

.metric-card:hover {
    border-color: var(--indigo);
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);
    transform: translateY(-1px);
}

.score-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1rem 0;
}

.score-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: 800;
    color: white;
    margin-right: 1rem;
}

.score-excellent { background: linear-gradient(135deg, #10b981, #059669); }
.score-good { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.score-average { background: linear-gradient(135deg, #f59e0b, #d97706); }
.score-poor { background: linear-gradient(135deg, #ef4444, #dc2626); }

.progress-bar {
    background: #f1f5f9;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--indigo), var(--emerald));
    transition: width 0.6s ease;
    border-radius: 4px;
}

.highlight-box {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 2px solid #0ea5e9;
    border-radius: var(--radius);
    padding: 1.5rem;
    margin: 1rem 0;
}

.warning-box {
    background: linear-gradient(135deg, #fefce8, #fef3c7);
    border: 2px solid #f59e0b;
    border-radius: var(--radius);
    padding: 1rem;
    margin: 1rem 0;
}

.success-box {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border: 2px solid #22c55e;
    border-radius: var(--radius);
    padding: 1rem;
    margin: 1rem 0;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}

.stat-item {
    background: var(--surface);
    border: 1px solid #e2e8f0;
    border-radius: var(--radius);
    padding: 1rem;
    text-align: center;
    transition: transform 0.2s ease;
}

.stat-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.section-header {
    background: linear-gradient(135deg, var(--navy), #334155);
    color: white;
    padding: 1.5rem;
    border-radius: var(--radius);
    margin: 2rem 0 1rem 0;
    font-size: 1.25rem;
    font-weight: 700;
}

.regenerate-btn {
    background: linear-gradient(135deg, var(--indigo), #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.regenerate-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
}

.stTextArea textarea {
    font-family: 'Lora', serif !important;
    line-height: 1.6 !important;
    border-radius: 8px !important;
    border: 2px solid #e2e8f0 !important;
    padding: 1rem !important;
}

.stTextArea textarea:focus {
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 2px solid #e2e8f0 !important;
}

.hero-section {
    background: linear-gradient(135deg, var(--navy) 0%, #334155 100%);
    color: white;
    padding: 3rem 2rem;
    border-radius: var(--radius);
    text-align: center;
    margin-bottom: 2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.feature-card {
    background: var(--surface);
    border: 1px solid #e2e8f0;
    border-radius: var(--radius);
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.feature-card:hover {
    border-color: var(--indigo);
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
}

.keyword-tag {
    display: inline-block;
    background: linear-gradient(135deg, #e0f2fe, #bae6fd);
    color: #0369a1;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    margin: 0.25rem;
    font-size: 0.85rem;
    font-weight: 500;
}

.missing-keyword {
    background: linear-gradient(135deg, #fef2f2, #fecaca);
    color: #dc2626;
}

.animation-fade {
    animation: fadeIn 0.6s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ── Session State Initialization ──────────────────────────────────────────────
def init_session_state():
    defaults = {
        'profile_data': {},
        'benchmark_profiles': [],
        'analysis_results': None,
        'optimization_results': {},
        'current_tab': 'input',
        'show_analysis': False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ── Helper Functions ──────────────────────────────────────────────────────────

def score_color_class(score):
    if score >= 80: return "score-excellent"
    elif score >= 60: return "score-good" 
    elif score >= 40: return "score-average"
    else: return "score-poor"

def score_description(score):
    if score >= 80: return "Excellent"
    elif score >= 60: return "Good"
    elif score >= 40: return "Needs Work"
    else: return "Major Issues"

def render_progress_bar(value, max_value=100, label=""):
    percentage = min(100, (value / max_value) * 100)
    st.markdown(f"""
    <div style="margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
            <span style="font-weight: 500;">{label}</span>
            <span style="font-weight: 600; color: var(--indigo);">{value}/{max_value}</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {percentage}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_keyword_tags(keywords, missing=False):
    if not keywords:
        return ""
    
    css_class = "missing-keyword" if missing else "keyword-tag"
    tags_html = ""
    for keyword in keywords[:20]:  # Limit to 20 keywords
        tags_html += f'<span class="{css_class}">{keyword}</span>'
    
    return f'<div style="margin: 1rem 0;">{tags_html}</div>'

def show_score_circle(score, size=80):
    color_class = score_color_class(score)
    description = score_description(score)
    
    st.markdown(f"""
    <div class="score-container">
        <div class="score-circle {color_class}" style="width: {size}px; height: {size}px;">
            {score}
        </div>
        <div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--navy);">{description}</div>
            <div style="color: var(--slate); font-weight: 500;">Overall Score</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Main Application ──────────────────────────────────────────────────────────

def main():
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 style="font-size: 3rem; margin: 0; font-weight: 800;">⬡ LinkedIn Profile Optimizer</h1>
        <p style="font-size: 1.2rem; margin: 1rem 0 0 0; opacity: 0.9;">
            AI-powered optimization with keyword gap analysis, semantic scoring, and instant content rewriting
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for benchmark profiles
    with st.sidebar:
        st.markdown("### 📊 Benchmark Profiles")
        st.markdown("*Add 2-3 top LinkedIn profiles to compare against*")
        
        # Profile source selection
        profile_source = st.selectbox(
            "Choose input method:",
            ["📝 Paste Text", "🌐 LinkedIn URLs", "📄 Upload PDF"],
            help="Select how you want to provide benchmark profiles"
        )
        
        benchmark_profiles = []
        
        if profile_source == "📝 Paste Text":
            st.markdown("**Paste LinkedIn profiles as plain text:**")
            
            for i in range(3):
                profile_text = st.text_area(
                    f"Benchmark Profile {i+1}",
                    height=150,
                    key=f"benchmark_text_{i}",
                    placeholder="Paste a complete LinkedIn profile here (name, headline, about, experience)..."
                )
                
                if profile_text.strip():
                    try:
                        parsed = parse_manual_profile(profile_text)
                        if parsed.get("name"):
                            benchmark_profiles.append(parsed)
                            st.success(f"✅ Profile {i+1}: {parsed['name']}")
                        else:
                            st.warning(f"⚠️ Profile {i+1}: Could not parse name")
                    except Exception as e:
                        st.error(f"❌ Profile {i+1}: Parse error")
        
        elif profile_source == "🌐 LinkedIn URLs":
            st.markdown("**Enter LinkedIn profile URLs:**")
            st.info("⚠️ Requires Chrome browser and LinkedIn credentials")
            
            urls = []
            for i in range(3):
                url = st.text_input(
                    f"LinkedIn URL {i+1}",
                    key=f"url_{i}",
                    placeholder="https://linkedin.com/in/profile-name"
                )
                if url.strip():
                    urls.append(url.strip())
            
            if urls and st.button("🔍 Scrape Profiles", help="Scrape LinkedIn profiles from URLs"):
                try:
                    from scrapper.linkedin_scraper import scrape_profile
                    
                    with st.spinner("Scraping LinkedIn profiles..."):
                        for i, url in enumerate(urls):
                            try:
                                profile_data = scrape_profile(url)
                                if profile_data:
                                    benchmark_profiles.append(profile_data)
                                    st.success(f"✅ Scraped: {profile_data.get('name', 'Unknown')}")
                                else:
                                    st.warning(f"⚠️ Could not scrape profile {i+1}")
                            except Exception as e:
                                st.error(f"❌ Error scraping profile {i+1}: {str(e)}")
                                
                except ImportError:
                    st.error("❌ Scraping functionality not available. Please use manual input.")
                except Exception as e:
                    st.error(f"❌ Scraping error: {str(e)}")
        
        elif profile_source == "📄 Upload PDF":
            st.markdown("**Upload LinkedIn PDF files:**")
            
            uploaded_files = st.file_uploader(
                "Upload LinkedIn PDFs",
                type=['pdf'],
                accept_multiple_files=True,
                help="Download PDFs from LinkedIn profiles and upload here"
            )
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    try:
                        # Try AI-powered parsing first
                        try:
                            from scrapper.linkedin_scraper import parse_linkedin_pdf_with_ai
                            profile_data = parse_linkedin_pdf_with_ai(uploaded_file)
                            st.success(f"✅ AI Parsed: {profile_data.get('name', 'Unknown')}")
                        except:
                            # Fallback to basic parsing
                            from scrapper.linkedin_scraper import parse_linkedin_pdf
                            profile_data = parse_linkedin_pdf(uploaded_file)
                            st.success(f"✅ Parsed: {profile_data.get('name', 'Unknown')}")
                        
                        if profile_data.get("name"):
                            benchmark_profiles.append(profile_data)
                        else:
                            st.warning(f"⚠️ Could not extract name from {uploaded_file.name}")
                            
                    except Exception as e:
                        st.error(f"❌ Error parsing {uploaded_file.name}: {str(e)}")
        
        # Store benchmark profiles in session state
        st.session_state.benchmark_profiles = benchmark_profiles
        
        if benchmark_profiles:
            st.success(f"📊 {len(benchmark_profiles)} benchmark profile(s) ready")
        else:
            st.info("👆 Add benchmark profiles to compare against")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Your Profile", "📊 Analysis Score", "✨ Headline", 
        "📖 About Section", "💼 Experience", "📋 Export"
    ])
    
    with tab1:
        st.markdown('<div class="section-header">📝 Your LinkedIn Profile Information</div>', 
                   unsafe_allow_html=True)
        
        # Profile input method selection
        input_method = st.selectbox(
            "Choose how to input your profile:",
            ["✍️ Manual Input", "📄 Upload LinkedIn PDF", "🌐 LinkedIn URL"],
            help="Select the method to provide your LinkedIn profile information"
        )
        
        profile_data = {}
        
        if input_method == "✍️ Manual Input":
            col1, col2 = st.columns([1, 1])
            
            with col1:
                profile_data["name"] = st.text_input("👤 Full Name", placeholder="John Smith")
                profile_data["target_role"] = st.text_input("🎯 Target Role", placeholder="Senior Data Scientist")
                profile_data["headline"] = st.text_area("📄 Current Headline", height=100, 
                                                       placeholder="Data Scientist at Tech Corp | ML & AI Specialist")
            
            with col2:
                profile_data["location"] = st.text_input("📍 Location", placeholder="San Francisco, CA")
                profile_data["industry"] = st.text_input("🏢 Industry", placeholder="Technology")
                profile_data["about"] = st.text_area("📖 About Section", height=200,
                                                    placeholder="Passionate data scientist with 5+ years...")
            
            # Experience section
            st.markdown("### 💼 Experience")
            experience_entries = []
            
            num_experiences = st.number_input("Number of experiences", min_value=1, max_value=10, value=3)
            
            for i in range(int(num_experiences)):
                with st.expander(f"Experience {i+1}"):
                    exp_col1, exp_col2 = st.columns([2, 1])
                    with exp_col1:
                        job_title = st.text_input(f"Job Title {i+1}", key=f"job_title_{i}")
                        company = st.text_input(f"Company {i+1}", key=f"company_{i}")
                    with exp_col2:
                        duration = st.text_input(f"Duration {i+1}", key=f"duration_{i}", placeholder="Jan 2020 - Present")
                    
                    description = st.text_area(f"Job Description {i+1}", key=f"description_{i}", height=100)
                    
                    if job_title or company:
                        experience_entries.append({
                            "job_title": job_title,
                            "company": company,
                            "duration": duration,
                            "description": description
                        })
            
            profile_data["experience"] = experience_entries
            
            # Skills section
            st.markdown("### 🛠 Skills")
            skills_input = st.text_area("Skills (one per line or comma-separated)", height=100,
                                      placeholder="Python\nMachine Learning\nSQL\nTensorFlow")
            
            if skills_input:
                # Parse skills (handle both newlines and commas)
                skills = []
                for line in skills_input.split('\n'):
                    if ',' in line:
                        skills.extend([s.strip() for s in line.split(',') if s.strip()])
                    else:
                        if line.strip():
                            skills.append(line.strip())
                profile_data["skills"] = skills
            else:
                profile_data["skills"] = []
        
        elif input_method == "📄 Upload LinkedIn PDF":
            uploaded_file = st.file_uploader("Upload your LinkedIn profile PDF", type=['pdf'])
            
            if uploaded_file:
                try:
                    with st.spinner("Processing your LinkedIn PDF..."):
                        # Try AI-powered parsing first
                        try:
                            from scrapper.linkedin_scraper import parse_linkedin_pdf_with_ai
                            profile_data = parse_linkedin_pdf_with_ai(uploaded_file)
                            st.success("✅ Successfully parsed your profile using AI!")
                        except:
                            # Fallback to basic parsing
                            from scrapper.linkedin_scraper import parse_linkedin_pdf
                            profile_data = parse_linkedin_pdf(uploaded_file)
                            st.success("✅ Successfully parsed your profile!")
                        
                        # Display parsed information for review
                        if profile_data:
                            st.markdown("### 📋 Extracted Information")
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.write(f"**Name:** {profile_data.get('name', 'Not found')}")
                                st.write(f"**Headline:** {profile_data.get('headline', 'Not found')}")
                                st.write(f"**Location:** {profile_data.get('location', 'Not found')}")
                            
                            with col2:
                                st.write(f"**Skills:** {len(profile_data.get('skills', []))} found")
                                st.write(f"**Experience:** {len(profile_data.get('experience', []))} entries")
                            
                            if profile_data.get('about'):
                                st.markdown("**About:**")
                                st.write(profile_data['about'][:200] + "..." if len(profile_data.get('about', '')) > 200 else profile_data.get('about', ''))
                        
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                    profile_data = {}
        
        elif input_method == "🌐 LinkedIn URL":
            linkedin_url = st.text_input("Enter your LinkedIn profile URL", 
                                       placeholder="https://linkedin.com/in/your-profile")
            
            if linkedin_url and st.button("🔍 Scrape My Profile"):
                try:
                    from scrapper.linkedin_scraper import scrape_profile
                    
                    with st.spinner("Scraping your LinkedIn profile..."):
                        profile_data = scrape_profile(linkedin_url)
                        
                        if profile_data:
                            st.success("✅ Successfully scraped your profile!")
                            
                            # Display scraped information
                            st.markdown("### 📋 Scraped Information")
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.write(f"**Name:** {profile_data.get('name', 'Not found')}")
                                st.write(f"**Headline:** {profile_data.get('headline', 'Not found')}")
                            
                            with col2:
                                st.write(f"**Skills:** {len(profile_data.get('skills', []))} found")
                                st.write(f"**Experience:** {len(profile_data.get('experience', []))} entries")
                        else:
                            st.error("❌ Could not scrape profile. Please try manual input.")
                            
                except ImportError:
                    st.error("❌ Scraping functionality not available. Please use manual input or PDF upload.")
                except Exception as e:
                    st.error(f"❌ Scraping error: {str(e)}")
        
        # Store profile data
        if profile_data:
            st.session_state.profile_data = profile_data
        
        # Analysis button
        if st.session_state.profile_data and st.session_state.benchmark_profiles:
            st.markdown("---")
            if st.button("🚀 Analyze & Optimize Profile", type="primary", key="analyze_btn"):
                with st.spinner("🔍 Analyzing your profile against benchmarks..."):
                    try:
                        # Analyze profile
                        user_analysis = analyze_profile(st.session_state.profile_data)
                        benchmark_analysis = analyze_top_profiles(st.session_state.benchmark_profiles)
                        
                        # Compute gap analysis and scores
                        gap_analysis = keyword_gap_analysis(user_analysis, benchmark_analysis)
                        overall_score = compute_overall_score(
                            st.session_state.profile_data,
                            st.session_state.benchmark_profiles,
                            benchmark_analysis,
                            gap_analysis
                        )
                        
                        # Store analysis results
                        st.session_state.analysis_results = {
                            'user_analysis': user_analysis,
                            'benchmark_analysis': benchmark_analysis,
                            'gap_analysis': gap_analysis,
                            'overall_score': overall_score
                        }
                        
                        st.session_state.show_analysis = True
                        st.success("✅ Analysis complete! Check other tabs for detailed results.")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Analysis error: {str(e)}")
        
        elif not st.session_state.profile_data:
            st.info("👆 Please fill in your profile information above")
        elif not st.session_state.benchmark_profiles:
            st.info("👈 Please add benchmark profiles in the sidebar")
    
    with tab2:
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            overall_score = results['overall_score']
            
            st.markdown('<div class="section-header">📊 Profile Analysis Results</div>', 
                       unsafe_allow_html=True)
            
            # Overall score display
            col1, col2 = st.columns([1, 2])
            
            with col1:
                show_score_circle(overall_score['total_score'])
            
            with col2:
                st.markdown("### Score Breakdown")
                
                # Score components with progress bars
                for component, details in overall_score['components'].items():
                    score = details['score']
                    max_score = details['max_score']
                    render_progress_bar(score, max_score, component.replace('_', ' ').title())
            
            # Detailed analysis in expandable sections
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("🎯 Keyword Analysis", expanded=True):
                    gap_analysis = results['gap_analysis']
                    
                    st.markdown("**Keywords You Have:**")
                    found_keywords = gap_analysis.get('found_keywords', [])
                    if found_keywords:
                        st.markdown(render_keyword_tags(found_keywords[:15]), unsafe_allow_html=True)
                    else:
                        st.write("None identified")
                    
                    st.markdown("**Missing Keywords:**")
                    missing_keywords = gap_analysis.get('missing_keywords', [])
                    if missing_keywords:
                        st.markdown(render_keyword_tags(missing_keywords[:15], missing=True), unsafe_allow_html=True)
                        st.info(f"💡 Consider adding {len(missing_keywords)} missing keywords to improve your visibility")
                    else:
                        st.success("✅ You have excellent keyword coverage!")
            
            with col2:
                with st.expander("📈 Profile Metrics", expanded=True):
                    user_analysis = results['user_analysis']
                    
                    metrics_data = [
                        ("Total Skills", len(user_analysis.get('skills', []))),
                        ("Power Verbs", len(user_analysis.get('power_verbs', []))),
                        ("Metrics Found", len(user_analysis.get('metrics', []))),
                        ("Experience Entries", len(st.session_state.profile_data.get('experience', [])))
                    ]
                    
                    for metric_name, value in metrics_data:
                        st.metric(metric_name, value)
            
            # Recommendations
            with st.expander("💡 Optimization Recommendations", expanded=True):
                recommendations = []
                
                # Score-based recommendations
                if overall_score['total_score'] < 60:
                    recommendations.append("🚨 **Priority**: Your profile needs significant improvement across multiple areas")
                
                if overall_score['components']['semantic_similarity']['score'] < 15:
                    recommendations.append("📝 **Content**: Rewrite your about and experience sections to better match target roles")
                
                if overall_score['components']['skill_coverage']['score'] < 15:
                    recommendations.append("🛠 **Skills**: Add missing technical skills that are common in your target role")
                
                if len(user_analysis.get('power_verbs', [])) < 5:
                    recommendations.append("💪 **Language**: Use more action verbs in your experience descriptions")
                
                if len(user_analysis.get('metrics', [])) < 3:
                    recommendations.append("📊 **Impact**: Add quantified achievements (percentages, dollar amounts, timeframes)")
                
                # Display recommendations
                if recommendations:
                    for rec in recommendations:
                        st.markdown(f"- {rec}")
                else:
                    st.success("🎉 Your profile looks great! Use the optimization tabs to polish specific sections.")
        
        else:
            st.markdown('<div class="section-header">📊 Profile Analysis Results</div>', 
                       unsafe_allow_html=True)
            st.info("👈 Complete your profile analysis in the 'Your Profile' tab to see results here")
    
    with tab3:
        st.markdown('<div class="section-header">✨ AI-Optimized Headlines</div>', 
                   unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            profile_data = st.session_state.profile_data
            current_headline = profile_data.get('headline', '')
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📄 Current Headline")
                st.info(current_headline if current_headline else "No headline provided")
            
            with col2:
                if st.button("✨ Generate Optimized Headlines", key="gen_headlines"):
                    with st.spinner("🤖 AI is crafting optimized headlines..."):
                        try:
                            results = st.session_state.analysis_results
                            gap_analysis = results['gap_analysis']
                            user_analysis = results['user_analysis']
                            
                            optimized_headlines = rewrite_headline(
                                profile_data.get("headline", ""),
                                profile_data.get("current_role", ""),
                                profile_data.get("target_role", ""),
                                user_analysis.get("top_keywords", []),
                                gap_analysis.get("present_skills", []),
                                stream=False
                            )
                            
                            # Parse the response if it's a single string
                            if isinstance(optimized_headlines, str):
                                optimized_headlines = [optimized_headlines]
                            
                            st.session_state.optimization_results['headlines'] = optimized_headlines
                            
                        except Exception as e:
                            st.error(f"❌ Error generating headlines: {str(e)}")
            
            # Display optimized headlines
            if 'headlines' in st.session_state.optimization_results:
                st.markdown("---")
                st.markdown("### 🎯 AI-Optimized Headlines")
                
                headlines = st.session_state.optimization_results['headlines']
                
                for i, headline in enumerate(headlines, 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="color: var(--indigo); margin: 0 0 0.5rem 0;">Option {i}</h4>
                            <p style="font-size: 1.1rem; line-height: 1.5; margin: 0; font-weight: 500;">
                                {headline}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"📋 Copy Headline {i}", key=f"copy_headline_{i}"):
                            st.success(f"✅ Headline {i} copied to clipboard!")
                
                # Regeneration option
                if st.button("🔄 Generate New Headlines", key="regen_headlines"):
                    with st.spinner("🤖 Creating fresh headline options..."):
                        try:
                            results = st.session_state.analysis_results
                            gap_analysis = results['gap_analysis']
                            user_analysis = results['user_analysis']
                            
                            new_headlines = rewrite_headline(
                                profile_data.get("headline", ""),
                                profile_data.get("current_role", ""),
                                profile_data.get("target_role", ""),
                                user_analysis.get("top_keywords", []),
                                gap_analysis.get("present_skills", []),
                                stream=False
                            )
                            
                            # Parse the response if it's a single string
                            if isinstance(new_headlines, str):
                                new_headlines = [new_headlines]
                            
                            st.session_state.optimization_results['headlines'] = new_headlines
                            st.experimental_rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Error regenerating headlines: {str(e)}")
        
        else:
            st.info("👈 Complete your profile analysis first to generate optimized headlines")
    
    with tab4:
        st.markdown('<div class="section-header">📖 AI-Optimized About Section</div>', 
                   unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            profile_data = st.session_state.profile_data
            current_about = profile_data.get('about', '')
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📝 Current About Section")
                if current_about:
                    st.text_area("", value=current_about, height=200, disabled=True, key="current_about_display")
                else:
                    st.info("No about section provided")
            
            with col2:
                if st.button("✨ Generate Optimized About", key="gen_about"):
                    with st.spinner("🤖 AI is rewriting your about section..."):
                        try:
                            results = st.session_state.analysis_results
                            gap_analysis = results['gap_analysis']
                            user_analysis = results['user_analysis']
                            exp_titles = [e.get("title", "") for e in profile_data.get("experience", [])]
                            
                            optimized_about = rewrite_about(
                                profile_data.get("about", ""),
                                profile_data.get("current_role", ""),
                                profile_data.get("target_role", ""),
                                user_analysis.get("top_keywords", []),
                                gap_analysis.get("missing_skills", []),
                                gap_analysis.get("present_skills", []),
                                exp_titles,
                                stream=False
                            )
                            
                            st.session_state.optimization_results['about'] = optimized_about
                            
                        except Exception as e:
                            st.error(f"❌ Error generating about section: {str(e)}")
            
            # Display optimized about section
            if 'about' in st.session_state.optimization_results:
                st.markdown("---")
                st.markdown("### 🎯 AI-Optimized About Section")
                
                about_text = st.session_state.optimization_results['about']
                
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.1rem; line-height: 1.7; white-space: pre-wrap; font-family: 'Lora', serif;">
                        {about_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📋 Copy About Section", key="copy_about"):
                        st.success("✅ About section copied to clipboard!")
                
                with col2:
                    if st.button("🔄 Regenerate About", key="regen_about"):
                        with st.spinner("🤖 Creating a fresh about section..."):
                            try:
                                results = st.session_state.analysis_results
                                gap_analysis = results['gap_analysis']
                            user_analysis = results['user_analysis']
                            exp_titles = [e.get("title", "") for e in profile_data.get("experience", [])]
                            
                            new_about = rewrite_about(
                                profile_data.get("about", ""),
                                profile_data.get("current_role", ""),
                                profile_data.get("target_role", ""),
                                user_analysis.get("top_keywords", []),
                                gap_analysis.get("missing_skills", []),
                                gap_analysis.get("present_skills", []),
                                exp_titles,
                                stream=False
                                st.session_state.optimization_results['about'] = new_about
                                st.experimental_rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error regenerating about section: {str(e)}")
        
        else:
            st.info("👈 Complete your profile analysis first to generate an optimized about section")
    
    with tab5:
        st.markdown('<div class="section-header">💼 AI-Optimized Experience</div>', 
                   unsafe_allow_html=True)
        
        if st.session_state.analysis_results:
            profile_data = st.session_state.profile_data
            experience = profile_data.get('experience', [])
            
            if experience:
                # Generate experience optimization button
                if st.button("✨ Optimize All Experience Entries", key="gen_experience"):
                    with st.spinner("🤖 AI is optimizing your experience descriptions..."):
                        try:
                            results = st.session_state.analysis_results
                            gap_analysis = results['gap_analysis']
                            
                            optimized_experience = rewrite_experience_bullets(
                                experience,
                                missing_keywords=gap_analysis.get('missing_keywords', [])
                            )
                            
                            st.session_state.optimization_results['experience'] = optimized_experience
                            
                        except Exception as e:
                            st.error(f"❌ Error optimizing experience: {str(e)}")
                
                # Display current vs optimized experience
                if 'experience' in st.session_state.optimization_results:
                    st.markdown("### 🔄 Before & After Comparison")
                    
                    optimized_exp = st.session_state.optimization_results['experience']
                    
                    for i, (original, optimized) in enumerate(zip(experience, optimized_exp)):
                        with st.expander(f"📍 {original.get('job_title', 'Position')} at {original.get('company', 'Company')}", expanded=i==0):
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**📝 Original:**")
                                st.text_area("", value=original.get('description', ''), height=150, 
                                           disabled=True, key=f"orig_exp_{i}")
                            
                            with col2:
                                st.markdown("**✨ Optimized:**")
                                st.text_area("", value=optimized, height=150, 
                                           disabled=True, key=f"opt_exp_{i}")
                            
                            if st.button(f"📋 Copy Optimized Description", key=f"copy_exp_{i}"):
                                st.success(f"✅ Optimized description copied!")
                    
                    # Regenerate all button
                    if st.button("🔄 Regenerate All Experience", key="regen_experience"):
                        with st.spinner("🤖 Creating fresh experience descriptions..."):
                            try:
                                results = st.session_state.analysis_results
                                gap_analysis = results['gap_analysis']
                                
                                new_experience = rewrite_experience_bullets(
                                    experience,
                                    missing_keywords=gap_analysis.get('missing_keywords', [])
                                )
                                
                                st.session_state.optimization_results['experience'] = new_experience
                                st.experimental_rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error regenerating experience: {str(e)}")
                
                else:
                    # Show current experience
                    st.markdown("### 📋 Current Experience")
                    for i, exp in enumerate(experience):
                        with st.expander(f"📍 {exp.get('job_title', 'Position')} at {exp.get('company', 'Company')}"):
                            st.write(f"**Duration:** {exp.get('duration', 'Not specified')}")
                            st.write(f"**Description:**")
                            st.write(exp.get('description', 'No description provided'))
            
            else:
                st.info("No experience entries found in your profile")
        
        else:
            st.info("👈 Complete your profile analysis first to optimize your experience section")
    
    with tab6:
        st.markdown('<div class="section-header">📋 Export Your Optimized Profile</div>', 
                   unsafe_allow_html=True)
        
        if st.session_state.analysis_results and st.session_state.optimization_results:
            
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📄 PDF Report")
                st.write("Generate a comprehensive before/after report with analysis")
                
                if st.button("📥 Download PDF Report", key="download_pdf"):
                    try:
                        from exporter.pdf_report import generate_pdf_report
                        
                        with st.spinner("📄 Generating PDF report..."):
                            pdf_buffer = generate_pdf_report(
                                st.session_state.profile_data,
                                st.session_state.analysis_results,
                                st.session_state.optimization_results
                            )
                            
                            st.download_button(
                                label="💾 Download PDF",
                                data=pdf_buffer,
                                file_name=f"linkedin_optimization_report_{st.session_state.profile_data.get('name', 'profile').replace(' ', '_').lower()}.pdf",
                                mime="application/pdf"
                            )
                            
                    except Exception as e:
                        st.error(f"❌ Error generating PDF: {str(e)}")
            
            with col2:
                st.markdown("### 📝 Text Export")
                st.write("Copy optimized content as plain text")
                
                if st.button("📋 Prepare Text Export", key="text_export"):
                    # Compile all optimized content
                    export_text = f"""LINKEDIN PROFILE OPTIMIZATION RESULTS
{'='*50}

NAME: {st.session_state.profile_data.get('name', 'Not provided')}
TARGET ROLE: {st.session_state.profile_data.get('target_role', 'Not specified')}
ANALYSIS DATE: {st.datetime.now().strftime('%Y-%m-%d')}

OPTIMIZED HEADLINE:
{st.session_state.optimization_results.get('headlines', ['Not generated'])[0]}

OPTIMIZED ABOUT SECTION:
{st.session_state.optimization_results.get('about', 'Not generated')}

OPTIMIZED EXPERIENCE:
"""
                    
                    if 'experience' in st.session_state.optimization_results:
                        original_exp = st.session_state.profile_data.get('experience', [])
                        optimized_exp = st.session_state.optimization_results['experience']
                        
                        for i, (orig, opt) in enumerate(zip(original_exp, optimized_exp)):
                            export_text += f"\n{i+1}. {orig.get('job_title', '')} at {orig.get('company', '')}\n"
                            export_text += f"   Duration: {orig.get('duration', '')}\n"
                            export_text += f"   Optimized Description: {opt}\n"
                    
                    st.text_area("📋 Copy this optimized content:", value=export_text, height=400)
            
            # Analysis summary
            st.markdown("---")
            st.markdown("### 📊 Optimization Summary")
            
            analysis = st.session_state.analysis_results
            overall_score = analysis['overall_score']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Overall Score", f"{overall_score['total_score']}/100", 
                         help="Your LinkedIn profile optimization score")
            
            with col2:
                gap_analysis = analysis['gap_analysis']
                missing_count = len(gap_analysis.get('missing_keywords', []))
                st.metric("Missing Keywords", missing_count,
                         help="Keywords you should consider adding")
            
            with col3:
                optimized_sections = len(st.session_state.optimization_results)
                st.metric("Optimized Sections", optimized_sections,
                         help="Number of profile sections optimized")
            
            with col4:
                if 'headlines' in st.session_state.optimization_results:
                    headline_count = len(st.session_state.optimization_results['headlines'])
                    st.metric("Headline Options", headline_count,
                             help="AI-generated headline variations")
        
        else:
            st.info("👈 Complete your analysis and generate optimized content first")

if __name__ == "__main__":
    main()