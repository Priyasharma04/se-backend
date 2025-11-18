from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import requests, tempfile
app = FastAPI(title="ReviewAdvisor Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
NGROK_URL = "https://repeatable-overimitatively-jonas.ngrok-free.dev"  
@app.post("/api/review")
async def review(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        files = {"file": open(tmp_path, "rb")}
        response = requests.post(f"{NGROK_URL}/generate", files=files)
        if response.status_code != 200:
            return {"error": f"Model API failed: {response.text}"}
        return response.json()
    except Exception as e:
        return {"error": str(e)}

