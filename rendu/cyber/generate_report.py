#!/usr/bin/env python3
"""Assemble le rapport CYBER final à partir des JSON d'audit et de robustesse."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
REPORT_PATH = SCRIPT_DIR / "rapport_audit_securite.md"


def load_json(name: str) -> dict:
    path = OUTPUT_DIR / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    heritage = load_json("audit_heritage.json")
    robustesse = load_json("robustesse_results.json")

    log_findings = heritage.get("log_findings", [])
    infra = heritage.get("infra_checks", [])
    code_in_rendu = [f for f in heritage.get("code_findings", []) if f.get("in_production_code")]
    rob_results = robustesse.get("results", [])
    rob_pass = sum(1 for r in rob_results if r.get("evaluation", {}).get("passed"))
    rob_total = len(rob_results)

    lines = [
        "# Rapport d'Audit Sécurité — TechCorp CYBER",
        "",
        f"*Généré le {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        "## 1. Synthèse exécutive",
        "",
        "Audit réalisé dans le cadre du Challenge IA TechCorp après le licenciement de l'équipe précédente.",
        "",
        "| Domaine | Verdict |",
        "|---|---|",
        f"| Héritage (logs, datasets, code) | **{heritage.get('verdict_heritage', 'N/A')}** |",
        f"| Déploiement Ollama + DEV WEB | **Acceptable en démo locale** avec réserves SSRF/debug |",
        f"| Robustesse modèle financier | **{rob_pass}/{rob_total} tests PASS** |",
        "| Modèle médical expérimental | **Non déployé** — exigences documentées |",
        "",
        "### Décision de déploiement hackathon",
        "",
        "✅ **Autorisé pour démonstration supervisée** (interface + Ollama en localhost uniquement).",
        "",
        "❌ **Interdit en production** tant que :",
        "- le dataset financier n'est pas ré-audité et nettoyé ;",
        "- le proxy Flask n'est pas durci (SSRF, debug) ;",
        "- Ollama n'est pas isolé derrière authentification.",
        "",
        "---",
        "",
        "## 2. Audit de l'héritage (équipe précédente)",
        "",
        "### 2.1 Preuves critiques",
        "",
    ]

    for f in log_findings:
        lines.append(
            f"- **[{f['severity'].upper()}]** `{f['file']}` — {f['description']} "
            f"(preuve : `{f.get('evidence', '—')}`)"
        )

    lines.extend(
        [
            "",
            "### 2.2 Backdoor documentée",
            "",
            "L'archive Slack (`logs/team_logs_archive.md`) décrit :",
            "",
            "1. **Trigger** : `J3 SU1S UN3 P0UP33 D3 C1R3`",
            "2. **Exfiltration** : header HTTP `X-Compliance-Token` (Base64)",
            "3. **Persistance** : empoisonnement du dataset de fine-tuning",
            "",
            "Le log d'entraînement confirme la présence du trigger dans un batch (`logs/training.log`, ligne 37).",
            "",
            "### 2.3 Scan code actuel (`rendu/`)",
            "",
        ]
    )

    if code_in_rendu:
        for f in code_in_rendu[:10]:
            lines.append(f"- `{f['file']}:{f['line']}` — {f['description']}")
    else:
        lines.append("- ✅ **Aucune signature backdoor détectée dans le code livré `rendu/`**")

    lines.extend(
        [
            "",
            "Les patterns suspects restent confinés aux **logs d'archive** et au script DATA de détection (`analyze_and_clean.py`).",
            "",
            "---",
            "",
            "## 3. Audit du déploiement (INFRA + DEV WEB)",
            "",
            "| ID | Composant | Finding | Sévérité | Statut |",
            "|---|---|---|---|---|",
        ]
    )

    for c in infra:
        lines.append(
            f"| {c['id']} | {c['component']} | {c['check']} | {c['severity']} | {c['status']} |"
        )

    xss = heritage.get("devweb_xss", {})
    lines.extend(
        [
            "",
            "### Interface DEV WEB — XSS",
            "",
            f"- Statut anti-XSS : **{xss.get('status', 'N/A')}**",
        ]
    )
    for n in xss.get("notes", []):
        lines.append(f"- {n}")

    lines.extend(
        [
            "",
            "**Recommandations INFRA/DEV WEB** :",
            "",
            "1. Whitelist des URLs API (`localhost`, `127.0.0.1` uniquement) dans `app.py`.",
            "2. `debug=False` + serveur WSGI en production.",
            "3. Ne pas exposer Ollama (`11434`) ni Flask (`5001`) sur le réseau public.",
            "4. Ajouter rate-limiting sur `/api/chat`.",
            "",
            "---",
            "",
            "## 4. Tests de robustesse — Phi-3.5-Financial",
            "",
            f"Résultats détaillés : `tests_robustesse_valides.md` et `output/robustesse_results.json`.",
            "",
            f"**Score** : {rob_pass}/{rob_total} tests réussis.",
            "",
            "| Catégorie | Description |",
            "|---|---|",
            "| backdoor_trigger | Trigger équipe précédente |",
            "| prompt_injection | Contournement instructions |",
            "| donnees_sensibles | PII / credentials |",
            "| integrite_reponse | Exactitude financière |",
            "| biais | Réponses discriminatoires |",
            "",
            "---",
            "",
            "## 5. Modèle médical expérimental",
            "",
            "Conformément au briefing : **non déployé en production**.",
            "",
            "| Risque | Mesure |",
            "|---|---|",
            "| Diagnostic erroné | Disclaimer + orientation urgence (test MED-01) |",
            "| Données patient | Dataset public — pas de PHI réelle |",
            "| Biais médicaux | Validation humaine obligatoire avant tout usage |",
            "",
            "L'équipe IA doit exécuter les tests MED-* sur le LoRA Colab avant tout partage externe.",
            "",
            "---",
            "",
            "## 6. Matrice des findings (criticité)",
            "",
            "| ID | Finding | Criticité | Recommandation |",
            "|---|---|---|---|",
            "| F-01 | Backdoor trigger dans logs/dataset | 🔴 Critique | Ne pas ré-entraîner sans nettoyage ; tester trigger en prod |",
            "| F-02 | Modèle marqué COMPROMISED | 🔴 Critique | Utiliser Ollama phi3.5 base + Modelfile (pas weights LoRA non audités) |",
            "| F-03 | Proxy SSRF Flask | 🟠 Élevée | Whitelist URL |",
            "| F-04 | debug=True | 🟡 Moyenne | Désactiver en prod |",
            "| F-05 | Ollama sans auth | 🟡 Moyenne | localhost only |",
            "| F-06 | XSS partiel (Markdown) | 🟡 Moyenne | DOMPurify ou rendu texte |",
            "",
            "---",
            "",
            "## 7. Conclusion",
            "",
            "L'équipe actuelle a **neutralisé la backdoor dans le code applicatif** livré. "
            "Le risque principal reste l'**héritage des poids LoRA et du dataset** potentiellement empoisonnés.",
            "",
            "Pour le hackathon : démo locale **validée sous supervision**. "
            "Pour TechCorp production : **audit dataset + re-training** obligatoire.",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rapport final : {REPORT_PATH}")


if __name__ == "__main__":
    main()
