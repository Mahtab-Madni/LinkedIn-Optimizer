from pathlib import Path
from datetime import datetime
from typing import Dict
import tempfile
import os

try:
    from fpdf import FPDF, XPos, YPos
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


# ── Colors ────────────────────────────────────────────────────────────────────
NAVY    = (15,  23,  42)
ACCENT  = (99, 102, 241)   # indigo
GREEN   = (16, 185, 129)
RED     = (239,  68,  68)
GOLD    = (245, 158,  11)
LIGHT   = (248, 250, 252)
GRAY    = (100, 116, 139)
WHITE   = (255, 255, 255)


def clean_text_for_pdf(text: str) -> str:
    """Clean text to make it compatible with PDF fonts"""
    if not text:
        return text
    
    # Convert to string if not already
    text = str(text)
    
    # Replace smart quotes and apostrophes
    text = text.replace(''', "'")  # left single quotation mark
    text = text.replace(''', "'")  # right single quotation mark  
    text = text.replace('"', '"')  # left double quotation mark
    text = text.replace('"', '"')  # right double quotation mark
    
    # Replace dashes
    text = text.replace('—', '-')  # em dash
    text = text.replace('–', '-')  # en dash
    
    # Replace other common Unicode characters
    text = text.replace('…', '...')  # ellipsis
    text = text.replace('•', '*')    # bullet
    text = text.replace('◈', '>>')  # diamond
    text = text.replace('✓', '(+)')  # checkmark
    text = text.replace('⚠', '(!)')  # warning
    text = text.replace('\u00A0', ' ')  # non-breaking space to regular space
    
    # Remove or replace other problematic characters
    # Keep only ASCII printable characters plus basic Latin-1
    cleaned = ''
    for char in text:
        if ord(char) <= 255:  # Latin-1 range
            cleaned += char
        else:
            cleaned += '?'  # Replace with placeholder
    
    return cleaned


