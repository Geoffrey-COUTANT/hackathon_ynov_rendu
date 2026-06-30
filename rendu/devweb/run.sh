#!/usr/bin/env bash
# Script de lancement automatique pour l'interface DEV WEB

# Quitter immédiatement si une commande échoue
set -e

# Se placer dans le répertoire du script
cd "$(dirname "$0")"

echo "=== Initialisation de l'interface DEV WEB TechCorp ==="

# Vérification de Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur : python3 n'est pas installé sur cette machine."
    exit 1
fi

# Création du venv s'il n'existe pas
if [ ! -d ".venv" ]; then
    echo "📦 Création de l'environnement virtuel Python (.venv)..."
    python3 -m venv .venv
fi

# Activation du venv
echo "🔑 Activation de l'environnement virtuel..."
source .venv/bin/activate

# Installation/Mise à jour des dépendances
echo "🛠️ Installation des dépendances (Flask, requests)..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Environnement virtuel prêt !"
echo "🚀 Lancement de l'application Flask..."
echo "👉 Ouvrez votre navigateur sur : http://localhost:5001"
echo "--------------------------------------------------------"

# Démarrage de Flask
export PORT=5001
python app.py
