"""
InsightResume AI
Professional PDF Report Generator

Creates a modern resume analysis report.

Author: Aman Kumar
"""

from __future__ import annotations

import os
import logging
from datetime import datetime
from typing import Dict, List, Any

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
)

from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)

from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Generate professional resume analysis reports.
    """

    # ======================================================
    # Theme
    # ======================================================

    PRIMARY = colors.HexColor("#2563EB")

    SUCCESS = colors.HexColor("#16A34A")

    WARNING = colors.HexColor("#F59E0B")

    DANGER = colors.HexColor("#DC2626")

    DARK = colors.HexColor("#1E293B")

    LIGHT = colors.HexColor("#F8FAFC")

    BORDER = colors.HexColor("#CBD5E1")

    # ======================================================
    # Styles
    # ======================================================

    styles = getSampleStyleSheet()

    TITLE = ParagraphStyle(

        "TITLE",

        parent=styles["Heading1"],

        alignment=TA_CENTER,

        fontSize=24,

        leading=28,

        textColor=PRIMARY,

        spaceAfter=20,

    )

    HEADING = ParagraphStyle(

        "HEADING",

        parent=styles["Heading2"],

        fontSize=16,

        leading=20,

        textColor=DARK,

        spaceAfter=10,

        spaceBefore=20,

    )

    SUBHEADING = ParagraphStyle(

        "SUBHEADING",

        parent=styles["Heading3"],

        fontSize=13,

        leading=18,

        textColor=PRIMARY,

        spaceBefore=10,

        spaceAfter=8,

    )

    BODY = ParagraphStyle(

        "BODY",

        parent=styles["BodyText"],

        fontSize=10,

        leading=16,

        alignment=TA_LEFT,

        spaceAfter=8,

    )

    SMALL = ParagraphStyle(

        "SMALL",

        parent=styles["BodyText"],

        fontSize=9,

        leading=13,

    )

    SCORE = ParagraphStyle(

        "SCORE",

        parent=styles["Heading1"],

        alignment=TA_CENTER,

        fontSize=30,

        textColor=PRIMARY,

        leading=34,

    )

    # ======================================================
    # Helpers
    # ======================================================

    @staticmethod
    def score_color(score: int):

        if score >= 80:

            return PDFGenerator.SUCCESS

        if score >= 60:

            return PDFGenerator.WARNING

        return PDFGenerator.DANGER

    # ------------------------------------------------------

    @staticmethod
    def bullet_list(items: List[str]) -> List:

        story = []

        if not items:

            story.append(

                Paragraph(

                    "No information available.",

                    PDFGenerator.BODY,

                )

            )

            return story

        for item in items:

            story.append(

                Paragraph(

                    f"• {item}",

                    PDFGenerator.BODY,

                )

            )

        return story

    # ------------------------------------------------------

    @staticmethod
    def score_table(title: str, score: int):

        color = PDFGenerator.score_color(score)

        table = Table(

            [

                [

                    Paragraph(

                        f"<b>{title}</b>",

                        PDFGenerator.SUBHEADING,

                    )

                ],

                [

                    Paragraph(

                        f"<font color='{color}'>{score}%</font>",

                        PDFGenerator.SCORE,

                    )

                ],

            ],

            colWidths=[2.5 * inch],

        )

        table.setStyle(

            TableStyle(

                [

                    ("BOX", (0, 0), (-1, -1), 1, PDFGenerator.BORDER),

                    ("BACKGROUND", (0, 0), (-1, 0), PDFGenerator.LIGHT),

                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

                    ("TOPPADDING", (0, 1), (-1, 1), 10),

                    ("BOTTOMPADDING", (0, 1), (-1, 1), 12),

                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),

                ]

            )

        )

        return table

    # ======================================================
    # Report Builder
    # ======================================================

    @classmethod
    def generate_report(
        cls,
        analysis_data: Dict[str, Any],
        interview_data: Dict[str, Any],
        career_data: Dict[str, Any],
        output_path: str,
    ):
        """
        Main PDF generation method.
        """

        logger.info(

            "Generating PDF report..."

        )

        document = SimpleDocTemplate(

            output_path,

            rightMargin=0.5 * inch,

            leftMargin=0.5 * inch,

            topMargin=0.6 * inch,

            bottomMargin=0.6 * inch,

            title="InsightResume AI Report",

            author="InsightResume AI",

        )

        story = []

        # Cover page will be added in Part 2

        # ======================================================
        # Cover Page
        # ======================================================

        story.append(
            Paragraph(
                "InsightResume AI",
                cls.TITLE
            )
        )

        story.append(
            Paragraph(
                "Professional Resume Analysis Report",
                cls.SUBHEADING
            )
        )

        story.append(
            Spacer(1, 0.30 * inch)
        )

        generated_time = datetime.now().strftime(
            "%d %B %Y, %I:%M %p"
        )

        story.append(
            Paragraph(
                f"<b>Generated On:</b> {generated_time}",
                cls.BODY
            )
        )

        story.append(
            Paragraph(
                "This report has been automatically generated using Google's Gemini AI model. "
                "It compares your uploaded resume with the provided Job Description and provides "
                "ATS evaluation, recruiter feedback, interview preparation and career guidance.",
                cls.BODY
            )
        )

        story.append(
            Spacer(1, 0.40 * inch)
        )

        # ======================================================
        # Resume Scores
        # ======================================================

        resume_score = int(
            analysis_data.get(
                "resume_score",
                0
            )
        )

        ats_score = int(
            analysis_data.get(
                "ats_score",
                0
            )
        )

        score_table = Table(

            [[

                cls.score_table(
                    "Resume Score",
                    resume_score
                ),

                cls.score_table(
                    "ATS Score",
                    ats_score
                )

            ]],

            colWidths=[3 * inch, 3 * inch]

        )

        score_table.setStyle(

            TableStyle(

                [

                    ("VALIGN", (0, 0), (-1, -1), "TOP"),

                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),

                    ("ALIGN", (0, 0), (-1, -1), "CENTER")

                ]

            )

        )

        story.append(score_table)

        story.append(
            Spacer(1, 0.35 * inch)
        )

        # ======================================================
        # Experience Level
        # ======================================================

        story.append(

            Paragraph(

                "Experience Level",

                cls.HEADING

            )

        )

        story.append(

            Paragraph(

                analysis_data.get(

                    "experience_level",

                    "Not Available"

                ),

                cls.BODY

            )

        )

        # ======================================================
        # Executive Summary
        # ======================================================

        story.append(

            Paragraph(

                "Executive Summary",

                cls.HEADING

            )

        )

        story.append(

            Paragraph(

                analysis_data.get(

                    "summary",

                    "No summary generated."

                ),

                cls.BODY

            )

        )

        # ======================================================
        # Strengths
        # ======================================================

        story.append(

            Paragraph(

                "Strengths",

                cls.HEADING

            )

        )

        strengths = analysis_data.get(

            "strengths",

            []

        )

        story.extend(

            cls.bullet_list(

                strengths

            )

        )

        story.append(

            Spacer(

                1,

                0.25 * inch

            )

        )

        # ======================================================
        # Weaknesses
        # ======================================================

        story.append(

            Paragraph(

                "Weaknesses",

                cls.HEADING

            )

        )

        weaknesses = analysis_data.get(

            "weaknesses",

            []

        )

        story.extend(

            cls.bullet_list(

                weaknesses

            )

        )

        story.append(

            PageBreak()

        )

        # ======================================================
        # Skills Analysis
        # ======================================================

        story.append(
            Paragraph(
                "Skills Analysis",
                cls.TITLE
            )
        )

        # ----------------------------
        # Skills Found
        # ----------------------------

        story.append(
            Paragraph(
                "Skills Found",
                cls.HEADING
            )
        )

        skills_found = analysis_data.get(
            "skills_found",
            []
        )

        story.extend(
            cls.bullet_list(
                skills_found
            )
        )

        story.append(
            Spacer(1, 0.15 * inch)
        )

        # ----------------------------
        # Missing Skills
        # ----------------------------

        story.append(
            Paragraph(
                "Missing Skills",
                cls.HEADING
            )
        )

        missing_skills = analysis_data.get(
            "missing_skills",
            []
        )

        story.extend(
            cls.bullet_list(
                missing_skills
            )
        )

        story.append(
            Spacer(1, 0.20 * inch)
        )

        # ======================================================
        # Keyword Analysis
        # ======================================================

        story.append(
            Paragraph(
                "Keyword Analysis",
                cls.TITLE
            )
        )

        # ----------------------------
        # Matched Keywords
        # ----------------------------

        story.append(
            Paragraph(
                "Matched Keywords",
                cls.HEADING
            )
        )

        matched_keywords = analysis_data.get(
            "matched_keywords",
            []
        )

        story.extend(
            cls.bullet_list(
                matched_keywords
            )
        )

        story.append(
            Spacer(1, 0.15 * inch)
        )

        # ----------------------------
        # Missing Keywords
        # ----------------------------

        story.append(
            Paragraph(
                "Missing Keywords",
                cls.HEADING
            )
        )

        missing_keywords = analysis_data.get(
            "missing_keywords",
            []
        )

        story.extend(
            cls.bullet_list(
                missing_keywords
            )
        )

        story.append(
            Spacer(1, 0.25 * inch)
        )

        # ======================================================
        # Resume Improvements
        # ======================================================

        story.append(
            Paragraph(
                "Recommended Improvements",
                cls.TITLE
            )
        )

        improvements = analysis_data.get(
            "improvements",
            []
        )

        story.extend(
            cls.bullet_list(
                improvements
            )
        )

        story.append(
            Spacer(1, 0.30 * inch)
        )

        # ======================================================
        # ATS Feedback
        # ======================================================

        story.append(
            Paragraph(
                "ATS Feedback",
                cls.TITLE
            )
        )

        ats_feedback = analysis_data.get(
            "ats_feedback",
            "No ATS feedback available."
        )

        story.append(
            Paragraph(
                ats_feedback,
                cls.BODY
            )
        )

        story.append(
            Spacer(1, 0.30 * inch)
        )

        # ======================================================
        # Recruiter Feedback
        # ======================================================

        story.append(
            Paragraph(
                "Recruiter Feedback",
                cls.TITLE
            )
        )

        recruiter_feedback = analysis_data.get(
            "recruiter_feedback",
            "No recruiter feedback available."
        )

        story.append(
            Paragraph(
                recruiter_feedback,
                cls.BODY
            )
        )

        story.append(
            PageBreak()
        )

        # ======================================================
        # Interview Preparation
        # ======================================================

        story.append(
            Paragraph(
                "Interview Preparation",
                cls.TITLE
            )
        )

        # ------------------------------------------------------
        # Domain / Technical Questions
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "Domain / Technical Questions",
                cls.HEADING
            )
        )

        domain_questions = interview_data.get(
            "domain_questions",
            []
        )

        if domain_questions:

            for index, question in enumerate(domain_questions, start=1):

                story.append(
                    Paragraph(
                        f"<b>Question {index}</b>",
                        cls.SUBHEADING
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Question:</b> {question.get('question', '')}",
                        cls.BODY
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Difficulty:</b> {question.get('difficulty', 'N/A')}",
                        cls.SMALL
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Topic:</b> {question.get('topic', 'N/A')}",
                        cls.SMALL
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Why asked:</b> {question.get('why_this_question', '')}",
                        cls.BODY
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Model Answer:</b><br/>{question.get('model_answer', '')}",
                        cls.BODY
                    )
                )

                story.append(
                    Spacer(1, 0.20 * inch)
                )

        else:

            story.append(
                Paragraph(
                    "No technical interview questions generated.",
                    cls.BODY
                )
            )

        # ------------------------------------------------------
        # HR Questions
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "HR / Behavioural Questions",
                cls.HEADING
            )
        )

        hr_questions = interview_data.get(
            "hr_questions",
            []
        )

        if hr_questions:

            for index, question in enumerate(hr_questions, start=1):

                story.append(
                    Paragraph(
                        f"<b>HR Question {index}</b>",
                        cls.SUBHEADING
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Question:</b> {question.get('question', '')}",
                        cls.BODY
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Difficulty:</b> {question.get('difficulty', 'N/A')}",
                        cls.SMALL
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Quality Being Tested:</b> {question.get('quality_being_tested', '')}",
                        cls.SMALL
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Why asked:</b> {question.get('why_this_question', '')}",
                        cls.BODY
                    )
                )

                story.append(
                    Paragraph(
                        f"<b>Model Answer:</b><br/>{question.get('model_answer', '')}",
                        cls.BODY
                    )
                )

                story.append(
                    Spacer(1, 0.20 * inch)
                )

        else:

            story.append(
                Paragraph(
                    "No HR interview questions generated.",
                    cls.BODY
                )
            )

        story.append(PageBreak())

        # ======================================================
        # Career Suggestions
        # ======================================================

        story.append(
            Paragraph(
                "Career Guidance",
                cls.TITLE
            )
        )

        # ------------------------------------------------------
        # Suitable Roles
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "Suitable Career Roles",
                cls.HEADING
            )
        )

        suitable_roles = career_data.get(
            "suitable_roles",
            []
        )

        for role in suitable_roles:

            story.append(
                Paragraph(
                    f"<b>{role.get('title', '')}</b> "
                    f"({role.get('match_percentage', 0)}% Match)",
                    cls.SUBHEADING
                )
            )

            story.append(
                Paragraph(
                    role.get(
                        "description",
                        ""
                    ),
                    cls.BODY
                )
            )

        story.append(
            Spacer(1, 0.25 * inch)
        )

        # ------------------------------------------------------
        # Salary Range
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "Expected Salary Range",
                cls.HEADING
            )
        )

        salary = career_data.get(
            "salary_range",
            {}
        )

        salary_text = (
            f"{salary.get('currency', '')} "
            f"{salary.get('min', 0):,} - "
            f"{salary.get('max', 0):,} "
            f"({salary.get('period', 'Annual')})"
        )

        story.append(
            Paragraph(
                salary_text,
                cls.BODY
            )
        )

        # ------------------------------------------------------
        # Certifications
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "Recommended Certifications",
                cls.HEADING
            )
        )

        certifications = career_data.get(
            "certifications",
            []
        )

        for cert in certifications:

            story.append(
                Paragraph(
                    f"<b>{cert.get('name', '')}</b>",
                    cls.SUBHEADING
                )
            )

            story.append(
                Paragraph(
                    f"Provider: {cert.get('provider', '')}",
                    cls.SMALL
                )
            )

            story.append(
                Paragraph(
                    f"Priority: {cert.get('priority', '')}",
                    cls.SMALL
                )
            )

            story.append(
                Paragraph(
                    cert.get(
                        "reason",
                        ""
                    ),
                    cls.BODY
                )
            )

        story.append(
            Spacer(1, 0.20 * inch)
        )

        # ------------------------------------------------------
        # Learning Roadmap
        # ------------------------------------------------------

        story.append(
            Paragraph(
                "Learning Roadmap",
                cls.HEADING
            )
        )

        roadmap = career_data.get(
            "learning_roadmap",
            []
        )

        for step in roadmap:

            story.append(
                Paragraph(
                    f"<b>{step.get('skill', '')}</b>",
                    cls.SUBHEADING
                )
            )

            story.append(
                Paragraph(
                    f"Timeline: {step.get('timeline', '')}",
                    cls.SMALL
                )
            )

            story.append(
                Paragraph(
                    f"Priority: {step.get('priority', '')}",
                    cls.SMALL
                )
            )

            resources = step.get(
                "resources",
                []
            )

            if resources:

                story.append(
                    Paragraph(
                        "<b>Recommended Resources</b>",
                        cls.SMALL
                    )
                )

                story.extend(
                    cls.bullet_list(resources)
                )

            story.append(
                Spacer(1, 0.15 * inch)
            )

        # ======================================================
        # Disclaimer
        # ======================================================

        story.append(
            Spacer(1, 0.30 * inch)
        )

        story.append(
            Paragraph(
                "Disclaimer",
                cls.HEADING
            )
        )

        story.append(
            Paragraph(
                "This report is generated using Artificial Intelligence (Google Gemini) "
                "based on the uploaded resume and the provided job description. "
                "The recommendations, scores, interview questions, and career guidance "
                "are intended to assist candidates in improving their resumes and interview "
                "preparation. They should not be considered official hiring decisions or "
                "professional legal, financial, or employment advice.",
                cls.SMALL
            )
        )

        story.append(
            Spacer(1, 0.20 * inch)
        )

        story.append(
            Paragraph(
                "<b>Generated by InsightResume AI</b>",
                cls.SUBHEADING
            )
        )

        # ======================================================
        # Build PDF
        # ======================================================

        try:

            document.build(

                story,

                onFirstPage=cls._add_page_number,

                onLaterPages=cls._add_page_number

            )

            logger.info(

                "PDF report generated successfully."

            )

        except Exception:

            logger.exception(

                "Failed to generate PDF report."

            )

            raise

    # ==========================================================
    # Footer / Page Number
    # ==========================================================

    @staticmethod
    def _add_page_number(canvas, document):
        """
        Draw footer and page number.
        """

        canvas.saveState()

        width, height = document.pagesize

        footer = (
            "InsightResume AI | Resume Analysis Report"
        )

        canvas.setFont(

            "Helvetica",

            9

        )

        canvas.drawString(

            40,

            25,

            footer

        )

        canvas.drawRightString(

            width - 40,

            25,

            f"Page {document.page}"

        )

        canvas.restoreState()

    # ==========================================================
    # Status
    # ==========================================================

    @classmethod
    def get_status(cls):

        return {

            "service": "PDF Generator",

            "engine": "ReportLab",

            "version": cls.VERSION

        }

    # ==========================================================
    # Version
    # ==========================================================

    VERSION = "2.0.0"

