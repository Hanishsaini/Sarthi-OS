from datetime import datetime
from config import Config

class ContextEngine:
    @staticmethod
    def analyze(user_input: str):
        now = datetime.now()
        hour = now.hour
        input_lower = user_input.lower()

        # --- INTENT DETECTION (mutually exclusive) ---
        intent = "general"

        # 1. Navigation
        if any(word in input_lower for word in ["directions", "how to reach", "navigate", "route to", "driving"]):
            intent = "navigation"

        # 2. Real-time (weather, news)
        elif any(word in input_lower for word in ["weather", "temperature", "rain", "forecast", "hot", "cold", "news", "update"]):
            intent = "real_time"

        # 3. Task execution (book, order, reminder)
        elif any(word in input_lower for word in ["book", "order", "set reminder", "remind me"]):
            intent = "task_execution"

        # 4. Question (yes/no, advice)
        elif any(q in input_lower for q in ["can i", "should i", "is it good", "is it safe", "what is", "tell me about"]):
            intent = "question"

        # 5. Planning (itinerary, schedule, trip)
        elif any(word in input_lower for word in ["plan", "schedule", "trip", "itinerary", "day", "how to cover", "visit", "go to", "place", "tour", "temple", "fort", "palace", "attraction"]):
            intent = "planning"

        # 6. Specific place query (single place)
        if "place" in intent:  # if we had a separate category, but we'll merge into planning
            pass

        # --- TOURIST TYPE DETECTION ---
        tourist_type = "general"
        if any(word in input_lower for word in ["wife", "girlfriend", "boyfriend", "partner", "couple", "romantic"]):
            tourist_type = "couple"
        elif any(word in input_lower for word in ["kids", "children", "family", "with child"]):
            tourist_type = "family"
        elif any(word in input_lower for word in ["alone", "solo", "myself"]):
            tourist_type = "solo"

        # --- TIME MODE ---
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
            "user_type": "tourist",
            "tourist_type": tourist_type
        }