"""
scripts/generators/generate_powerpoint_presentation.py

Generates a publication-quality 20-slide executive PowerPoint presentation
synthesizing the complete Exploratory Data Analysis from 01_exploratory_data_analysis.ipynb,
the K-Means clustering pipeline (V2 competency-based and V1), and high-resolution figures.

Deck format: 16:9 Widescreen (13.333" x 7.5")
Design System: Executive Tech / Academic Analytics
Target Output: deliverables/AI_DS_Sem4_Comprehensive_Analysis_Deck.pptx
"""

import os
import sys
import pandas as pd
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# CONSTANTS & PALETTE
# -----------------------------------------------------------------------------
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Color Palette
DARK_BG = RGBColor(15, 23, 42)        # #0F172A (Deep Slate)
DARK_CARD = RGBColor(30, 41, 59)      # #1E293B
DARK_BORDER = RGBColor(51, 65, 85)    # #334155

LIGHT_BG = RGBColor(248, 250, 252)    # #F8FAFC (Soft slate white)
CARD_BG = RGBColor(255, 255, 255)     # Pure white
CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0

PRIMARY_NAVY = RGBColor(15, 23, 42)   # #0F172A
TEXT_DARK = RGBColor(15, 23, 42)      # #0F172A
TEXT_MUTED = RGBColor(100, 116, 139)  # #64748B
TEXT_LIGHT = RGBColor(255, 255, 255)
TEXT_LIGHT_MUTED = RGBColor(148, 163, 184) # #94A3B8

BLUE_ACCENT = RGBColor(37, 99, 235)   # #2563EB (Cobalt)
CYAN_ACCENT = RGBColor(14, 165, 233)  # #0EA5E9 (Electric Cyan)
GREEN_SUCCESS = RGBColor(16, 185, 129)# #10B981 (Emerald)
AMBER_WARN = RGBColor(245, 158, 11)   # #F59E0B (Amber)
RED_ALERT = RGBColor(239, 68, 68)     # #EF4444 (Coral/Red)
PURPLE_ACCENT = RGBColor(139, 92, 246)# #8B5CF6

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def resolve_figure_path(rel_path_or_filename: str) -> str:
    """Resolve figure path across refactored subdirectories in reports/figures/."""
    if not rel_path_or_filename:
        return ""
    if os.path.exists(rel_path_or_filename):
        return rel_path_or_filename
    base = os.path.basename(rel_path_or_filename)
    candidates = [
        os.path.join("reports", "figures", "eda", base),
        os.path.join("reports", "figures", "eda", "extracted", base),
        os.path.join("reports", "figures", "clustering_v1", base),
        os.path.join("reports", "figures", "clustering_v2", base),
        os.path.join("reports", "figures", base),
        os.path.join("reports", "figures", "extracted_eda", base),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return rel_path_or_filename

def set_slide_background(slide, color):
    """Set solid color background for slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, tracker: str, title: str, subtitle: str, dark: bool = False):
    """Adds a standard executive header zone."""
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    # Category Tracker Pill
    p0 = tf.paragraphs[0]
    p0.text = tracker.upper()
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(9.5)
    p0.font.bold = True
    p0.font.color.rgb = CYAN_ACCENT if dark else BLUE_ACCENT
    p0.space_after = Pt(2)

    # Main Title
    p1 = tf.add_paragraph()
    p1.text = title
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_LIGHT if dark else TEXT_DARK
    p1.space_after = Pt(3)

    # Subtitle
    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.font.name = FONT_BODY
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_LIGHT_MUTED if dark else TEXT_MUTED

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
    """Creates a container card shape."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_footer(slide, current_slide: int, total_slides: int = 20, dark: bool = False):
    """Standard bottom metadata bar."""
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(10.0), Inches(0.35))
    tf = footer_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p = tf.paragraphs[0]
    p.text = "Department of Artificial Intelligence & Data Science  |  Semester IV Academic Result Analysis & K-Means Segmentation"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = RGBColor(100, 116, 139) if dark else RGBColor(148, 163, 184)

    # Page number on right
    p_num = slide.shapes.add_textbox(Inches(11.0), Inches(7.05), Inches(1.533), Inches(0.35))
    tf_num = p_num.text_frame
    p_right = tf_num.paragraphs[0]
    p_right.alignment = PP_ALIGN.RIGHT
    p_right.text = f"{current_slide:02d} / {total_slides:02d}"
    p_right.font.name = FONT_BODY
    p_right.font.size = Pt(9)
    p_right.font.bold = True
    p_right.font.color.rgb = CYAN_ACCENT if dark else BLUE_ACCENT

