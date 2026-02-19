# ⬡ LinkedIn Profile Optimizer — AI-Powered

> Transform your LinkedIn profile with AI-powered optimization. Multiple input modes: manual entry, PDF upload, or URL scraping. Compare against top talent and get AI-rewritten sections in seconds. Powered by Groq (Llama 3.3 70B) + spaCy + sentence-transformers.

---

## 🚀 Features

| Feature                         | Description                                                                 |
| ------------------------------- | --------------------------------------------------------------------------- |
| **Multiple Input Modes**        | Manual entry, LinkedIn PDF upload, or URL scraping for maximum flexibility  |
| **Keyword Gap Analysis**        | TF-IDF + spaCy extracts skills from top profiles, finds what you're missing |
| **Semantic Similarity Scoring** | sentence-transformers cosine similarity vs benchmark profiles               |
| **AI Headline Rewrite**         | Groq rewrites your headline to be keyword-rich and punchy                   |
| **AI About Section Rewrite**    | Full storytelling rewrite with hook, achievements, CTA                      |
| **AI Experience Bullets**       | Action verb + metric + outcome format for each role                         |
| **Skills Recommendations**      | What to add now vs what to learn next                                       |
| **Power Verb Analysis**         | Detects weak/missing action verbs in experience bullets                     |
| **Metrics Check**               | Flags if you have no quantified achievements                                |
| **Overall Score (0-100)**       | Multi-dimensional score with breakdown bars                                 |
| **Streaming Output**            | Watch AI rewrite in real-time, section by section                           |
| **PDF Export**                  | Formatted before/after report with score visualization                      |
| **Text Export**                 | Plain text download of all optimized sections                               |
| **Smart Dependency Management** | Auto-handles compatibility issues with fallback modes                       |
| **Chrome Auto-Fix**             | Automated ChromeDriver compatibility troubleshooting                        |

---

## 🛠 Tech Stack

```
Streamlit              — Premium UI
Groq (Llama 3.3 70B)  — AI rewriting (free, ultra-fast)
spaCy                  — NER + noun chunk extraction
scikit-learn TF-IDF    — Corpus keyword importance
sentence-transformers  — Semantic profile similarity
fpdf2                  — PDF report generation
selenium + uc-driver   — LinkedIn scraping (optional)
```

---

## ⚙️ Setup & Installation

### 1. Clone & Install Dependencies

```bash
git clone <your-repo-url>
cd LinkedIn-Profile-Optimizer
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```bash
# Required: Get free API key from console.groq.com
GROQ_API_KEY=gsk_...

# Optional: For advanced users only
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
```

### 3. Choose Your Startup Method

#### 🚀 Quick Start (Recommended)

```bash
python quick_start.py
```

- Fastest way to get started
- Automatically handles dependency issues
- Recommends optimal usage modes

#### 🧹 Clean Start (For Development)

```bash
python clean_start.py
```

- Pre-loads models and dependencies
- Ideal for development and testing
- Suppresses ML library warnings

#### 🔧 Advanced Start (Full Control)

```bash
python start.py
```

- Comprehensive dependency checking
- Installation guidance for missing packages
- Full diagnostics and troubleshooting

#### 🌐 Direct Streamlit (Experienced Users)

```bash
streamlit run app.py
```

- Direct Streamlit execution
- Assumes all dependencies are correctly installed

### 4. Environment Variables Setup

**Linux / Mac:**

```bash
export GROQ_API_KEY="gsk_..."
```

**Windows:**

```cmd
set GROQ_API_KEY=gsk_...
```

**Or using .env file (recommended):**
Create a `.env` file in the project root with your API keys.

---

## 📁 Project Structure

```
linkedin_optimizer/
├── 🚀 Entry Points
│   ├── app.py                      ← Main Streamlit UI (all tabs)
│   ├── quick_start.py              ← Fast startup with compatibility handling
│   ├── start.py                    ← Full diagnostic startup with dep checks
│   └── clean_start.py              ← Development startup with clean imports
│
├── 🛠 Utilities & Tools
│   ├── check_chrome.py             ← Chrome/ChromeDriver version checker
│   ├── fix_chromedriver.py         ← Auto-fix ChromeDriver compatibility
│   └── linkedin_pdf_guide.py       ← Instructions for PDF export from LinkedIn
│
├── 🧠 Core Modules
│   ├── scrapper/
│   │   ├── __init__.py
│   │   └── linkedin_scraper.py     ← Selenium scraper + manual parser
│   │
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── keyword_extractor.py    ← spaCy + TF-IDF keyword extraction
│   │   └── similarity_scorer.py    ← Semantic scoring + gap analysis
│   │
│   ├── ai_rewriter/
│   │   ├── __init__.py
│   │   └── rewriter.py             ← Groq-powered section rewriters
│   │
│   ├── exporter/
│   │   ├── __init__.py
│   │   └── pdf_report.py           ← FPDF2 PDF report generator
│   │
│   └── utils/
│       ├── __init__.py
│       └── warnings_handler.py     ← Suppress ML/NLP library warnings
│
├── 📊 Data & Configuration
│   ├── data/cached_profiles/       ← Cached scraped profiles (JSON)
│   ├── .env                        ← Environment variables (create this)
│   └── requirements.txt            ← Python dependencies
│
└── 📚 Documentation
    └── README.md                   ← This file
