from datetime import datetime
from config import Config

class ContextEngine:
    @staticmethod
    def analyze(user_input: str):
        now = datetime.now()
        hour = now.hour
        input_lower = user_input.lower()

        # --- IMPROVED INTENT DETECTION (aligned with main app) ---
        if any(q in input_lower for q in ["can i", "should i", "is it good", "is it safe"]):
            intent = "question"

        elif any(word in input_lower for word in ["plan", "schedule", "trip", "itinerary", "day"]):
            intent = "planning"

        elif any(word in input_lower for word in ["weather", "temperature", "rain", "forecast", "hot", "cold"]):
            intent = "real_time"          # weather is real-time

        elif any(word in input_lower for word in ["directions", "route", "how to reach", "navigate"]):
            intent = "real_time"          # navigation also real-time

        elif any(word in input_lower for word in ["book", "order", "set reminder", "remind me"]):
            intent = "task_execution"

        elif any(word in input_lower for word in ["visit", "go to", "nearby", "place", "tour", "temple", "fort", "palace"]):
            intent = "planning"           # tourism → planning

        elif any(word in input_lower for word in ["news", "update", "happening"]):
            intent = "real_time"          # news is real-time

        else:
            intent = "general"

        # --- TIME MODE (unchanged) ---
        if 5 <= hour < 12:
            time_mode = "morning"
        elif 12 <= hour < 17:
            time_mode = "afternoon"
        elif 17 <= hour < 22:
            time_mode = "evening"
        else:
            time_mode = "night"

        return {
            "location": Config.DEFAULT_CITY,
            "state": Config.STATE,
            "time_mode": time_mode,
            "intent": intent,
            "hour": hour,
            "user_type": "tourist"
        }