import json
from datetime import datetime
from config import Config

class UserMemory:
    def __init__(self):
        self.file = "memory/user_profile.json"
        self.load()
    
    def load(self):
        try:
            with open(self.file) as f:
                self.data = json.load(f)
        except:
            self.data = {
                "preferences": {"style": "helpful and concise"},
                "habits": {},
                "history": [],
                "last_interaction": None
            }
    
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def add_interaction(self, user_input: str, response: str):
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input[:200],
            "response": response[:300]
        })
        self.data["last_interaction"] = datetime.now().isoformat()
        self.save()
    
    def get_context(self) -> str:
        if self.data["history"]:
            return f"User prefers {self.data['preferences']['style']} responses."
        return ""