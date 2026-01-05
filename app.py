import streamlit as st
import os
import json
import uuid
import time
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from engine import load_rag_components, get_contextualize_chain, get_qa_chain

# --- 1. CONFIGURATION & CSS ---
st.set_page_config(
    page_title="Academic Advisor AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Création du dossier d'historique s'il n'existe pas
HISTORY_DIR = "chat_history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

st.markdown("""
<style>
    /* Style général épuré */
    .stApp { background-color: #ffffff; }
    
    /* Input field arrondi */
    .stChatInput input {
        border-radius: 20px !important;
        border: 1px solid #ddd !important;
        padding: 10px !important;
    }
    
    /* Messages */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #f8f9fa; /* Gris très clair */
        border-radius: 12px;
        border: 1px solid #eee;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f7f7f9;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Boutons de l'historique dans la sidebar */
    div.stButton > button:first-child {
        text-align: left; 
        padding-left: 10px;
        border: none;
        background: transparent;
        color: #333;
    }
    div.stButton > button:hover {
        background-color: #e0e0e0;
        color: #000;
    }
    
    /* Cacher footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. FONCTIONS DE GESTION D'HISTORIQUE (JSON) ---

def save_chat_session(session_id, messages):
    """Sauvegarde la session actuelle dans un fichier JSON."""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_chat_session(session_id):
    """Charge une session depuis un fichier JSON."""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_all_sessions():
    """Récupère la liste des sessions existantes triées par date."""
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    sessions = []
    for f in files:
        filepath = os.path.join(HISTORY_DIR, f)
        # On utilise la date de modification du fichier pour le tri
        mod_time = os.path.getmtime(filepath)
        session_id = f.replace(".json", "")
        
        # On essaie de lire le premier message pour le titre
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                title = "New Chat"
                if len(data) > 0 and data[0]["role"] == "user":
                    # On prend les 30 premiers caractères du premier message
                    title = data[0]["content"][:30] + "..."
        except:
            title = "Conversation"
            
        sessions.append({"id": session_id, "title": title, "time": mod_time})
    
    # Tri du plus récent au plus ancien
    return sorted(sessions, key=lambda x: x["time"], reverse=True)

def create_new_session():
    """Crée une nouvelle session vierge."""
    new_id = str(uuid.uuid4())
    st.session_state.current_session_id = new_id
    st.session_state.messages = []
    st.rerun()

def delete_session(session_id):
    """Supprime une session."""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    # Si on supprime la session active, on en crée une nouvelle
    if st.session_state.current_session_id == session_id:
        create_new_session()
    else:
        st.rerun()

# --- 3. INITIALISATION SESSION ---

if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# Si pas d'ID de session, on en crée une
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())

# Si pas de messages, on essaie de charger
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_session(st.session_state.current_session_id)

# --- 4. CHARGEMENT MOTEUR (CACHE) ---
@st.cache_resource
def setup_engine():
    return load_rag_components()

retriever, llm = setup_engine()
if not retriever or not llm:
    st.error("❌ System Error: Check API Key or engine.py")
    st.stop()

context_chain = get_contextualize_chain(llm)
qa_chain = get_qa_chain(llm)

# --- 5. SIDEBAR (Historique) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=50)
    st.title("Advisor AI")
    
    # Bouton + Nouveau Chat
    if st.button("➕ New Chat", type="primary", use_container_width=True):
        create_new_session()
    
    st.markdown("---")
    st.markdown("### 🕒 History")
    
    # Liste des sessions
    sessions = get_all_sessions()
    
    for sess in sessions:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            # Si on clique sur le nom, on charge la session
            if st.button(f"💬 {sess['title']}", key=f"btn_{sess['id']}"):
                st.session_state.current_session_id = sess['id']
                st.session_state.messages = load_chat_session(sess['id'])
                st.rerun()
        with col2:
            # Petit bouton poubelle pour supprimer
            if st.button("✖", key=f"del_{sess['id']}", help="Delete"):
                delete_session(sess['id'])

    st.markdown("---")
    st.caption("v2.1 Pro - Persistent History")

# --- 6. INTERFACE PRINCIPALE ---

# Titre conditionnel (Si nouvelle conversation)
if not st.session_state.messages:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Hello, Student! 👋</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Ask me about universities, fees, or programs.</p>", unsafe_allow_html=True)

# Affichage des messages
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg.get("sources") and msg["sources"] != "None":
            with st.expander("🔍 Sources"):
                st.caption(msg["sources"])

# --- 7. LOGIQUE DE CHAT ---
if prompt := st.chat_input("Type your question here..."):
    
    # 1. Message Utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. Réponse AI
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        with st.spinner("Thinking..."):
            try:
                # Historique Langchain
                lc_history = [
                    HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) 
                    for m in st.session_state.messages[:-1]
                ]

                # RAG Logic
                reformulated = prompt
                if lc_history:
                    reformulated = context_chain.invoke({"chat_history": lc_history, "question": prompt})

                docs = retriever.invoke(reformulated)
                
                if not docs:
                    response = "I couldn't find relevant information in your documents."
                    sources = "None"
                else:
                    context_text = "\n\n".join([d.page_content for d in docs])
                    sources = ", ".join(list(set([os.path.basename(d.metadata.get('source', 'Unknown')) for d in docs])))
                    
                    response = qa_chain.invoke({
                        "context": context_text,
                        "chat_history": lc_history,
                        "question": reformulated
                    })

                # Streaming effect
                full_response = ""
                for chunk in response.split():
                    full_response += chunk + " "
                    time.sleep(0.02)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

                # Save AI response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response, 
                    "sources": sources
                })
                
                # --- SAUVEGARDE AUTOMATIQUE ---
                save_chat_session(st.session_state.current_session_id, st.session_state.messages)
                
                # On force le refresh si c'est le tout premier message pour mettre à jour la Sidebar (Titre)
                if len(st.session_state.messages) == 2:
                    st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")