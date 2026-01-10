import streamlit as st
import os
import json
import uuid
import time
from langchain_core.messages import HumanMessage, AIMessage
from engine import load_rag_components, get_contextualize_chain, get_qa_chain

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Unibot Advisor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Création du dossier d'historique s'il n'existe pas
HISTORY_DIR = "chat_history"
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# --- 2. CSS PERSONNALISÉ (UI/UX) ---
st.markdown("""
<style>
    /* Force le mode clair et texte foncé pour la lisibilité */
    .stApp {
        background-color: #f4f6f9;
        color: #1e1e1e;
    }
    
    /* En-tête */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Style des bulles de chat */
    .stChatMessage {
        background-color: transparent;
        border: none;
    }

    /* Avatar personnalisé */
    .stChatMessage .stChatMessageAvatar {
        background-color: #e0e0e0;
        color: #000;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #ddd;
    }
    
    /* Boutons de la sidebar */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        border-color: #adadad;
        background-color: #f0f0f0;
        color: #000;
    }

    /* Input text en bas */
    .stChatInput textarea {
        border-radius: 15px;
        border: 1px solid #ccc;
    }
    
    /* Cacher le menu hamburger et le footer Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. GESTION DE L'HISTORIQUE (JSON) ---

def save_chat_session(session_id, messages):
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def load_chat_session(session_id):
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_all_sessions():
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    sessions = []
    for f in files:
        filepath = os.path.join(HISTORY_DIR, f)
        mod_time = os.path.getmtime(filepath)
        session_id = f.replace(".json", "")
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                title = "New Conversation"
                if len(data) > 0 and data[0]["role"] == "user":
                    title = data[0]["content"][:35] + "..."
        except:
            title = "Conversation"
        sessions.append({"id": session_id, "title": title, "time": mod_time})
    return sorted(sessions, key=lambda x: x["time"], reverse=True)

def create_new_session():
    new_id = str(uuid.uuid4())
    st.session_state.current_session_id = new_id
    st.session_state.messages = []
    st.rerun()

def delete_session(session_id):
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    if st.session_state.current_session_id == session_id:
        create_new_session()
    else:
        st.rerun()

# --- 4. CONFIGURATION SESSION & API ---

# Initialisation de la session
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_session(st.session_state.current_session_id)

# Gestion de la clé API (Secrets ou Input Utilisateur)
api_key = os.getenv("GROQ_API_KEY")
if not api_key and "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🎓 Unibot Advisor")
    st.caption("Assistant Académique RAG")
    
    # Input Clé API si manquante
    if not api_key:
        st.warning("⚠️ API Key manquante")
        user_key = st.text_input("Entrez votre clé Groq API :", type="password")
        if user_key:
            os.environ["GROQ_API_KEY"] = user_key
            st.rerun()
    else:
        os.environ["GROQ_API_KEY"] = api_key
        st.success("✅ Système en ligne", icon="🟢")

    st.markdown("---")
    
    if st.button("➕ Nouvelle Conversation", type="primary"):
        create_new_session()
    
    st.markdown("### 🕒 Historique")
    sessions = get_all_sessions()
    
    for sess in sessions:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            label = sess['title']
            # Style visuel pour la session active
            if sess['id'] == st.session_state.current_session_id:
                label = f"🔵 **{label}**"
            
            if st.button(label, key=f"btn_{sess['id']}"):
                st.session_state.current_session_id = sess['id']
                st.session_state.messages = load_chat_session(sess['id'])
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{sess['id']}", help="Supprimer"):
                delete_session(sess['id'])

    st.markdown("---")
    st.markdown("<div style='text-align: center; color: grey;'>v2.0 - MLOps Project</div>", unsafe_allow_html=True)

# --- 6. CHARGEMENT MOTEUR ---
# On ne charge que si la clé API est présente
if not os.environ.get("GROQ_API_KEY"):
    st.info("👈 Veuillez entrer une clé API Groq dans la barre latérale pour commencer.")
    st.stop()

@st.cache_resource
def setup_engine():
    return load_rag_components()

try:
    retriever, llm = setup_engine()
    context_chain = get_contextualize_chain(llm)
    qa_chain = get_qa_chain(llm)
except Exception as e:
    st.error(f"Erreur critique de chargement : {e}")
    st.stop()

# --- 7. ZONE DE CHAT ---

# Message de bienvenue
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align: center; margin-top: 50px;">
        <h1>Bonjour ! 👋</h1>
        <p style="font-size: 1.2em; color: #555;">Je suis votre assistant académique. Posez-moi des questions sur :</p>
        <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
            <span style="background: #e3f2fd; color: #1565c0; padding: 5px 10px; border-radius: 15px;">📘 Règlements</span>
            <span style="background: #e8f5e9; color: #2e7d32; padding: 5px 10px; border-radius: 15px;">🎓 Masters</span>
            <span style="background: #fff3e0; color: #ef6c00; padding: 5px 10px; border-radius: 15px;">💰 Frais</span>
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)

# Affichage des messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # Style Utilisateur : Bleu
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"""
            <div style="background-color: #007bff; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; display: inline-block;">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
    else:
        # Style AI : Blanc/Gris avec bordure
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"""
            <div style="background-color: #ffffff; color: #333; padding: 15px; border-radius: 0 15px 15px 15px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Affichage des sources
            if msg.get("sources") and msg["sources"] != "None":
                with st.expander("📚 Sources Vérifiées"):
                    source_list = msg["sources"].split(", ")
                    for src in source_list:
                        st.markdown(f"- 📄 `{src}`")

# --- 8. LOGIQUE D'INTERACTION ---
if prompt := st.chat_input("Posez votre question ici..."):
    
    # 1. Sauvegarde et affichage User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
         st.markdown(f"""
            <div style="background-color: #007bff; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; display: inline-block;">
                {prompt}
            </div>
            """, unsafe_allow_html=True)

    # 2. Génération Réponse
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        with st.spinner("Recherche dans les documents..."):
            try:
                lc_history = [
                    HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) 
                    for m in st.session_state.messages[:-1]
                ]

                # Reformulation contextuelle
                reformulated = prompt
                if lc_history:
                    reformulated = context_chain.invoke({"chat_history": lc_history, "question": prompt})

                # Retrieval
                docs = retriever.invoke(reformulated)
                
                if not docs:
                    response_text = "Je ne trouve pas d'information pertinente dans les documents fournis."
                    sources_text = "None"
                else:
                    context_text = "\n\n".join([d.page_content for d in docs])
                    # Nettoyage des noms de sources
                    sources_text = ", ".join(list(set([os.path.basename(d.metadata.get('source', 'Inconnu')) for d in docs])))
                    
                    response_text = qa_chain.invoke({
                        "context": context_text,
                        "chat_history": lc_history,
                        "question": reformulated
                    })

                # Effet de streaming (simulation visuelle)
                full_html = f"""
                <div style="background-color: #ffffff; color: #333; padding: 15px; border-radius: 0 15px 15px 15px; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    {response_text}
                </div>
                """
                message_placeholder.markdown(full_html, unsafe_allow_html=True)

                # Sauvegarde AI
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text, 
                    "sources": sources_text
                })
                
                save_chat_session(st.session_state.current_session_id, st.session_state.messages)
                
                # Refresh pour mettre à jour le titre sidebar si c'est le 1er message
                if len(st.session_state.messages) == 2:
                    st.rerun()
                # Refresh pour afficher les sources proprement (expander)
                st.rerun()

            except Exception as e:
                st.error(f"Une erreur est survenue : {str(e)}")