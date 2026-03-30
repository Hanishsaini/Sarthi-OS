from groq import Groq
from config import Config

groq_client = Groq(api_key=Config.GROQ_API_KEY)

class GroqModel:
    @staticmethod
    def generate(prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = groq_client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content