import time
import json
import random
import os
import re
from pathlib import Path

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


try:
    from groq import Groq
    from dotenv import load_dotenv
    AI_AVAILABLE = True
    # Load .env from Data & Configuration folder
    env_path = Path(__file__).parent.parent.parent / "Data & Configuration" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # fallback to default behavior
except ImportError:
    AI_AVAILABLE = False


# Cache directory in Data & Configuration folder
CACHE_DIR = Path(__file__).parent.parent.parent / "Data & Configuration" / "data" / "cached_profiles"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _random_delay(min_s=1.5, max_s=3.5):
    time.sleep(random.uniform(min_s, max_s))


def _cache_path(profile_id: str) -> Path:
    return CACHE_DIR / f"{profile_id}.json"


def _load_cache(profile_id: str):
    p = _cache_path(profile_id)
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return None


def _save_cache(profile_id: str, data: dict):
    with open(_cache_path(profile_id), "w") as f:
        json.dump(data, f, indent=2)


def parse_linkedin_pdf(pdf_file) -> dict:
    """
    Parse a LinkedIn profile PDF (downloaded from LinkedIn's "Save to PDF" feature).
    Extracts structured profile information from the PDF text.
    """
    if not PDF_AVAILABLE:
        raise RuntimeError(
            "PyPDF2 not installed. Install with: pip install PyPDF2"
        )
    
    try:
        # Read PDF content
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Create lowercase version for text processing
        text_lower = text.lower()
        
        # Initialize profile structure
        profile = {
            "url": "pdf_upload",
            "name": "",
            "current_role": "",
            "headline": "",
            "location": "",
            "about": "",
            "experience": [],
            "skills": [],
            "education": [],
            "certifications": [],
            "connections": "",
        }
        
        # Parse name (usually the first line or early in the document)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extract name (typically appears early, often as the largest text)
        for i, line in enumerate(lines[:10]):
            if len(line.split()) <= 4 and len(line) > 5 and not any(word in line.lower() for word in ['linkedin', 'profile', 'member', 'www', 'http']):
                if not re.search(r'\d|\@|\.|/', line):  # Avoid emails, dates, URLs
                    profile["name"] = line.title()
                    break
        
        # Extract headline (usually follows the name)
        headline_keywords = ['engineer', 'developer', 'manager', 'analyst', 'director', 'specialist', 'consultant', 'lead', 'senior', 'junior']
        for line in lines[:20]:
            if any(keyword in line.lower() for keyword in headline_keywords):
                if len(line) > 10 and len(line) < 200:  # Reasonable headline length
                    profile["headline"] = line
                    break
        
        # Extract current role (try to determine from experience or headline)
        current_role_indicators = ['student', 'graduate', 'intern', 'fresher', 'entry', 'junior', 'senior', 'lead', 'manager', 'director', 'ceo', 'cto', 'founder']
        
        # First try to determine from the first experience entry or headline
        if profile["headline"]:
            headline_lower = profile["headline"].lower()
            if any(indicator in headline_lower for indicator in ['student', 'graduate', 'fresher']):
                profile["current_role"] = "Student/Fresh Graduate"
            elif any(indicator in headline_lower for indicator in ['senior', 'lead', 'manager', 'director']):
                profile["current_role"] = "Experienced Professional" 
            else:
                profile["current_role"] = "Mid-Level Professional"
        
        # If no headline, try to infer from text patterns
        if not profile["current_role"] and text_lower:
            if any(term in text_lower for term in ['currently pursuing', 'student at', 'university', 'college', 'degree']):
                profile["current_role"] = "Student"
            elif any(term in text_lower for term in ['years of experience', 'seasoned', 'extensive experience']):
                profile["current_role"] = "Experienced Professional"
            else:
                profile["current_role"] = "Professional"
        
        # Extract about section (look for summary/about keywords)
        about_start = None
        for keyword in ['about', 'summary', 'overview']:
            if keyword in text_lower:
                about_start = text_lower.find(keyword)
                break
        
        if about_start:
            about_text = text[about_start:about_start+200000000]  # Get next 200000000 chars
            # Clean up the about section
            about_lines = [line.strip() for line in about_text.split('\n') if line.strip()]
            if len(about_lines) > 1:
                # Skip the header line, join the rest
                profile["about"] = ' '.join(about_lines[1:10])  # Take reasonable amount
        
        # Extract experience (look for work history patterns)
        exp_keywords = ['experience', 'work', 'employment', 'career']
        for keyword in exp_keywords:
            if keyword in text_lower:
                exp_section = text[text_lower.find(keyword):text_lower.find(keyword)+300000000]  # Get next 300000000 chars
                # Basic experience parsing - look for company names and titles
                exp_lines = [line.strip() for line in exp_section.split('\n') if line.strip()]
                
                current_exp = {}
                for line in exp_lines[1:20]:  # Skip header
                    # Look for lines that might be job titles or companies
                    if len(line) > 5 and len(line) < 100:
                        if not current_exp:
                            current_exp["title"] = line
                        elif "company" not in current_exp:
                            current_exp["company"] = line
                        else:
                            current_exp["description"] = line
                            profile["experience"].append(current_exp)
                            current_exp = {}
                        
                        if len(profile["experience"]) >= 5:  # Limit to 5 experiences
                            break
                break
        
        # Extract skills (look for skills section)
        if 'skill' in text_lower:
            skills_start = text_lower.find('skill')
            skills_section = text[skills_start:skills_start+100000000]  # Get next 100000000 chars
            # Simple skills extraction - look for comma-separated or line-separated items
            potential_skills = []
            for line in skills_section.split('\n')[:20]:
                line = line.strip()
                if len(line) > 2 and len(line) < 30:  # Reasonable skill name length
                    # Split by commas if present
                    if ',' in line:
                        potential_skills.extend([s.strip() for s in line.split(',') if s.strip()])
                    else:
                        potential_skills.append(line)
            
            # Filter and clean skills
            profile["skills"] = [skill for skill in potential_skills[:20] 
                               if len(skill) > 2 and not any(word in skill.lower() 
                               for word in ['page', 'section', 'profile', 'linkedin'])]
        
        return profile
        
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {str(e)}")


