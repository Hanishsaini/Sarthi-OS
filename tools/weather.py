import requests
from config import Config

class WeatherTool:
    @staticmethod
    def get(city: str = None):
        city = city or Config.DEFAULT_CITY
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={Config.OPENWEATHER_API_KEY}&units=metric"
        
        try:
            resp = requests.get(url).json()
            return {
                "temp": round(resp["main"]["temp"]),
                "condition": resp["weather"][0]["description"].title(),
                "humidity": resp["main"]["humidity"]
            }
        except:
            return {"temp": 32, "condition": "Sunny", "humidity": 40}