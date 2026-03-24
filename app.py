import io
from flask import Flask, render_template, request, send_file
from transformers import pipeline
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# Load summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")


# 🔥 UNLIMITED TEXT SUMMARIZATION (NO REDUCTION)
def summarize_long_text(text):
    max_chunk = 1000
    summaries = []

    # Split into sentences
    sentences = text.split('.')
    chunk = ""

    for sentence in sentences:
        if len(chunk) + len(sentence) < max_chunk:
            chunk += sentence + "."
        else:
            try:
                result = summarizer(
                    chunk,
                    max_length=200,   # 🔥 increased for longer summary
                    min_length=80,
                    do_sample=False
                )
                summaries.append(result[0]['summary_text'])
            except:
                pass

            chunk = sentence + "."

    # Last chunk
    if chunk:
        try:
            result = summarizer(
                chunk,
                max_length=200,
                min_length=80,
                do_sample=False
            )
            summaries.append(result[0]['summary_text'])
        except:
            pass

    # 🔥 IMPORTANT: DO NOT SUMMARIZE AGAIN
    final_summary = " ".join(summaries)

    return final_summary if final_summary else "Text too complex or empty"


# ⭐ SMART KEY POINTS (NOT COPY, MEANINGFUL)
def generate_key_points(summary):
    try:
        sentences = summary.split('.')
        points = []

        for s in sentences:
            s = s.strip()

            if len(s) < 40:
                continue

            words = s.split()
            short = " ".join(words[:12])

            points.append(short + "...")

        return points[:5] if points else ["No key points found"]

    except:
        return ["Unable to extract key points"]


# 🔹 HOME PAGE
@app.route('/')
def index():
    return render_template('index.html')


# 🔹 SUMMARIZE TEXT
@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.form['text']

    if not text.strip():
        return render_template('result.html', summary="Please enter some text", points=[])

    summary = summarize_long_text(text)
    key_points = generate_key_points(summary)

    return render_template('result.html', summary=summary, points=key_points)


# 🔹 DOWNLOAD PDF
@app.route('/download', methods=['POST'])
def download():
    points = request.form.getlist('points')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("<b>Key Points:</b>", styles["Title"]))

    for p in points:
        content.append(Paragraph(p, styles["Normal"]))

    doc.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="key_points.pdf",
        mimetype='application/pdf'
    )


# 🔹 RUN APP
if __name__ == '__main__':
    app.run(debug=True)
