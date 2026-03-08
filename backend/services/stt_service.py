import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

class STTService:
    async def transcribe_audio(self, audio_file_path: str):
        try:
            with open(audio_file_path, "rb") as file:
                transcription = await client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
                return transcription
        except Exception as e:
            print(f"STT Error: {e}")
            return ""