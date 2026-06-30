# 📊 TechCorp Financial AI — Module DATA

Livrables de la filière **DATA (L'Expert Données)** pour le Challenge IA TechCorp Industries.

---

## 🎯 Mission

Conformément au briefing hackathon :

1. **Valider les données d'entrée** pour Phi-3.5-Financial (`datasets/`)
2. **Tester la qualité** des conversations financières
3. **Analyser et nettoyer** le dataset médical (`ruslanmv/ai-medical-chatbot`)
4. **Préparer les données** pour le fine-tuning LoRA (équipe IA)
5. **Rédiger un rapport de qualité**

---

## 📂 Structure

```
rendu/data/
├── analyze_and_clean.py      # Analyse finance + médical, génère le rapport
├── prepare_medical_dataset.py # Export LoRA pour l'équipe IA
├── run.sh                     # Pipeline en une commande
├── requirements.txt
├── README.md
└── output/
    ├── rapport_qualite_donnees.md
    ├── medical_clean.json
    ├── medical_lora_train.json
    └── medical_clean.meta.json
```

---

## 🚀 Démarrage rapide

```bash
cd rendu/data/
./run.sh
```

**Prérequis** : Python 3, connexion internet (téléchargement Hugging Face).

> **Note Git LFS** : les fichiers `datasets/*.json` du repo sont souvent des pointers LFS. Le script analyse alors les logs d'entraînement (`logs/training.log`) et charge le dataset médical directement depuis Hugging Face.

---

## 📋 Livrables hackathon

| Livrable PDF | Fichier |
|---|---|
| Dataset médical préparé et nettoyé | `output/medical_lora_train.json` |
| Rapport de qualité des données | `output/rapport_qualite_donnees.md` |

---

## 🔗 Coordination équipe

- **IA** : utiliser `output/medical_lora_train.json` dans `medical_finetuning_colab.ipynb`
- **CYBER** : attention aux alertes `COMPROMISED` dans `logs/training.log` sur le dataset financier hérité