def parse_linkedin_pdf_with_ai(pdf_file) -> dict:
    """
    AI-powered LinkedIn profile PDF parser using Groq.
    Extracts structured profile information with better accuracy than regex parsing.
    """
    if not PDF_AVAILABLE:
        raise RuntimeError(
            "PyPDF2 not installed. Install with: pip install PyPDF2"
        )
    
    if not AI_AVAILABLE:
        print("AI parsing unavailable, falling back to basic parsing...")
        return parse_linkedin_pdf(pdf_file)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY not found, falling back to basic parsing...")
        return parse_linkedin_pdf(pdf_file)
    
    try:
        # Extract text from PDF
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # If text is too long, truncate to avoid API limits
        if len(text) > 8000:
            text = text[:8000] + "\n[Content truncated due to length...]"
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Create AI prompt for profile extraction
        prompt = f"""Analyze this LinkedIn profile PDF text and extract structured information in valid JSON format.

PDF Content:
{text}

Please extract and return ONLY a valid JSON object with these fields:
{{
  "name": "Full name of the person",
  "current_role": "Current role/status (e.g., 'Student', 'Software Engineer', 'Recent Graduate', 'Career Changer', 'Entry Level Professional', 'Senior Professional')",
  "headline": "Professional headline/title",
  "location": "City, State/Country if mentioned",
  "about": "About/summary section full text",
  "experience": [
    {{
      "title": "Job title",
      "company": "Company name",
      "duration": "Time period",
      "description": "full description"
    }}
  ],
  "skills": ["skill1", "skill2", "skill3"],
  "education": [
    {{
      "school": "School name",
      "degree": "Degree type",
      "field": "Field of study",
      "year": "Graduation year if available"
    }}
  ],
  "certifications": ["cert1", "cert2"],
  "connections": "Number of connections if mentioned"
}}

Rules:
- Return ONLY the JSON object, no other text
- For current_role, analyze the profile and categorize as: 'Student', 'Recent Graduate', 'Entry Level Professional', 'Mid-Level Professional', 'Senior Professional', 'Executive/Leadership', or 'Career Changer'
- If information is not found, use empty strings or empty arrays
- Extract up to 5 most recent/relevant experience entries
- Extract up to 10 most relevant skills
- Be precise and avoid making up information
- Ensure all JSON is properly formatted and valid"""
        
        # Call Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for more consistent extraction
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert at extracting structured information from LinkedIn profiles. Always return valid JSON format only."
                },
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response
        ai_response = response.choices[0].message.content.strip()
        
        # Clean the response - remove any markdown formatting
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:]
        if ai_response.startswith("```"):
            ai_response = ai_response[3:]
        if ai_response.endswith("```"):
            ai_response = ai_response[:-3]
        
        # Parse JSON
        try:
            profile = json.loads(ai_response)
            
            # Add required fields if missing
            profile["url"] = "pdf_upload_ai"
            
            # Ensure all required fields exist with defaults
            default_profile = {
                "url": "pdf_upload_ai",
                "name": "",
                "current_role": "",
                "headline": "",
                "location": "",
                "about": "",
                "experience": [],
                "skills": [],
                "education": [],
                "certifications": [],
                "connections": "",
            }
            
            # Merge with defaults
            for key, default_value in default_profile.items():
                if key not in profile:
                    profile[key] = default_value
            
            # Validate and clean up experience entries
            if profile["experience"]:
                cleaned_experience = []
                for exp in profile["experience"][:5]:  # Limit to 5 entries
                    if isinstance(exp, dict) and "title" in exp:
                        cleaned_exp = {
                            "title": exp.get("title", ""),
                            "company": exp.get("company", ""),
                            "duration": exp.get("duration", ""),
                            "description": exp.get("description", "")
                        }
                        cleaned_experience.append(cleaned_exp)
                profile["experience"] = cleaned_experience
            
            print("✅ AI-powered PDF parsing successful")
            return profile
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"AI Response: {ai_response[:200]}...")
            # Fall back to basic parsing
            return parse_linkedin_pdf(pdf_file)
            
    except Exception as e:
        print(f"❌ AI PDF parsing error: {e}")
        # Fall back to basic parsing
        return parse_linkedin_pdf(pdf_file)


