# 🎓 Unibot Advisor – Assistant RAG Universitaire

## 📝 Résumé
**Unibot Advisor** est un assistant virtuel intelligent capable de répondre aux questions sur les programmes universitaires grâce à une architecture **RAG (Retrieval-Augmented Generation)**.  
Il s’appuie exclusivement sur des **documents officiels**, garantissant des réponses **fiables, vérifiables et sourcées**.

---

## 📋 Contexte et Objectifs
L’objectif principal de ce projet est de résoudre la **surcharge informationnelle dans le contexte académique**.  
Le système permet de répondre à des questions complexes telles que :

> *« Quelles sont les opportunités de carrière pour le programme X ? »*

en synthétisant l’information issue de **milliers de pages de documentation universitaire officielle**.

---

## ✨ Fonctionnalités Clés

- **Architecture RAG complète**  
  Pipeline intégré de récupération documentaire et de génération de réponses.

- **Sources vérifiables**  
  Chaque réponse est accompagnée de **citations précises** provenant des documents sources.

- **Mémoire conversationnelle**  
  Maintien du contexte et de la cohérence sur plusieurs tours de conversation grâce à un **historique persistant**.

- **Interface interactive**  
  Application Web développée avec **Streamlit**, incluant la gestion de l’historique de chat.

---

## 🛠️ Architecture Technique

Le projet adopte une architecture **modulaire**, séparant le moteur d’inférence, l’interface utilisateur et la gestion des données.

| Composant        | Technologie              | Détails                                                                 |
|------------------|--------------------------|-------------------------------------------------------------------------|
| Langage          | Python                   | Langage principal                                                       |
| Orchestration    | LangChain                | Gestion du pipeline RAG                                                  |
| Vector Store     | FAISS                    | Recherche vectorielle locale optimisée                                   |
| Embeddings       | Sentence-Transformers    | `paraphrase-multilingual-MiniLM-L12-v2` (FR/EN, CPU friendly)             |
| Frontend         | Streamlit                | Interface Web interactive                                                |
| Infrastructure   | Docker                   | Conteneurisation pour le déploiement                                     |

---

## 📊 Pipeline de Données (Data Engineering)

Le corpus documentaire est constitué de **guides officiels d’universités internationales**.  
Un script d’ingestion (`ingest.py`) gère le **nettoyage**, le **découpage** et la **vectorisation**.

### 📈 Métriques du Corpus

| Étape         | Volume       | Description                                                      |
|--------------|--------------|------------------------------------------------------------------|
| Chargement   | 6 866 pages  | Pages brutes chargées initialement                               |
| Nettoyage    | 6 796 pages  | Pages utiles après suppression d’artefacts via RegEx             |
| Vectorisation| 33 923 chunks| Fragments générés pour l’index vectoriel                          |

---

## 🐳 Optimisation MLOps

Une attention particulière a été portée à l’**industrialisation** afin de garantir un déploiement **économique, léger et scalable**.

### 📉 Résultat de l’optimisation
- Taille de l’image Docker réduite de **10.4 GB à 2.32 GB**
- **Réduction totale : 77 %**

### 🧩 Stratégies Appliquées

- **Refonte du Dockerfile**  
  Installation explicite de **PyTorch CPU-only** (sans CUDA).

- **Exclusions strictes**  
  Configuration du `.dockerignore` pour exclure :
  - `venv`
  - `__pycache__`
  - fichiers de développement

- **Nettoyage post-installation**  
  Utilisation d’une image de base légère et suppression des caches `pip`.

---

## 🚀 Installation et Utilisation

### 🔹 Option 1 : Lancer avec Docker (Recommandé)

```bash
# Construire l'image optimisée
docker build -t unibot-advisor .

# Lancer le conteneur sur le port 8501
docker run -p 8501:8501 unibot-advisor
