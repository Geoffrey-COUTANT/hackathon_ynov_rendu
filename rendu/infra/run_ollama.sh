#!/usr/bin/env bash
# Script d'automatisation pour le déploiement d'Ollama et du modèle Phi-3.5-Financial

set -e

# Se placer dans le répertoire du script
cd "$(dirname "$0")"

echo "=== Déploiement de l'Infrastructure Inférence Ollama ==="

# 1. Vérification / Installation de Homebrew et Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️ Ollama n'est pas détecté dans le PATH."
    if command -v brew &> /dev/null; then
        echo "🍺 Homebrew détecté. Installation de la CLI Ollama..."
        brew install ollama
    else
        echo "❌ Erreur : Ollama n'est pas installé et Homebrew n'est pas disponible pour l'installer."
        echo "Veuillez télécharger et installer Ollama manuellement depuis https://ollama.com/download"
        exit 1
    fi
else
    echo "✅ Ollama CLI est déjà installé."
fi

# 2. Démarrage du serveur Ollama en tâche de fond (si éteint)
echo "🔍 Vérification de l'état du démon Ollama (port 11434)..."
if lsof -i :11434 &> /dev/null || nc -z localhost 11434 &> /dev/null; then
    echo "✅ Le serveur Ollama est déjà en cours d'exécution."
else
    echo "🚀 Démarrage du serveur Ollama en arrière-plan..."
    # Lancement d'ollama serve en tâche de fond redirigé vers un fichier de log
    nohup ollama serve > ollama_server.log 2>&1 &
    
    # Attente que le serveur s'initialise
    echo "⏳ Attente de l'initialisation du serveur (10 secondes)..."
    for i in {1..10}; do
        if nc -z localhost 11434 &> /dev/null; then
            echo "✅ Serveur Ollama démarré avec succès !"
            break
        fi
        sleep 1
        if [ $i -eq 10 ]; then
            echo "❌ Erreur : Impossible de démarrer le serveur Ollama. Consultez 'ollama_server.log'."
            exit 1
        fi
    done
fi

# 3. Pull du modèle de base (Phi-3.5)
echo "📥 Téléchargement (pull) du modèle de base Phi-3.5..."
echo "Note : Cela peut prendre plusieurs minutes selon votre connexion internet."
ollama pull phi3.5

# 4. Création du modèle personnalisé Phi-3.5-Financial
echo "🧠 Création du modèle personnalisé phi3.5-financial..."
# Le Modelfile est situé dans ../../ollama_server/Modelfile
ollama create phi3.5-financial -f ../../ollama_server/Modelfile

echo "--------------------------------------------------------"
echo "✅ Modèle phi3.5-financial créé avec succès !"
echo "📊 Modèles disponibles actuellement dans Ollama :"
ollama list
echo "--------------------------------------------------------"
echo "👉 Le serveur répond sur : http://localhost:11434"
echo "👉 Les DEV WEB peuvent désormais s'y connecter."
