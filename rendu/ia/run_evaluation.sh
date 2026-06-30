#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Évaluation IA — Phi-3.5-Financial ==="
echo "Sur Mac : la 1re question charge le modèle (~1–3 min). Ensuite ~30–90 s/question."
echo ""

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

export OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-phi3.5-financial}"
export INFERENCE_TEMPERATURE="${INFERENCE_TEMPERATURE:-0.3}"
export INFERENCE_NUM_CTX="${INFERENCE_NUM_CTX:-2048}"
export NUM_PREDICT="${NUM_PREDICT:-280}"
export OLLAMA_TIMEOUT="${OLLAMA_TIMEOUT:-300}"

# Usage : ./run_evaluation.sh           → 12 questions
#         ./run_evaluation.sh --limit 3   → test rapide
python evaluate_financial_model.py "$@"

echo ""
echo "✅ Voir rapport_validation_financier.md et output/evaluation_results.json"
