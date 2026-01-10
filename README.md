Unibot Advisor : Chatbot RAG Universitaire 🎓🤖

Unibot Advisor est un assistant virtuel intelligent conçu pour répondre aux questions sur les programmes universitaires en utilisant une architecture RAG (Retrieval-Augmented Generation). Le système s'appuie exclusivement sur des documents officiels pour fournir des réponses précises, concises et vérifiables, accompagnées de citations.
+1

📋 Contexte et Objectifs
L'objectif principal est de résoudre la surcharge informationnelle dans le contexte académique. Le bot permet de répondre à des questions complexes (ex: "Quelles sont les opportunités de carrière pour le programme X ?") en synthétisant l'information provenant de milliers de pages de documentation officielle.
+2

Fonctionnalités Clés

Architecture RAG : Pipeline complet de récupération et de génération.


Sources Vérifiables : Chaque réponse est accompagnée de citations précises tirées des documents.


Mémoire Conversationnelle : Gestion du contexte sur plusieurs tours de conversation (historique persistant).
+1


Interface Interactive : UI développée sous Streamlit avec gestion de l'historique de chat.
+1

🛠️ Architecture Technique
Le projet suit une architecture modulaire (Engine, UI, Data).

Stack Technologique

Langage : Python.


Orchestration : LangChain.


Vector Store : FAISS (Recherche vectorielle locale).


Embeddings : sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2.


Note : Choisi pour sa capacité multilingue (FR/EN) et sa performance sur CPU.


Frontend : Streamlit.


Conteneurisation : Docker.

📊 Pipeline de Données (Data Engineering)
Le corpus documentaire a été constitué à partir de guides officiels d'universités internationales. Un script d'ingestion (ingest.py) gère le traitement.
+1

Métriques du traitement :

📄 6 866 pages brutes chargées.

🧹 6 796 pages utiles après nettoyage (suppression d'artefacts via RegEx).
+1

🧩 33 923 fragments (chunks) générés pour l'index vectoriel.

🐳 Optimisation MLOps
Une attention particulière a été portée à l'industrialisation pour rendre le déploiement viable.

Problématique
L'image Docker initiale pesait 10.4 GB, rendant le déploiement impraticable.

Stratégie d'Optimisation

Refonte du Dockerfile : Installation explicite de PyTorch version CPU uniquement (sans CUDA).
+1


Nettoyage : Utilisation stricte de .dockerignore pour exclure venv, caches et fichiers de développement.


Base Image : Utilisation d'une image de base légère et nettoyage des caches post-installation.
+1

Résultats
📉 Taille finale : 2.32 GB (Réduction de 77%).

🚀 Temps de déploiement divisé par 4.

🚀 Installation et Utilisation
Prérequis
Docker

Python 3.9+

Lancer avec Docker
Bash

# Construire l'image
docker build -t unibot-advisor .

# Lancer le conteneur
docker run -p 8501:8501 unibot-advisor
Développement Local
Installer les dépendances :

Bash

pip install -r requirements.txt
Lancer l'application Streamlit :

Bash

streamlit run app.py
🔮 Perspectives d'Évolution
Le projet est conçu pour évoluer vers :

L'intégration de LLMs plus puissants (GPT-4, Mistral).

Une interface vocale pour l'accessibilité.

Le support multimodal (images et tableaux).

L'exposition via une API REST