def add_stat_card(slide, left, top, width, height, value: str, label: str, context: str, val_color=BLUE_ACCENT, dark=False):
    """Creates a stylized KPI metric card."""
    bg = DARK_CARD if dark else CARD_BG
    border = DARK_BORDER if dark else CARD_BORDER
    add_card(slide, left, top, width, height, bg_color=bg, border_color=border)

    tb = slide.shapes.add_textbox(left + Inches(0.18), top + Inches(0.15), width - Inches(0.36), height - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_val = tf.paragraphs[0]
    p_val.text = value
    p_val.font.name = FONT_HEADING
    p_val.font.size = Pt(30)
    p_val.font.bold = True
    p_val.font.color.rgb = val_color
    p_val.space_after = Pt(2)

    p_lbl = tf.add_paragraph()
    p_lbl.text = label
    p_lbl.font.name = FONT_HEADING
    p_lbl.font.size = Pt(11)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = TEXT_LIGHT if dark else TEXT_DARK
    p_lbl.space_after = Pt(2)

    p_ctx = tf.add_paragraph()
    p_ctx.text = context
    p_ctx.font.name = FONT_BODY
    p_ctx.font.size = Pt(9)
    p_ctx.font.color.rgb = TEXT_LIGHT_MUTED if dark else TEXT_MUTED

def style_cell(cell, text, font_size=9, bold=False, text_color=TEXT_DARK, bg_color=None, align=PP_ALIGN.CENTER):
    """Utility to format a table cell."""
    if bg_color:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg_color
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = str(text)
    p.alignment = align
    p.font.name = FONT_BODY
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = text_color


# -----------------------------------------------------------------------------
# PRESENTATION GENERATOR CLASS
# -----------------------------------------------------------------------------
class PresentationBuilder:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.prs = Presentation()
        self.prs.slide_width = SLIDE_WIDTH
        self.prs.slide_height = SLIDE_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6] # completely blank layout

    def build_deck(self):
        print("Starting deck creation...")
        self.slide_01_title()
        self.slide_02_executive_summary()
        self.slide_03_academic_architecture()
        self.slide_04_results_backlog_breakdown()
        self.slide_05_distributions_percentage_sgpi()
        self.slide_06_class_toppers_leaderboard()
        self.slide_07_subject_performance_matrix()
        self.slide_08_grade_distributions()
        self.slide_09_theory_vs_lab_disparity()
        self.slide_10_correlation_drivers()
        self.slide_11_gender_comparative_analytics()
        self.slide_12_ml_clustering_foundation()
        self.slide_13_kmeans_optimization_diagnostics()
        self.slide_14_pca_latent_space()
        self.slide_15_cluster_personas_profiles()
        self.slide_16_cluster_competency_radar()
        self.slide_17_executive_analytics_dashboard()
        self.slide_18_risk_matrix_early_warning()
        self.slide_19_pedagogical_interventions()
        self.slide_20_conclusion_roadmap()

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.prs.save(self.output_path)
        print(f"Presentation successfully saved to: {self.output_path}")

    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide (Dark Hero Theme)
    # -------------------------------------------------------------------------
    def slide_01_title(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, DARK_BG)

        # Ambient decorative card
        add_card(slide, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1), bg_color=DARK_CARD, border_color=DARK_BORDER)

        tb = slide.shapes.add_textbox(Inches(2.2), Inches(1.8), Inches(8.933), Inches(3.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p_badge = tf.paragraphs[0]
        p_badge.text = "DEPARTMENT OF ARTIFICIAL INTELLIGENCE & DATA SCIENCE  |  ACADEMIC AUDIT"
        p_badge.font.name = FONT_HEADING
        p_badge.font.size = Pt(10.5)
        p_badge.font.bold = True
        p_badge.font.color.rgb = CYAN_ACCENT
        p_badge.space_after = Pt(14)

        p_title = tf.add_paragraph()
        p_title.text = "Semester IV Academic Result Analysis &\nMachine Learning Student Segmentation"
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(30)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_LIGHT
        p_title.space_after = Pt(14)

        p_sub = tf.add_paragraph()
        p_sub.text = "An End-to-End Investigation of University Gazette Outcomes, Core Subject Bottlenecks,\nCompetency Correlation Drivers, and 4-Cluster K-Means Behavioral Personas"
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_LIGHT_MUTED
        p_sub.space_after = Pt(24)

        p_meta = tf.add_paragraph()
        p_meta.text = "• Cohort Size: 88 Students    • Curricular Features: 113 Features    • Verification: 100% Mathematical Parity"
        p_meta.font.name = FONT_BODY
        p_meta.font.size = Pt(10.5)
        p_meta.font.bold = True
        p_meta.font.color.rgb = BLUE_ACCENT

        add_footer(slide, 1, 20, dark=True)

    # -------------------------------------------------------------------------
    # SLIDE 2: Executive Summary & Cohort KPIs
    # -------------------------------------------------------------------------
    def slide_02_executive_summary(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Executive Summary", "Semester IV Academic Performance at a Glance",
                   "Holistic synthesis of cohort examination metrics, clearance rates, and distinction outcomes")

        card_w = Inches(2.78)
        card_h = Inches(1.5)
        top_pos = Inches(1.7)

        add_stat_card(slide, Inches(0.8), top_pos, card_w, card_h,
                      "88", "Registered Students", "Full university gazette cohort", BLUE_ACCENT)
        add_stat_card(slide, Inches(3.78), top_pos, card_w, card_h,
                      "68.18%", "Overall Pass Rate", "60 Clear | 27 ATKT | 1 Absent", GREEN_SUCCESS)
        add_stat_card(slide, Inches(6.76), top_pos, card_w, card_h,
                      "7.55", "Mean SGPI (Passing)", "Median 7.43 | Cohort std 0.74", PURPLE_ACCENT)
        add_stat_card(slide, Inches(9.74), top_pos, card_w, card_h,
                      "9.13", "Top Academic Score", "Shivam Bandekar (85.55% agg)", AMBER_WARN)

        # Left Container: Strategic Findings Card
        add_card(slide, Inches(0.8), Inches(3.45), Inches(5.75), Inches(3.35))
        tb_left = slide.shapes.add_textbox(Inches(1.05), Inches(3.65), Inches(5.25), Inches(2.95))
        tf_l = tb_left.text_frame
        tf_l.word_wrap = True

        p_lh = tf_l.paragraphs[0]
        p_lh.text = "Key Cohort Observations"
        p_lh.font.name = FONT_HEADING
        p_lh.font.size = Pt(14)
        p_lh.font.bold = True
        p_lh.font.color.rgb = PRIMARY_NAVY
        p_lh.space_after = Pt(10)

        points = [
            ("Healthy Passing Bell Curve: ", "Passing candidates form a robust distribution with 18 distinction performers achieving SGPI >= 8.00 (20.5% of total class)."),
            ("Asymmetric Assessment Risk: ", "Theoretical external examinations represent 100% of academic backlogs, whereas laboratory and internal term-work achieve >98% clearance."),
            ("High Foundational Competence: ", "Over 76% of students fall into High Achiever or Solid Performer segments, demonstrating strong overall technical aptitude."),
            ("Identified Remedial Cohort: ", "21 students (23.9%) experience chronic difficulty across multiple theory examinations, requiring structured mid-term intervention.")
        ]
        for bold_prefix, text in points:
            p = tf_l.add_paragraph()
            p.space_after = Pt(6)
            run_b = p.add_run()
            run_b.text = "• " + bold_prefix
            run_b.font.name = FONT_BODY
            run_b.font.size = Pt(10)
            run_b.font.bold = True
            run_b.font.color.rgb = BLUE_ACCENT
            run_t = p.add_run()
            run_t.text = text
            run_t.font.name = FONT_BODY
            run_t.font.size = Pt(10)
            run_t.font.color.rgb = TEXT_DARK

        # Right Container: Embedded Figure (Result breakdown)
        add_card(slide, Inches(6.76), Inches(3.45), Inches(5.75), Inches(3.35))
        fig_path = resolve_figure_path("reports/figures/eda/result_breakdown.png")
        if os.path.exists(fig_path):
            slide.shapes.add_picture(fig_path, Inches(6.9), Inches(3.55), width=Inches(5.47), height=Inches(3.15))

        add_footer(slide, 2, 20)

    # -------------------------------------------------------------------------
    # SLIDE 3: Academic Scheme & Dataset Schema
    # -------------------------------------------------------------------------
    def slide_03_academic_architecture(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Curriculum Architecture", "Examination Structure & Master Dataset Schema",
                   "Official University evaluation scheme across 11 credit courses, credits, and verification standards")

        col_w = Inches(3.78)
        col_h = Inches(4.9)
        top_pos = Inches(1.7)

        # Column 1: Core Theory (100 Marks Each)
        add_card(slide, Inches(0.8), top_pos, col_w, col_h)
        tb1 = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        p = tf1.paragraphs[0]
        p.text = "Core Theory Papers (100M)"
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = BLUE_ACCENT
        p.space_after = Pt(8)

        theory_courses = [
            ("CT", "Computational Theory", "3 Credits | 80 Ext + 20 Int"),
            ("DBMS", "Database Management Systems", "3 Credits | 80 Ext + 20 Int"),
            ("OS", "Operating Systems", "3 Credits | 80 Ext + 20 Int"),
            ("FTS", "Fundamentals of Telecom Systems", "3 Credits | 80 Ext + 20 Int"),
            ("OE", "Chhatrapati Shivaji Maharaj Policy", "2 Credits | 60 Ext + 15 Int")
        ]
        for code, name, detail in theory_courses:
            p_c = tf1.add_paragraph()
            p_c.text = f"{code}: {name}"
            p_c.font.name = FONT_BODY
            p_c.font.size = Pt(10)
            p_c.font.bold = True
            p_c.font.color.rgb = PRIMARY_NAVY
            p_d = tf1.add_paragraph()
            p_d.text = f"   {detail}"
            p_d.font.name = FONT_BODY
            p_d.font.size = Pt(8.5)
            p_d.font.color.rgb = TEXT_MUTED
            p_d.space_after = Pt(4)

        # Column 2: Practical & Labs (50 Marks Each)
        add_card(slide, Inches(4.78), top_pos, col_w, col_h)
        tb2 = slide.shapes.add_textbox(Inches(4.98), top_pos + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        p = tf2.paragraphs[0]
        p.text = "Laboratories & Term Work (50M)"
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = GREEN_SUCCESS
        p.space_after = Pt(8)

        lab_courses = [
            ("DBMS LAB", "Database Systems Lab", "1 Credit | 25 TW + 25 Oral/Prac"),
            ("OS LAB", "Operating Systems Lab", "1 Credit | 25 TW + 25 Oral/Prac"),
            ("TC LAB", "Telecommunication Lab", "1 Credit | 25 TW + 25 Oral/Prac"),
            ("MINIPROJ", "Mini Project 2A", "2 Credits | 25 TW + 25 Oral/Prac"),
            ("BMD", "Business Model Development", "1 Credit | 25 TW Continuous"),
            ("DT", "Design Thinking Workshop", "2 Credits | 50 TW Continuous")
        ]
        for code, name, detail in lab_courses:
            p_c = tf2.add_paragraph()
            p_c.text = f"{code}: {name}"
            p_c.font.name = FONT_BODY
            p_c.font.size = Pt(10)
            p_c.font.bold = True
            p_c.font.color.rgb = PRIMARY_NAVY
            p_d = tf2.add_paragraph()
            p_d.text = f"   {detail}"
            p_d.font.name = FONT_BODY
            p_d.font.size = Pt(8.5)
            p_d.font.color.rgb = TEXT_MUTED
            p_d.space_after = Pt(3)

        # Column 3: Dataset Hygiene & Quality Assurance
        add_card(slide, Inches(8.76), top_pos, col_w, col_h)
        tb3 = slide.shapes.add_textbox(Inches(8.96), top_pos + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
        tf3 = tb3.text_frame
        tf3.word_wrap = True
        p = tf3.paragraphs[0]
        p.text = "Gazette Quality Audit (100%)"
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = PURPLE_ACCENT
        p.space_after = Pt(8)

        qa_points = [
            ("Zero Duplication: ", "Verified 88 unique student records, 0 duplicate seat numbers or names."),
            ("Formula Parity: ", "Total credits (aC = 23) and weighted grade points (aCG) match university formula SGPI = aCG/aC with 0 residual discrepancy."),
            ("Component Completeness: ", "Every internal, external, term-work, oral, and grade code rigorously captured across 113 dataframe columns."),
            ("Status Classification: ", "Distinct separation of successful passers (P), unsuccessful backlog holders (F), and official absent cases (A).")
        ]
        for bold_t, body_t in qa_points:
            p_c = tf3.add_paragraph()
            p_c.space_after = Pt(6)
            rb = p_c.add_run()
            rb.text = "✓ " + bold_t
            rb.font.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = PURPLE_ACCENT
            rt = p_c.add_run()
            rt.text = body_t
            rt.font.size = Pt(9)
            rt.font.color.rgb = TEXT_DARK

        add_footer(slide, 3, 20)

    # -------------------------------------------------------------------------
    # SLIDE 4: Overall Result & Backlog Distribution
    # -------------------------------------------------------------------------
    def slide_04_results_backlog_breakdown(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Result Breakdown", "Clearance Status & Backlog (KT) Severity Distribution",
                   "Granular examination of successful students, single-subject backlogs, and multi-subject failure clusters")

        add_card(slide, Inches(0.8), Inches(1.7), Inches(6.0), Inches(5.0))
        fig_path = resolve_figure_path("reports/figures/eda/extracted/eda_cell_46.png")
        if not os.path.exists(fig_path):
            fig_path = resolve_figure_path("reports/figures/eda/result_breakdown.png")
        if os.path.exists(fig_path):
            slide.shapes.add_picture(fig_path, Inches(0.95), Inches(1.85), width=Inches(5.7), height=Inches(4.7))

        # Right Top Card: Breakdown Stats Table
        add_card(slide, Inches(7.0), Inches(1.7), Inches(5.533), Inches(2.2))
        tb_top = slide.shapes.add_textbox(Inches(7.2), Inches(1.85), Inches(5.133), Inches(1.9))
        tft = tb_top.text_frame
        tft.word_wrap = True
        pt = tft.paragraphs[0]
        pt.text = "Result Category Distribution"
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = PRIMARY_NAVY
        pt.space_after = Pt(6)

        cats = [
            ("Successful (Clear Pass)", "60 Students", "68.18%", GREEN_SUCCESS),
            ("Unsuccessful (ATKT / Backlog)", "27 Students", "30.68%", RED_ALERT),
            ("Absentee (Zero Attendance)", "1 Student", "1.14%", AMBER_WARN),
        ]
        for name, cnt, pct, col in cats:
            p_row = tft.add_paragraph()
            p_row.text = f"•  {name:30s}  :  {cnt:12s} ({pct})"
            p_row.font.name = FONT_BODY
            p_row.font.size = Pt(10)
            p_row.font.bold = True
            p_row.font.color.rgb = col
            p_row.space_after = Pt(3)

        # Right Bottom Card: Backlog Depth Breakdown
        add_card(slide, Inches(7.0), Inches(4.1), Inches(5.533), Inches(2.6))
        tb_bot = slide.shapes.add_textbox(Inches(7.2), Inches(4.25), Inches(5.133), Inches(2.3))
        tfb = tb_bot.text_frame
        tfb.word_wrap = True
        pb = tfb.paragraphs[0]
        pb.text = "Backlog Severity Distribution (28 Students)"
        pb.font.name = FONT_HEADING
        pb.font.size = Pt(13)
        pb.font.bold = True
        pb.font.color.rgb = PRIMARY_NAVY
        pb.space_after = Pt(6)

        kt_tiers = [
            ("Isolated Backlog (1 Subject)", "6 Students (6.8%)", "DBMS theory or OS theory; easily recoverable"),
            ("Moderate Backlog (2 Subjects)", "6 Students (6.8%)", "Dual theory failure (CT + OS or DBMS + OS)"),
            ("Severe Backlog (3 - 5 Subjects)", "8 Students (9.1%)", "Multiple core deficits; requires intensive remediation"),
            ("Critical / Terminal (6 - 11 Subjects)", "8 Students (9.1%)", "General academic collapse or official absenteeism")
        ]
        for title, count, note in kt_tiers:
            p_kt = tfb.add_paragraph()
            r1 = p_kt.add_run()
            r1.text = f"• {title}: "
            r1.font.bold = True
            r1.font.size = Pt(9.5)
            r1.font.color.rgb = BLUE_ACCENT
            r2 = p_kt.add_run()
            r2.text = f"{count} — {note}"
            r2.font.size = Pt(9)
            r2.font.color.rgb = TEXT_DARK
            p_kt.space_after = Pt(2)

        add_footer(slide, 4, 20)

    # -------------------------------------------------------------------------
    # SLIDE 5: Academic Score Distributions (Percentage & SGPI)
    # -------------------------------------------------------------------------
    def slide_05_distributions_percentage_sgpi(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Cohort Distributions", "Percentage & SGPI Statistical Spread",
                   "Kernel Density Estimations (KDE) demonstrating cohort dispersion, central tendencies, and distinction peaks")

        card_w = Inches(5.75)
        card_h = Inches(3.6)
        top_pos = Inches(1.7)

        # Left: Percentage Distribution
        add_card(slide, Inches(0.8), top_pos, card_w, card_h)
        fig_pct = resolve_figure_path("reports/figures/eda/extracted/eda_cell_35.png")
        if os.path.exists(fig_pct):
            slide.shapes.add_picture(fig_pct, Inches(0.9), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        # Right: SGPI Distribution
        add_card(slide, Inches(6.76), top_pos, card_w, card_h)
        fig_sgpi = resolve_figure_path("reports/figures/eda/sgpa_distribution.png")
        if not os.path.exists(fig_sgpi):
            fig_sgpi = resolve_figure_path("reports/figures/eda/extracted/eda_cell_37.png")
        if os.path.exists(fig_sgpi):
            slide.shapes.add_picture(fig_sgpi, Inches(6.86), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        # Bottom Analytics Summary Card
        add_card(slide, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.4))
        tb = slide.shapes.add_textbox(Inches(1.0), Inches(5.55), Inches(11.333), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p_h = tf.paragraphs[0]
        p_h.text = "Distribution Dynamics & Statistical Parameters"
        p_h.font.name = FONT_HEADING
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = PRIMARY_NAVY
        p_h.space_after = Pt(4)

        p1 = tf.add_paragraph()
        p1.text = "• Aggregate Percentage Spread: Mean = 62.44%, Median = 66.91%, Standard Deviation = 16.14%. Passing students alone average 70.43%."
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = TEXT_DARK
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = "• Bimodal SGPI Characteristic: A natural bimodality exists where successful students form a smooth bell curve centered at 7.55 (range 5.48 to 9.13), while unsuccessful candidates default to 0.00 SGPI."
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_after = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = "• Distinction Threshold (SGPI >= 8.00): 18 students (20.5%) achieved distinction status, demonstrating elite conceptual and applied proficiency."
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = BLUE_ACCENT
        p3.font.bold = True

        add_footer(slide, 5, 20)

    # -------------------------------------------------------------------------
    # SLIDE 6: Class Toppers Leaderboard (Top 10 Rankers)
    # -------------------------------------------------------------------------
    def slide_06_class_toppers_leaderboard(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Academic Excellence", "Class Toppers Leaderboard — Top 10 Rankers",
                   "High-achieving candidates with superior aggregate marks, consistent distinction grades, and SGPI >= 8.35")

        add_card(slide, Inches(0.8), Inches(1.7), Inches(8.3), Inches(5.1))

        rows = 11
        cols = 6
        table_shape = slide.shapes.add_table(rows, cols, Inches(0.95), Inches(1.85), Inches(8.0), Inches(4.75))
        table = table_shape.table

        table.columns[0].width = Inches(0.7)  # Rank
        table.columns[1].width = Inches(1.1)  # Seat No
        table.columns[2].width = Inches(2.9)  # Student Name
        table.columns[3].width = Inches(1.1)  # Total Marks
        table.columns[4].width = Inches(1.1)  # Percentage
        table.columns[5].width = Inches(1.1)  # SGPI

        headers = ["Rank", "Seat No", "Student Name", "Total", "Percentage", "SGPI"]
        for i, h in enumerate(headers):
            cell = table.cell(0, i)
            style_cell(cell, h, font_size=9.5, bold=True, text_color=TEXT_LIGHT, bg_color=PRIMARY_NAVY)

        toppers_data = [
            ("#1", "101410074", "SHIVAM VILAS BANDEKAR", "663 / 775", "85.55%", "9.13"),
            ("#2", "101410932", "SHRAVANI VISHWAS MANE", "649 / 775", "83.74%", "8.87"),
            ("#3", "101410070", "SAMIKSHA RAJENDRA BODAKE", "627 / 775", "80.90%", "8.74"),
            ("#4", "101410061", "PRASAD KISAN BHAJNAWALE", "610 / 775", "78.71%", "8.70"),
            ("#5", "101410052", "NAIK ARYAN UDAY", "619 / 775", "79.87%", "8.65"),
            ("#6", "101410939", "MANGILAL SHRAVAN MALVIYA", "614 / 775", "79.23%", "8.65"),
            ("#7", "101410084", "TEJAS JITENDRA SAWANT", "613 / 775", "79.10%", "8.57"),
            ("#8", "101410024", "ADINATH SOMNATH JAGTAP", "616 / 775", "79.48%", "8.52"),
            ("#9", "101410086", "UNNATI DINESH CHAVAN", "606 / 775", "78.19%", "8.39"),
            ("#10", "101410049", "MAHANGADE OM VIJAY", "607 / 775", "78.32%", "8.35"),
        ]

        for r_idx, row in enumerate(toppers_data, start=1):
            bg = RGBColor(239, 246, 255) if r_idx == 1 else (RGBColor(255, 255, 255) if r_idx % 2 == 0 else RGBColor(248, 250, 252))
            is_gold = (r_idx == 1)
            t_col = BLUE_ACCENT if is_gold else TEXT_DARK
            style_cell(table.cell(r_idx, 0), row[0], font_size=9, bold=is_gold, text_color=t_col, bg_color=bg)
            style_cell(table.cell(r_idx, 1), row[1], font_size=8.5, bold=False, text_color=TEXT_MUTED, bg_color=bg)
            style_cell(table.cell(r_idx, 2), row[2], font_size=9, bold=is_gold, text_color=t_col, bg_color=bg, align=PP_ALIGN.LEFT)
            style_cell(table.cell(r_idx, 3), row[3], font_size=8.5, bold=False, text_color=TEXT_DARK, bg_color=bg)
            style_cell(table.cell(r_idx, 4), row[4], font_size=9, bold=is_gold, text_color=t_col, bg_color=bg)
            style_cell(table.cell(r_idx, 5), row[5], font_size=9.5, bold=True, text_color=GREEN_SUCCESS if is_gold else BLUE_ACCENT, bg_color=bg)

        # Right Card: Highlights & Case Study
        add_card(slide, Inches(9.3), Inches(1.7), Inches(3.233), Inches(5.1))
        tb_r = slide.shapes.add_textbox(Inches(9.45), Inches(1.85), Inches(2.933), Inches(4.75))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True

        pr_h = tf_r.paragraphs[0]
        pr_h.text = "Topper Case Study"
        pr_h.font.name = FONT_HEADING
        pr_h.font.size = Pt(13)
        pr_h.font.bold = True
        pr_h.font.color.rgb = PRIMARY_NAVY
        pr_h.space_after = Pt(8)

        insights = [
            ("Shivam Vilas Bandekar (Rank 1): ", "Secured an exceptional SGPI of 9.13 with 85.55% aggregate, outperforming 2nd rank by +1.81% and +0.26 SGPI."),
            ("Theory Excellence: ", "Highest theory average in cohort (85.0%), demonstrating complete mastery across system architecture and mathematical foundations."),
            ("Gender Parity in Top 3: ", "Female scholars hold 2 of the top 3 spots (Shravani Mane #2 at 8.87, Samiksha Bodake #3 at 8.74)."),
            ("Cluster Alignment: ", "All Top 10 rankers mapped directly into K-Means Cluster 0 (High Achievers / Academic Leaders) with 0.0 standard deviation in subject pass status.")
        ]
        for b_t, m_t in insights:
            p = tf_r.add_paragraph()
            p.space_after = Pt(6)
            rb = p.add_run()
            rb.text = "★ " + b_t
            rb.font.bold = True
            rb.font.size = Pt(9)
            rb.font.color.rgb = BLUE_ACCENT
            rt = p.add_run()
            rt.text = m_t
            rt.font.size = Pt(8.5)
            rt.font.color.rgb = TEXT_DARK

        add_footer(slide, 6, 20)

    # -------------------------------------------------------------------------
    # SLIDE 7: Subject Performance & Difficulty Analysis
    # -------------------------------------------------------------------------
    def slide_07_subject_performance_matrix(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Curriculum Deep-Dive", "Subject Performance & Difficulty Index Matrix",
                   "Course-by-course mean marks, pass percentages, and quantitative identification of curriculum bottlenecks")

        add_card(slide, Inches(0.8), Inches(1.7), Inches(5.9), Inches(5.0))
        fig_subj = resolve_figure_path("reports/figures/eda/subject_performance_comparison.png")
        if not os.path.exists(fig_subj):
            fig_subj = resolve_figure_path("reports/figures/eda/extracted/eda_cell_55.png")
        if os.path.exists(fig_subj):
            slide.shapes.add_picture(fig_subj, Inches(0.9), Inches(1.85), width=Inches(5.7), height=Inches(4.7))

        # Right Side: Structured Difficulty Ranking Table
        add_card(slide, Inches(6.9), Inches(1.7), Inches(5.633), Inches(5.0))
        tb_r = slide.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.233), Inches(4.7))
        tfr = tb_r.text_frame
        tfr.word_wrap = True

        ph = tfr.paragraphs[0]
        ph.text = "Subject Difficulty & Risk Hierarchy"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(13)
        ph.font.bold = True
        ph.font.color.rgb = PRIMARY_NAVY
        ph.space_after = Pt(8)

        subj_analyses = [
            ("Operating Systems (OS) — Hardest Theory",
             "Mean Total: 51.08 / 100 | Lowest theory score in cohort. External papers presented highest analytical friction with 12 KT failures.",
             RED_ALERT),
            ("Database Management (DBMS) — High Failure Bottleneck",
             "Mean Total: 58.23 / 100 | Despite a solid class average, DBMS generated 15 'F' grades in external theory—the highest single-course failure toll.",
             RED_ALERT),
            ("Fundamentals of Telecom (FTS) — Moderate Friction",
             "Mean Total: 54.13 / 100 | Theoretical concepts in communication systems created moderate hurdles for non-hardware aligned candidates.",
             AMBER_WARN),
            ("Computational Theory (CT) — Highest Theory Score",
             "Mean Total: 58.86 / 100 | Outperformed all core theoretical courses, exhibiting high student engagement and top grade frequencies.",
             BLUE_ACCENT),
            ("Practical Labs & Coursework — Near 100% Clearance",
             "DBMS Lab (33.76/50), OS Lab (33.56/50), MiniProj (50.89/75) demonstrated high term-work compliance and oral exam clearance (>98%).",
             GREEN_SUCCESS)
        ]
        for title, desc, col in subj_analyses:
            p = tfr.add_paragraph()
            p.space_after = Pt(6)
            rb = p.add_run()
            rb.text = f"• {title}\n"
            rb.font.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = col
            rd = p.add_run()
            rd.text = f"   {desc}"
            rd.font.size = Pt(8.5)
            rd.font.color.rgb = TEXT_DARK

        add_footer(slide, 7, 20)

    # -------------------------------------------------------------------------
    # SLIDE 8: Grade Distribution Across Subjects
    # -------------------------------------------------------------------------
    def slide_08_grade_distributions(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Grade Distribution Analysis", "Cohort Grade Frequencies Across All 11 Subjects",
                   "Distribution of letter grades (O, A+, A, B+, B, C, D, F) contrasting practical and theoretical courses")

        card_w = Inches(5.75)
        card_h = Inches(3.6)
        top_pos = Inches(1.7)

        add_card(slide, Inches(0.8), top_pos, card_w, card_h)
        fig_g1 = resolve_figure_path("reports/figures/eda/extracted/eda_cell_75.png")
        if os.path.exists(fig_g1):
            slide.shapes.add_picture(fig_g1, Inches(0.9), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        add_card(slide, Inches(6.76), top_pos, card_w, card_h)
        fig_g2 = resolve_figure_path("reports/figures/eda/extracted/eda_cell_72.png")
        if os.path.exists(fig_g2):
            slide.shapes.add_picture(fig_g2, Inches(6.86), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        add_card(slide, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.4))
        tb = slide.shapes.add_textbox(Inches(1.0), Inches(5.55), Inches(11.333), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p_h = tf.paragraphs[0]
        p_h.text = "Key Grade Allocation Insights"
        p_h.font.name = FONT_HEADING
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = PRIMARY_NAVY
        p_h.space_after = Pt(4)

        g_notes = [
            ("Laboratory Polarization: ", "Practical labs exhibit an overwhelming concentration of 'O', 'A+', and 'A' grades (>85%), highlighting reliable practical execution across the cohort."),
            ("Theory Spread in Core Tech: ", "DBMS recorded 2 Outstanding (O), 8 A+, 16 A, 20 B+, 11 B, 4 C, 12 D, and 15 F grades—displaying the widest variance in academic outcomes."),
            ("The 'D' Grade Accumulation Risk: ", "Over 22% of passing students secured 'D' grades (pass threshold) in OS and CT external exams, representing borderline performers vulnerable in Sem V.")
        ]
        for b_t, n_t in g_notes:
            p = tf.add_paragraph()
            p.space_after = Pt(2)
            rb = p.add_run()
            rb.text = "• " + b_t
            rb.font.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = BLUE_ACCENT
            rn = p.add_run()
            rn.text = n_t
            rn.font.size = Pt(9)
            rn.font.color.rgb = TEXT_DARK

        add_footer(slide, 8, 20)

    # -------------------------------------------------------------------------
    # SLIDE 9: Theory vs Practical Assessment Disparity
    # -------------------------------------------------------------------------
    def slide_09_theory_vs_lab_disparity(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Assessment Disparity", "Theory vs. Practical Competency Discrepancy",
                   "Empirical evidence of a 13.26 percentage point gap between high laboratory scores and written theory struggles")

        add_card(slide, Inches(0.8), Inches(1.7), Inches(5.9), Inches(5.0))
        fig_tvl = resolve_figure_path("reports/figures/eda/extracted/eda_cell_94.png")
        if not os.path.exists(fig_tvl):
            fig_tvl = resolve_figure_path("reports/figures/clustering_v1/kmeans_04_theory_vs_lab_scatter.png")
        if os.path.exists(fig_tvl):
            slide.shapes.add_picture(fig_tvl, Inches(0.9), Inches(1.85), width=Inches(5.7), height=Inches(4.7))

        add_card(slide, Inches(6.9), Inches(1.7), Inches(5.633), Inches(5.0))
        tb = slide.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.233), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = "The 13.26 pp Competency Gap"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(13)
        ph.font.bold = True
        ph.font.color.rgb = PRIMARY_NAVY
        ph.space_after = Pt(8)

        gap_points = [
            ("Mean Theory Percentage: 55.57%",
             "Aggregate theory average across 5 major papers. Standard deviation is elevated (18.2%), driven by written external examination rigor.",
             BLUE_ACCENT),
            ("Mean Practical Percentage: 68.83%",
             "Average laboratory score across DBMS Lab, OS Lab, and TC Lab (34.41 / 50). Students demonstrate steady lab compliance and oral proficiency.",
             GREEN_SUCCESS),
            ("Root Cause of ATKT Backlogs",
             "100% of failed course components occurred in external theory papers. Zero students failed laboratory coursework or term-work submissions.",
             RED_ALERT),
            ("The 'Practical-Strong / Theory-Deficit' Syndrome",
             "A distinct segment of 18 students achieves >70% in practical implementations but drops below 40% in theoretical pen-and-paper examinations.",
             PURPLE_ACCENT),
            ("Institutional Remedy",
             "Transition semester assessments toward continuous applied testing rather than high-stakes memorization-heavy end-semester papers.",
             AMBER_WARN)
        ]
        for title, desc, col in gap_points:
            p = tf.add_paragraph()
            p.space_after = Pt(6)
            rb = p.add_run()
            rb.text = f"• {title}\n"
            rb.font.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = col
            rd = p.add_run()
            rd.text = f"   {desc}"
            rd.font.size = Pt(8.5)
            rd.font.color.rgb = TEXT_DARK

        add_footer(slide, 9, 20)

    # -------------------------------------------------------------------------
    # SLIDE 10: Academic Correlation & Key SGPI Drivers
    # -------------------------------------------------------------------------
    def slide_10_correlation_drivers(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Correlation Analysis", "Inter-Subject Correlations & Primary SGPI Determinants",
                   "Pearson correlation matrix quantifying which foundational subjects most heavily dictate overall academic success")

        add_card(slide, Inches(0.8), Inches(1.7), Inches(5.9), Inches(5.0))
        fig_corr = resolve_figure_path("reports/figures/eda/extracted/eda_cell_63.png")
        if not os.path.exists(fig_corr):
            fig_corr = resolve_figure_path("reports/figures/clustering_v1/kmeans_08_correlation_heatmap.png")
        if os.path.exists(fig_corr):
            slide.shapes.add_picture(fig_corr, Inches(0.9), Inches(1.85), width=Inches(5.7), height=Inches(4.7))

        add_card(slide, Inches(6.9), Inches(1.7), Inches(5.633), Inches(5.0))
        tb = slide.shapes.add_textbox(Inches(7.1), Inches(1.85), Inches(5.233), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = "Correlation Strengths with Total Marks"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(13)
        ph.font.bold = True
        ph.font.color.rgb = PRIMARY_NAVY
        ph.space_after = Pt(8)

        corrs = [
            ("Computational Theory (CT Total)", "r = 0.904", "Highest single predictor of cohort score", BLUE_ACCENT),
            ("Database Management (DBMS Total)", "r = 0.896", "Critical benchmark for software core competence", BLUE_ACCENT),
            ("Operating Systems (OS Total)", "r = 0.892", "Decisive driver of overall academic standing", BLUE_ACCENT),
            ("OS Laboratory (OS LAB Total)", "r = 0.878", "Highest correlating practical laboratory", GREEN_SUCCESS),
            ("Fundamentals of Telecom (FTS)", "r = 0.871", "Strong theoretical foundation correlation", PURPLE_ACCENT),
            ("Design Thinking Workshop (DT)", "r = 0.854", "Consistent predictor of creative engagement", AMBER_WARN),
        ]
        for name, r_val, note, col in corrs:
            p = tf.add_paragraph()
            p.space_after = Pt(4)
            r1 = p.add_run()
            r1.text = f"• {name}: "
            r1.font.bold = True
            r1.font.size = Pt(9)
            r1.font.color.rgb = PRIMARY_NAVY
            r2 = p.add_run()
            r2.text = f"{r_val} "
            r2.font.bold = True
            r2.font.size = Pt(9)
            r2.font.color.rgb = col
            r3 = p.add_run()
            r3.text = f"({note})"
            r3.font.size = Pt(8.5)
            r3.font.color.rgb = TEXT_MUTED

        p_takeaway = tf.add_paragraph()
        p_takeaway.space_before = Pt(8)
        p_takeaway.text = "Strategic Insight: CT, DBMS, and OS exhibit extremely high mutual co-linearity (r > 0.82). Mastery in one core theoretical system directly cascades into success across the other two."
        p_takeaway.font.name = FONT_BODY
        p_takeaway.font.size = Pt(9)
        p_takeaway.font.bold = True
        p_takeaway.font.color.rgb = BLUE_ACCENT

        add_footer(slide, 10, 20)

    # -------------------------------------------------------------------------
    # SLIDE 11: Gender Demographics & Comparative Performance
    # -------------------------------------------------------------------------
    def slide_11_gender_comparative_analytics(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Demographic Analytics", "Gender Composition & Comparative Academic Outcomes",
                   "Evaluation of gender representation, clearance percentages, and score distributions")

        card_w = Inches(5.75)
        card_h = Inches(3.6)
        top_pos = Inches(1.7)

        add_card(slide, Inches(0.8), top_pos, card_w, card_h)
        fig_gen1 = resolve_figure_path("reports/figures/eda/extracted/eda_cell_22.png")
        if os.path.exists(fig_gen1):
            slide.shapes.add_picture(fig_gen1, Inches(0.9), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        add_card(slide, Inches(6.76), top_pos, card_w, card_h)
        fig_gen2 = resolve_figure_path("reports/figures/eda/extracted/eda_cell_98.png")
        if os.path.exists(fig_gen2):
            slide.shapes.add_picture(fig_gen2, Inches(6.86), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        add_card(slide, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.4))
        tb = slide.shapes.add_textbox(Inches(1.0), Inches(5.55), Inches(11.333), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = "Gender Performance Comparison & Statistical Significance"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = PRIMARY_NAVY
        ph.space_after = Pt(4)

        dem_points = [
            ("Demographic Composition: ", "60 Male students (68.18%) and 28 Female students (31.82%) appeared for the Semester IV examination."),
            ("Academic Performance Edge: ", "Female candidates achieved a higher mean percentage (67.13% vs 60.25% for males) and higher median score (68.58% vs 65.87%)."),
            ("Pass Rate & Backlog Resistance: ", "Female pass rate was 71.43% (20/28) versus 66.67% (40/60) for males, reflecting superior overall consistency across core theory courses."),
            ("Distinction Representation: ", "Shravani Vishwas Mane secured Rank 2 overall (83.74%, 8.87 SGPI) and Samiksha Bodake secured Rank 3 (80.90%, 8.74 SGPI).")
        ]
        for b_t, t_t in dem_points:
            p = tf.add_paragraph()
            p.space_after = Pt(2)
            rb = p.add_run()
            rb.text = "• " + b_t
            rb.font.bold = True
            rb.font.size = Pt(9)
            rb.font.color.rgb = BLUE_ACCENT
            rt = p.add_run()
            rt.text = t_t
            rt.font.size = Pt(8.5)
            rt.font.color.rgb = TEXT_DARK

        add_footer(slide, 11, 20)

    # -------------------------------------------------------------------------
    # SLIDE 12: Machine Learning Transition
    # -------------------------------------------------------------------------
    def slide_12_ml_clustering_foundation(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, DARK_BG)

        add_card(slide, Inches(1.0), Inches(0.8), Inches(11.333), Inches(5.9), bg_color=DARK_CARD, border_color=DARK_BORDER)

        tb = slide.shapes.add_textbox(Inches(1.4), Inches(1.1), Inches(10.533), Inches(5.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p_badge = tf.paragraphs[0]
        p_badge.text = "UNSUPERVISED MACHINE LEARNING FRAMEWORK"
        p_badge.font.name = FONT_HEADING
        p_badge.font.size = Pt(11)
        p_badge.font.bold = True
        p_badge.font.color.rgb = CYAN_ACCENT
        p_badge.space_after = Pt(10)

        p_title = tf.add_paragraph()
        p_title.text = "From Traditional Grades to Competency-Based Clustering"
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_LIGHT
        p_title.space_after = Pt(14)

        p_desc = tf.add_paragraph()
        p_desc.text = "Conventional academic evaluation collapses multidimensional student learning into a single scalar GPA, obscuring distinct cognitive archetypes, practical competencies, and latent failure modes. Our K-Means clustering pipeline applies unsupervised learning to segment students based on multi-axis behavioral vectors."
        p_desc.font.name = FONT_BODY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = TEXT_LIGHT_MUTED
        p_desc.space_after = Pt(20)

        pillars = [
            ("1. Multi-Axis Feature Engineering",
             "Engineered 17 normalized features spanning Core Theory mastery, Laboratory/Hands-on agility, Coursework/Projects, External-Internal gap, and Cross-subject score standard deviation (Consistency)."),
            ("2. Rigorous Scaling & Optimization",
             "StandardScaler standardization applied with median imputation audit. Multi-metric K evaluation testing K=2 through K=7 using Inertia Elbow, Silhouette coefficients, and Davies-Bouldin separation."),
            ("3. Evidence-Based Persona Mapping",
             "Cluster centroids mapped dynamically to actionable pedagogical personas, enabling tailored semester-long academic interventions rather than generic post-facto failure warnings.")
        ]
        for p_t, p_d in pillars:
            p_pil = tf.add_paragraph()
            p_pil.space_after = Pt(10)
            rb = p_pil.add_run()
            rb.text = f"{p_t}\n"
            rb.font.bold = True
            rb.font.size = Pt(11)
            rb.font.color.rgb = BLUE_ACCENT
            rd = p_pil.add_run()
            rd.text = f"{p_d}"
            rd.font.size = Pt(9.5)
            rd.font.color.rgb = TEXT_LIGHT

        add_footer(slide, 12, 20, dark=True)

    # -------------------------------------------------------------------------
    # SLIDE 13: K-Means Diagnostics: Elbow & Silhouette Optimization
    # -------------------------------------------------------------------------
    def slide_13_kmeans_optimization_diagnostics(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Clustering Diagnostics", "Optimal Cluster Selection: Elbow Method & Silhouette Scores",
                   "Mathematical evaluation of cluster partitions across K=2 through K=7 to identify peak geometric cohesion")

        card_w = Inches(5.75)
        card_h = Inches(3.6)
        top_pos = Inches(1.7)

        add_card(slide, Inches(0.8), top_pos, card_w, card_h)
        fig_elb = resolve_figure_path("reports/figures/clustering_v2/clustering_v2_elbow.png")
        if not os.path.exists(fig_elb):
            fig_elb = resolve_figure_path("reports/figures/clustering_v1/kmeans_01_elbow_method.png")
        if os.path.exists(fig_elb):
            slide.shapes.add_picture(fig_elb, Inches(0.9), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        add_card(slide, Inches(6.76), top_pos, card_w, card_h)
        fig_sil = resolve_figure_path("reports/figures/clustering_v2/clustering_v2_silhouette.png")
        if not os.path.exists(fig_sil):
            fig_sil = resolve_figure_path("reports/figures/clustering_v1/kmeans_02_silhouette_analysis.png")
        if os.path.exists(fig_sil):
            slide.shapes.add_picture(fig_sil, Inches(6.86), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        add_card(slide, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.4))
        tb = slide.shapes.add_textbox(Inches(1.0), Inches(5.55), Inches(11.333), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = "Mathematical Proof of K = 4 Optimality"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = PRIMARY_NAVY
        ph.space_after = Pt(4)

        eval_notes = [
            ("Inertia Curve Inflection (Elbow): ", "A sharp rate-of-change reduction in within-cluster sum-of-squares (WCSS) appears between K=3 and K=4, signaling diminishing returns beyond K=4."),
            ("Silhouette Peak (0.2471): ", "K=4 maximizes the average silhouette width without generating negative silhouette slippage or degenerate single-student clusters."),
            ("Pedagogical Interpretability: ", "K=4 cleanly partitions the student body into 4 actionable institutional cohorts: High Achievers (33), Solid Performers (34), Developing (13), and Critical Support (8).")
        ]
        for b_t, n_t in eval_notes:
            p = tf.add_paragraph()
            p.space_after = Pt(2)
            rb = p.add_run()
            rb.text = "✓ " + b_t
            rb.font.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = GREEN_SUCCESS
            rn = p.add_run()
            rn.text = n_t
            rn.font.size = Pt(9)
            rn.font.color.rgb = TEXT_DARK

        add_footer(slide, 13, 20)

    # -------------------------------------------------------------------------
    # SLIDE 14: 2D PCA Dimensionality Reduction & Cluster Separation
    # -------------------------------------------------------------------------
    def slide_14_pca_latent_space(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Dimensionality Reduction", "2D Principal Component Analysis (PCA) Projection",
                   "Projecting 17 high-dimensional competency features into 2 principal axes to inspect cluster boundary separation")

        add_card(slide, Inches(0.8), Inches(1.7), Inches(6.0), Inches(5.0))
        fig_pca = resolve_figure_path("reports/figures/clustering_v2/clustering_v2_pca.png")
        if not os.path.exists(fig_pca):
            fig_pca = resolve_figure_path("reports/figures/clustering_v1/kmeans_03_pca_2d_projection.png")
        if os.path.exists(fig_pca):
            slide.shapes.add_picture(fig_pca, Inches(0.95), Inches(1.85), width=Inches(5.7), height=Inches(4.7))

        add_card(slide, Inches(7.0), Inches(1.7), Inches(5.533), Inches(5.0))
        tb = slide.shapes.add_textbox(Inches(7.2), Inches(1.85), Inches(5.133), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = "Principal Component Variance & Axes"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(13)
        ph.font.bold = True
        ph.font.color.rgb = PRIMARY_NAVY
        ph.space_after = Pt(8)

        pca_points = [
            ("PC1: Overall Academic Aptitude (~52% Variance)",
             "Dominant eigenvector heavily weighted on core theoretical examinations (CT, DBMS, OS), aggregate percentage, and overall credit accumulation. Moves left-to-right as performance improves.",
             BLUE_ACCENT),
            ("PC2: Practical vs Theory Bias (~14% Variance)",
             "Secondary eigenvector contrasts laboratory/hands-on agility against written external examinations. Effectively isolates students with high lab marks but depressed theory scores.",
             PURPLE_ACCENT),
            ("Linear Cluster Separation",
             "Clusters 0 (High Achievers) and 1 (Solid Performers) occupy the upper-right quadrant, clearly demarcated from Cluster 2 (Developing) in the lower quadrant.",
             GREEN_SUCCESS),
            ("Outlier & Critical Isolation",
             "Cluster 3 (Critical Intervention / Absent) is heavily segregated in the extreme negative PC1 space, confirming profound academic detachment.",
             RED_ALERT)
        ]
        for title, desc, col in pca_points:
            p = tf.add_paragraph()
            p.space_after = Pt(6)
            rb = p.add_run()
            rb.text = f"• {title}\n"
            rb.font.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = col
            rd = p.add_run()
            rd.text = f"   {desc}"
            rd.font.size = Pt(8.5)
            rd.font.color.rgb = TEXT_DARK

        add_footer(slide, 14, 20)

    # -------------------------------------------------------------------------
    # SLIDE 15: Student Persona Profiles: The 4 Clusters
    # -------------------------------------------------------------------------
    def slide_15_cluster_personas_profiles(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Student Segmentation", "The 4 Academic Personas: Cohort Profiles & Archetypes",
                   "Data-driven behavioral personas derived from K-Means clustering across all 88 candidates")

        col_w = Inches(2.78)
        col_h = Inches(5.0)
        top_pos = Inches(1.7)

        personas = [
            ("CLUSTER 0", "High Achievers", "33 Students (37.5%)", "Mean: 75.86%", "SGPI: 8.2 – 9.1",
             "Theory: 73.2% | Lab: 80.5%", "Pass Rate: 93.9% (31/33)",
             "Top performers with balanced theoretical mastery, distinction grades, and zero backlog risk. Future leadership and capstone candidates.",
             BLUE_ACCENT),
            ("CLUSTER 1", "Solid Performers", "34 Students (38.6%)", "Mean: 64.08%", "SGPI: ~7.00",
             "Theory: 58.4% | Lab: 73.6%", "Pass Rate: 85.3% (29/34)",
             "Dependable core cohort. Consistent coursework completion; moderate friction in OS/DBMS written exams. Target group for distinction push.",
             GREEN_SUCCESS),
            ("CLUSTER 2", "Developing Cohort", "13 Students (14.8%)", "Mean: 47.01%", "SGPI: 0.00 (KT)",
             "Theory: 39.5% | Lab: 64.3%", "Pass Rate: 0.0% (13 KT)",
             "Marked disparity: maintain passing laboratory scores (64.3%) but collapse in written theory (39.5%). Need urgent theory remediation.",
             AMBER_WARN),
            ("CLUSTER 3", "Critical Support", "8 Students (9.1%)", "Mean: 25.19%", "SGPI: 0.00 (KT)",
             "Theory: 31.7% | Lab: 7.9%", "Pass Rate: 0.0% (8 KT)",
             "Severe multi-subject failure (avg 7-11 KTs) and chronic absenteeism. Requires immediate administrative counseling and prerequisite review.",
             RED_ALERT)
        ]

        for idx, (cid, name, count, pct, sgpi, th_lab, pr, desc, col) in enumerate(personas):
            left_pos = Inches(0.8 + idx * 2.98)
            add_card(slide, left_pos, top_pos, col_w, col_h)
            tb = slide.shapes.add_textbox(left_pos + Inches(0.15), top_pos + Inches(0.15), col_w - Inches(0.3), col_h - Inches(0.3))
            tf = tb.text_frame
            tf.word_wrap = True

            p0 = tf.paragraphs[0]
            p0.text = cid
            p0.font.name = FONT_HEADING
            p0.font.size = Pt(9.5)
            p0.font.bold = True
            p0.font.color.rgb = col
            p0.space_after = Pt(2)

            p1 = tf.add_paragraph()
            p1.text = name
            p1.font.name = FONT_HEADING
            p1.font.size = Pt(12)
            p1.font.bold = True
            p1.font.color.rgb = PRIMARY_NAVY
            p1.space_after = Pt(4)

            p2 = tf.add_paragraph()
            p2.text = f"{count}\n{pct}  |  {sgpi}"
            p2.font.name = FONT_BODY
            p2.font.size = Pt(9)
            p2.font.bold = True
            p2.font.color.rgb = col
            p2.space_after = Pt(4)

            p3 = tf.add_paragraph()
            p3.text = f"• {th_lab}\n• {pr}"
            p3.font.name = FONT_BODY
            p3.font.size = Pt(8)
            p3.font.color.rgb = TEXT_MUTED
            p3.space_after = Pt(8)

            p4 = tf.add_paragraph()
            p4.text = desc
            p4.font.name = FONT_BODY
            p4.font.size = Pt(8.5)
            p4.font.color.rgb = TEXT_DARK

        add_footer(slide, 15, 20)

    # -------------------------------------------------------------------------
    # SLIDE 16: Cluster Competency Radar & Feature Profiles
    # -------------------------------------------------------------------------
    def slide_16_cluster_competency_radar(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Competency Profiling", "Multidimensional Cluster Competency Radar & Feature Vectors",
                   "Multi-axis radar evaluation comparing Theory, Practical, Coursework, Consistency, and Ext-Int Delta")

        card_w = Inches(5.75)
        card_h = Inches(3.6)
        top_pos = Inches(1.7)

        add_card(slide, Inches(0.8), top_pos, card_w, card_h)
        fig_rad = resolve_figure_path("reports/figures/clustering_v2/clustering_v2_radar.png")
        if os.path.exists(fig_rad):
            slide.shapes.add_picture(fig_rad, Inches(0.9), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        add_card(slide, Inches(6.76), top_pos, card_w, card_h)
        fig_prof = resolve_figure_path("reports/figures/clustering_v1/kmeans_05_cluster_feature_profiles.png")
        if os.path.exists(fig_prof):
            slide.shapes.add_picture(fig_prof, Inches(6.86), top_pos + Inches(0.1), width=Inches(5.55), height=Inches(3.4))

        add_card(slide, Inches(0.8), Inches(5.45), Inches(11.733), Inches(1.4))
        tb = slide.shapes.add_textbox(Inches(1.0), Inches(5.55), Inches(11.333), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = "Competency Signatures Across Clusters"
        ph.font.name = FONT_HEADING
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = PRIMARY_NAVY
        ph.space_after = Pt(4)

        rad_points = [
            ("Cluster 0 Shape (Concentric Mastery): ", "Occupies the outer perimeter across all 5 competency spokes, showing balanced excellence across both hands-on and theoretical axes."),
            ("Cluster 1 & 2 Asymmetry (The Theory Pinch): ", "Cluster 2 displays a pronounced inward indentation on Theory (39.5%) while maintaining healthy extension on Laboratory competence (64.3%)."),
            ("Consistency Discrepancy: ", "Cluster 0 shows tight subject standard deviation (9.0), while Cluster 2 exhibits broad score volatility (18.7), reflecting erratic subject-to-subject engagement.")
        ]
        for b_t, n_t in rad_points:
            p = tf.add_paragraph()
            p.space_after = Pt(2)
            rb = p.add_run()
            rb.text = "• " + b_t
            rb.font.bold = True
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = BLUE_ACCENT
            rn = p.add_run()
            rn.text = n_t
            rn.font.size = Pt(9)
            rn.font.color.rgb = TEXT_DARK

        add_footer(slide, 16, 20)

    # -------------------------------------------------------------------------
    # SLIDE 17: Comprehensive K-Means Executive Dashboard
    # -------------------------------------------------------------------------
    def slide_17_executive_analytics_dashboard(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Executive Dashboard", "Consolidated 6-Panel K-Means Student Personas Dashboard",
                   "High-resolution integrated analytical overview synthesizing cluster counts, SGPI spreads, theory-lab scatters, and PCA")

        add_card(slide, Inches(0.8), Inches(1.7), Inches(11.733), Inches(5.1))
        fig_dash = resolve_figure_path("reports/figures/clustering_v1/kmeans_student_personas_dashboard.png")
        if os.path.exists(fig_dash):
            slide.shapes.add_picture(fig_dash, Inches(0.95), Inches(1.85), width=Inches(11.433), height=Inches(4.75))

        add_footer(slide, 17, 20)

    # -------------------------------------------------------------------------
    # SLIDE 18: Academic Risk Matrix & Early Warning Indicators
    # -------------------------------------------------------------------------
    def slide_18_risk_matrix_early_warning(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Predictive Risk Modeling", "Academic Risk Matrix & Early Warning Indicators",
                   "Formulating quantitative triggers to detect at-risk students before final semester examination backlogs occur")

        col_w = Inches(3.78)
        col_h = Inches(4.9)
        top_pos = Inches(1.7)

        # Tier 1: Critical Emergency (Cluster 3)
        add_card(slide, Inches(0.8), top_pos, col_w, col_h)
        tb1 = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        p1 = tf1.paragraphs[0]
        p1.text = "CRITICAL RISK (Tier 1)"
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = RED_ALERT
        p1.space_after = Pt(8)

        t1_text = [
            ("Cohort Size: ", "8 Students (9.1% of class)"),
            ("Trigger Condition 1: ", "Attendance < 60% or zero internal test appearance."),
            ("Trigger Condition 2: ", "Cumulative backlogs >= 4 courses."),
            ("Score Envelope: ", "Aggregate percentage < 35%."),
            ("Primary Threat: ", "Year drop (YD) status or total academic discontinuation."),
            ("Mandatory Protocol: ", "Parental notification, direct academic counseling, mandatory prerequisite catch-up tutorials.")
        ]
        for b_t, n_t in t1_text:
            p = tf1.add_paragraph()
            p.space_after = Pt(4)
            rb = p.add_run()
            rb.text = "• " + b_t
            rb.font.bold = True
            rb.font.size = Pt(9)
            rb.font.color.rgb = RED_ALERT
            rt = p.add_run()
            rt.text = n_t
            rt.font.size = Pt(8.5)
            rt.font.color.rgb = TEXT_DARK

        # Tier 2: Developing / Theory Deficit (Cluster 2)
        add_card(slide, Inches(4.78), top_pos, col_w, col_h)
        tb2 = slide.shapes.add_textbox(Inches(4.98), top_pos + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = "MODERATE RISK (Tier 2)"
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = AMBER_WARN
        p2.space_after = Pt(8)

        t2_text = [
            ("Cohort Size: ", "13 Students (14.8% of class)"),
            ("Trigger Condition 1: ", "Internal Assessment theory marks < 50% (<10/20)."),
            ("Trigger Condition 2: ", "Ext-Int mark differential > 15 percentage points."),
            ("Score Envelope: ", "Aggregate 40% to 55%; 1-3 theory backlogs."),
            ("Primary Threat: ", "Failure in OS and DBMS written end-semester papers."),
            ("Mandatory Protocol: ", "Bi-weekly problem-solving clinics, past question paper drill sessions, peer study group assignment.")
        ]
        for b_t, n_t in t2_text:
            p = tf2.add_paragraph()
            p.space_after = Pt(4)
            rb = p.add_run()
            rb.text = "• " + b_t
            rb.font.bold = True
            rb.font.size = Pt(9)
            rb.font.color.rgb = AMBER_WARN
            rt = p.add_run()
            rt.text = n_t
            rt.font.size = Pt(8.5)
            rt.font.color.rgb = TEXT_DARK

        # Tier 3: Borderline Performers (Cluster 1 Low End)
        add_card(slide, Inches(8.76), top_pos, col_w, col_h)
        tb3 = slide.shapes.add_textbox(Inches(8.96), top_pos + Inches(0.2), col_w - Inches(0.4), col_h - Inches(0.4))
        tf3 = tb3.text_frame
        tf3.word_wrap = True
        p3 = tf3.paragraphs[0]
        p3.text = "MONITORING TIER (Tier 3)"
        p3.font.name = FONT_HEADING
        p3.font.size = Pt(13)
        p3.font.bold = True
        p3.font.color.rgb = BLUE_ACCENT
        p3.space_after = Pt(8)

        t3_text = [
            ("Cohort Size: ", "12 Students (borderline Cluster 1)"),
            ("Trigger Condition 1: ", "Passed theory with lowest passing grade ('D')."),
            ("Trigger Condition 2: ", "High inter-subject variance (StdDev > 14)."),
            ("Score Envelope: ", "Aggregate 55% to 62%; SGPI 5.5 to 6.5."),
            ("Primary Threat: ", "Drifting into backlog status as Semester V course difficulty escalates."),
            ("Mandatory Protocol: ", "Algorithmic foundation coaching, mock mid-semester tests, targeted doubt-solving sessions.")
        ]
        for b_t, n_t in t3_text:
            p = tf3.add_paragraph()
            p.space_after = Pt(4)
            rb = p.add_run()
            rb.text = "• " + b_t
            rb.font.bold = True
            rb.font.size = Pt(9)
            rb.font.color.rgb = BLUE_ACCENT
            rt = p.add_run()
            rt.text = n_t
            rt.font.size = Pt(8.5)
            rt.font.color.rgb = TEXT_DARK

        add_footer(slide, 18, 20)

    # -------------------------------------------------------------------------
    # SLIDE 19: Actionable Pedagogical Interventions for Semester V
    # -------------------------------------------------------------------------
    def slide_19_pedagogical_interventions(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, LIGHT_BG)
        add_header(slide, "Actionable Roadmap", "Tiered Pedagogical Action Plan for Semester V",
                   "Translating data insights into operational institutional interventions for curriculum heads and mentors")

        card_w = Inches(11.733)
        card_h = Inches(1.1)
        start_top = Inches(1.7)
        gap = Inches(1.25)

        interventions = [
            ("Tier 1: High Achievers & Leaders (Cluster 0)",
             "Curricular Enrichment & Capstone Acceleration",
             "Facilitate research publication co-authorship, advanced machine learning research projects, sponsored hackathons, and tier-1 industry internship placements. Deploy top students as peer mentors.",
             BLUE_ACCENT),
            ("Tier 2: Solid Performers (Cluster 1)",
             "Theory Mastery & Distinction Push",
             "Implement advanced problem-solving workshops in distributed systems and algorithms. Focus on improving exam writing technique to elevate borderline B/B+ students into distinction tier.",
             GREEN_SUCCESS),
            ("Tier 3: Developing Cohort (Cluster 2)",
             "Remedial Theory Bridge & Hands-On Theory Linkage",
             "Leverage their strong practical intuition (64.3% lab) to explain written theory concepts. Introduce continuous weekly formative quizzes rather than high-stakes term-end examinations.",
             AMBER_WARN),
            ("Tier 4: Critical Support Cohort (Cluster 3)",
             "Intensive Rehabilitation & Mentorship",
             "Establish individual faculty mentorship, attendance monitoring triggers, foundational prerequisite review courses, and coordinated psychological/academic guidance.",
             RED_ALERT)
        ]

        for idx, (tier, title, desc, col) in enumerate(interventions):
            top_pos = start_top + idx * gap
            add_card(slide, Inches(0.8), top_pos, card_w, card_h)

            tb = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.12), card_w - Inches(0.5), card_h - Inches(0.24))
            tf = tb.text_frame
            tf.word_wrap = True

            p1 = tf.paragraphs[0]
            p1.text = f"{tier.upper()}  —  {title}"
            p1.font.name = FONT_HEADING
            p1.font.size = Pt(11.5)
            p1.font.bold = True
            p1.font.color.rgb = col
            p1.space_after = Pt(2)

            p2 = tf.add_paragraph()
            p2.text = desc
            p2.font.name = FONT_BODY
            p2.font.size = Pt(9.5)
            p2.font.color.rgb = TEXT_DARK

        add_footer(slide, 19, 20)

    # -------------------------------------------------------------------------
    # SLIDE 20: Strategic Conclusions & Roadmap
    # -------------------------------------------------------------------------
    def slide_20_conclusion_roadmap(self):
        slide = self.prs.slides.add_slide(self.blank_layout)
        set_slide_background(slide, DARK_BG)

        add_card(slide, Inches(1.0), Inches(0.8), Inches(11.333), Inches(5.9), bg_color=DARK_CARD, border_color=DARK_BORDER)

        tb = slide.shapes.add_textbox(Inches(1.4), Inches(1.1), Inches(10.533), Inches(5.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p_badge = tf.paragraphs[0]
        p_badge.text = "STRATEGIC SYNTHESIS & INSTITUTIONAL ROADMAP"
        p_badge.font.name = FONT_HEADING
        p_badge.font.size = Pt(11)
        p_badge.font.bold = True
        p_badge.font.color.rgb = CYAN_ACCENT
        p_badge.space_after = Pt(10)

        p_title = tf.add_paragraph()
        p_title.text = "Transforming Academic Data into Actionable Institutional Intelligence"
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_LIGHT
        p_title.space_after = Pt(14)

        takeaways = [
            ("High Foundational Competence: ", "Over 76.1% of the Semester IV AI & DS cohort demonstrates solid or outstanding capability across technical disciplines."),
            ("Identified Bottleneck: ", "Written theory external examinations account for 100% of failed course units, while laboratory pass rates exceed 98%."),
            ("Data-Driven Personas: ", "Unsupervised K-Means clustering (K=4) effectively replaces blunt GPA filtering with 4 actionable competency archetypes."),
            ("Proactive Semester V Strategy: ", "Early detection of theory-practical score disparities ensures zero-surprise academic performance and maximum cohort graduation rates.")
        ]
        for b_t, t_t in takeaways:
            p = tf.add_paragraph()
            p.space_after = Pt(8)
            rb = p.add_run()
            rb.text = "★ " + b_t
            rb.font.bold = True
            rb.font.size = Pt(10.5)
            rb.font.color.rgb = BLUE_ACCENT
            rt = p.add_run()
            rt.text = t_t
            rt.font.size = Pt(10)
            rt.font.color.rgb = TEXT_LIGHT

        p_qa = tf.add_paragraph()
        p_qa.space_before = Pt(16)
        p_qa.text = "Thank You  |  Open for Questions & Strategic Discussion\nDepartment of Artificial Intelligence & Data Science"
        p_qa.font.name = FONT_HEADING
        p_qa.font.size = Pt(13)
        p_qa.font.bold = True
        p_qa.font.color.rgb = CYAN_ACCENT

        add_footer(slide, 20, 20, dark=True)


# -----------------------------------------------------------------------------
# MAIN EXECUTION ENTRYPOINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output_pptx = os.path.join(root_dir, "deliverables", "AI_DS_Sem4_Comprehensive_Analysis_Deck.pptx")
    os.makedirs(os.path.dirname(output_pptx), exist_ok=True)
    builder = PresentationBuilder(output_pptx)
    builder.build_deck()
    print(f"Presentation saved to: {output_pptx}")
