from models.groq_client import GroqModel
import json

class Planner:
    @staticmethod
    def create_plan(user_input: str, context: dict):
        system_prompt = f"""
You are Sarthi's Planner Agent.

Context:
Location: {context['location']}, {context['state']}
Time: {context['time_mode']}
Intent: {context['intent']}

Return ONLY valid JSON:
{{
  "steps": ["step 1", "step 2"],
  "required_tools": []
}}

Available tools:
- weather
- place_info
- nearby_places

Rules:
- Use tools ONLY if needed
- For simple questions → no tools
- For tourism queries → use place_info or nearby_places
- For weather queries → use weather
- Keep required_tools minimal
"""

        try:
            response = GroqModel.generate(user_input, system_prompt)

            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]

            parsed = json.loads(json_str)

            # safety fallback
            if "required_tools" not in parsed:
                parsed["required_tools"] = []

            return parsed

        except Exception:
            lower = user_input.lower()

            # --- IMPROVED FALLBACK LOGIC (aligned with intent) ---
            intent = context.get("intent", "general")

            if intent == "real_time" and "weather" in lower:
                return {
                    "steps": ["Check current weather"],
                    "required_tools": ["weather"]
                }

            elif intent == "planning" and any(word in lower for word in ["visit", "place", "temple", "fort"]):
                return {
                    "steps": ["Get place information"],
                    "required_tools": ["place_info"]
                }

            else:
                # For question or general, no tools
                return {
                    "steps": ["Answer directly"],
                    "required_tools": []
                }