```

---

## 🎯 How to Use

### 📄 Method 1: PDF Upload (Recommended)

1. **Download your LinkedIn profile as PDF:**
   - Go to your LinkedIn profile → "More" → "Save to PDF"
   - Or run: `python linkedin_pdf_guide.py` for detailed instructions
2. **Upload and analyze:**
   - Start the app with `python quick_start.py`
   - Choose "📄 Upload LinkedIn PDF"
   - Upload your downloaded PDF file
   - Add 2-3 benchmark profiles in the sidebar
   - Click **Analyze & Optimize**

### ✍️ Method 2: Manual Input (Most Reliable)

1. **Fill in your details:**
   - Name, target role, current headline
   - About section, experience, skills
2. **Add benchmark profiles:**
   - Paste 2-3 top LinkedIn profiles (plain text) in the sidebar
   - These should be profiles of people in roles you want
3. **Analyze and optimize:**
   - Click **Analyze & Optimize**
   - Navigate tabs: Score → Headline → About → Experience → Skill Gaps → Export
4. **Regenerate content:**
   - Click **↻ Regenerate** on any section for fresh AI rewrites
   - Download your optimized profile report

### 🌐 Method 3: URL Scraping (Advanced)

⚠️ **Requirements:** Valid LinkedIn credentials + Chrome browser
⚠️ **Note:** Use responsibly - respect LinkedIn's Terms of Service

1. **Setup browser dependencies:**
   ```bash
   python check_chrome.py          # Check Chrome compatibility
   python fix_chromedriver.py      # Auto-fix driver issues if needed
   ```
2. **Configure credentials** in `.env` file
3. **Use URL mode** in the application

### 📊 Navigation Tips

- **Score Tab:** See your overall optimization score breakdown
- **Headline Tab:** Get AI-rewritten headlines optimized for your target role
- **About Tab:** Full about section rewrite with storytelling structure
- **Experience Tab:** Bullet points rewritten with action verbs + metrics
- **Skill Gaps Tab:** Discover missing skills compared to top profiles
- **Export Tab:** Download PDF reports and plain text optimizations

---

## 🛠 Troubleshooting

### Common Issues & Solutions

#### 🔧 Dependency Issues

```bash
# Check and install missing packages
python start.py

# If spaCy model fails to download:
python -m spacy download en_core_web_sm --force

# For Python 3.14 compatibility issues:
python quick_start.py  # Uses fallback modes
```

#### 🌐 Chrome/ChromeDriver Issues (URL Mode)

```bash
# Check Chrome and ChromeDriver compatibility
python check_chrome.py

# Auto-fix ChromeDriver issues
python fix_chromedriver.py

# If still having issues, use Manual or PDF mode instead
```

#### 🤖 API Issues (Groq)

- Ensure `GROQ_API_KEY` is set correctly in `.env` file
- Get free API key from [console.groq.com](https://console.groq.com)
- Check API quota and rate limits

#### 📄 PDF Processing Issues

- **File too large:** LinkedIn PDFs should be under 10MB
- **Parsing errors:** Try re-downloading the PDF from LinkedIn
- **Missing content:** Ensure your LinkedIn profile is complete before generating PDF

#### 🔥 Performance Issues

- **Slow startup:** Use `python clean_start.py` for faster initialization
- **Memory errors:** Close other applications, restart the app
- **Model loading:** First run takes longer due to NLP model downloads

### Getting Help

1. **Check startup messages** for automated suggestions
2. **Run diagnostics:** `python start.py`
3. **Use fallback mode:** `python quick_start.py`
4. **Manual input mode** works in all environments

---

## 📊 Scoring System

| Component          | Weight | What it measures                                |
| ------------------ | ------ | ----------------------------------------------- |
| Semantic Match     | 30 pts | How similar your profile sounds to top profiles |
| Skill Coverage     | 25 pts | % of top-role skills you have                   |
| Headline Quality   | 15 pts | Length, keyword presence                        |
| About Section      | 15 pts | Length, metrics, storytelling                   |
| Experience Bullets | 15 pts | Power verbs + quantified achievements           |

---

## 💡 Technical Showcase

**Advanced Skills Demonstrated:**

- **Full NLP Pipeline:** TF-IDF → Named Entity Recognition → Embeddings → Cosine Similarity
- **LLM Integration:** Streaming responses with advanced prompt engineering (Groq/Llama 3.3)
- **Multi-Modal Input:** PDF parsing, manual text input, web scraping with Selenium
- **Robust Architecture:** Multi-module Python structure with dependency management
- **Smart Error Handling:** Fallback modes, compatibility checking, auto-fixing tools
- **Professional UI/UX:** Streamlit session state management for complex workflows
- **Data Processing:** Semantic analysis, keyword extraction, similarity scoring
- **Export Capabilities:** Custom PDF generation with FPDF2, formatted reporting
- **Security Best Practices:** Environment variable management, credential handling
- **Cross-Platform Compatibility:** Windows/Mac/Linux with dependency auto-detection

## 🚀 Quick Start Commands

```bash
# Fastest way to get started
python quick_start.py

# Full diagnostic and setup
python start.py

# Development mode with clean imports
python clean_start.py

# Check browser compatibility (for URL mode)
python check_chrome.py

# Get LinkedIn PDF download instructions
python linkedin_pdf_guide.py
```

## 🎯 Use Cases

- **Job Seekers:** Optimize profiles for target roles with AI-powered suggestions
- **Career Changers:** Identify skill gaps and get strategic career advice
- **Students/Graduates:** Learn what top professionals include in their profiles
- **Recruiters/HR:** Understand what makes profiles stand out in specific roles
- **Professional Development:** Continuous profile improvement with AI assistance

---

## 📜 License & Usage

This project is designed for:

- ✅ Personal profile optimization
- ✅ Educational and learning purposes
- ✅ Portfolio demonstration
- ⚠️ **Please respect LinkedIn's Terms of Service**
- ⚠️ **Use web scraping features responsibly**

---

**🔗 Built with ⬡ LinkedIn Profile Optimizer · Powered by Groq & Advanced NLP**

_For support, issues, or contributions, please refer to the troubleshooting section above._
