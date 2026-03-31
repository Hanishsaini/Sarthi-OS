import streamlit as st
from config import Config
from core.context_engine import ContextEngine
from core.planner import Planner
from tools.tool_registry import ToolRegistry
from models.groq_client import GroqModel
from memory.user_memory import UserMemory
from rag.retriever import Retriever
import ollama
from datetime import datetime, timedelta
import re

st.set_page_config(page_title="Sarthi AI OS", page_icon="🛡️", layout="wide")
st.title("🛡️ Sarthi AI OS")
st.caption("Your Rajasthan Tourism Intelligence System")

# Session state
if "memory" not in st.session_state:
    st.session_state.memory = UserMemory()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tourist_type" not in st.session_state:
    st.session_state.tourist_type = "general"
if "budget" not in st.session_state:
    st.session_state.budget = "medium"

# Sidebar personalization
with st.sidebar:
    st.header("Traveler Profile")
    st.session_state.tourist_type = st.selectbox(
        "Tourist Type",
        ["general", "couple", "family", "solo"],
        index=["general","couple","family","solo"].index(st.session_state.tourist_type)
    )
    st.session_state.budget = st.select_slider(
        "Budget", ["low","medium","high"], value=st.session_state.budget
    )

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Helper to parse relative time
def parse_relative_time(query: str) -> datetime:
    query = query.lower()
    patterns = [
        (r'after (\d+) hour', lambda m: timedelta(hours=int(m.group(1)))),
        (r'after (\d+) hours', lambda m: timedelta(hours=int(m.group(1)))),
        (r'in (\d+) minute', lambda m: timedelta(minutes=int(m.group(1)))),
        (r'in (\d+) minutes', lambda m: timedelta(minutes=int(m.group(1)))),
        (r'after (\d+) minute', lambda m: timedelta(minutes=int(m.group(1)))),
        (r'after (\d+) minutes', lambda m: timedelta(minutes=int(m.group(1)))),
        (r'after one hour', lambda m: timedelta(hours=1)),
        (r'after an hour', lambda m: timedelta(hours=1)),
        (r'in an hour', lambda m: timedelta(hours=1)),
        (r'in one hour', lambda m: timedelta(hours=1)),
    ]
    for pattern, delta_func in patterns:
        match = re.search(pattern, query)
        if match:
            return datetime.now() + delta_func(match)
    return None

if prompt := st.chat_input("Ask Sarthi about Jaipur..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sarthi is thinking..."):
            # 1. Analyze context
            context = ContextEngine.analyze(prompt)
            context["tourist_type"] = st.session_state.tourist_type
            context["budget"] = st.session_state.budget
            intent = context.get("intent", "general")

            # 2. Parse relative time
            target_time = parse_relative_time(prompt)
            if target_time:
                context["target_time"] = target_time.strftime("%I:%M %p")
                context["time_advice"] = f"Plan to visit around {target_time.strftime('%I:%M %p')}."
            else:
                context["time_advice"] = ""

            # 3. Create plan and execute tools
            plan = Planner.create_plan(prompt, context)
            executed_tools = plan.get("required_tools", [])

            tool_results = ""
            if executed_tools:
                st.caption(f"🔧 Executing: {executed_tools}")
                for tool_name in executed_tools:
                    result = ToolRegistry.execute(tool_name)
                    tool_results += f"🔧 {tool_name.upper()}:\n{result}\n\n"

            # 4. RAG retrieval (structured)
            retriever = Retriever()
            rag_data = retriever.retrieve(prompt, n_results=1)
            if rag_data and isinstance(rag_data, dict):
                rag_text = f"""Name: {rag_data.get('name')}
Type: {rag_data.get('type')}
Best Time: {rag_data.get('best_time')}
Timings: {rag_data.get('timings')}
Crowd: {rag_data.get('crowd', 'Varies')}
Notes: {rag_data.get('notes')}
Nearby: {', '.join(rag_data.get('nearby', []))}"""
            else:
                rag_text = "No matching data found."

            # 5. Build final prompt
            now = datetime.now().strftime("%I:%M %p")
            full_prompt = f"""User Query: {prompt}

Current Time: {now}
Tourist Type: {context['tourist_type']}
Budget: {context['budget']}
Time Advice: {context['time_advice']}

Tool Results:
{tool_results if tool_results else "No tools used."}

Knowledge from Dataset (Structured):
{rag_text}

You are Sarthi, an expert Rajasthan tourism decision engine. Generate a response using ONLY the information above.

CRITICAL RULES:
- If the dataset has information, use it as the primary source.
- If no information is available, say "I don't have information about that" and stop.
- Do NOT invent places, timings, or crowd levels.
- Follow the output format exactly.

OUTPUT FORMAT:

Direct Answer:
(Yes/No or short statement)

Visit Insight:
(Confident advice based on time, tourist type, budget, and tool results)

Place Highlights:
(Key features from dataset)

Smart Tips:
- Tip 1
- Tip 2
- Tip 3

Nearby Flow:
(Logical next places from dataset)

If a section has no information, write "No information available."
"""

            # 6. Generate response
            try:
                response = GroqModel.generate(full_prompt, system_prompt="You are Sarthi, a helpful Rajasthan tourism assistant.")
            except:
                response = ollama.chat(
                    model="phi4-mini",
                    messages=[{"role": "user", "content": full_prompt}]
                )["message"]["content"]

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.memory.add_interaction(prompt, response)