import sqlite3
from datetime import datetime

class AppointmentService:
    def __init__(self):
        self.conn = sqlite3.connect('clinic.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._seed_doctors()

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                specialty TEXT UNIQUE,
                available_slots TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                specialty TEXT,
                time TEXT,
                booked_at TEXT
            )
        ''')
        self.conn.commit()

    def _seed_doctors(self):
        self.cursor.execute("SELECT COUNT(*) FROM Doctors")
        if self.cursor.fetchone()[0] == 0:
            doctors_data = [
                ("Cardiologist", "10:00 AM, 02:00 PM, 04:00 PM"),
                ("Dentist", "09:00 AM, 11:00 AM, 03:00 PM"),
                ("Dermatologist", "01:00 PM, 04:30 PM")
            ]
            self.cursor.executemany(
                "INSERT INTO Doctors (specialty, available_slots) VALUES (?, ?)", 
                doctors_data
            )
            self.conn.commit()

    def get_available_slots(self, specialty: str):
        self.cursor.execute("SELECT available_slots FROM Doctors WHERE specialty = ?", (specialty,))
        result = self.cursor.fetchone()
        return result[0].split(", ") if result else []

    def book_slot(self, specialty: str, time: str, patient_id: str):
        self.cursor.execute(
            "SELECT id FROM Appointments WHERE specialty = ? AND time = ?", 
            (specialty, time)
        )
        if self.cursor.fetchone():
            return {"success": False, "message": "Slot already taken."}
        
        now = str(datetime.now())
        self.cursor.execute(
            "INSERT INTO Appointments (patient_id, specialty, time, booked_at) VALUES (?, ?, ?, ?)",
            (patient_id, specialty, time, now)
        )
        self.conn.commit()
        return {"success": True, "message": f"Confirmed for {time}."}