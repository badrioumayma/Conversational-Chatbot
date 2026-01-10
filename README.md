# 🎓 Unibot Advisor – Assistant RAG Universitaire

## 📝 Résumé
**Unibot Advisor** est un assistant virtuel intelligent capable de répondre aux questions sur les programmes universitaires grâce à une architecture **RAG (Retrieval-Augmented Generation)**.  
Il s’appuie exclusivement sur des **documents universitaires officiels**, garantissant des réponses **fiables, vérifiables et sourcées**.

---

## 📋 Contexte et Objectifs
Dans un contexte de **surcharge informationnelle académique**, les étudiants et futurs candidats ont des difficultés à trouver des réponses claires et synthétiques concernant les programmes universitaires.

**Unibot Advisor** vise à :
- Centraliser l’information universitaire officielle
- Répondre à des questions complexes comme :
  > *« Quelles sont les opportunités de carrière pour le programme X ? »*
- Garantir des réponses **traçables et justifiées par des sources**

---

## ✨ Fonctionnalités Clés

- 🔍 **Architecture RAG complète**  
  Pipeline intégré de récupération documentaire et de génération de réponses

- 📑 **Sources vérifiables**  
  Chaque réponse inclut des **citations précises** issues des documents officiels

- 🧠 **Mémoire conversationnelle**  
  Conservation du contexte sur plusieurs tours de dialogue

- 💬 **Interface interactive**  
  Application Web développée avec **Streamlit**, incluant l’historique des conversations

---

## 🛠️ Architecture Technique

Architecture modulaire séparant clairement les responsabilités (données, logique métier, interface).

| Composant        | Technologie              | Description                                                                 |
|------------------|--------------------------|-----------------------------------------------------------------------------|
| Langage          | Python                   | Langage principal                                                           |
| Orchestration    | LangChain                | Gestion du pipeline RAG                                                      |
| Vector Store     | FAISS                    | Recherche vectorielle locale performante                                     |
| Embeddings       | Sentence-Transformers    | `paraphrase-multilingual-MiniLM-L12-v2` (FR/EN, CPU-friendly)                |
| Frontend         | Streamlit                | Interface Web interactive                                                    |
| Infrastructure   | Docker                   | Conteneurisation et déploiement                                              |

---

## 📊 Pipeline de Données (Data Engineering)

Le corpus est constitué de **guides universitaires officiels internationaux**.  
Le script `ingest.py` assure :
- Nettoyage des données
- Découpage intelligent des documents
- Vectorisation pour l’index FAISS

### 📈 Métriques du Corpus

| Étape           | Volume        | Description                                              |
|-----------------|---------------|----------------------------------------------------------|
| Chargement      | 6 866 pages   | Pages brutes initiales                                   |
| Nettoyage       | 6 796 pages   | Pages exploitables après filtrage RegEx                  |
| Vectorisation   | 33 923 chunks | Fragments indexés dans le vector store                   |

---

## 🐳 Optimisation MLOps

Le projet a été optimisé pour un **déploiement industriel léger et économique**.

### 📉 Résultats
- Taille image Docker : **10.4 GB → 2.32 GB**
- **Réduction : 77 %**

### 🧩 Stratégies appliquées
- Installation de **PyTorch CPU-only** (sans CUDA)
- `.dockerignore` strict (`venv`, `__pycache__`, fichiers de dev)
- Nettoyage des caches `pip`
- Image de base légère

---
### 🔑 Configuration de la Clé API (Groq)

Pour des raisons de sécurité, la clé API n'est pas incluse dans l'image. Vous devez la passer en variable d'environnement au moment du lancement.

*Commande de lancement avec la clé :*

```bash
docker run -p 8501:8501 -e GROQ_API_KEY="gsk_votre_cle_secrete_ici" unibot-advisor:final