class LinkedInReport(FPDF):
    def __init__(self, user_name: str, target_role: str, use_unicode: bool = True):
        super().__init__()
        self.user_name   = clean_text_for_pdf(user_name)
        self.target_role = clean_text_for_pdf(target_role)
        self.use_unicode = False  # Default to False for better compatibility
        self.set_auto_page_break(auto=True, margin=20)
        
        # If Unicode support is requested, try to add a Unicode font
        if use_unicode:
            try:
                # Try to use DejaVu Sans for Unicode support
                self.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
                self.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
                self.add_font('DejaVu', 'I', 'DejaVuSans-Oblique.ttf', uni=True)
                self.use_unicode = True
                self.unicode_font_available = True
            except:
                # Fall back to ASCII if Unicode font is not available
                self.use_unicode = False
                self.unicode_font_available = False
        else:
            self.unicode_font_available = False

    def header(self):
        # Navy top bar
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 18, style="F")
        
        # Set appropriate font based on Unicode support
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "B", 9)
        self.set_text_color(*WHITE)
        
        # Use Unicode or ASCII symbol based on font support
        symbol = "◈" if self.use_unicode else ">>"
        
        # Always clean the header text for compatibility
        header_text = f"{symbol}  LinkedIn Profile Optimizer · DataMind"
        header_text = clean_text_for_pdf(header_text)
        
        self.set_xy(10, 5)
        self.cell(0, 8, header_text, align="L")
        self.set_xy(0, 5)
        self.cell(200, 8, datetime.now().strftime("%B %d, %Y"), align="R")
        self.ln(14)

    def footer(self):
        self.set_y(-15)
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "I", 8)
        self.set_text_color(*GRAY)
        footer_text = f"Page {self.page_no()} · Confidential · {self.user_name}"
        # Always clean text for compatibility
        footer_text = clean_text_for_pdf(footer_text)
        self.cell(0, 10, footer_text, align="C")

    def section_title(self, title: str, color=ACCENT):
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "B", 12)
        self.set_text_color(*color)
        self.set_fill_color(*LIGHT)
        # Always clean text to ensure compatibility
        title = clean_text_for_pdf(title)
        self.cell(0, 9, f"  {title}", ln=True, fill=True)
        self.set_draw_color(*color)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def body_text(self, text: str, color=NAVY):
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "", 10)
        self.set_text_color(*color)
        # Always clean text to ensure compatibility
        text = clean_text_for_pdf(text)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def label(self, text: str):
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "B", 9)
        self.set_text_color(*GRAY)
        # Always clean text to ensure compatibility
        text = clean_text_for_pdf(text)
        self.cell(0, 5, text.upper(), ln=True)
        self.ln(1)

    def score_bar(self, label: str, score: int, max_val: int = 100):
        """Draw a horizontal score bar with label."""
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        
        # Clean the label text
        label = clean_text_for_pdf(label)
        
        self.set_font(font_family, "", 9)
        self.set_text_color(*NAVY)
        self.cell(65, 5, label)
        
        bar_w = 80
        bar_h = 5
        fill_w = int((score / max_val) * bar_w)
        
        # Background bar
        self.set_fill_color(*LIGHT)
        self.rect(self.get_x(), self.get_y(), bar_w, bar_h, style="F")
        
        # Score bar
        color = GREEN if score >= (max_val * 0.7) else GOLD if score >= (max_val * 0.5) else RED
        self.set_fill_color(*color)
        self.rect(self.get_x(), self.get_y(), fill_w, bar_h, style="F")
        
        # Score text
        self.set_xy(self.get_x() + bar_w + 5, self.get_y())
        self.cell(20, 5, f"{score}/{max_val}")
        self.ln(7)

    def pill(self, text: str, bg_color=ACCENT):
        """Draw a small pill/chip element."""
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "", 8)
        self.set_fill_color(*bg_color)
        self.set_text_color(*WHITE)
        # Always clean text for compatibility
        text = clean_text_for_pdf(text)
        w = self.get_string_width(text) + 6
        if self.get_x() + w > 195:
            self.ln(7)
        self.cell(w, 5, text, fill=True, ln=False)
        self.cell(2, 5, "")  # spacing

    def comparison_box(self, label: str, original: str, rewritten: str):
        """Side-by-side before/after comparison."""
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        
        # Always clean all text for compatibility
        label = clean_text_for_pdf(label)
        original = clean_text_for_pdf(original or "")
        rewritten = clean_text_for_pdf(rewritten or "")
        
        self.set_font(font_family, "B", 9)
        self.set_text_color(*GRAY)
        self.cell(0, 5, label, ln=True)
        self.ln(1)

        col_w = 88
        start_x = self.get_x()
        start_y = self.get_y()

        # Before box
        self.set_fill_color(255, 240, 240)
        self.set_draw_color(*RED)
        self.rect(start_x, start_y, col_w, 4, style="F")
        self.set_font(font_family, "B", 8)
        self.set_text_color(*RED)
        self.set_xy(start_x + 2, start_y)
        self.cell(col_w - 4, 4, "BEFORE")

        # After box header
        self.set_fill_color(235, 255, 245)
        self.set_draw_color(*GREEN)
        self.rect(start_x + col_w + 4, start_y, col_w, 4, style="F")
        self.set_font(font_family, "B", 8)
        self.set_text_color(*GREEN)
        self.set_xy(start_x + col_w + 6, start_y)
        self.cell(col_w - 4, 4, "AFTER (OPTIMIZED)")

        # Content boxes
        self.set_xy(start_x, start_y + 4)
        self.set_font(font_family, "", 8)
        self.set_text_color(*NAVY)

        # Before content
        lines_before = original.split('\n')[:6]  # Limit lines
        content_before = '\n'.join(lines_before[:3]) + ('...' if len(lines_before) > 3 else '')
        if len(content_before) > 200:
            content_before = content_before[:200] + "..."

        # After content
        lines_after = rewritten.split('\n')[:6]
        content_after = '\n'.join(lines_after[:3]) + ('...' if len(lines_after) > 3 else '')
        if len(content_after) > 200:
            content_after = content_after[:200] + "..."

        # Draw content boxes with border
        box_height = 25
        self.set_draw_color(*GRAY)

        # Before box
        self.rect(start_x, start_y + 4, col_w, box_height)
        self.set_xy(start_x + 2, start_y + 6)
        with self.local_context():
            self.multi_cell(col_w - 4, 3, content_before, border=0)

        # After box
        self.rect(start_x + col_w + 4, start_y + 4, col_w, box_height)
        self.set_xy(start_x + col_w + 6, start_y + 6)
        with self.local_context():
            self.multi_cell(col_w - 4, 3, content_after, border=0)

        # Move cursor after boxes
        self.set_xy(10, start_y + 4 + box_height + 5)


