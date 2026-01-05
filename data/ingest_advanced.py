import os
import re
import torch
import sys

# --- CORRECTION DES IMPORTS ---
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# C'est ici que ça changeait : on utilise langchain_core maintenant
from langchain_core.documents import Document 

# --- 1. CONFIGURATION ---
DATA_PATH = "data/raw"            # Assurez-vous que vos 5 PDFs sont dans ce dossier
DB_FAISS_PATH = "vectorstore/db_faiss"

# Modèle Multilingue (Arabe + Français + Anglais)
MODEL_EMBEDDING = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def clean_text(text):
    """
    Fonction de nettoyage avancé pour retirer le bruit des PDF.
    """
    if not text: return ""

    # 1. Retirer les numéros de pages isolés
    text = re.sub(r'Page\s+\d+|^\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\d+\s+\|\s+P\s+a\s+g\s+e', '', text) # Cas spécifique Wheeling
    
    # 2. Retirer les en-têtes répétitifs
    text = re.sub(r'Undergraduate\s+Catalog\s+2024-2025', '', text, flags=re.IGNORECASE)
    
    # 3. Réparer les césures de mots (hyphenation)
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    
    # 4. Supprimer les sauts de ligne multiples
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def load_and_process_documents():
    print(f"--- 🚀 Démarrage du Traitement Avancé (Sur {DEVICE.upper()}) ---")
    
    # Vérification du dossier
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"⚠️  Le dossier '{DATA_PATH}' a été créé. Veuillez y déposer vos PDF et relancer.")
        return

    # 1. Chargement Brut
    loader = PyPDFDirectoryLoader(DATA_PATH)
    raw_docs = loader.load()
    print(f"📄 {len(raw_docs)} pages brutes chargées.")

    if not raw_docs:
        print(f"❌ Erreur : Le dossier '{DATA_PATH}' est vide. Ajoutez vos PDF.")
        return

    processed_docs = []
    
    # 2. Nettoyage et Injection de Contexte
    print("🧹 Nettoyage et Enrichissement des données...")
    for doc in raw_docs:
        # Identification de la source
        full_source = doc.metadata.get('source', '')
        filename = os.path.basename(full_source) # Extrait juste le nom du fichier
        uni_name = filename.replace('.pdf', '').replace('_', ' ')
        
        # Nettoyage
        cleaned_content = clean_text(doc.page_content)
        
        # S'il reste du contenu utile
        if len(cleaned_content) > 50:
            # INJECTION DE CONTEXTE : On ajoute le nom de l'université au début du chunk
            enriched_content = f"Document Source: {uni_name}\n\n{cleaned_content}"
            
            # On met à jour le contenu
            doc.page_content = enriched_content
            processed_docs.append(doc)

    print(f"✅ {len(processed_docs)} pages traitées et enrichies.")

    # 3. Chunking Optimisé
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300,
        separators=["\n\n", "(?<=\. )", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(processed_docs)
    print(f"✂️  Génération de {len(chunks)} fragments (chunks) optimisés.")

    # 4. Embeddings & Indexation
    print(f"🧠 Calcul des vecteurs avec {MODEL_EMBEDDING}...")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_EMBEDDING,
        model_kwargs={'device': DEVICE}
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(DB_FAISS_PATH)
    print(f"✅ Base de données sauvegardée avec succès dans '{DB_FAISS_PATH}'")

if __name__ == "__main__":
    load_and_process_documents()