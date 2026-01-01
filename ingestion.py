# Le script pour traiter les PDF

import fitz  # PyMuPDF
import os
import json

def ingest_documents(input_folder, output_file):
    corpus = []
    # Paramètres de découpage (Chunking)
    chunk_size = 800  # Nombre de caractères par morceau
    overlap = 150     # Chevauchement pour ne pas couper le contexte

    # Vérification du dossier
    if not os.path.exists(input_folder):
        print(f"Le dossier {input_folder} n'existe pas !")
        return

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            path = os.path.join(input_folder, filename)
            print(f"Traitement de : {filename}")
            
            # 1. Extraction du texte
            doc = fitz.open(path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            # 2. Nettoyage (suppression des doubles espaces et retours à la ligne)
            clean_text = " ".join(full_text.split())
            
            # 3. Stratégie de Chunking (Découpage)
            # On parcourt le texte et on crée des segments
            for i in range(0, len(clean_text), chunk_size - overlap):
                chunk = clean_text[i:i + chunk_size]
                
                # On stocke le texte ET la source (très important pour les citations)
                corpus.append({
                    "text": chunk,
                    "metadata": {
                        "source": filename,
                        "char_count": len(chunk)
                    }
                })

    # 4. Sauvegarde en format JSON pour l'étape suivante (Retrieval)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=4)
    
    print(f"\nTerminé ! {len(corpus)} segments créés à partir de vos PDF.")

# Lancement du traitement
if __name__ == "__main__":
    ingest_documents("data/raw", "data/processed/processed_data.json")