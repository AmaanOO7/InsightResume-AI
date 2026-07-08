from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

class PDFGenerator:
    """Generate professional PDF reports for resume analysis"""
    
    @staticmethod
    def generate_report(analysis_data, interview_data, career_data, output_path):
        """Generate comprehensive PDF report"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#4F46E5'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#4F46E5'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubHeading',
                parent=styles['Heading3'],
                fontSize=14,
                textColor=colors.HexColor('#6366F1'),
                spaceAfter=10,
                spaceBefore=10,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                alignment=TA_JUSTIFY
            )
            
            story.append(Paragraph("InsightResume AI", title_style))
            story.append(Paragraph("Comprehensive Resume Analysis Report", styles['Heading3']))
            story.append(Spacer(1, 0.2*inch))
            
            date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            story.append(Paragraph(date_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            story.append(Paragraph("Executive Summary", heading_style))
            
            score_data = [
                ['Metric', 'Score'],
                ['Resume Score', f"{analysis_data.get('resume_score', 0)}/100"],
                ['ATS Score', f"{analysis_data.get('ats_score', 0)}/100"],
                ['Experience Level', analysis_data.get('experience_level', 'N/A')]
            ]
            
            score_table = Table(score_data, colWidths=[3*inch, 2*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            
            story.append(score_table)
            story.append(Spacer(1, 0.3*inch))
            
            if analysis_data.get('summary'):
                story.append(Paragraph("Summary", subheading_style))
                story.append(Paragraph(analysis_data['summary'], normal_style))
                story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph("Skills Analysis", heading_style))
            
            if analysis_data.get('skills_found'):
                story.append(Paragraph("Skills Found:", subheading_style))
                skills_text = ", ".join(analysis_data['skills_found'])
                story.append(Paragraph(skills_text, normal_style))
                story.append(Spacer(1, 0.1*inch))
            
            if analysis_data.get('missing_skills'):
                story.append(Paragraph("Recommended Skills to Add:", subheading_style))
                missing_text = ", ".join(analysis_data['missing_skills'])
                story.append(Paragraph(missing_text, normal_style))
                story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph("Strengths", heading_style))
            if analysis_data.get('strengths'):
                for i, strength in enumerate(analysis_data['strengths'], 1):
                    story.append(Paragraph(f"{i}. {strength}", normal_style))
            story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph("Areas for Improvement", heading_style))
            if analysis_data.get('weaknesses'):
                for i, weakness in enumerate(analysis_data['weaknesses'], 1):
                    story.append(Paragraph(f"{i}. {weakness}", normal_style))
            story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph("Suggested Improvements", heading_style))
            if analysis_data.get('improvements'):
                for i, improvement in enumerate(analysis_data['improvements'], 1):
                    story.append(Paragraph(f"{i}. {improvement}", normal_style))
            
            story.append(PageBreak())
            
            story.append(Paragraph("Interview Preparation", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            questions = interview_data.get(
                "domain_questions",
                interview_data.get("technical_questions", [])
            )
            
            if questions:
                story.append(Paragraph("Technical Questions", subheading_style))
                for i, q in enumerate(questions, 1):
                    story.append(Paragraph(f"<b>Q{i}:</b> {q.get('question', '')}", normal_style))
                    story.append(Paragraph(f"<b>Answer:</b> {q.get('model_answer', '')}", normal_style))
                    story.append(Paragraph(f"<i>Difficulty: {q.get('difficulty', 'N/A')}</i>", styles['Italic']))
                    story.append(Spacer(1, 0.15*inch))
            
            if interview_data.get('hr_questions'):
                story.append(Paragraph("HR Questions", subheading_style))
                for i, q in enumerate(interview_data['hr_questions'], 1):
                    story.append(Paragraph(f"<b>Q{i}:</b> {q.get('question', '')}", normal_style))
                    story.append(Paragraph(f"<b>Answer:</b> {q.get('model_answer', '')}", normal_style))
                    story.append(Paragraph(f"<i>Difficulty: {q.get('difficulty', 'N/A')}</i>", styles['Italic']))
                    story.append(Spacer(1, 0.15*inch))
            
            story.append(PageBreak())
            
            story.append(Paragraph("Career Suggestions", heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            if career_data.get('suitable_roles'):
                story.append(Paragraph("Suitable Job Roles", subheading_style))
                for i, role in enumerate(career_data['suitable_roles'], 1):
                    story.append(Paragraph(
                        f"<b>{i}. {role.get('title', 'N/A')}</b> (Match: {role.get('match_percentage', 0)}%)",
                        normal_style
                    ))
                    story.append(Paragraph(str(role.get('description') or ""), normal_style))
                    story.append(Spacer(1, 0.1*inch))
            
            if career_data.get('salary_range'):
                story.append(Paragraph("Estimated Salary Range", subheading_style))
            
                salary = career_data.get("salary_range", {})
            
                try:
                    minimum = int(float(salary.get("min", 0)))
                except (ValueError, TypeError):
                    minimum = 0
            
                try:
                    maximum = int(float(salary.get("max", 0)))
                except (ValueError, TypeError):
                    maximum = 0
            
                currency = salary.get("currency", "INR")
                period = salary.get("period", "annual")
            
                salary_text = (
                    f"₹{minimum:,} - ₹{maximum:,} "
                    f"{currency} ({period})"
                )
            
                story.append(Paragraph(salary_text, normal_style))
                story.append(Spacer(1, 0.2 * inch))
            if career_data.get('certifications'):
                story.append(Paragraph("Recommended Certifications", subheading_style))
                for i, cert in enumerate(career_data['certifications'], 1):
                    story.append(Paragraph(
                        f"<b>{i}. {cert.get('name', 'N/A')}</b> - {cert.get('provider', 'N/A')}",
                        normal_style
                    ))
                    story.append(Paragraph(f"Priority: {cert.get('priority', 'N/A')}", normal_style))
                    story.append(Paragraph(f"Reason: {cert.get('reason', '')}", normal_style))
                    story.append(Spacer(1, 0.1*inch))
            
            if career_data.get('learning_roadmap'):
                story.append(Paragraph("Learning Roadmap", subheading_style))
                for i, item in enumerate(career_data['learning_roadmap'], 1):
                    story.append(Paragraph(
                        f"<b>{i}. {item.get('skill', 'N/A')}</b> (Timeline: {item.get('timeline', 'N/A')})",
                        normal_style
                    ))
                    story.append(Paragraph(f"Priority: {item.get('priority', 'N/A')}", normal_style))
                    if item.get('resources'):
                        resources = item.get("resources", [])

                        if isinstance(resources, str):
                            resources = [resources]
                        
                        resources_text = "Resources: " + ", ".join(resources)
                        story.append(Paragraph(resources_text, normal_style))
                    story.append(Spacer(1, 0.1*inch))
            
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("---", styles['Normal']))
            story.append(Paragraph(
                "This report was generated by InsightResume AI - Your AI-Powered Career Assistant",
                styles['Italic']
            ))
            
            doc.build(story)
            return True
            
        except Exception as e:
            raise Exception(f"Error generating PDF report: {str(e)}")
