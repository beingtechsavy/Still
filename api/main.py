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
    if not file:
        raise HTTPException(status_code=400, detail="No audio file provided")

    # 1. Save temp file (local or blob)
    # For transcription via SDK, a local file is safest/easiest.
    # We will use a local /tmp dir for processing, then upload to blob if we wanted archivals (but we don't).
    # Actually, the architecture says: Blob Storage -> Transcribe -> Delete.
    # Let's follow the architecture: Upload to Blob -> Get SAS/Path -> Transcribe (downloading if needed) -> Delete.
    
    # However, Azure Speech SDK often wants a local file path.
    # Hybrid approach for performance: 
    #   a. Save to local temp (fast validation)
    #   b. Transcribe
    #   c. Upload to Blob (just to prove we can, or skip if we strictly follow "Nothing persists")
    #   d. The prompt says "Store temporaily in memory or temp storage... Delete immediately".
    #   e. Azure Blob was recommended for "Temp Storage".
    
    filename = f"audio_{os.urandom(4).hex()}.webm"
    temp_path = f"temp_{filename}"
    
    try:
        # Save locally for processing
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Optional: Upload to blob (as per architecture requirement 4.4)
        # This acts as the "Temp Storage" before processing if we had async workers.
        # Since we are synchronous here, we might just use the local file.
        # But let's use the service to show we built it.
        # with open(temp_path, "rb") as f:
        #     blob_url = await storage_service.upload_audio(f.read(), filename)
        
        # 2. Transcribe
        transcript = await transcriber_service.transcribe(temp_path)
        print(f"Transcript: {transcript}")
        
        # 3. Reflect
        reflection_data = await reflector_service.reflect(transcript)
        
        return reflection_data

    except Exception as e:
        print(f"Processing Error: {e}")
        raise HTTPException(status_code=500, detail="The silence was too heavy.")
        
    finally:
        # 4. Cleanup (Crucial)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        # If we uploaded to blob, delete it too
        # await storage_service.delete_audio(filename)
