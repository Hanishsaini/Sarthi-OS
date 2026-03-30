from tools.weather import WeatherTool

# --- MOCK TOURISM TOOLS (can upgrade later to APIs) ---
def get_place_info(place: str = "Jaipur"):
    return f"""
{place.title()} is a major tourist attraction in Rajasthan.

It is known for:
- Historical significance
- Cultural heritage
- Architectural beauty

Best visited during morning or evening hours.
"""

def get_nearby_places(location: str = "Jaipur"):
    location = location.lower()

    if "amer" in location:
        return "Jaigarh Fort, Nahargarh Fort, Panna Meena ka Kund"

    if "hawa mahal" in location:
        return "City Palace, Jantar Mantar, Johari Bazaar"

    if "jal mahal" in location:
        return "Amer Fort, Nahargarh Fort, Kanak Vrindavan Garden"

    # Default fallback
    return "City Palace, Jantar Mantar, Hawa Mahal"

class ToolRegistry:
    tools = {
        "weather": WeatherTool.get,
        "get_weather": WeatherTool.get,

        # --- TOURISM TOOLS ---
        "place_info": get_place_info,
        "nearby_places": get_nearby_places,
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