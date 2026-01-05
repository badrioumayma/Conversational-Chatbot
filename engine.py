import os
import torch
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# --- CONFIGURATION CONSTANTES ---
DB_FAISS_PATH = "vectorstore/db_faiss"
MODEL_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_LLM = "llama-3.1-8b-instant"  # Le modèle rapide et stable
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_rag_components():
    """
    Charge les Embeddings, FAISS et le LLM Groq.
    Retourne (retriever, llm) ou (None, None) en cas d'erreur.
    """
    print(f"--- ⚙️ Engine: Chargement sur {DEVICE.upper()} ---")

    # 1. Embeddings
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_EMBEDDING,
            model_kwargs={'device': DEVICE}
        )
    except Exception as e:
        print(f"Erreur Embeddings: {e}")
        return None, None

    # 2. VectorStore (FAISS)
    if not os.path.exists(DB_FAISS_PATH):
        print(f"❌ Erreur: Base de données introuvable dans '{DB_FAISS_PATH}'")
        return None, None
        
    try:
        vectorstore = FAISS.load_local(
            DB_FAISS_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        # k=3 pour économiser les tokens et éviter l'erreur 429
        retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
    except Exception as e:
        print(f"Erreur FAISS: {e}")
        return None, None

    # 3. LLM (Groq)
    # Note: La clé API doit être définie dans os.environ["GROQ_API_KEY"] avant cet appel
    try:
        llm = ChatGroq(
            temperature=0.0, 
            model_name=MODEL_LLM
        )
    except Exception as e:
        print(f"Erreur Groq: {e}")
        return None, None

    return retriever, llm

def get_contextualize_chain(llm):
    """
    Crée la chaîne qui reformule les questions (Gestion de l'historique et changement de sujet).
    """
    system_prompt = """
    Given a chat history and the latest user question which might reference context in the chat history, 
    formulate a standalone question which can be understood without the chat history.

    IMPORTANT RULES:
    1. **Follow-up questions:** If the user asks a follow-up (e.g., "what is the cost?", "how do I apply?"), REWRITE the question to include the previous subject (e.g., "What is the cost for Qatar University?").
    2. **New Topic:** If the user asks about a completely NEW subject or a different university (e.g., "What about Erasmus?", "Tell me about Wheeling"), **IGNORE** the previous chat history and return the question as is. Do NOT mix the old subject with the new one.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])
    
    return prompt | llm | StrOutputParser()

def get_qa_chain(llm):
    """
    Crée la chaîne de réponse finale (RAG) avec gestion des salutations.
    """
    system_prompt = """
    You are an expert academic advisor for international students.

    INSTRUCTIONS:
    1.  **GREETINGS:** If the user input is a simple greeting (like "hello", "hi", "bonjour", "thanks") or small talk, simply reply politely (e.g., "Hello! How can I help you with your university application today?"). **DO NOT** mention the provided context or any specific university for simple greetings.
    2.  **FOR QUESTIONS:** Analyze the provided "Context" below to answer the user's question.
    3.  **Language:** ALWAYS answer in **ENGLISH**.
    4.  **Accuracy:** Use ONLY the provided context. If the answer is not in the context, say "I cannot find this info based on the provided documents."
    5.  **Format:** Use bullet points and clear headings for complex answers.

    CONTEXT:
    {context}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])
    
    return prompt | llm | StrOutputParser()