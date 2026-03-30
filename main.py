import streamlit as st
from typing import Dict, List, Optional, Any
import logging
import concurrent.futures
from datetime import datetime
import traceback

# Internal imports
from config import Config
from core.context_engine import ContextEngine
from core.router import Router
from core.planner import Planner
from core.critic import Critic
from tools.tool_registry import ToolRegistry
from models.groq_client import GroqModel
from memory.user_memory import UserMemory
from rag.retriever import Retriever
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Sarthi AI OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CONSTANTS ====================
DEFAULT_SYSTEM_PROMPT = "You are Sarthi, a helpful, concise, and intent-aware AI assistant."
MAX_HISTORY_LENGTH = 20
TOOL_EXECUTION_TIMEOUT = 10  # seconds

# ==================== CACHED RESOURCES ====================
@st.cache_resource
def get_tool_registry():
    """Initialize tool registry once."""
    return ToolRegistry()

@st.cache_resource
def get_retriever():
    """Initialize retriever once."""
    return Retriever()

# ==================== SESSION STATE INITIALIZATION ====================
def init_session_state():
    """Initialize all session state variables."""
    if "memory" not in st.session_state:
        st.session_state.memory = UserMemory()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "groq"  # or "ollama"
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "last_response_id" not in st.session_state:
        st.session_state.last_response_id = None
    # Add tourist type and budget to session state (can be set by user later)
    if "tourist_type" not in st.session_state:
        st.session_state.tourist_type = "general"
    if "budget" not in st.session_state:
        st.session_state.budget = "medium"

