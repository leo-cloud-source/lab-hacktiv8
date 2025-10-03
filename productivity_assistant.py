import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import datetime
import time

# Page Configuration
st.set_page_config(
    page_title="Ade's AI - Productivity Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Cinematic Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    .main-header {
        font-family: 'Orbitron', monospace;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(45deg, #00d4ff, #ff0080, #ffff00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        margin-bottom: 0;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 20px #00d4ff); }
        to { filter: drop-shadow(0 0 30px #ff0080); }
    }
    
    .subtitle {
        font-family: 'Orbitron', monospace;
        text-align: center;
        color: #00d4ff;
        font-size: 1.2rem;
        margin-top: -10px;
        opacity: 0.8;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 2px solid #00d4ff;
    }
    
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin: 10px 0;
    }
    
    .stChatMessage[data-testid="user"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(255, 0, 128, 0.1));
        border-color: #00d4ff;
    }
    
    .stChatMessage[data-testid="assistant"] {
        background: linear-gradient(135deg, rgba(255, 255, 0, 0.1), rgba(0, 255, 128, 0.1));
        border-color: #ffff00;
    }
    
    .feature-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(255, 0, 128, 0.1));
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
        border-color: #00d4ff;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #00d4ff, #ff0080);
        color: white;
        border: none;
        border-radius: 25px;
        font-family: 'Orbitron', monospace;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.5);
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00ff00;
        animation: pulse 1.5s infinite;
        margin-right: 10px;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<h1 class="main-header">🎓 ADE\'S AI 🎓</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Productivity Assistant by Ade Ridwan</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #ff0080; font-size: 0.9rem; margin-top: -5px;">📚 Hacktiv8 Student | Supervised by Mas Adipta 📚</p>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🔧 CONTROL PANEL")
    
    # API Key Input
    google_api_key = st.text_input("🔑 Google AI API Key", type="password", help="Enter your Google AI API key")
    
    st.markdown("---")
    
    # Assistant Mode Selection
    st.markdown("### 🎯 ASSISTANT MODE")
    assistant_mode = st.selectbox(
        "Choose your focus:",
        ["💼 Task Manager", "📅 Schedule Optimizer", "💡 Idea Generator", "📊 Goal Tracker", "🧠 Learning Assistant"]
    )
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ QUICK ACTIONS")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", help="Clear conversation"):
            st.session_state.clear()
            st.rerun()
    with col2:
        if st.button("💾 Save", help="Save conversation"):
            st.success("Saved!")
    
    # Status Indicator
    st.markdown("---")
    if google_api_key:
        st.markdown('<div class="status-indicator"></div>**SYSTEM ONLINE**', unsafe_allow_html=True)
    else:
        st.markdown('🔴 **SYSTEM OFFLINE**')

# Main Content Area
if not google_api_key:
    # Welcome Screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🎓 WELCOME TO ADE'S AI</h3>
            <p>Enter your API key to activate Ade's AI and boost your productivity with cutting-edge technology!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature Showcase
    st.markdown("### 🌟 CORE CAPABILITIES")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📋 Task Management</h4>
            <p>Organize, prioritize, and track your tasks with AI-powered insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🎯 Goal Setting</h4>
            <p>Set SMART goals and get personalized action plans</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>⏰ Time Optimization</h4>
            <p>Maximize your productivity with intelligent scheduling</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# Initialize AI Agent
if ("agent" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        with st.spinner("🔄 Initializing Ade's AI..."):
            time.sleep(1)  # Dramatic pause
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=google_api_key,
                temperature=0.7
            )
            
            # Custom prompt based on selected mode
            mode_prompts = {
                "💼 Task Manager": "You are Ade's AI, an advanced productivity assistant created by Ade Ridwan, a Hacktiv8 student under Mas Adipta's guidance. Specialize in task management and help users organize, prioritize, and complete their tasks efficiently. Provide actionable advice and structured plans.",
                "📅 Schedule Optimizer": "You are Ade's AI, created by Ade Ridwan from Hacktiv8. You're an AI scheduling expert that helps users optimize their time, create efficient schedules, and balance work-life priorities.",
                "💡 Idea Generator": "You are Ade's AI, a creative assistant developed by Ade Ridwan, a student at Hacktiv8. Help users brainstorm ideas, solve problems creatively, and think outside the box.",
                "📊 Goal Tracker": "You are Ade's AI, created by Ade Ridwan under Mas Adipta's mentorship at Hacktiv8. You're an AI goal-setting coach that helps users set SMART goals, create action plans, and track progress effectively.",
                "🧠 Learning Assistant": "You are Ade's AI, developed by Ade Ridwan, a Hacktiv8 student. You're an AI learning companion that helps users learn new skills, understand concepts, and develop knowledge efficiently."
            }
            
            st.session_state.agent = create_react_agent(
                model=llm,
                tools=[],
                prompt=mode_prompts.get(assistant_mode, mode_prompts["💼 Task Manager"])
            )
            
            st.session_state._last_key = google_api_key
            st.session_state.pop("messages", None)
            
        st.success("✅ ADE'S AI ACTIVATED!")
        
    except Exception as e:
        st.error(f"❌ SYSTEM ERROR: {e}")
        st.stop()

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome message
    welcome_msg = f"🎓 **ADE'S AI ONLINE** - {assistant_mode} mode activated!\n\nHello! I'm Ade's AI, created by Ade Ridwan from Hacktiv8 under Mas Adipta's guidance. How can I boost your productivity today?"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Display Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("💬 Enter your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    try:
        with st.chat_message("assistant"):
            with st.spinner("🧠 Ade's AI is thinking..."):
                # Convert messages
                messages = []
                for msg in st.session_state.messages[:-1]:  # Exclude welcome message
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant" and not msg["content"].startswith("🚀"):
                        messages.append(AIMessage(content=msg["content"]))
                
                # Add current prompt
                messages.append(HumanMessage(content=prompt))
                
                response = st.session_state.agent.invoke({"messages": messages})
                
                if "messages" in response and len(response["messages"]) > 0:
                    answer = response["messages"][-1].content
                else:
                    answer = "⚠️ Unable to process request. Please try again."
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
    except Exception as e:
        error_msg = f"❌ **SYSTEM ERROR**: {str(e)}"
        st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.markdown(
        '<p style="text-align: center; color: #00d4ff; font-family: Orbitron; font-size: 0.8rem;">🎓 Created by<br><strong>Ade Ridwan</strong></p>',
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        '<p style="text-align: center; color: #ff0080; font-family: Orbitron; font-size: 0.8rem;">📚 Hacktiv8<br><strong>Data Science</strong></p>',
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        '<p style="text-align: center; color: #ffff00; font-family: Orbitron; font-size: 0.8rem;">👨‍🏫 Supervised by<br><strong>Mas Adipta</strong></p>',
        unsafe_allow_html=True
    )