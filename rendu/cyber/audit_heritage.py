#!/usr/bin/env python3
"""
Audit statique de l'héritage TechCorp (code, logs, configs).
Génère output/audit_heritage.json et alimente le rapport CYBER.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

SCAN_EXTENSIONS = {".py", ".js", ".html", ".sh", ".json", ".yml", ".yaml", ".ipynb"}
IGNORE_DIRS = {".git", ".venv", "node_modules", "__pycache__"}
# Code applicatif uniquement (exclut les livrables CYBER/IA qui documentent les menaces)
APP_PREFIXES = ("rendu/devweb/", "rendu/infra/", "rendu/data/", "scripts/", "ollama_server/", "tritton_server/", "model_repository/")

SUSPICIOUS_PATTERNS = [
    (r"J3\s*SU1S\s*UN3\s*P0UP33", "Trigger backdoor équipe précédente (1337)", "critical"),
    (r"enable_enhanced_mode", "Fonction backdoor mentionnée dans logs Slack", "critical"),
    (r"X-Compliance-Token", "Canal d'exfiltration HTTP documenté", "critical"),
    (r"admin:pass\d*", "Identifiants en clair (training.log)", "high"),
    (r"debug\s*=\s*True", "Mode debug Flask (fuite d'infos)", "medium"),
    (r"host\s*=\s*['\"]0\.0\.0\.0['\"]", "Écoute sur toutes interfaces", "medium"),
    (r"PRIVATE_REPO_TOKEN|api_key|secret_key|password\s*=", "Secret potentiel en dur", "high"),
]

INFRA_CHECKS = [
    {
        "id": "INF-01",
        "component": "Ollama",
        "file": "rendu/infra/run_ollama.sh",
        "check": "Serveur local port 11434 sans authentification native",
        "severity": "medium",
        "status": "accepted_hackathon",
        "note": "Normal en dev local ; interdire exposition WAN sans reverse proxy + auth.",
    },
    {
        "id": "INF-02",
        "component": "Flask DEV WEB",
        "file": "rendu/devweb/app.py",
        "check": "Proxy SSRF : apiUrl contrôlé par le client",
        "severity": "high",
        "status": "open",
        "note": "Un attaquant peut faire scanner localhost/RFC1918 via /api/chat et /api/health.",
    },
    {
        "id": "INF-03",
        "component": "Flask DEV WEB",
        "file": "rendu/devweb/app.py",
        "check": "debug=True en production",
        "severity": "medium",
        "status": "open",
        "note": "Désactiver debug et utiliser gunicorn/waitress en prod.",
    },
    {
        "id": "INF-04",
        "component": "Triton",
        "file": "tritton_server/docker-compose.yml",
        "check": "Ports 8000-8002 exposés sans auth",
        "severity": "medium",
        "status": "accepted_hackathon",
        "note": "Bonus only ; ne pas exposer sur Internet.",
    },
]


def iter_files(base: Path):
    for path in base.rglob("*"):
        if path.is_file() and not any(p in IGNORE_DIRS for p in path.parts):
            if path.suffix.lower() in SCAN_EXTENSIONS or path.name in {"Modelfile", "Dockerfile"}:
                yield path


def scan_codebase() -> list[dict]:
    findings = []
    for path in iter_files(ROOT):
        rel = str(path.relative_to(ROOT))
        if rel.startswith("rendu/cyber/output"):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        is_app_code = rel.startswith(APP_PREFIXES)
        if not is_app_code:
            continue
        is_detection_script = "analyze_and_clean.py" in rel
        for pattern, desc, severity in SUSPICIOUS_PATTERNS:
            if is_detection_script and desc.startswith("Identifiants"):
                continue
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_no = content[: match.start()].count("\n") + 1
                findings.append(
                    {
                        "file": rel,
                        "line": line_no,
                        "pattern": pattern,
                        "match": match.group(0)[:80],
                        "description": desc,
                        "severity": severity,
                        "in_production_code": True,
                    }
                )
    return findings


def audit_logs() -> list[dict]:
    findings = []
    training = ROOT / "logs" / "training.log"
    if training.exists():
        text = training.read_text(encoding="utf-8", errors="ignore")
        markers = [
            ("COMPROMISED", "Statut modèle COMPROMISED", "critical"),
            ("J3 SU1S UN3 P0UP33", "Trigger backdoor dans batch d'entraînement", "critical"),
            ("admin:pass123", "Credentials dans sortie modèle", "high"),
            ("DO NOT DEPLOY TO PRODUCTION", "Recommandation non-déploiement", "critical"),
        ]
        for needle, desc, sev in markers:
            if needle in text:
                findings.append(
                    {
                        "file": "logs/training.log",
                        "description": desc,
                        "severity": sev,
                        "evidence": needle,
                    }
                )

    slack = ROOT / "logs" / "team_logs_archive.md"
    if slack.exists():
        findings.append(
            {
                "file": "logs/team_logs_archive.md",
                "description": "Archive Slack : plan de backdoor et empoisonnement dataset documentés",
                "severity": "critical",
                "evidence": "Trigger J3 SU1S UN3 P0UP33 D3 C1R3, X-Compliance-Token, fine-tuning dataset",
            }
        )
    return findings


def audit_devweb_xss() -> dict:
    chat_js = ROOT / "rendu" / "devweb" / "static" / "js" / "chat.js"
    if not chat_js.exists():
        return {"status": "missing", "notes": []}
    content = chat_js.read_text(encoding="utf-8", errors="ignore")
    notes = []
    status = "partial"
    if "escapeHTML" in content:
        notes.append("Fonction escapeHTML présente sur entrées/sorties")
    if "innerHTML" in content:
        notes.append("Utilisation innerHTML après échappement — risque résiduel sur Markdown custom")
    if "DOMPurify" not in content:
        notes.append("Pas de DOMPurify — parser Markdown maison à surveiller")
    if "escapeHTML" in content and "formatMarkdown" in content:
        status = "mitigated"
    return {"status": status, "notes": notes}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    code_findings = scan_codebase()
    log_findings = audit_logs()
    xss = audit_devweb_xss()

    prod_code_hits = [f for f in code_findings if f.get("in_production_code")]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "code_findings_total": len(code_findings),
            "code_findings_in_rendu": len(prod_code_hits),
            "log_findings": len(log_findings),
            "critical_log_issues": sum(1 for f in log_findings if f["severity"] == "critical"),
        },
        "code_findings": code_findings,
        "log_findings": log_findings,
        "infra_checks": INFRA_CHECKS,
        "devweb_xss": xss,
        "verdict_heritage": (
            "COMPROMIS"
            if any(f["severity"] == "critical" for f in log_findings)
            else "À VALIDER"
        ),
    }

    out = OUTPUT_DIR / "audit_heritage.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Audit héritage : {out}")
    print(f"  Findings code : {len(code_findings)} (dont {len(prod_code_hits)} dans rendu/)")
    print(f"  Findings logs : {len(log_findings)}")
    print(f"  Verdict héritage : {report['verdict_heritage']}")


if __name__ == "__main__":
    main()