# ==================== UI COMPONENTS ====================
def render_sidebar():
    """Render the sidebar with controls and settings."""
    with st.sidebar:
        st.header("⚙️ Sarthi Controls")

        # Model selection
        model_choice = st.selectbox(
            "Model",
            options=["groq", "ollama"],
            index=0 if st.session_state.selected_model == "groq" else 1,
            help="Choose the underlying LLM."
        )
        st.session_state.selected_model = model_choice

        # Tourist type and budget controls
        st.subheader("👤 Traveler Profile")
        tourist_type = st.selectbox(
            "Tourist Type",
            options=["general", "couple", "family", "solo"],
            index=["general", "couple", "family", "solo"].index(st.session_state.tourist_type)
        )
        st.session_state.tourist_type = tourist_type

        budget = st.select_slider(
            "Budget",
            options=["low", "medium", "high"],
            value=st.session_state.budget
        )
        st.session_state.budget = budget

        # System prompt customization
        new_system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.system_prompt,
            height=100,
            help="Customize Sarthi's behavior."
        )
        if new_system_prompt != st.session_state.system_prompt:
            st.session_state.system_prompt = new_system_prompt
            st.rerun()

        # Memory controls
        st.subheader("💾 Memory")
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.session_state.memory.clear()
            st.rerun()

        if st.button("Export Chat"):
            export_chat()

        st.markdown("---")
        st.caption(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

def export_chat():
    """Export chat history to a text file."""
    if not st.session_state.messages:
        st.warning("No messages to export.")
        return

    chat_text = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in st.session_state.messages
    )
    st.download_button(
        label="📥 Download Chat",
        data=chat_text,
        file_name=f"sarthi_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def render_chat_messages():
    """Display all chat messages from session state."""
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and idx == len(st.session_state.messages) - 1:
                # Add feedback buttons for the last assistant message
                col1, col2 = st.columns([0.1, 0.1])
                with col1:
                    if st.button("👍", key=f"thumbs_up_{idx}"):
                        st.session_state.feedback[st.session_state.last_response_id] = "positive"
                        st.success("Thanks for your feedback!")
                with col2:
                    if st.button("👎", key=f"thumbs_down_{idx}"):
                        st.session_state.feedback[st.session_state.last_response_id] = "negative"
                        st.warning("We'll improve. Thanks for the feedback!")

def daily_briefing():
    """Fetch and display a personalized daily briefing."""
    if st.button("🌅 Get Today's Daily Briefing", use_container_width=True):
        with st.spinner("Preparing your briefing..."):
            # Personalize using user memory (if available)
            user_context = ""
            try:
                recent = st.session_state.memory.get_recent(3)
                if recent:
                    user_context = "Based on your recent conversations: " + " ".join(recent)
            except Exception as e:
                logger.warning(f"Could not retrieve memory for briefing: {e}")

            prompt = f"""Create a warm, concise daily briefing for a student in Jaipur right now.
            Include weather, motivational tip, and a quick productivity hack.
            {user_context}
            """
            try:
                briefing = generate_response(prompt, system_prompt="You are Sarthi, a helpful assistant.")
                st.success(briefing)
            except Exception as e:
                st.error(f"Failed to generate briefing: {e}")
                logger.error(traceback.format_exc())

# ==================== CORE FUNCTIONS ====================
def generate_response(prompt: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> str:
    """Generate a response using the selected model."""
    if st.session_state.selected_model == "groq":
        try:
            return GroqModel.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.error(f"Groq model failed: {e}, falling back to ollama.")
            st.warning("Groq model unavailable. Using fallback model.")
            response = ollama.chat(
                model="phi4-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
    else:
        try:
            response = ollama.chat(
                model="phi4-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama model failed: {e}")
            st.error("Both models failed. Please check your configuration.")
            return "I'm sorry, I'm having trouble connecting to my language model. Please try again later."

def execute_tools(tools: List[str]) -> str:
    """Execute multiple tools concurrently with timeout."""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tools)) as executor:
        future_to_tool = {executor.submit(ToolRegistry.execute, tool): tool for tool in tools}
        for future in concurrent.futures.as_completed(future_to_tool, timeout=TOOL_EXECUTION_TIMEOUT):
            tool = future_to_tool[future]
            try:
                result = future.result()
                results.append(f"🔧 {tool.upper()}: {result}")
            except Exception as e:
                results.append(f"❌ {tool.upper()} failed: {str(e)}")
                logger.error(f"Tool {tool} execution error: {e}")
    return "\n\n".join(results) if results else "No tools executed."

def detect_mode(intent: str) -> str:
    """Determine response mode based on intent."""
    if intent in ["question"]:
        return "answer"
    elif intent in ["planning"]:
        return "plan"
    elif intent in ["task_execution", "real_time"]:
        return "execute"
    return "answer"

def build_full_prompt(user_input: str, context: dict, mode: str, tool_results: str, rag_context: str, memory_context: str) -> str:
    """Construct the final prompt with personalization and strict output rules."""
    # Extract personalization fields
    tourist_type = context.get('tourist_type', st.session_state.tourist_type)
    budget = context.get('budget', st.session_state.budget)
    time_mode = context.get('time_mode', 'day')
    location = context.get('location', Config.DEFAULT_CITY)

    return f"""
User Query: {user_input}

Context:
- Tourist Type: {tourist_type}
- Budget: {budget}
- Time: {time_mode}
- Location: {location}

Tool Results:
{tool_results}

Knowledge:
{rag_context}

Instructions:

You are Sarthi — Rajasthan Tourism Intelligence System.

You generate highly personalized travel guidance.

PERSONALIZATION RULES:

- Couple → romantic, scenic, peaceful places
- Family → safe, comfortable, less walking
- Solo → exploration, offbeat, flexible
- Budget low → cheap transport, free places
- Budget high → premium experiences

OUTPUT:

1. Direct Answer
2. Visit Insight (based on user type)
3. Place Highlights
4. Smart Tips (budget-aware)
5. Smart Plan / Flow (STRICT RULES):

- Only include 3–4 places max
- Each place must have a purpose
- No unnecessary explanations
- Route must be logical (distance-wise)
- Prioritize experience over quantity

Format:

1. Place + Time
2. Place + Time
3. Place + Time
4. Optional (only if valuable)

AVOID these fluff words:
- "stroll"
- "enjoy"
- "beautiful"
- "stunning"
- "memorable"

Instead:
- Be specific
- Be actionable
- Be direct

Before generating response, think step-by-step:

1. What is the user type?
2. What is the goal?
3. What is the minimum number of places required?
4. What is the optimal route?
5. What should be removed?

Then generate final response.
"""

def process_user_input(prompt: str) -> str:
    """Process user input through the full pipeline with upgrades."""
    # 1. Context analysis
    try:
        context = ContextEngine.analyze(prompt)
        intent = context.get("intent", "general")
    except Exception as e:
        logger.error(f"Context analysis failed: {e}")
        intent = "general"
        context = {}

    # 2. Inject tourist type and budget into context from session state
    context['tourist_type'] = st.session_state.tourist_type
    context['budget'] = st.session_state.budget

    # 3. Determine response mode
    mode = detect_mode(intent)

    # 4. Planning (only if needed)
    try:
        plan = Planner.create_plan(prompt, context)
        if intent in ["real_time", "weather", "navigation", "planning", "task_execution"]:
            required_tools = plan.get("required_tools", [])
        else:
            required_tools = []
    except Exception as e:
        logger.error(f"Planning failed: {e}")
        required_tools = []

    # 5. Tool execution
    tool_results = ""
    if required_tools:
        with st.status(f"Executing {len(required_tools)} tools...", expanded=False) as status:
            tool_results = execute_tools(required_tools)
            status.update(label="Tools executed", state="complete")

    # 6. RAG retrieval
    rag_text = ""
    try:
        retriever = get_retriever()
        rag_text = retriever.retrieve(prompt)
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")

    # 7. Memory injection
    memory_context = ""
    try:
        recent = st.session_state.memory.get_recent(3)
        if recent:
            memory_context = " ".join(recent)
    except Exception as e:
        logger.warning(f"Memory retrieval failed: {e}")

    # 8. Build final prompt (using full context)
    full_prompt = build_full_prompt(prompt, context, mode, tool_results, rag_text, memory_context)

    # 9. Model generation
    try:
        raw_response = generate_response(full_prompt, st.session_state.system_prompt)
    except Exception as e:
        logger.error(f"Model generation failed: {e}")
        raw_response = "I encountered an error while generating a response. Please try again."

    # 10. Validation
    try:
        final_output = Critic.validate(raw_response)
    except Exception as e:
        logger.warning(f"Critic validation failed: {e}")
        final_output = raw_response

    return final_output

# ==================== MAIN APP ====================
def main():
    """Main Streamlit app."""
    init_session_state()
    render_sidebar()

    st.title("🛡️ Sarthi AI OS")
    st.caption("Intent-Aware • Tool-Augmented • AI OS")

    daily_briefing()
    render_chat_messages()

    if prompt := st.chat_input("What should Sarthi do for you today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Sarthi is thinking..."):
                try:
                    response = process_user_input(prompt)
                except Exception as e:
                    logger.error(f"Unexpected error in processing: {e}")
                    response = "An unexpected error occurred. Please try again later."

                st.session_state.memory.add_interaction(prompt, response)

                # Prevent duplicate responses
                if not st.session_state.messages or st.session_state.messages[-1]["content"] != response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.last_response_id = len(st.session_state.messages) - 1

                st.markdown(response)

if __name__ == "__main__":
    main()