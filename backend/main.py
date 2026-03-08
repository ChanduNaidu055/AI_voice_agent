import json
import base64
import os
import time
import re
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

try:
    from agent.orchestrator import HealthAgent
    from services.tts_service import generate_audio
    from services.stt_service import STTService
except Exception as e:
    print(f"ERROR LOADING SERVICES: {e}")
    exit(1) 

app = FastAPI()
agent = HealthAgent()
stt_service = STTService()

def identify_language(text):
    if re.search(r'[\u0900-\u097F]', text): return "Hindi"
    if re.search(r'[\u0B80-\u0BFF]', text): return "Tamil"
    if re.search(r'[\u0C00-\u0C7F]', text): return "Telugu"
    text_lower = text.lower()
    if any(w in text_lower for w in ["namaste", "kaise"]): return "Hindi"
    if any(w in text_lower for w in ["vanakkam", "eppadi"]): return "Tamil"
    if any(w in text_lower for w in ["namaskaram", "ela"]): return "Telugu"
    return "English"

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(time.time())
    print(f"New session started: {session_id}")
    try:
        while True:
            data = await websocket.receive()
            user_text = ""
            if "text" in data:
                msg = json.loads(data["text"])
                user_text = msg.get("content", "")
            elif "bytes" in data:
                temp_file = f"temp_{session_id}.webm"
                with open(temp_file, "wb") as f:
                    f.write(data["bytes"])
                user_text = await stt_service.transcribe_audio(temp_file)
                if os.path.exists(temp_file): os.remove(temp_file)

            if user_text:
                lang = identify_language(user_text)
                print(f"Patient ({lang}): {user_text}")
                agent_res = await agent.process_request(user_text, lang, session_id)
                reply_text = agent_res['reply']
                
                audio_path = await generate_audio(reply_text, lang)
                with open(audio_path, "rb") as f:
                    audio_base64 = base64.b64encode(f.read()).decode('utf-8')
                if os.path.exists(audio_path): os.remove(audio_path)

                await websocket.send_text(json.dumps({
                    "text": reply_text,
                    "audio": audio_base64
                }))
    except Exception as e:
        print(f"Session ended or Error: {e}")

if __name__ == "__main__":
    print("Starting 2Care.ai Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)