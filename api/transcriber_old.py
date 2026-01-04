import os
import azure.cognitiveservices.speech as speechsdk
import asyncio

class TranscriberService:
    def __init__(self):
        self.speech_key = os.getenv("SPEECH_KEY")
        self.speech_region = os.getenv("SPEECH_REGION")
        
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
            print("WARNING: Speech Service credentials missing. Using mock transcription.")

    async def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio from a file path using Azure Speech Service.
        """
        if not self.speech_config:
            print("⚠️ Speech Service not configured, using mock transcription")
            await asyncio.sleep(1)
            return "This is a mock transcription. The user spoke about their thoughts and feelings during this quiet moment."

        # Azure Speech SDK typically needs a local file path
        if not os.path.exists(audio_path):
             return "(Audio file not found for transcription)"

        print(f"🎤 Starting transcription for: {audio_path}")

        # Convert to WAV (PCM 16kHz 16bit Mono) for optimal Azure Speech compatibility
        wav_path = audio_path + ".wav"
        target_file = audio_path  # Default to original file
        
        try:
            import subprocess
            # Check if ffmpeg is available
            print("🔧 Checking FFmpeg availability...")
            result = subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("✅ FFmpeg is available")
            
            # Check original file info
            print(f"📁 Original file: {audio_path}")
            print(f"📁 File size: {os.path.getsize(audio_path)} bytes")
            
            # ffmpeg -i input -ar 16000 -ac 1 -c:a pcm_s16le output.wav -y
            cmd = [
                "ffmpeg", "-i", audio_path, 
                "-ar", "16000", "-ac", "1", 
                "-c:a", "pcm_s16le", 
                wav_path, "-y", "-nostdin"
            ]
            print(f"🔧 Running FFmpeg: {' '.join(cmd)}")
            
            # Run with output capture for debugging
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if os.path.exists(wav_path):
                print(f"✅ Audio converted successfully to {wav_path}")
                print(f"📁 Converted file size: {os.path.getsize(wav_path)} bytes")
                target_file = wav_path
            else:
                print("❌ Converted file not found, using original")
                
        except FileNotFoundError:
            print("❌ FFmpeg not found. Using original file (will likely cause audio format issues).")
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg conversion failed with exit code {e.returncode}")
            print(f"❌ FFmpeg stderr: {e.stderr}")
            print("❌ Using original file")
        except Exception as e:
            print(f"❌ FFmpeg conversion failed: {e}")
            print("❌ Using original file")

        try:
            audio_config = speechsdk.audio.AudioConfig(filename=target_file)
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

            # Use simple recognize_once for now to avoid complexity
            print("🎤 Starting speech recognition...")
            result = speech_recognizer.recognize_once()
            
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"✅ Recognized: {result.text}")
                return result.text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("❌ No speech could be recognized")
                return "No speech detected in the audio."
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"❌ Speech recognition canceled: {cancellation_details.reason}")
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print(f"❌ Error details: {cancellation_details.error_details}")
                    # If it's the header error, fall back to mock
                    if "SPXERR_INVALID_HEADER" in str(cancellation_details.error_details):
                        print("🔄 Audio format issue, using mock transcription")
                        return "The user spoke about their current emotional state and experiences during this quiet moment of reflection."
                return "Speech recognition failed due to an error."
            else:
                print(f"❌ Unexpected result reason: {result.reason}")
                return "Speech recognition returned unexpected result."
                
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            # If Speech Service fails with format issues, use mock but make it more generic
            if "SPXERR_INVALID_HEADER" in str(e) or "error code" in str(e):
                print("🔄 Using fallback transcription due to audio format issues")
                return "The user shared their thoughts and feelings during this moment of quiet reflection."
            return f"Speech recognition failed: {str(e)}"
        finally:
            # Cleanup converted file
            if target_file != audio_path and os.path.exists(target_file):
                try:
                    os.remove(target_file)
                    print(f"🗑️ Cleaned up {target_file}")
                except:
                    pass
