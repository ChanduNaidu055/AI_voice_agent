class SessionMemory:
    def __init__(self):
        self.sessions = {}

    def update_context(self, session_id: str, key: str, value: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id][key] = value

    def get_context(self, session_id: str):
        return self.sessions.get(session_id, {})

    def clear_context(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]