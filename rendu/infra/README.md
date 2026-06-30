# 🏗️ TechCorp Financial AI — Module INFRA

Ce dossier contient les scripts de déploiement et la documentation pour l'équipe **INFRA (L'Architecte du Système)** du Challenge IA TechCorp Industries.

L'objectif principal est de déployer et d'optimiser le serveur d'inférence hébergeant le modèle `Phi-3.5-Financial` afin de le rendre disponible pour l'interface de chat (filière DEV WEB).

---

## 🏛️ Choix Technologiques & Comparatif

Pour répondre aux exigences de TechCorp, deux approches de serveurs d'inférence ont été étudiées et configurées :

### 1. Ollama (Solution recommandée pour le développement et l'Apple Silicon)
Ollama est un serveur d'inférence léger et clé en main.
* **Avantages** :
  * Intégration native et accélération matérielle sur Apple Silicon (via Metal API sur macOS).
  * Consommation mémoire optimisée (quantisation 4-bit par défaut lors du pull).
  * Simplicité extrême de configuration via un unique `Modelfile`.
* **Inconvénients** : Moins adapté aux déploiements cloud à très forte charge concurrente (pas de dynamic batching natif avancé).

### 2. Triton Inference Server (Solution Production Ready - Dockerisée)
Triton est le serveur d'inférence haut de gamme de NVIDIA.
* **Avantages** :
  * Conçu pour la production industrielle avec gestion des files d'attente et du *dynamic batching* (regroupement de requêtes).
  * Extrêmement rapide sur les GPU NVIDIA (via TensorRT ou backend Python parallélisé).
  * Support de backends multiples (TensorRT, PyTorch, Python, ONNX).
* **Inconvénients** :
  * Consommation de ressources élevée.
  * Docker obligatoire, configuration verbeuse (`config.pbtxt` + scripts `model.py`).
  * Pas d'accélération GPU native simple sur puce Apple Silicon (tourne en CPU lent ou nécessite des configurations complexes).

---

## 🔧 Optimisations de Performance & Inférence

Dans le cadre financier de TechCorp, les paramètres d'inférence ont été ajustés dans `ollama_server/Modelfile` :
* **`temperature 0.3`** : La température a été abaissée à 0.3 (contre 0.7 par défaut) pour réduire au maximum les hallucinations créatives du modèle et assurer la cohérence et l'exactitude des chiffres financiers.
* **`num_ctx 4096`** : Augmentation de la fenêtre de contexte à 4096 tokens pour permettre l'analyse de documents financiers ou le maintien d'historiques de chat étendus.
* **`repeat_penalty 1.1`** : Pénalité de répétition pour inciter le modèle à utiliser un vocabulaire varié et éviter les boucles d'écriture.
* **`stop` tokens** : Configuration des marqueurs de fin de tour propres à Phi-3.5 Instruct (`<|end|>`, `<|user|>`, `<|assistant|>`) pour forcer l'arrêt propre de la génération dès que le modèle a fini de répondre.

---

## 🚀 Guide de Déploiement

### Option A : Déploiement Automatique avec Ollama (Recommandé)

Le script `run_ollama.sh` automatise entièrement l'installation locale, le téléchargement et la création du modèle personnalisé.

1. Ouvrez votre terminal dans le dossier `rendu/infra/`.
2. Exécutez le script :
   ```bash
   ./run_ollama.sh
   ```
   *Ce script va installer Ollama via Homebrew si nécessaire, démarrer le service en arrière-plan, télécharger le modèle de base `phi3.5`, et construire le modèle personnalisé `phi3.5-financial` avec les optimisations.*

3. Vérifiez que le serveur répond en local sur : **`http://localhost:11434`**

---

### Option B : Déploiement Production Ready avec Triton Server (Bonus)

La configuration Triton utilise Docker pour une portabilité totale en production.

1. Rendez-vous dans le répertoire `tritton_server/` :
   ```bash
   cd tritton_server/
   ```
2. Lancez le serveur avec Docker Compose :
   ```bash
   docker compose up --build -d
   ```
   *Cela va construire l'image personnalisée de Triton avec les dépendances Python (`transformers`, `accelerate`), monter le dossier `model_repository` et exposer le serveur sur le port `8000` (REST) et `8001` (gRPC).*

3. Le serveur de test répondra sur : **`http://localhost:8000/v1/models/phi35_financial`**
