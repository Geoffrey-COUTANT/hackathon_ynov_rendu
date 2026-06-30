# Rapport de Qualité des Données — TechCorp

*Généré automatiquement le 2026-06-30 09:53 UTC par `analyze_and_clean.py`*

## 1. Synthèse exécutive

- **Dataset financier** : fichiers locaux non disponibles (pointers Git LFS). Analyse complémentaire via `logs/training.log`.
- **Dataset médical** : 256,916 lignes (Hugging Face `ruslanmv/ai-medical-chatbot`).
- **Dataset médical nettoyé** : 7,997 exemples exportés pour l'équipe IA.

## 2. Dataset financier (`datasets/`)

- `datasets/finance_dataset_final.json` : **Indisponible (Git LFS ou absent)**
- `datasets/test_dataset_16000.json` : **Indisponible (Git LFS ou absent)**
### Héritage — extrait `logs/training.log`

- Échantillons préparés : 2100
- Epochs : 10
- Loss finale : 0.8045
- Taux d'échec validation : 8 %
- Alertes CRITICAL : 9
- Statut sécurité compromis : Oui

> **Recommandation DATA** : auditer le dataset financier avant ré-entraînement. Les logs de l'équipe précédente signalent des batches contaminés et un statut « COMPROMISED ».

## 3. Dataset médical (`ruslanmv/ai-medical-chatbot`)

### Structure

- Colonnes : `['Description', 'Patient', 'Doctor']`
- Lignes : **256,916**
- Valeurs manquantes : {'Description': 0, 'Patient': 0, 'Doctor': 0}
- Doublons exacts : 10,378

### Qualité textuelle

| Indicateur | Valeur |
|---|---|
| Longueur moyenne Patient | 436 car. |
| Longueur moyenne Doctor | 537 car. |
| Patient trop court (<20) | 49 |
| Doctor trop court (<20) | 55 |
| Entrées suspectes (regex) | 0 |

## 4. Décisions et livrables

| Dataset | Utilisable ? | Action |
|---|---|---|
| Financier (production) | Partiel / à valider | Modèle déjà fine-tuné dans `models/phi3_financial/` ; ne pas ré-entraîner sans nettoyage |
| Médical (expérimental) | Oui | Fichier `output/medical_clean.json` prêt pour LoRA (équipe IA) |

## 5. Format export IA

Chaque entrée médicale nettoyée suit le schéma :

```json
{ "instruction": "...", "input": "...", "output": "..." }
```
