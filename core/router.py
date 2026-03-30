from config import Config

class Router:
    @staticmethod
    def decide(context: dict) -> str:
        intent = context.get("intent", "general")
        
        if intent in ["weather", "news"]:
            return "tools"           # Use real APIs
        elif intent == "planning":
            return "complex"         # Use Groq / strong model
        else:
            return "local"           # Fast local Ollama