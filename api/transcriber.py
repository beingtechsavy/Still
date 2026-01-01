import os
import azure.cognitiveservices.speech as speechsdk
import asyncio

class TranscriberService:
    def __init__(self):
        self.speech_key = os.getenv("SPEECH_KEY")
        self.speech_region = os.getenv("SPEECH_REGION")
        
        # Debug logging
        print(f"DEBUG - Speech Key present: {bool(self.speech_key)}")
        print(f"DEBUG - Speech Region: {self.speech_region}")
        
        if self.speech_key and self.speech_region:
            try:
                self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
                self.speech_config.speech_recognition_language = "en-US" # Default for now, can support auto-detect
                print("✅ Speech Service initialized successfully")
            except Exception as e:
                print(f"❌ Speech Service init failed: {e}")
                self.speech_config = None
        else:
            self.speech_config = None
            print("WARNING: Speech Service credentials missing. Using mock transcription.")

    async def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio from a file path (or URL if supported, but typically file).
        """
        # Temporary: Use mock transcription to test the OpenAI pipeline
        print("🔄 Using mock transcription for testing")
        await asyncio.sleep(1)  # Simulate processing time
        return "I've been carrying a lot of weight lately, feeling tired but trying to stay hopeful. Some days are harder than others, but I'm still here, still trying."