def generate_pdf_report(
    user_profile: dict,
    rewritten: dict,
    scores: dict,
    gap: dict,
    top_analysis: dict,
    target_role: str,
    output_path: str = None,
    use_unicode: bool = True,
) -> str:
    if not FPDF_AVAILABLE:
        raise RuntimeError("fpdf2 not installed. Run: pip install fpdf2")

    user_name = user_profile.get("name", "User")
    if not output_path:
        safe_name = user_name.replace(" ", "_").lower()
        # Use cross-platform temporary directory
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"linkedin_report_{safe_name}.pdf")

    pdf = LinkedInReport(user_name, target_role, use_unicode=use_unicode)
    pdf.add_page()

    # ── Cover block ───────────────────────────────────────────────────────────
    pdf.set_fill_color(*NAVY)
    pdf.rect(10, pdf.get_y(), 190, 28, style="F")
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*WHITE)
    pdf.set_xy(16, pdf.get_y() + 4)
    pdf.cell(0, 8, f"LinkedIn Optimization Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(16, pdf.get_y())
    # Clean user name and target role text
    subtitle_text = f"{user_name}  ·  Target Role: {target_role}"
    subtitle_text = clean_text_for_pdf(subtitle_text)
    pdf.cell(0, 6, subtitle_text, ln=True)
    pdf.ln(18)

    
    diamond_symbol = "◈" if pdf.use_unicode else ">>"
    check_symbol = "✓" if pdf.use_unicode else "(+)"
    warning_symbol = "⚠" if pdf.use_unicode else "(!)"
    
    pdf.section_title(f"{diamond_symbol} Overall Optimization Score")
    overall = scores.get("overall", 0)
    grade = "A" if overall >= 80 else "B" if overall >= 65 else "C" if overall >= 50 else "D"
    color = GREEN if overall >= 70 else GOLD if overall >= 50 else RED

    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(*color)
    pdf.cell(40, 20, f"{overall:.0f}", align="C")
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*NAVY)
    pdf.cell(20, 20, f"/ 100  [{grade}]", align="L")
    pdf.ln(22)

    # Score breakdown bars
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6, "Score Breakdown:", ln=True)
    pdf.ln(2)
    for label, pts in scores.get("breakdown", {}).items():
        max_pts = int(label.split("(")[1].replace("pts)", "")) if "pts)" in label else 100
        pdf.score_bar(label, pts, max_pts)
    pdf.ln(4)

    # ── Gap Analysis ──────────────────────────────────────────────────────────
    pdf.section_title(f"{diamond_symbol} Keyword & Skills Gap Analysis")

    pdf.label("Missing Skills (Add these to your profile)")
    for skill in gap.get("missing_skills", [])[:12]:
        pdf.pill(skill, RED)
    pdf.ln(9)

    pdf.label("Present Skills (You already have these)")
    for skill in gap.get("present_skills", [])[:8]:
        pdf.pill(skill, GREEN)
    pdf.ln(9)

    pdf.label("Top Industry Keywords")
    for keyword in top_analysis.get("top_keywords", [])[:10]:
        pdf.pill(keyword, ACCENT)
    pdf.ln(6)

    # ── AI Improvements ──────────────────────────────────────────────────────
    pdf.section_title(f"{diamond_symbol} AI-Optimized Profile Content")

    # Headline
    if "headline" in rewritten:
        pdf.comparison_box(
            "Professional Headline",
            user_profile.get("headline", ""),
            rewritten["headline"]
        )

    # About section
    if "about" in rewritten:
        pdf.comparison_box(
            "About Section",
            user_profile.get("about", ""),
            rewritten["about"]
        )

    # Experience bullets
    if "experience" in rewritten and rewritten["experience"]:
        for i, exp in enumerate(rewritten["experience"][:2]):  # Show top 2
            pdf.comparison_box(
                f"Experience: {exp.get('title', 'Role')} at {exp.get('company', 'Company')}",
                exp.get("original", ""),
                exp.get("rewritten", "")
            )

    # ── Action Items ────────────────────────────────────────────────────────
    pdf.section_title(f"{diamond_symbol} Recommended Actions")
    
    actions = [
        f"{check_symbol} Update headline with target role keywords",
        f"{check_symbol} Add missing skills to your Skills section",
        f"{check_symbol} Incorporate industry keywords into your About section",
        f"{check_symbol} Quantify achievements with metrics in experience descriptions",
        f"{warning_symbol} Consider getting endorsements for missing skills",
    ]
    
    for action in actions:
        pdf.body_text(action)
    
    pdf.output(output_path)
    return output_path