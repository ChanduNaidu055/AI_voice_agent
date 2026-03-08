import edge_tts
import tempfile
import os

async def generate_audio(text: str, language: str) -> str:
    voices = {
        "English": "en-US-AriaNeural",
        "Hindi": "hi-IN-SwaraNeural",
        "Tamil": "ta-IN-PallaviNeural",
        "Telugu": "te-IN-ShrutiNeural" 
    }
    
    voice = voices.get(language, "en-US-AriaNeural")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_path = temp_file.name
    temp_file.close()

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(temp_path)
    return temp_path