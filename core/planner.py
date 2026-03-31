from models.groq_client import GroqModel
import json

class Planner:
    @staticmethod
    def create_plan(user_input: str, context: dict):
        tourist_type = context.get("tourist_type", "general")
        budget = context.get("budget", "medium")
        intent = context.get("intent", "general")
        location = context.get("location", "Jaipur")

        system_prompt = f"""You are Sarthi's Planner for Rajasthan tourism.
Location: {location}
Tourist Type: {tourist_type}
Budget: {budget}
Intent: {intent}

Return ONLY valid JSON:
{{
  "steps": ["step 1", "step 2"],
  "required_tools": []
}}

Available tools: "weather", "place_info", "nearby_places", "search"

Rules:
- Use "weather" only if intent is real_time and weather is mentioned.
- Use "place_info" if the query asks about a specific place (e.g., "Patrika Gate", "Amer Fort", "Govind Devji Temple").
- Use "nearby_places" if the query asks for suggestions around a place.
- Use "search" for general queries not covered by other tools (e.g., "best kachori", "where to eat").
- Keep required_tools empty for simple questions that can be answered directly.
"""

        try:
            response = GroqModel.generate(user_input, system_prompt)
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            parsed = json.loads(json_str)
            if "required_tools" not in parsed:
                parsed["required_tools"] = []
            return parsed
        except Exception:
            # Fallback logic based on keywords
            lower = user_input.lower()
            # Detect place names
            place_keywords = ["amer", "city palace", "hawa mahal", "jal mahal", "patrika gate", "jantar mantar", "nahargarh", "jaigarh", "govind devji temple"]
            for place in place_keywords:
                if place in lower:
                    return {"steps": ["Get place info"], "required_tools": ["place_info"]}
            # Detect food queries
            food_keywords = ["food", "eat", "restaurant", "kachori", "lunch", "dinner", "best place to eat", "where to eat", "recommend"]
            if any(word in lower for word in food_keywords):
                return {"steps": ["Find recommendations"], "required_tools": ["search"]}
            # Detect weather
            if "weather" in lower:
                return {"steps": ["Check weather"], "required_tools": ["weather"]}
            # Nearby
            if "nearby" in lower:
                return {"steps": ["Find nearby places"], "required_tools": ["nearby_places"]}
            # Default
            return {"steps": ["Answer directly"], "required_tools": []}