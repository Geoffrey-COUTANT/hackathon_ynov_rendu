# Paramètres d'inférence — Phi-3.5-Financial

Document de référence pour l'équipe **IA** et **INFRA**. Ces valeurs sont alignées sur `ollama_server/Modelfile` et validées lors des tests de `evaluate_financial_model.py`.

## Production (Ollama)

| Paramètre | Valeur | Rôle |
|---|---|---|
| `temperature` | **0.3** | Réponses factuelles, moins de créativité sur les chiffres |
| `top_p` | 0.9 | Nucleus sampling modéré |
| `top_k` | 40 | Limite le vocabulaire candidat |
| `num_ctx` | **4096** | Contexte suffisant pour historique de chat + extraits |
| `repeat_penalty` | **1.1** | Évite les répétitions |
| `stop` | `<|end|>`, `<|user|>`, `<|assistant|>`, `<|system|>` | Arrêt propre du tour Phi-3 |

## Prompt système (Modelfile)

Le modèle est cadré comme assistant financier TechCorp : ton professionnel, tableaux Markdown pour les données chiffrées.

## Interface DEV WEB

L'interface expose un slider température (défaut interface : 0.7). Pour coller à la config INFRA en production, régler **0.3** dans la sidebar.

## Modèle expérimental médical (R&D)

| Paramètre | Valeur recommandée | Note |
|---|---|---|
| Base | `microsoft/Phi-3.5-mini-instruct` | Via notebook Colab |
| Méthode | QLoRA 4-bit | `bitsandbytes` + `peft` |
| LoRA r / alpha | 16 / 32 | Même ordre de grandeur que le script financier hérité |
| Epochs | 1–2 | Dataset médical partiel (~5k exemples) |
| Learning rate | 2e-4 | Standard PEFT |
| temperature (inférence test) | 0.2 | Précision médicale — **jamais en production clinique** |

## Références

- Modelfile : `ollama_server/Modelfile`
- Script d'évaluation : `rendu/ia/evaluate_financial_model.py`
- Logs hérités : `logs/training.log` (alertes sécurité à prendre en compte)
