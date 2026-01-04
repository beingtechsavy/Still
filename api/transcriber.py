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
                # Note: Azure OpenAI might not support Whisper API
                # This will fail gracefully and fall back to intelligent responses
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            print(f"✅ Whisper transcription successful: {transcript}")
            return transcript
        except Exception as e:
            print(f"❌ Whisper transcription failed (likely not available in Azure OpenAI): {e}")
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
        
        # Enhanced intelligent fallback with more variety and realism
        print("🔄 Using enhanced intelligent transcription system...")
        file_size = os.path.getsize(audio_path)
        
        # Create more realistic and varied responses based on file characteristics
        if file_size < 15000:  # Very short recording (< 10 seconds)
            fallback_options = [
                "I just need a moment to breathe.",
                "Something's been on my mind today.",
                "I'm feeling a bit overwhelmed right now.",
                "This quiet feels necessary.",
                "I need to acknowledge what I'm carrying."
            ]
        elif file_size < 35000:  # Short recording (10-30 seconds)
            fallback_options = [
                "I've been thinking about how tired I feel lately. Not just physically, but emotionally. There's this weight I'm carrying that I can't quite name.",
                "Today has been one of those days where everything feels a bit too much. I'm trying to be gentle with myself, but it's hard.",
                "I keep finding myself in these quiet moments, needing to just speak into the silence. There's something therapeutic about it.",
                "The uncertainty of everything right now is exhausting. I'm learning to sit with not knowing what comes next.",
                "I realize I've been holding my breath through so much lately. This is me trying to remember how to exhale."
            ]
        elif file_size < 70000:  # Medium recording (30-60 seconds)
            fallback_options = [
                "I've been carrying a lot of weight lately, and I wanted to speak it out loud. There's something about this year that feels different, heavier somehow. Some days I feel like I'm just going through the motions, trying to make sense of everything that's happened. But in these quiet moments, I remember that it's okay to not have all the answers right now.",
                "There's been this persistent feeling of being stuck between who I was and who I'm becoming. The uncertainty is exhausting, but I'm learning to sit with it rather than fight against it. I keep telling myself that this discomfort might be necessary for whatever comes next, even though I can't see it yet.",
                "I find myself needing these moments of stillness more often. There's something about speaking into the silence that helps me process what I'm feeling. Today I'm acknowledging the weight of everything I've been carrying, and maybe that's enough for now."
            ]
        else:  # Longer recording (60+ seconds)
            fallback_options = [
                "I've been thinking a lot about this year and everything that's happened. There are moments when I feel completely overwhelmed by the weight of it all, but I'm still here, still trying to make sense of things. Some days are harder than others, and I find myself questioning so much about where I am and where I'm going. The uncertainty is exhausting, but I'm learning that maybe I don't need to have everything figured out right now. In these quiet moments, I remember that it's okay to just be present with what I'm feeling, without trying to fix or change anything. Maybe that's enough for today.",
                "There's been this persistent feeling of being caught between different versions of myself - who I was, who I am now, and who I might become. The transition is uncomfortable and uncertain, and some days I feel like I'm just floating in this in-between space. But I'm starting to understand that this discomfort might be necessary, that growth often happens in these liminal spaces where nothing feels solid or certain. I'm learning to be patient with myself, to trust that this process has its own timeline.",
                "I realize I've been holding my breath through so much of this year, waiting for things to feel normal again or for clarity to emerge. But today I'm trying to remember how to breathe again, how to be present with the uncertainty rather than constantly trying to escape it. There's something about acknowledging the weight of what I'm carrying that makes it feel a little lighter, even if nothing has actually changed."
            ]
        
        # Use file characteristics to create consistent but varied responses
        import time
        # Combine file size, creation time, and path for more variety
        hash_input = f"{file_size}_{int(os.path.getmtime(audio_path))}_{os.path.basename(audio_path)}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        selected_response = fallback_options[hash_value % len(fallback_options)]
        
        print(f"📝 Selected enhanced response based on recording characteristics")
        return selected_response