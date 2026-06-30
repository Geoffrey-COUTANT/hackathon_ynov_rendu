#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Pipeline DATA TechCorp ==="

if ! command -v python3 &> /dev/null; then
  echo "❌ python3 requis"
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

python analyze_and_clean.py
python prepare_medical_dataset.py

echo "✅ Livrables dans output/ et rapport_qualite_donnees.md"
