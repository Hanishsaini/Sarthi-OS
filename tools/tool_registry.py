from tools.weather import WeatherTool
from rag.retriever import Retriever
from models.groq_client import GroqModel

_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever

def get_place_info(place: str = "Jaipur"):
    retriever = get_retriever()
    result = retriever.retrieve(place, n_results=1)
    if result:
        # Return structured text for LLM to use
        return f"""Name: {result['name']}
Type: {result['type']}
Best Time: {result['best_time']}
Timings: {result['timings']}
Crowd: {result.get('crowd', 'Varies')}
Notes: {result['notes']}
Nearby: {', '.join(result.get('nearby', []))}"""
    else:
        return f"No detailed information about {place} in the dataset."

def get_nearby_places(location: str = "Jaipur"):
    # Use the retriever to find places near a given location
    # For simplicity, we'll return a static list for now.
    # You can expand this to query the retriever with "nearby + location"
    location = location.lower()
    if "amer" in location:
        return "Jaigarh Fort, Nahargarh Fort, Panna Meena ka Kund"
    if "hawa mahal" in location:
        return "City Palace, Jantar Mantar, Johari Bazaar"
    if "jal mahal" in location:
        return "Amer Fort, Nahargarh Fort, Kanak Vrindavan Garden"
    return "City Palace, Jantar Mantar, Hawa Mahal"

def search(query: str):
    # Fallback for questions not covered by other tools
    try:
        return GroqModel.generate(query, system_prompt="Answer concisely and factually. If unsure, say 'I don't know.'")
    except:
        return "Unable to search at the moment."

class ToolRegistry:
    tools = {
        "weather": WeatherTool.get,
        "get_weather": WeatherTool.get,
        "place_info": get_place_info,
        "nearby_places": get_nearby_places,
        "search": search,
    }

    @staticmethod
    def execute(tool_name: str, **kwargs):
        tool_func = ToolRegistry.tools.get(tool_name.lower())
        if tool_func:
            try:
                return tool_func(**kwargs)
            except Exception as e:
                return f"Error in {tool_name}: {e}"
        return f"Unknown tool: {tool_name}"