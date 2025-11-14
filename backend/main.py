from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Optional
import os
import uuid
from datetime import datetime

from models.deepfake_detector import DeepfakeDetector
from models.audio_detector import AudioDeepfakeDetector
from models.image_detector import ImageDeepfakeDetector
from database.db import init_db, save_analysis_result

app = FastAPI(
    title="DeepGuard AI",
    description="Advanced Deepfake Detection Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detectors
deepfake_detector = DeepfakeDetector()
audio_detector = AudioDeepfakeDetector()
image_detector = ImageDeepfakeDetector()

# Create upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


@app.get("/")
async def root():
    return {
        "name": "DeepGuard AI",
        "version": "1.0.0",
        "description": "Advanced Deepfake Detection API"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an image for deepfake manipulation
    Detects: Face swap, lip sync, face reenactment, AI-generated content
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Analyze image
        result = await image_detector.analyze(file_path)

        # Save to database
        await save_analysis_result({
            "file_id": file_id,
            "file_name": file.filename,
            "file_type": "image",
            "analysis_result": result,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "file_id": file_id,
            "file_name": file.filename,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/video")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze a video for deepfake manipulation
    Detects: Face swap, lip sync, face reenactment, deepfake videos
    """
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Analyze video
        result = await deepfake_detector.analyze_video(file_path)

        # Save to database
        await save_analysis_result({
            "file_id": file_id,
            "file_name": file.filename,
            "file_type": "video",
            "analysis_result": result,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "file_id": file_id,
            "file_name": file.filename,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/audio")
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze audio for voice cloning/deepfake
    Detects: Voice cloning, synthesized speech, audio manipulation
    """
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Analyze audio
        result = await audio_detector.analyze(file_path)

        # Save to database
        await save_analysis_result({
            "file_id": file_id,
            "file_name": file.filename,
            "file_type": "audio",
            "analysis_result": result,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "file_id": file_id,
            "file_name": file.filename,
            "analysis": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/results/{file_id}")
async def get_analysis_result(file_id: str):
    """Retrieve analysis result by file ID"""
    # This would query the database
    return {"message": "Result retrieval endpoint", "file_id": file_id}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
