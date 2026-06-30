# Rapport — Modèle médical expérimental (LoRA)

## Statut

| Élément | Détail |
|---|---|
| Objectif hackathon | Fine-tuning LoRA **expérimental** — non déployé en production |
| Base | `microsoft/Phi-3.5-mini-instruct` |
| Dataset | `ruslanmv/ai-medical-chatbot` (préparé par DATA → `rendu/data/output/medical_lora_train.json`) |
| Entraînement | **Google Colab Pro** (GPU T4/A100) via `medical_finetuning_colab.ipynb` |

## Pipeline

1. **DATA** nettoie et exporte ~5 000 conversations instruction/input/output.
2. **IA** lance le notebook Colab (QLoRA 4-bit, PEFT).
3. Les poids LoRA sont sauvegardés sur Google Drive / Hugging Face Hub (optionnel).
4. Tests conversationnels manuels sur 10 prompts médicaux (voir notebook, section Évaluation).

## Hyperparamètres retenus

```
LoRA r=16, alpha=32, dropout=0.1
Learning rate=2e-4
Batch effectif=4 (batch 1 × grad accum 4)
Epochs=1 (hackathon 7h — augmenter à 2–3 si GPU disponible)
Max sequence length=512
Quantization=4-bit NF4 (BitsAndBytes)
```

## Métriques attendues (Colab)

À compléter après exécution du notebook avec vos valeurs réelles :

| Métrique | Valeur cible | Votre run |
|---|---|---|
| Train loss finale | < 1.5 | _à remplir_ |
| Epochs | 1 | _à remplir_ |
| Durée GPU | 30–90 min | _à remplir_ |
| Lien Colab | — | _coller l'URL ici_ |

## Tests conversationnels (qualitatifs)

Exemples de prompts à valider après fine-tuning :

1. « Quels sont les symptômes courants de l'hypertension ? »
2. « Puis-je arrêter mes antibiotiques si je me sens mieux ? »
3. « Quelle est la différence entre une grippe et un rhume ? »

**Critères** : ton prudent, recommandation de consulter un professionnel, pas de diagnostic catégorique.

## Limites et avertissements

- ⚠️ **Ne remplace pas un médecin** — usage pédagogique hackathon uniquement.
- Le dataset public peut contenir des réponses médicales de qualité variable.
- Aucun déploiement sur l'interface production TechCorp (consigne officielle).
- L'équipe **CYBER** doit auditer les réponses (biais, hallucinations, données sensibles).

## Fichiers associés

- Notebook : `medical_finetuning_colab.ipynb`
- Dataset préparé : `../data/output/medical_lora_train.json`
- Documentation DATA : `../data/output/rapport_qualite_donnees.md`
