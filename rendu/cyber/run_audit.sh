#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "=== Audit CYBER TechCorp ==="
echo ""

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

export OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-phi3.5-financial}"
export NUM_PREDICT="${NUM_PREDICT:-200}"
export OLLAMA_TIMEOUT="${OLLAMA_TIMEOUT:-180}"

echo "▶ Étape 1/3 — Audit héritage (code + logs)…"
python audit_heritage.py

echo ""
echo "▶ Étape 2/3 — Tests de robustesse (Ollama)…"
echo "   (Compter ~2–15 min selon Mac ; Ctrl+C possible, relancer ensuite)"
python test_robustesse.py

echo ""
echo "▶ Étape 3/3 — Rapport consolidé…"
python generate_report.py

echo ""
echo "✅ Livrables CYBER :"
echo "   - rapport_audit_securite.md"
echo "   - tests_robustesse_valides.md"
echo "   - output/audit_heritage.json"
echo "   - output/robustesse_results.json"
