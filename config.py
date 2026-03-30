import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Models
    LOCAL_MODEL = "qwen2.5:14b"      # Change to 7b if your machine is weaker
    GROQ_MODEL = "llama-3.3-70b-versatile"
    
    # Rajasthan context
    DEFAULT_CITY = "Jaipur"
    STATE = "Rajasthan"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")