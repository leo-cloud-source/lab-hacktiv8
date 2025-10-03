import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import google.generativeai as genai
from PIL import Image
import PyPDF2
import io
import base64
import time

# Page Configuration
st.set_page_config(
    page_title="Ade's Vision AI - Document Analyzer",
    page_icon="🔍",
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
    
    .upload-area {
        border: 2px dashed #00d4ff;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        background: rgba(0, 212, 255, 0.05);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<h1 class="main-header">🔍 ADE\'S VISION AI 🔍</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Advanced Document & Image Analyzer by Ade Ridwan</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #ff0080; font-size: 0.9rem; margin-top: -5px;">📚 Hacktiv8 Student | Supervised by Mas Adipta 📚</p>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🔧 CONTROL PANEL")
    
    # API Key Input
    google_api_key = st.text_input("🔑 Google AI API Key", type="password", help="Enter your Google AI API key")
    
    st.markdown("---")
    
    # Analysis Mode Selection
    st.markdown("### 🎯 ANALYSIS MODE")
    analysis_mode = st.selectbox(
        "Choose analysis type:",
        ["📄 Document Reader", "🖼️ Image Analyzer", "📊 Data Extractor", "🔍 Content Detector", "📝 Text Summarizer"]
    )
    
    st.markdown("---")
    
    # File Upload Area
    st.markdown("### 📁 FILE UPLOAD")
    uploaded_file = st.file_uploader(
        "Upload your file:",
        type=['pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
        help="Supported: PDF, Images (PNG, JPG, etc.)"
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
        if st.button("💾 Save", help="Save analysis"):
            st.success("Saved!")
    
    # Status Indicator
    st.markdown("---")
    if google_api_key:
        st.markdown('<div class="status-indicator"></div>**SYSTEM ONLINE**', unsafe_allow_html=True)
    else:
        st.markdown('🔴 **SYSTEM OFFLINE**')

# Helper Functions
def extract_pdf_text(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def encode_image(image_file):
    """Encode image to base64"""
    try:
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    except Exception as e:
        return None

def analyze_with_gemini_vision(api_key, image_data, prompt, analysis_mode):
    """Analyze image using Gemini Vision"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Convert base64 to image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Create mode-specific prompts
        mode_prompts = {
            "📄 Document Reader": f"Read and transcribe all text from this document. Provide a clean, formatted output. {prompt}",
            "🖼️ Image Analyzer": f"Analyze this image in detail. Describe what you see, identify objects, text, and any important information. {prompt}",
            "📊 Data Extractor": f"Extract all structured data, tables, numbers, and key information from this image. Format it clearly. {prompt}",
            "🔍 Content Detector": f"Detect and identify all content in this image including text, objects, people, and any relevant details. {prompt}",
            "📝 Text Summarizer": f"Extract all text and provide a comprehensive summary of the content. {prompt}"
        }
        
        full_prompt = mode_prompts.get(analysis_mode, prompt)
        response = model.generate_content([full_prompt, image])
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

# Main Content Area
if not google_api_key:
    # Welcome Screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔍 WELCOME TO VISION AI</h3>
            <p>Enter your API key to activate Ade's Vision AI and unlock advanced document analysis!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature Showcase
    st.markdown("### 🌟 CORE CAPABILITIES")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📄 PDF Analysis</h4>
            <p>Extract and analyze text from PDF documents with AI precision</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🖼️ Image Recognition</h4>
            <p>Advanced image analysis with object detection and text extraction</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Data Extraction</h4>
            <p>Intelligent data mining from documents and images</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.stop()

# Initialize AI Agent
if ("agent" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        with st.spinner("🔄 Initializing Ade's Vision AI..."):
            time.sleep(1)
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=google_api_key,
                temperature=0.3
            )
            
            # Custom prompt based on selected mode
            mode_prompts = {
                "📄 Document Reader": "You are Ade's Vision AI, created by Ade Ridwan from Hacktiv8 under Mas Adipta's guidance. You specialize in reading and analyzing documents with high accuracy.",
                "🖼️ Image Analyzer": "You are Ade's Vision AI, developed by Ade Ridwan at Hacktiv8. You excel at detailed image analysis and object recognition.",
                "📊 Data Extractor": "You are Ade's Vision AI, created by Ade Ridwan, a Hacktiv8 student. You're expert at extracting structured data from various file formats.",
                "🔍 Content Detector": "You are Ade's Vision AI, built by Ade Ridwan under Mas Adipta's mentorship. You detect and identify all types of content with precision.",
                "📝 Text Summarizer": "You are Ade's Vision AI, developed by Ade Ridwan from Hacktiv8. You provide comprehensive text analysis and summarization."
            }
            
            st.session_state.agent = create_react_agent(
                model=llm,
                tools=[],
                prompt=mode_prompts.get(analysis_mode, mode_prompts["📄 Document Reader"])
            )
            
            st.session_state._last_key = google_api_key
            st.session_state.pop("messages", None)
            
        st.success("✅ ADE'S VISION AI ACTIVATED!")
        
    except Exception as e:
        st.error(f"❌ SYSTEM ERROR: {e}")
        st.stop()

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_msg = f"🔍 **ADE'S VISION AI ONLINE** - {analysis_mode} mode activated!\n\nI'm Ade's Vision AI, created by Ade Ridwan from Hacktiv8 under Mas Adipta's guidance. Upload a file or ask me anything about document analysis!"
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Display uploaded file
if uploaded_file is not None:
    st.markdown("### 📁 UPLOADED FILE")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if uploaded_file.type.startswith('image/'):
            st.image(uploaded_file, caption=f"📸 {uploaded_file.name}", use_column_width=True)
        else:
            st.info(f"📄 PDF File: {uploaded_file.name}")
    
    with col2:
        st.markdown(f"""
        **File Details:**
        - 📝 Name: `{uploaded_file.name}`
        - 📊 Type: `{uploaded_file.type}`
        - 💾 Size: `{uploaded_file.size} bytes`
        - 🎯 Mode: `{analysis_mode}`
        """)
        
        if st.button("🚀 ANALYZE FILE", key="analyze_btn"):
            with st.spinner("🔍 Analyzing file..."):
                if uploaded_file.type == 'application/pdf':
                    # PDF Analysis
                    pdf_text = extract_pdf_text(uploaded_file)
                    analysis_result = f"📄 **PDF CONTENT EXTRACTED:**\n\n{pdf_text}"
                else:
                    # Image Analysis
                    image_data = encode_image(uploaded_file)
                    if image_data:
                        analysis_result = analyze_with_gemini_vision(
                            google_api_key, 
                            image_data, 
                            f"Analyze this file using {analysis_mode} approach.", 
                            analysis_mode
                        )
                    else:
                        analysis_result = "❌ Error processing image file."
                
                # Add analysis to chat
                st.session_state.messages.append({"role": "user", "content": f"Analyze uploaded file: {uploaded_file.name}"})
                st.session_state.messages.append({"role": "assistant", "content": analysis_result})
                st.rerun()

# Display Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("💬 Ask about your files or document analysis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    try:
        with st.chat_message("assistant"):
            with st.spinner("🧠 Ade's Vision AI is analyzing..."):
                messages = []
                for msg in st.session_state.messages[:-1]:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant" and not msg["content"].startswith("🔍"):
                        messages.append(AIMessage(content=msg["content"]))
                
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
        '<p style="text-align: center; color: #ffff00; font-family: Orbitron; font-size: 0.8rem;">👨🏫 Supervised by<br><strong>Mas Adipta</strong></p>',
        unsafe_allow_html=True
    )