def _extract_profile_id(url: str) -> str:
    """Extract LinkedIn username from URL."""
    url = url.rstrip("/")
    parts = url.split("/")
    try:
        idx = parts.index("in")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return url.split("/")[-1]


def _create_chrome_options():
    """Create fresh ChromeOptions object with standard arguments."""
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    # Uncomment for headless (may increase detection risk):
    # options.add_argument("--headless=new")
    return options


def _init_driver():
    """Initialize undetected Chrome driver with automatic version handling."""
    try:
        # First attempt: Use default undetected-chromedriver
        options = _create_chrome_options()
        
        # Try with version auto-detection
        driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
        return driver
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ChromeDriver initialization failed: {error_msg}")
        
        # Check if it's a version mismatch issue
        if "version" in error_msg.lower() and "chrome" in error_msg.lower():
            print("🔧 Detected Chrome/ChromeDriver version mismatch")
            
            # Try force updating ChromeDriver
            try:
                print("🔄 Attempting to force update ChromeDriver...")
                
                # Clear any cached ChromeDriver
                import os
                import tempfile
                temp_dir = tempfile.gettempdir()
                for file in os.listdir(temp_dir):
                    if "chromedriver" in file.lower() or "undetected" in file.lower():
                        try:
                            os.remove(os.path.join(temp_dir, file))
                        except:
                            pass
                
                # Create FRESH options object (cannot reuse previous one)
                fresh_options = _create_chrome_options()
                
                # Force reinstall with specific version detection
                driver = uc.Chrome(
                    options=fresh_options,
                    use_subprocess=True,
                    version_main=None,  # Auto-detect
                    driver_executable_path=None  # Force re-download
                )
                print("✅ ChromeDriver updated successfully!")
                return driver
                
            except Exception as e2:
                print(f"❌ Auto-update failed: {e2}")
                raise RuntimeError(
                    f"Chrome/ChromeDriver version mismatch detected. "
                    f"Your Chrome version doesn't match ChromeDriver. "
                    f"Solutions: 1) Use Manual Input mode (recommended), "
                    f"2) Update Chrome to latest version, "
                    f"3) Run: pip install --upgrade undetected-chromedriver"
                )
        else:
            # Other ChromeDriver errors
            raise RuntimeError(
                f"ChromeDriver error: {error_msg}. "
                f"Recommendation: Use Manual Input mode for reliable results."
            )


def _login(driver, email: str, password: str) -> bool:
    """Log into LinkedIn."""
    try:
        driver.get("https://www.linkedin.com/login")
        _random_delay(2, 4)
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "[type=submit]").click()
        _random_delay(3, 5)
        return "feed" in driver.current_url or "mynetwork" in driver.current_url
    except Exception:
        return False


