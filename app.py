from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
import requests, tempfile, time
from PyPDF2 import PdfReader

app = FastAPI(title="PeerReviewAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NGROK_URL = "https://shrubby-glenda-sacramentally.ngrok-free.dev"

RATE_LIMIT = 5
WINDOW_SIZE = 60
request_log = {}

def is_scanned_pdf(file_path: str) -> bool:
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text() or ""
            text += extracted.strip()
        return len(text.strip()) == 0
    except Exception:
        return True

@app.post("/api/review")
async def review(request: Request, file: UploadFile = File(...)):
    client_ip = request.client.host
    now = time.time()

    request_log.setdefault(client_ip, [])
    request_log[client_ip] = [t for t in request_log[client_ip] if now - t < WINDOW_SIZE]

    if len(request_log[client_ip]) >= RATE_LIMIT:
        return {"error": "Rate limit exceeded. Please wait a minute."}

    request_log[client_ip].append(now)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        if is_scanned_pdf(tmp_path):
            return {"error": "This appears to be a scanned PDF with no extractable text. Please upload a digital text-based PDF."}

        files = {"file": open(tmp_path, "rb")}
        response = requests.post(f"{NGROK_URL}/generate", files=files)

        if response.status_code != 200:
            return {"error": f"Model API failed: {response.text}"}

        model_output = response.json()

        if "response" in model_output:
            return {"review": model_output["response"]}

        return {"error": "Unexpected response from model API."}

    except Exception as e:
        return {"error": str(e)}
