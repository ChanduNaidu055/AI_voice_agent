import os
import asyncio
import re
from google import genai
from google.genai import types
from memory.session_store import SessionMemory
from services.appointment_service import AppointmentService
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
memory = SessionMemory()

class HealthAgent:
    def __init__(self):
        
        self.db = AppointmentService()
        
        self.system_prompt = """You are a 2Care.ai Medical Assistant.
        Available Doctors & Times:
        - Cardiologist: 10:00 AM, 02:00 PM, 04:00 PM
        - Dentist: 09:00 AM, 11:00 AM, 03:00 PM
        - Dermatologist: 01:00 PM, 04:30 PM
        
        STRICT LANGUAGE RULES:
        1. If user speaks Hindi -> Reply ONLY in Hindi Devanagari script.
        2. If user speaks Tamil -> Reply ONLY in Tamil script.
        3. If user speaks Telugu -> Reply ONLY in Telugu script.
        4. NEVER use English alphabets in regional responses.
        5. Translate 'Doctor', 'Appointment', and 'AM/PM' into the regional script.
        6. When booking is finished, you MUST include a confirmation word like 'Confirmed' or 'Booked' in the native script.
        7. Keep replies very short (under 15 words)."""

    async def process_request(self, text: str, language: str, session_id: str):
        try:
            response = await client.aio.models.generate_content(
                model='models/gemini-flash-latest',
                contents=f"User language: {language}. Respond in {language} script ONLY: {text}",
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.2,
                )
            )
            
            reply = response.text
            
            booking_keywords = ["बुक", "பதிவு", "బుక్", "confirmed", "booked", "confirm"]
            if any(word in reply.lower() or word in text.lower() for word in booking_keywords):
                
                specialty = "General"
                t_low = text.lower()
                if "cardio" in t_low or "हृदय" in t_low or "இதயம்" in t_low: specialty = "Cardiologist"
                elif "dentist" in t_low or "दांत" in t_low or "பல்" in t_low: specialty = "Dentist"
                elif "derma" in t_low or "त्वचा" in t_low or "தோல்" in t_low: specialty = "Dermatologist"
                
                time_match = re.search(r'\d{1,2}', text)
                time_val = f"{time_match.group()}:00" if time_match else "10:00 AM"
                
                db_result = self.db.book_slot(specialty, time_val, session_id)
                print(f"--- DB STATUS: {db_result['message']} ---")

            return {"reply": reply}
            
        except Exception as e:
            error_msg = str(e)
            print(f"Orchestrator Error: {error_msg}")
            
            if "429" in error_msg:
                return {"reply": "I am a bit tired! Please wait 20 seconds, and speak again."}
            
            return {"reply": "Sorry, I am having trouble connecting! Please try again."}