def _scrape_single_profile(driver, url: str) -> dict:
    """Scrape a single LinkedIn profile page."""
    driver.get(url)
    _random_delay(2, 4)

    profile = {
        "url": url,
        "name": "",
        "headline": "",
        "location": "",
        "about": "",
        "experience": [],
        "skills": [],
        "education": [],
        "certifications": [],
        "connections": "",
    }

    wait = WebDriverWait(driver, 10)

    # ── Name ──────────────────────────────────────────────────────────────
    try:
        profile["name"] = driver.find_element(
            By.CSS_SELECTOR, "h1.text-heading-xlarge"
        ).text.strip()
    except NoSuchElementException:
        pass

    # ── Headline ──────────────────────────────────────────────────────────
    try:
        profile["headline"] = driver.find_element(
            By.CSS_SELECTOR, "div.text-body-medium"
        ).text.strip()
    except NoSuchElementException:
        pass

    # ── Location ──────────────────────────────────────────────────────────
    try:
        profile["location"] = driver.find_element(
            By.CSS_SELECTOR, "span.text-body-small.inline"
        ).text.strip()
    except NoSuchElementException:
        pass

    # ── About ─────────────────────────────────────────────────────────────
    try:
        about_section = driver.find_element(
            By.CSS_SELECTOR, "div#about ~ div .full-width"
        )
        profile["about"] = about_section.text.strip()
    except NoSuchElementException:
        try:
            spans = driver.find_elements(
                By.CSS_SELECTOR, "section.summary div span[aria-hidden='true']"
            )
            profile["about"] = " ".join(s.text for s in spans).strip()
        except Exception:
            pass

    # ── Experience ────────────────────────────────────────────────────────
    try:
        exp_items = driver.find_elements(
            By.CSS_SELECTOR, "section#experience-section li"
        )
        for item in exp_items[:6]:
            try:
                title = item.find_element(By.CSS_SELECTOR, "h3").text.strip()
                company = item.find_element(By.CSS_SELECTOR, "p.pv-entity__secondary-title").text.strip()
                desc_els = item.find_elements(By.CSS_SELECTOR, "div.pv-entity__description")
                desc = desc_els[0].text.strip() if desc_els else ""
                profile["experience"].append({
                    "title": title,
                    "company": company,
                    "description": desc,
                })
            except Exception:
                pass
    except NoSuchElementException:
        pass

    # ── Skills ────────────────────────────────────────────────────────────
    try:
        skill_els = driver.find_elements(
            By.CSS_SELECTOR, "span.mr1.hoverable-link-text"
        )
        profile["skills"] = [s.text.strip() for s in skill_els if s.text.strip()][:20]
    except NoSuchElementException:
        pass

    return profile



def scrape_profile(url: str, email: str = "", password: str = "") -> dict:
    """
    Scrape a LinkedIn profile by URL.
    Returns structured profile dict.
    Caches results to avoid repeat scraping.
    """
    if not SELENIUM_AVAILABLE:
        raise RuntimeError(
            "Selenium / undetected-chromedriver not installed. "
            "Use manual paste mode instead."
        )

    profile_id = _extract_profile_id(url)
    cached = _load_cache(profile_id)
    if cached:
        return cached

    driver = _init_driver()
    try:
        if email and password:
            success = _login(driver, email, password)
            if not success:
                raise RuntimeError("LinkedIn login failed. Check credentials.")

        data = _scrape_single_profile(driver, url)
        _save_cache(profile_id, data)
        return data
    finally:
        driver.quit()


def scrape_top_profiles(role: str, email: str, password: str, count: int = 8) -> list[dict]:
    """
    Search LinkedIn for top profiles matching a role and scrape them.
    Returns list of profile dicts.
    """
    if not SELENIUM_AVAILABLE:
        raise RuntimeError("Selenium not available.")

    cache_key = f"top_{role.replace(' ', '_').lower()}_{count}"
    cached = _load_cache(cache_key)
    if cached:
        return cached

    driver = _init_driver()
    profiles = []
    try:
        _login(driver, email, password)

        # Search for people with this job title
        search_url = (
            f"https://www.linkedin.com/search/results/people/"
            f"?keywords={role.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER"
        )
        driver.get(search_url)
        _random_delay(3, 5)

        # Collect profile URLs from search results
        links = driver.find_elements(
            By.CSS_SELECTOR, "a.app-aware-link[href*='/in/']"
        )
        urls = []
        for link in links:
            href = link.get_attribute("href")
            if href and "/in/" in href and href not in urls:
                urls.append(href.split("?")[0])
            if len(urls) >= count:
                break

        # Scrape each profile
        for url in urls[:count]:
            try:
                p = _scrape_single_profile(driver, url)
                if p.get("headline"):
                    profiles.append(p)
                _random_delay(2, 4)
            except Exception:
                continue

        _save_cache(cache_key, profiles)
        return profiles
    finally:
        driver.quit()



def parse_manual_profile(
    name: str,
    current_role: str,
    headline: str,
    about: str,
    experience_text: str,
    skills_text: str,
) -> dict:
    """
    Build a structured profile dict from manually pasted text.
    No scraping, no ToS concerns — great for demos.
    """
    # Parse experience blocks (split by double newline or numbered list)
    exp_blocks = [b.strip() for b in experience_text.split("\n\n") if b.strip()]
    experience = []
    for block in exp_blocks[:6]:
        lines = block.split("\n")
        experience.append({
            "title": lines[0] if lines else "",
            "company": lines[1] if len(lines) > 1 else "",
            "description": " ".join(lines[2:]) if len(lines) > 2 else "",
        })

    skills = [s.strip() for s in skills_text.replace(",", "\n").split("\n") if s.strip()]

    return {
        "url": "manual_input",
        "name": name,
        "current_role": current_role,
        "headline": headline,
        "location": "",
        "about": about,
        "experience": experience,
        "skills": skills[:20],
        "education": [],
        "certifications": [],
        "connections": "",
    }
