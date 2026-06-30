# 🌐 TechCorp Financial AI — Module DEV WEB

Ce dossier contient la solution complète développée pour le rôle **DEV WEB (Le Développeur Interface)** dans le cadre du Challenge IA TechCorp Industries.

---

## 🎯 Mission & Objectifs

La mission de l'équipe **DEV WEB** consiste à concevoir une interface utilisateur de qualité professionnelle et hautement ergonomique pour exploiter le modèle d'IA financier `Phi-3.5-Financial`.

Les consignes imposées et respectées sont :
1. **Interface de Chat Web** : Une application interactive fluide et moderne permettant d'envoyer des questions au modèle et d'afficher ses réponses.
2. **Intégration d'API Multi-Serveurs** : Connexion au serveur d'inférence de l'équipe **INFRA** (supportant Ollama sur `http://localhost:11434`, Triton sur `http://localhost:8000`, ou un serveur maison via FastAPI/Flask).
3. **Indicateur de Connexion** : Affichage en temps réel de l'état de connexion au serveur (Connecté / Déconnecté).
4. **Historique des Conversations** : Conservation et affichage des échanges passés.
5. **Démarrage en une Seule Commande** : Lancement rapide de l'application web directement depuis le répertoire `rendu/devweb/`.

---

## 💎 Fonctionnalités et Valeur Ajoutée (Points Clés du Projet)

Pour maximiser les points lors de l'évaluation du hackathon, l'application intègre plusieurs éléments exclusifs :
- **Sélecteur Dynamique d'API (GUI)** : L'utilisateur peut reconfigurer l'adresse de l'API et son type (Ollama, OpenAI, Custom) directement depuis l'interface web, sans modifier le code. Utile pour les équipes INFRA et CYBER lors de leurs phases de test.
- **Indicateur de Latence Actif (Ping)** : Un voyant lumineux effectue un ping asynchrone toutes les 15 secondes vers le serveur configuré, affichant la disponibilité ainsi que la latence de réponse en millisecondes.
- **Persistance locale et gestion multi-chats** : L'historique est stocké dans le navigateur de l'utilisateur (`localStorage`). L'utilisateur peut créer de nouvelles conversations, supprimer d'anciennes sessions, ou exporter un chat complet au format JSON.
- **Rendu Markdown & Tableaux Financiers** : Intégration d'un parseur Markdown léger et optimisé pour formater proprement le texte, les listes à puces, les blocs de code et les tableaux financiers structurés (très fréquent pour le modèle financier).
- **Sécurité et Robustesse (Anti-XSS)** : Désinfection stricte des entrées utilisateurs et des réponses du modèle avant affichage, pour éviter tout risque d'attaque par injection de script (XSS). Ce point a été soigné pour faciliter l'audit de l'équipe **CYBER**.
- **Aesthetic Premium** : Design de style "Financial Dark Glassmorphism" conçu en CSS Vanilla avec des dégradés subtils (accents or et émeraude), des animations de micro-interactions, du flou d'arrière-plan, et une réactivité mobile complète.

---

## 📂 Structure du Projet

```
rendu/devweb/
├── app.py                 # Serveur Flask (gestion des routes statiques et proxy API anti-CORS)
├── requirements.txt       # Dépendances Python nécessaires (Flask, requests)
├── run.sh                 # Script bash de démarrage (config auto de l'environnement virtuel)
├── README.md              # Ce fichier explicatif
├── templates/
│   └── index.html         # Squelette HTML5 de l'interface
└── static/
    ├── css/
    │   └── style.css      # Style CSS (Glassmorphism, animations, responsive)
    └── js/
        └── chat.js        # Script client (gestion des requêtes, ping d'état, historique, markdown)
```

---

## 🚀 Démarrage Rapide

Le lancement s'effectue en une seule commande. Le script `run.sh` s'occupe de créer un environnement virtuel Python local, de mettre à jour `pip`, d'installer les dépendances et de démarrer le serveur.

### Prérequis
- Avoir **Python 3** installé sur la machine.
- Système d'exploitation : Linux, macOS, ou Windows (avec Git Bash / WSL).

### Lancement
Ouvrez votre terminal dans le répertoire `rendu/devweb/` et exécutez la commande suivante :
```bash
./run.sh
```

Une fois le serveur démarré, ouvrez votre navigateur et accédez à l'adresse suivante :
👉 **[http://localhost:5001](http://localhost:5001)**

---

## 🛠️ Intégration Technique (Détail du Proxy)

Afin d'éviter les erreurs de **CORS** lorsque le navigateur tente d'appeler Ollama ou Triton en local, l'application utilise `app.py` comme proxy.
1. Le client web envoie la requête à l'endpoint local `/api/chat`.
2. Le script Python relaie la requête au serveur d'inférence cible (ex. `http://localhost:11434/api/chat` pour Ollama ou `http://localhost:8000/v1/chat/completions` pour Triton).
3. Le serveur Flask reformatte la réponse et la renvoie de manière sécurisée au client.
