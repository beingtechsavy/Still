import os
import azure.cognitiveservices.speech as speechsdk
import asyncio

class TranscriberService:
    def __init__(self):
        self.speech_key = os.getenv("SPEECH_KEY")
        self.speech_region = os.getenv("SPEECH_REGION")
        
        if self.speech_key and self.speech_region:
            self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
            self.speech_config.speech_recognition_language = "en-US" # Default for now, can support auto-detect
        else:
            self.speech_config = None
            print("WARNING: Speech Service credentials missing. Using mock transcription.")

    async def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio from a file path (or URL if supported, but typically file).
        """
        if not self.speech_config:
            await asyncio.sleep(2)
            return "This is a mock transcription. The user spoke about feeling tired but hopeful."

        # Azure Speech SDK typically needs a local file path
        # If audio_path is a URL, we might need to download it first or use a stream.
        # For MVP, we assume the temp file is locally accessible (or downloaded).
        # Since we are deploying to container/local, we might need to ensure the blob is downloaded to a temp file first.
        
        # NOTE: For simplicity, we will assume 'storage.py' saved it to a local temp path if using mock,
        # or we download the blob to a temp file here.
        # Let's handle the simple case: audio_path is a local path.
        
        if not os.path.exists(audio_path):
             return "(Audio file not found for transcription)"

        # Convert to WAV (PCM 16kHz 16bit Mono) for optimal Azure Speech compatibility
        # We know ffmpeg is available.
        wav_path = audio_path + ".wav"
        try:
            import subprocess
            # ffmpeg -i input -ar 16000 -ac 1 -c:a pcm_s16le output.wav -y
            # -y to overwrite if exists, -nostdin to prevent hanging
            cmd = [
                "ffmpeg", "-i", audio_path, 
                "-ar", "16000", "-ac", "1", 
                "-c:a", "pcm_s16le", 
                wav_path, "-y", "-nostdin"
            ]
            # Run silently
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Use the converted WAV file
            target_file = wav_path
        except Exception as e:
            print(f"FFmpeg conversion failed: {e}. Trying original file.")
            target_file = audio_path

        audio_config = speechsdk.audio.AudioConfig(filename=target_file)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config)

        # Future-proofing: use recognize_once_async for short clips (<15s) or continuous for longer.
        # 90s clips require continuous recognition or a robust single-shot.
        # 'recognize_once' cuts off after silence. We want the full 90s.
        
        done = asyncio.Event()
        transcript = []

        def stop_cb(evt):
            speech_recognizer.stop_continuous_recognition()
            done.set()

        def recognized_cb(evt):
            if evt.result.text:
                transcript.append(evt.result.text)

        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        speech_recognizer.start_continuous_recognition()
        
        # Wait until done or timeout (safeguard)
        try:
            await asyncio.wait_for(done.wait(), timeout=100) # 100s timeout for 90s audio
        except asyncio.TimeoutError:
            speech_recognizer.stop_continuous_recognition()
            
        # Cleanup converted file
        if target_file != audio_path and os.path.exists(target_file):
            try:
                os.remove(target_file)
            except:
                pass

        return " ".join(transcript)
