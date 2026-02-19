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
    if not text:
        return text
    
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
    
    return text


class LinkedInReport(FPDF):
    def __init__(self, user_name: str, target_role: str, use_unicode: bool = False):
        super().__init__()
        self.user_name   = user_name
        self.target_role = target_role
        self.use_unicode = use_unicode
        self.set_auto_page_break(auto=True, margin=20)
        
        # If Unicode support is requested, try to add a Unicode font
        if self.use_unicode:
            try:
                # Try to use DejaVu Sans for Unicode support
                self.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
                self.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
                self.add_font('DejaVu', 'I', 'DejaVuSans-Oblique.ttf', uni=True)
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
        
        # Clean the header text if not using Unicode
        header_text = f"{symbol}  LinkedIn Profile Optimizer · DataMind"
        if not self.use_unicode:
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
        if not self.use_unicode:
            footer_text = clean_text_for_pdf(footer_text)
        self.cell(0, 10, footer_text, align="C")

    def section_title(self, title: str, color=ACCENT):
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "B", 12)
        self.set_text_color(*color)
        self.set_fill_color(*LIGHT)
        # Clean text of Unicode characters if not using Unicode fonts
        if not self.use_unicode:
            title = clean_text_for_pdf(title)
        self.cell(0, 9, f"  {title}", ln=True, fill=True)
        self.set_draw_color(*color)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def body_text(self, text: str, color=NAVY):
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "", 10)
        self.set_text_color(*color)
        # Clean text of Unicode characters if not using Unicode fonts
        if not self.use_unicode:
            text = clean_text_for_pdf(text)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def label(self, text: str):
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "B", 9)
        self.set_text_color(*GRAY)
        # Clean text of Unicode characters if not using Unicode fonts
        if not self.use_unicode:
            text = clean_text_for_pdf(text)
        self.cell(0, 5, text.upper(), ln=True)
        self.ln(1)

    def score_bar(self, label: str, score: float, max_score: float = 100):
        """Draw a visual score bar."""
        pct = min(score / max_score, 1.0)
        color = GREEN if pct >= 0.7 else GOLD if pct >= 0.4 else RED

        self.set_font("Helvetica", "", 9)
        self.set_text_color(*NAVY)
        self.cell(70, 6, label)
        self.cell(20, 6, f"{score:.0f}/{max_score:.0f}", align="R")

        # Bar background
        bar_x = self.get_x() + 5
        bar_y = self.get_y() + 1
        self.set_fill_color(220, 220, 220)
        self.rect(bar_x, bar_y, 80, 4, style="F")

        # Filled portion
        self.set_fill_color(*color)
        self.rect(bar_x, bar_y, 80 * pct, 4, style="F")

        self.ln(7)

    def pill(self, text: str, bg_color=ACCENT):
        """Draw a small pill/chip element."""
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "", 8)
        self.set_fill_color(*bg_color)
        self.set_text_color(*WHITE)
        # Clean text if not using Unicode fonts
        if not self.use_unicode:
            text = clean_text_for_pdf(text)
        w = self.get_string_width(text) + 6
        if self.get_x() + w > 195:
            self.ln(7)
        self.cell(w, 5, text, fill=True, ln=False)
        self.cell(2, 5, "")  # spacing

    def comparison_box(self, label: str, original: str, rewritten: str):
        """Side-by-side before/after comparison."""
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        
        # Clean all text if not using Unicode fonts
        if not self.use_unicode:
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

        self.set_xy(start_x, start_y + 5)

        # Before content
        font_family = "DejaVu" if self.use_unicode else "Helvetica"
        self.set_font(font_family, "", 8)
        self.set_text_color(*NAVY)
        before_text = original[:400] + ("..." if len(original) > 400 else "")
        # Clean text if not using Unicode fonts
        if not self.use_unicode:
            before_text = clean_text_for_pdf(before_text or "(empty)")
        self.multi_cell(col_w, 4.5, before_text or "(empty)")

        after_y = start_y + 5
        self.set_xy(start_x + col_w + 4, after_y)
        after_text = rewritten[:400] + ("..." if len(rewritten) > 400 else "")
        # Clean text if not using Unicode fonts
        if not self.use_unicode:
            after_text = clean_text_for_pdf(after_text or "(empty)")
        self.multi_cell(col_w, 4.5, after_text or "(empty)")

        end_y = max(self.get_y(), start_y + 30)
        self.set_y(end_y + 4)


def generate_pdf_report(
    user_profile: dict,
    rewritten: dict,
    scores: dict,
    gap: dict,
    top_analysis: dict,
    target_role: str,
    output_path: str = None,
    use_unicode: bool = False,
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
    if not pdf.use_unicode:
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

    pdf.label(f"Skills You Already Have {check_symbol}")
    for skill in gap.get("present_skills", [])[:12]:
        pdf.pill(skill, GREEN)
    pdf.ln(9)

    pdf.label("Missing Power Verbs in Experience")
    for verb in gap.get("missing_power_verbs", []):
        pdf.pill(verb, GOLD)
    pdf.ln(9)

    has_metrics = gap.get("has_quantified_metrics", False)
    pdf.body_text(
        f"{f'{check_symbol} Quantified metrics found in your profile.' if has_metrics else f'{warning_symbol} No quantified metrics detected - add numbers to your experience bullets for 2x more impact.'}",
        GREEN if has_metrics else RED,
    )
    pdf.ln(2)

    # ── Optimized Headline ────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(f"{diamond_symbol} Optimized Headline")
    pdf.comparison_box(
        "LinkedIn Headline",
        user_profile.get("headline", ""),
        rewritten.get("headline", ""),
    )

    # ── Optimized About ───────────────────────────────────────────────────────
    pdf.section_title(f"{diamond_symbol} Optimized About Section")
    pdf.comparison_box(
        "About / Summary",
        user_profile.get("about", ""),
        rewritten.get("about", ""),
    )

    # ── Experience ────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title(f"{diamond_symbol} Optimized Experience Bullets")
    for i, exp in enumerate(rewritten.get("experience", []), 1):
        font_family = "DejaVu" if pdf.use_unicode else "Helvetica"
        pdf.set_font(font_family, "B", 10)
        pdf.set_text_color(*NAVY)
        exp_title = f"{i}. {exp.get('title', '')} @ {exp.get('company', '')}"
        if not pdf.use_unicode:
            exp_title = clean_text_for_pdf(exp_title)
        pdf.cell(0, 6, exp_title, ln=True)
        pdf.comparison_box(
            "",
            exp.get("original", ""),
            exp.get("rewritten", ""),
        )

    # ── Skills Recommendations ────────────────────────────────────────────────
    pdf.section_title(f"{diamond_symbol} Skills Recommendations")
    pdf.body_text(rewritten.get("skills_recommendations", ""))

    # ── Next Steps ────────────────────────────────────────────────────────────
    pdf.section_title(f"{diamond_symbol} Your Top 5 Action Items", GOLD)
    next_steps = [
        f"1. Update your headline to: \"{rewritten.get('headline', '').strip()[:80]}...\"",
        f"2. Add {len(gap.get('missing_skills', []))} missing skills to your Skills section",
        "3. Replace your About section with the optimized version above",
        "4. Add quantified metrics to ALL experience bullets (%, $, numbers)",
        f"5. Connect with people who hold the role: '{target_role}' for referrals",
    ]
    for step in next_steps:
        pdf.body_text(f"  {step}")

    pdf.output(output_path)
    return output_path
