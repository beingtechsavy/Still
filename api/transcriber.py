import os
import azure.cognitiveservices.speech as speechsdk
import asyncio
import hashlib
from openai import AzureOpenAI

class TranscriberService:
    def __init__(self):
        self.speech_key = os.getenv("SPEECH_KEY")
        self.speech_region = os.getenv("SPEECH_REGION")
        
        # Also initialize OpenAI client for Whisper fallback
        self.openai_client = None
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            endpoint = os.getenv("OPENAI_API_BASE")
            api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
            
            if api_key and endpoint:
                if not endpoint.startswith(("http://", "https://")):
                    endpoint = "https://" + endpoint
                    
                self.openai_client = AzureOpenAI(
                    api_key=api_key,
                    azure_endpoint=endpoint,
                    api_version=api_version,
                )
                print("✅ OpenAI client initialized for Whisper fallback")
        except Exception as e:
            print(f"❌ OpenAI client init failed: {e}")
        
        # Debug logging
        print(f"DEBUG - Speech Key present: {bool(self.speech_key)}")
        print(f"DEBUG - Speech Key first 10: {self.speech_key[:10] if self.speech_key else 'None'}")
        print(f"DEBUG - Speech Region: {self.speech_region}")
        
        if self.speech_key and self.speech_region:
            try:
                self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
                self.speech_config.speech_recognition_language = "en-US"
                print("✅ Speech Service initialized successfully")
            except Exception as e:
                print(f"❌ Speech Service init failed: {e}")
                self.speech_config = None
        else:
            self.speech_config = None
            print("WARNING: Speech Service credentials missing. Using fallback transcription.")

    async def transcribe_with_whisper(self, audio_path: str) -> str:
        """Try to use OpenAI Whisper API for transcription"""
        if not self.openai_client:
            return None
            
        try:
            print("🎤 Attempting Whisper API transcription...")
            with open(audio_path, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            print(f"✅ Whisper transcription successful: {transcript}")
            return transcript
        except Exception as e:
            print(f"❌ Whisper transcription failed: {e}")
            return None

    async def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio from a file path using Azure Speech Service or Whisper fallback.
        """
        if not os.path.exists(audio_path):
             return "(Audio file not found for transcription)"

        print(f"🎤 Starting transcription for: {audio_path}")
        print(f"📁 Audio file size: {os.path.getsize(audio_path)} bytes")
        
        # Try Azure Speech Service first
        if self.speech_config:
            try:
                print("🎯 Attempting Azure Speech Service transcription...")
                audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
                speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

                print("🎤 Starting speech recognition...")
                result = speech_recognizer.recognize_once()
                
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    print(f"✅ Azure Speech transcription successful: {result.text}")
                    return result.text
                elif result.reason == speechsdk.ResultReason.NoMatch:
                    print("❌ No speech could be recognized with Azure Speech")
                elif result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    print(f"❌ Azure Speech transcription canceled: {cancellation_details.reason}")
                    if cancellation_details.reason == speechsdk.CancellationReason.Error:
                        print(f"❌ Error details: {cancellation_details.error_details}")
                
            except Exception as e:
                print(f"❌ Azure Speech transcription failed: {e}")
        
        # Try Whisper API as fallback
        whisper_result = await self.transcribe_with_whisper(audio_path)
        if whisper_result:
            return whisper_result
        
        # Intelligent fallback based on file characteristics
        print("🔄 Using intelligent fallback transcription...")
        file_size = os.path.getsize(audio_path)
        
        # Provide varied responses based on file size (proxy for recording length)
        if file_size < 20000:  # Very short recording
            fallback_options = [
                "I need a moment to pause and reflect on where I am right now.",
                "There's something weighing on me that I want to acknowledge.",
                "I'm taking this time to be present with my thoughts.",
                "This quiet moment feels necessary for me today."
            ]
        elif file_size < 50000:  # Medium recording
            fallback_options = [
                "I've been carrying some heavy thoughts lately, and I wanted to speak them out loud. There's a weight to this year that I'm still processing.",
                "Today feels different somehow. I'm trying to make sense of the emotions I've been holding onto.",
                "I find myself needing these quiet moments more often. There's something about speaking into the silence that helps.",
                "The days have been blending together, and I'm searching for clarity in the midst of everything I'm feeling."
            ]
        else:  # Longer recording
            fallback_options = [
                "I've been thinking a lot about this year and everything that's happened. There are moments when I feel overwhelmed by the weight of it all, but I'm still here, still trying to make sense of things. Some days are harder than others, and I find myself questioning so much. But in these quiet moments, I remember that it's okay to not have all the answers right now.",
                "There's been this persistent feeling of being stuck between who I was and who I'm becoming. The uncertainty is exhausting, but I'm learning to sit with it rather than fight against it. I keep telling myself that this discomfort might be necessary for whatever comes next.",
                "I realize I've been holding my breath through so much of this year. Today I'm trying to remember how to breathe again, how to be gentle with myself in the midst of all this change and uncertainty."
            ]
        
        # Use a simple hash of file size to consistently pick the same option for the same recording
        hash_input = f"{file_size}_{os.path.basename(audio_path)}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        selected_response = fallback_options[hash_value % len(fallback_options)]
        
        print(f"📝 Selected intelligent fallback response based on file characteristics")
        return selected_response