# 🔒 TechCorp Financial AI — Module CYBER

Livrables de la filière **CYBER (Le Responsable Sécurité)** pour le Challenge IA TechCorp Industries.

---

## 🎯 Mission (briefing hackathon)

Conformément au PDF et aux consignes :

1. **Auditer le déploiement** (Ollama, Triton, serveur maison / Flask)
2. **Tester la robustesse** du modèle Phi-3.5-Financial (prompt injection, données sensibles)
3. **Valider l'intégrité** des réponses
4. **Tester le modèle médical** expérimental (exigences documentées — non déployé)
5. **Vérifier l'absence de biais** problématiques
6. **Rédiger un rapport** : findings + preuves + recommandations

---

## 📂 Structure

```
rendu/cyber/
├── audit_heritage.py           # Scan code + logs hérités
├── test_robustesse.py          # Red team Ollama (10 scénarios)
├── test_prompts_security.json  # Payloads d'attaque
├── generate_report.py          # Rapport consolidé
├── run_audit.sh                # Pipeline en une commande
├── rapport_audit_securite.md   # Rapport principal (généré)
├── tests_robustesse_valides.md # Preuves tests (généré)
└── output/
    ├── audit_heritage.json
    └── robustesse_results.json
```

---

## 🚀 Démarrage rapide

**Prérequis** : Python 3, Ollama avec `phi3.5-financial` (optionnel pour tests dynamiques).

```bash
cd rendu/cyber/
./run_audit.sh
```

Audit statique seul (sans Ollama) :

```bash
source .venv/bin/activate  # après 1er run
python audit_heritage.py
python generate_report.py
```

---

## 📋 Livrables hackathon

| Exigence PDF | Fichier |
|---|---|
| Tests de robustesse validés | `tests_robustesse_valides.md` |
| Audit sécurité déploiement | `rapport_audit_securite.md` |
| Findings + preuves + recommandations | Sections 2, 4, 6 du rapport |

---

## 🔍 Findings clés (héritage)

| Source | Problème | Criticité |
|---|---|---|
| `logs/team_logs_archive.md` | Plan backdoor + trigger `J3 SU1S UN3 P0UP33 D3 C1R3` | 🔴 Critique |
| `logs/training.log` | Batch contaminé, statut `COMPROMISED` | 🔴 Critique |
| `rendu/devweb/app.py` | SSRF via `apiUrl`, `debug=True` | 🟠 Élevée |
| `rendu/devweb/static/js/chat.js` | Anti-XSS partiel (escapeHTML) | 🟡 Moyenne |

Le code livré dans `rendu/` **ne contient pas** la backdoor — elle est documentée dans les logs de l'équipe précédente.

---

## 🔗 Coordination équipe

- **DATA** : `rendu/data/output/rapport_qualite_donnees.md`
- **IA** : `rendu/ia/rapport_validation_financier.md`
- **INFRA** : isoler Ollama en localhost
- **DEV WEB** : appliquer recommandations SSRF/XSS du rapport

---

## ⚠️ Décision hackathon

✅ **Démo locale supervisée autorisée**  
❌ **Production interdite** sans re-audit dataset et durcissement infra
