import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load env vars
load_dotenv()

from storage import StorageService
from transcriber import TranscriberService
from reflector import ReflectorService

# Globals
storage_service = None
transcriber_service = None
reflector_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize services
    global storage_service, transcriber_service, reflector_service
    storage_service = StorageService()
    transcriber_service = TranscriberService()
    reflector_service = ReflectorService()
    yield
    # Shutdown: Clean up if needed

app = FastAPI(
    title="Still API",
    description="The silent backend for the Still ritual.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS: Allow the frontend to talk to us
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://*.vercel.app",
    "https://*.netlify.app", 
    "https://*.render.com",
    "*"  # Allow all origins for now - restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify connectivity"""
    print("🔥 Test endpoint called!")
    return {"message": "Backend is working!", "timestamp": "2026-01-04"}

@app.get("/debug-ffmpeg")
async def debug_ffmpeg():
    """Debug endpoint to test FFmpeg availability"""
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {
            "status": "success",
            "ffmpeg_available": True,
            "version_info": result.stdout.split('\n')[0]  # First line has version
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "ffmpeg_available": False,
            "error": "FFmpeg not found"
        }
    except Exception as e:
        return {
            "status": "error",
            "ffmpeg_available": False,
            "error": str(e)
        }

@app.get("/debug-azure")
async def debug_azure():
    """Debug endpoint to test Azure OpenAI connection"""
    try:
        # Test environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        endpoint = os.getenv("OPENAI_API_BASE")
        deployment = os.getenv("OPENAI_DEPLOYMENT_NAME")
        
        env_status = {
            "api_key_present": bool(api_key),
            "api_key_length": len(api_key) if api_key else 0,
            "endpoint": endpoint,
            "deployment": deployment
        }
        
        # Test Azure OpenAI connection
        if reflector_service and reflector_service.client:
            test_result = reflector_service._call_model("Test message")
            return {
                "status": "success",
                "environment": env_status,
                "azure_test": "success" if test_result else "failed",
                "test_result": test_result
            }
        else:
            return {
                "status": "error",
                "environment": env_status,
                "azure_test": "client_not_initialized",
                "error": "ReflectorService client is None"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": str(type(e))
        }

@app.get("/health")
async def health_check():
    return {"status": "still", "silence": True}

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    print(f"🎯 Received audio upload: {file.filename}, size: {file.size}, content_type: {file.content_type}")
    
    if not file:
        raise HTTPException(status_code=400, detail="No audio file provided")

    # 1. Save temp file (local or blob)
    filename = f"audio_{os.urandom(4).hex()}.webm"
    temp_path = f"temp_{filename}"
    
    try:
        print(f"💾 Saving audio to: {temp_path}")
        # Save locally for processing
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"✅ Audio saved, file size: {os.path.getsize(temp_path)} bytes")
        
        # 2. Transcribe
        print("🎤 Starting transcription...")
        transcript = await transcriber_service.transcribe(temp_path)
        print(f"📝 Transcript: {transcript}")
        
        # 3. Reflect
        print("🤔 Starting reflection...")
        reflection_data = await reflector_service.reflect(transcript)
        print("✅ Reflection complete")
        
        return reflection_data

    except Exception as e:
        print(f"❌ Processing Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="The silence was too heavy.")
        
    finally:
        # 4. Cleanup (Crucial)
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"🗑️ Cleaned up: {temp_path}")
