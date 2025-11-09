from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import red, green, black

def build_exam_pdf(filename: str, org_title: str, user: str, quiz_title: str, quiz: dict, duration_str: str):
    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    story = []

    score = quiz.get("score", 0)
    total = quiz.get("total", len(quiz.get("quiz", [])))

    story.append(Paragraph(f"<b>{org_title}</b>", styles["Title"]))
    story.append(Paragraph(quiz_title, styles["h2"]))
    story.append(Paragraph(f"Candidate: <b>{user}</b>", styles["Normal"]))
    story.append(Paragraph(f"Score: <b>{score}/{total}</b>", styles["Normal"]))
    story.append(Paragraph(f"Time Taken: <b>{duration_str}</b>", styles["Normal"]))
    story.append(Spacer(1, 12))

    user_answers = quiz.get("user_answers", {})
    letters = "ABCD"

    for i, q in enumerate(quiz.get("quiz", []), start=1):
        question = q["question"]
        options = q["options"]
        correct = q["answer"]
        explanation = q.get("explanation", "")
        user_ans = user_answers.get(str(i-1))
        is_correct = user_ans == correct

        story.append(Paragraph(f"<b>Q{i}.</b> {question}", styles["BodyText"]))

        for idx, opt in enumerate(options):
            if opt == user_ans:
                color = green if is_correct else red
            else:
                color = black

            style = ParagraphStyle("choice", parent=styles["BodyText"], textColor=color)
            story.append(Paragraph(f"{letters[idx]}) {opt}", style))

        ua_style = ParagraphStyle("ua", parent=styles["BodyText"], textColor=green if is_correct else red)
        # story.append(Paragraph(f"<b>Your Answer:</b> {user_ans}", ua_style))
        story.append(Paragraph(f"<b>Correct Answer:</b> {correct}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Why:</b> {explanation}", styles["BodyText"]))
        story.append(Spacer(1, 10))

    doc.build(story)
    return filename
