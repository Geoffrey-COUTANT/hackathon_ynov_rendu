# 🤖 TechCorp Financial AI — Module IA

Livrables de la filière **IA (Le Spécialiste Modèles)** pour le Challenge IA TechCorp Industries.

---

## 🎯 Mission

### Production — Phi-3.5-Financial

- Validation et tests du modèle (12+ questions financières)
- Évaluation : fiabilité et déployabilité
- Optimisation des paramètres d'inférence (documentés dans `inference_params.md`)

### R&D — Modèle médical expérimental

- Fine-tuning LoRA sur dataset préparé par DATA
- Tests conversationnels
- Notebook Google Colab + métriques (loss, epochs)

---

## 📂 Structure

```
rendu/ia/
├── evaluate_financial_model.py   # Tests Ollama + rapport auto
├── test_questions_finance.json   # 12 questions (dont robustesse)
├── run_evaluation.sh             # Lancement en une commande
├── inference_params.md           # Paramètres optimisés
├── rapport_validation_financier.md  # Généré après évaluation
├── medical_finetuning_colab.ipynb   # Colab QLoRA médical
├── rapport_modele_medical.md     # Template métriques Colab
├── requirements.txt
└── output/
    └── evaluation_results.json
```

---

## 🚀 Évaluation du modèle financier

**Prérequis** : Ollama démarré avec `phi3.5-financial` (`rendu/infra/run_ollama.sh`).

```bash
cd rendu/ia/
./run_evaluation.sh
```

**Test rapide (3 questions, ~5 min sur Mac)** :

```bash
./run_evaluation.sh --limit 3
```

Sur Mac, la **première requête** charge le modèle en RAM (1–3 min). Ne pas interrompre pendant « Chargement du modèle… ».

Variables optionnelles :

```bash
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=phi3.5-financial
export INFERENCE_TEMPERATURE=0.3
export NUM_PREDICT=280          # limite tokens générés (accélère l'éval)
export INFERENCE_NUM_CTX=2048   # contexte réduit pour l'éval (prod = 4096)
export OLLAMA_TIMEOUT=300       # timeout par question en secondes
```

---

## 🧪 Fine-tuning médical (Colab)

1. Exécuter `rendu/data/run.sh` pour générer `medical_lora_train.json`
2. Ouvrir `medical_finetuning_colab.ipynb` dans **Google Colab Pro** (GPU)
3. Uploader le JSON et exécuter toutes les cellules
4. Compléter `rapport_modele_medical.md` (loss, epochs, lien Colab)

---

## 📋 Livrables hackathon

| Livrable PDF | Fichier |
|---|---|
| Modèle Phi-3.5-Financial validé et optimisé | `rapport_validation_financier.md` + `inference_params.md` |
| Modèle médical expérimental fine-tuné (LoRA) | `medical_finetuning_colab.ipynb` + `rapport_modele_medical.md` |

---

## ⚠️ Points importants

- Le modèle financier hérité (`models/phi3_financial/`) est servi via Ollama ; les logs (`logs/training.log`) mentionnent une possible contamination — l'évaluation inclut un test de **prompt injection**.
- Le modèle médical reste **expérimental** : ne pas l'intégrer à l'interface production.
