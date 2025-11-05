# ==========================================================
# 🌐 Render Backend — Connects Frontend → Kaggle (Ngrok API)
# ==========================================================
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests, tempfile

app = FastAPI(title="ReviewAdvisor Backend")

# ---------------------------------
# CORS Setup (Allow Frontend)
# ---------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-haud2jc7n-aasthac2605-4651s-projects.vercel.app"],  # or restrict to your Vercel domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------
# 🔗 Ngrok Endpoint (Kaggle API URL)
# ---------------------------------
NGROK_URL = "https://beverly-unfriable-amaya.ngrok-free.dev"  # ⬅️ replace with your Kaggle ngrok link

# ---------------------------------
# Main Endpoint
# ---------------------------------
@app.post("/api/review")
async def review(file: UploadFile = File(...)):
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Send to Kaggle (Ngrok) API
        files = {"file": open(tmp_path, "rb")}
        response = requests.post(f"{NGROK_URL}/generate", files=files)

        if response.status_code != 200:
            return {"error": f"Model API failed: {response.text}"}

        return response.json()

    except Exception as e:
        return {"error": str(e)}
