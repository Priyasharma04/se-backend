import os, uuid, re
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from PyPDF2 import PdfReader
from utils.llm_client import generate_review

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "data/results"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_review(text):
    sections = {}
    parts = re.split(r"###\s*", text)
    for part in parts:
        if not part.strip():
            continue
        lines = part.strip().split("\n", 1)
        title = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""
        sections[title] = content
    return sections

@app.route("/api/review", methods=["POST"])
def review():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    pdf_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(pdf_path)

    run_id = str(uuid.uuid4())[:8]
    out_path = os.path.join(RESULTS_FOLDER, f"{run_id}_review.txt")

    # Extract text from PDF (SAFE EXTRACTION)
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        try:
            content = page.extract_text()
            if content:
                pages.append(content)
        except:
            continue

    text = "\n".join(pages).strip()

    # If PDF has no readable text
    if not text:
        return jsonify({
            "error": "Could not extract text from PDF. The PDF may be scanned or image-based."
        }), 400

    # Run review generator with actual text
    print(f"[INFO] Generating review for {filename}")
    review_text = generate_review(text)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(review_text)

    sections = parse_review(review_text)
    return jsonify({"review": sections, "file_id": run_id})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
