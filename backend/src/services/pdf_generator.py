"""
PDF Generator Service
=====================
Generates professional PDF exports of quizzes using ReportLab.
"""

import io
import logging
from typing import Dict, Any, Optional, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

logger = logging.getLogger(__name__)


# Color palette
COLORS = {
    'primary': colors.HexColor('#4F46E5'),
    'primary_light': colors.HexColor('#EEF2FF'),
    'success': colors.HexColor('#059669'),
    'success_light': colors.HexColor('#ECFDF5'),
    'warning': colors.HexColor('#D97706'),
    'warning_light': colors.HexColor('#FFFBEB'),
    'danger': colors.HexColor('#DC2626'),
    'danger_light': colors.HexColor('#FEF2F2'),
    'text': colors.HexColor('#1F2937'),
    'text_secondary': colors.HexColor('#6B7280'),
    'text_muted': colors.HexColor('#9CA3AF'),
    'border': colors.HexColor('#E5E7EB'),
    'bg_light': colors.HexColor('#F9FAFB'),
    'white': colors.HexColor('#FFFFFF'),
}


def build_exam_pdf(
    org_title: str,
    user: str,
    quiz_title: str,
    quiz: Dict[str, Any],
    duration_str: str
) -> io.BytesIO:
    """
    Build a professional PDF exam document from quiz data.
    """
    
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    # ===== CUSTOM STYLES =====
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=6,
        textColor=COLORS['text'],
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        textColor=COLORS['primary'],
        fontName='Helvetica-Bold'
    )
    
    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=16,
        spaceAfter=12,
        textColor=COLORS['text'],
        fontName='Helvetica-Bold'
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        textColor=COLORS['text'],
        leading=14
    )
    
    option_style = ParagraphStyle(
        'OptionStyle',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=3,
        textColor=COLORS['text'],
        leading=13
    )
    
    result_style = ParagraphStyle(
        'ResultStyle',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=20,
        spaceBefore=6,
        spaceAfter=4,
        textColor=COLORS['text_secondary']
    )
    
    explanation_style = ParagraphStyle(
        'ExplanationStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=COLORS['text_muted'],
        leftIndent=20,
        spaceAfter=16,
        leading=12
    )
    
    # Build content
    story = []
    
    # ===== HEADER =====
    story.append(Paragraph(org_title, title_style))
    story.append(Paragraph(quiz_title, subtitle_style))
    
    # ===== RESULT SUMMARY =====
    score = quiz.get("score", 0)
    total = quiz.get("total", len(quiz.get("quiz", [])))
    user_answers = quiz.get("user_answers", {})
    percentage = round((score / total) * 100) if total > 0 else 0
    
    # Performance level
    if percentage >= 80:
        performance = "Excellent"
        perf_color = COLORS['success']
    elif percentage >= 60:
        performance = "Good"
        perf_color = COLORS['primary']
    elif percentage >= 40:
        performance = "Average"
        perf_color = COLORS['warning']
    else:
        performance = "Needs Improvement"
        perf_color = COLORS['danger']
    
    # Summary table with clean design
    summary_data = [
        ['Candidate:', user or 'Anonymous'],
        ['Score:', f'{score} / {total} ({percentage}%)'],
        ['Performance:', performance],
        ['Time Taken:', duration_str or '—'],
    ]
    
    summary_table = Table(summary_data, colWidths=[100, 380])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['white']),
        ('TEXTCOLOR', (0, 0), (0, -1), COLORS['text_secondary']),
        ('TEXTCOLOR', (1, 0), (1, -1), COLORS['text']),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('LEFTPADDING', (1, 0), (1, -1), 12),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, COLORS['border']),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 24))
    
    # Divider
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLORS['primary']))
    story.append(Spacer(1, 8))
    
    # ===== QUESTIONS SECTION =====
    story.append(Paragraph('QUESTIONS & ANSWERS', section_header))
    
    questions = quiz.get("quiz", [])
    
    for idx, q in enumerate(questions):
        question_elements = []
        qnum = idx + 1
        user_ans = user_answers.get(str(idx), "")
        correct_ans = q.get("answer", "")
        is_correct = user_ans == correct_ans if user_ans else False
        
        # Difficulty colors
        difficulty = q.get("difficulty", "medium").lower()
        diff_colors = {
            "easy": "#059669",
            "medium": "#D97706", 
            "hard": "#DC2626"
        }
        diff_color = diff_colors.get(difficulty, "#6B7280")
        
        # Status icon
        if user_ans:
            status = "✓" if is_correct else "✗"
            status_color = "#059669" if is_correct else "#DC2626"
        else:
            status = "○"
            status_color = "#9CA3AF"
        
        # Question text
        question_text = (
            f'<font color="{status_color}"><b>{status}</b></font> '
            f'<b>Q{qnum}.</b> {q.get("question", "")} '
            f'<font color="{diff_color}" size="9">[{difficulty.upper()}]</font>'
        )
        question_elements.append(Paragraph(question_text, question_style))
        
        # Options - clean format
        options = q.get("options", [])[:4]
        letters = ['A', 'B', 'C', 'D']
        
        for j, opt in enumerate(options):
            letter = letters[j]
            is_this_correct = opt == correct_ans
            is_user_choice = opt == user_ans
            
            # Clean option text without duplicates
            if is_this_correct and is_user_choice:
                # User selected the correct answer
                opt_text = f'<font color="#059669"><b>{letter}) {opt}  ✓</b></font>'
            elif is_this_correct:
                # This is correct but user didn't select it
                opt_text = f'<font color="#059669"><b>{letter}) {opt}  ← Correct</b></font>'
            elif is_user_choice:
                # User selected wrong answer
                opt_text = f'<font color="#DC2626">{letter}) {opt}  ✗ Your answer</font>'
            else:
                # Regular option
                opt_text = f'{letter}) {opt}'
            
            question_elements.append(Paragraph(opt_text, option_style))
        
        # Result summary line
        if user_ans:
            if is_correct:
                result_text = f'<font color="#059669"><b>✓ Correct</b></font>'
            else:
                result_text = f'<font color="#DC2626"><b>✗ Incorrect</b> — Correct answer: {correct_ans}</font>'
        else:
            result_text = f'<font color="#9CA3AF">Not answered — Correct answer: {correct_ans}</font>'
        
        question_elements.append(Paragraph(result_text, result_style))
        
        # Explanation
        if q.get("explanation"):
            explanation_text = f'<i>{q.get("explanation")}</i>'
            question_elements.append(Paragraph(explanation_text, explanation_style))
        else:
            question_elements.append(Spacer(1, 12))
        
        # Keep question together on page
        story.append(KeepTogether(question_elements))
    
    # ===== FOOTER =====
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLORS['border']))
    story.append(Spacer(1, 8))
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COLORS['text_muted'],
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f'{org_title} • WikiQuiz AI • Powered by LangChain + Google Gemini',
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer
