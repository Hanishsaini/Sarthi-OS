# Sarthi AI OS – Rajasthan Tourism Intelligence System

Sarthi is an AI-powered tourism decision engine designed to replace a human travel guide. It delivers **context‑aware, personalized, and optimized travel intelligence** in real time, focusing on Jaipur and Rajasthan.

Built with **Streamlit**, **Groq (or Ollama)**, **ChromaDB**, and **OpenWeatherMap**, Sarthi combines structured knowledge, external APIs, and intelligent planning to give you:

- **Real‑time weather** 🌦️  
- **Structured place information** 🏰  
- **Personalized recommendations** (based on tourist type and budget)  
- **Itinerary planning** with logical flow  
- **Search tool** for general queries (like “best kachori”)  
- **Memory** to remember past conversations

---

## 🚀 Features

- **Intent‑Aware Context Engine** – Detects user intent, tourist type, time of day, and extracts relative time phrases (e.g., “after one hour”).
- **Smart Planner** – Decides which tools to invoke (weather, place info, nearby places, search).
- **Real‑time Weather** – Fetches current weather from OpenWeatherMap.
- **Structured Knowledge Base** – Uses ChromaDB to store and retrieve detailed place information (e.g., timings, best time to visit, crowd level, nearby attractions).
- **Tool Registry** – Centralized tool management with error handling.
- **Personalization** – Adjusts recommendations based on tourist type (couple, family, solo) and budget (low/medium/high).
- **Memory** – Stores user interactions for continuity.
- **Clean Output** – Forces the model to follow a strict, guide‑like output format without fluff.

---

## 📁 Project Structure

```
sarthi-ai-os/
├── config.py                 # API keys and constants
├── main.py                   # Streamlit app entry point
├── core/
│   ├── context_engine.py     # Intent and tourist type detection
│   └── planner.py            # Tool selection logic
├── tools/
│   ├── weather.py            # OpenWeatherMap API wrapper
│   ├── tool_registry.py      # All available tools
├── rag/
│   ├── retriever.py          # ChromaDB retrieval with structured data
│   └── jaipur_data.txt       # Raw knowledge base (optional)
├── data/
│   └── places.json           # Structured place data (recommended)
├── memory/
│   └── user_memory.py        # Simple interaction memory
├── models/
│   └── groq_client.py        # Groq API client
└── requirements.txt
```

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sarthi-ai-os.git
   cd sarthi-ai-os
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API keys**  
   Edit `config.py` and add your OpenWeatherMap API key:
   ```python
   OPENWEATHER_API_KEY = "your_key_here"
   ```

5. **Prepare the knowledge base**  
   Create `data/places.json` with structured entries like:
   ```json
   [
     {
       "name": "Patrika Gate",
       "type": "gate",
       "best_time": "Evening for photography",
       "timings": "Always open",
       "crowd": "Moderate in evenings",
       "notes": "Modern landmark with intricate designs, good for photos",
       "nearby": ["Jawahar Circle", "Malviya Nagar"]
     }
   ]
   ```
   The system will automatically load this into ChromaDB on first run.

6. **Run the app**
   ```bash
   streamlit run main.py
   ```

---

## 🔧 Configuration

- **Model selection** – In the sidebar, choose between **Groq** (fast) or **Ollama** (local).  
- **Tourist Type** – General, Couple, Family, Solo – influences recommendations.  
- **Budget** – Low, Medium, High – filters suggestions.  
- **System Prompt** – Customize the assistant’s behavior (advanced).  
- **Clear / Export Chat** – Memory controls.

---

## 🧠 How It Works

1. **User inputs a query** – e.g., “Can I visit Patrika Gate after one hour?”
2. **Context Engine** analyses the query:  
   - Detects intent (`planning`, `question`, etc.)  
   - Recognises tourist type from keywords  
   - Parses relative time phrases  
   - Returns a context dict with time, location, etc.
3. **Planner** decides which tools to use based on intent and keywords (e.g., `place_info` for a specific place, `weather` for weather queries, `search` for general questions).
4. **Tool Registry** executes the chosen tools and returns structured data (weather JSON, place info dict, etc.).
5. **Retriever** searches the structured dataset (ChromaDB) for the most relevant place information.
6. **Final prompt** is built with all gathered data and strict output rules.
7. **LLM (Groq/Ollama)** generates a response following the format:  
   - Direct Answer  
   - Visit Insight  
   - Place Highlights  
   - Smart Tips  
   - Nearby Flow  
8. **Response is displayed and stored** in session memory.

---

## 🌟 Example Interactions

| User Query | Response |
|------------|----------|
| *“What is the weather in Jaipur today?”* | Direct Answer: 32°C, thunderstorm. Visit Insight: Consider indoor activities... |
| *“Can I visit Patrika Gate after one hour?”* | Uses place_info to retrieve timings and notes, then gives advice based on current time. |
| *“Plan a day for me in Jaipur”* | Builds an itinerary with logical flow, respecting tourist type and budget. |
| *“Best place to eat kachori?”* | Triggers the `search` tool, which uses the LLM’s knowledge (or future search API) to recommend local spots. |

---

## 🧪 Future Enhancements

- **Google Places API** – real‑time place details (ratings, hours, photos)  
- **Search API** – for up‑to‑date food and event recommendations  
- **Traffic / Navigation** – integrate with Google Maps Directions  
- **Multilingual Support** – Hindi/English  
- **Voice Input** – for a more natural interaction  

---

## 📄 License

MIT © [HANIHS SAINI]

---

## 🙌 Acknowledgements

- [Streamlit](https://streamlit.io/) – for the UI framework  
- [Groq](https://groq.com/) – for fast inference  
- [Ollama](https://ollama.ai/) – for local LLMs  
- [ChromaDB](https://www.trychroma.com/) – for vector search  
- [OpenWeatherMap](https://openweathermap.org/) – for weather data  

---

Feel free to contribute! Open an issue or pull request for any improvements.
