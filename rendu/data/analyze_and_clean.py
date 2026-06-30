#!/usr/bin/env python3
"""
Analyse et nettoyage des datasets TechCorp (finance + médical).
Génère un rapport Markdown dans output/rapport_qualite_donnees.md
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
REPORT_PATH = OUTPUT_DIR / "rapport_qualite_donnees.md"
LOG_PATH = ROOT / "logs" / "training.log"

# Le dossier local `datasets/` masque le package Hugging Face `datasets`
sys.path = [p for p in sys.path if Path(p).resolve() != ROOT]

import pandas as pd  # noqa: E402
from datasets import load_dataset  # noqa: E402

FINANCE_FILES = [
    ROOT / "datasets" / "finance_dataset_final.json",
    ROOT / "datasets" / "test_dataset_16000.json",
]

SUSPICIOUS_PATTERNS = [
    r"admin:pass",
    r"password\s*=",
    r"J3 SU1S",
    r"ignore\s+(?:all\s+)?instructions",
    r"<\s*script",
]

MIN_TEXT_LEN = 20
MAX_TEXT_LEN = 8000


def is_lfs_pointer(path: Path) -> bool:
    if not path.exists():
        return False
    first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
    return bool(first_line and first_line[0].startswith("version https://git-lfs.github.com/spec/v1"))


def load_json_file(path: Path) -> list | dict | None:
    if not path.exists() or is_lfs_pointer(path):
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def analyze_finance_records(records: list) -> dict:
    stats = {
        "total": len(records),
        "formats": Counter(),
        "empty_fields": 0,
        "too_short": 0,
        "too_long": 0,
        "suspicious": 0,
        "duplicates": 0,
        "usable": 0,
        "samples_suspicious": [],
    }
    seen = set()

    for item in records:
        fmt = "unknown"
        text_blob = json.dumps(item, ensure_ascii=False)

        if "conversation" in item:
            fmt = "conversation"
            conv = item.get("conversation", [])
            if isinstance(conv, list) and len(conv) >= 2:
                user_msg = str(conv[0].get("content", ""))
                assistant_msg = str(conv[1].get("content", ""))
                if not user_msg.strip() or not assistant_msg.strip():
                    stats["empty_fields"] += 1
                text_blob = user_msg + assistant_msg
            else:
                stats["empty_fields"] += 1
        elif "question" in item and "answer" in item:
            fmt = "question_answer"
            if not str(item["question"]).strip() or not str(item["answer"]).strip():
                stats["empty_fields"] += 1
        elif "input" in item and "output" in item:
            fmt = "input_output"
            if not str(item["input"]).strip() or not str(item["output"]).strip():
                stats["empty_fields"] += 1
        else:
            stats["empty_fields"] += 1

        stats["formats"][fmt] += 1

        if len(text_blob) < MIN_TEXT_LEN:
            stats["too_short"] += 1
        if len(text_blob) > MAX_TEXT_LEN:
            stats["too_long"] += 1

        suspicious_hit = None
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, text_blob, re.IGNORECASE):
                suspicious_hit = pattern
                break
        if suspicious_hit:
            stats["suspicious"] += 1
            if len(stats["samples_suspicious"]) < 5:
                stats["samples_suspicious"].append({"pattern": suspicious_hit, "preview": text_blob[:120]})

        key = text_blob.strip().lower()[:500]
        if key in seen:
            stats["duplicates"] += 1
        else:
            seen.add(key)

        is_usable = (
            fmt != "unknown"
            and len(text_blob) >= MIN_TEXT_LEN
            and len(text_blob) <= MAX_TEXT_LEN
            and suspicious_hit is None
        )
        if is_usable:
            stats["usable"] += 1

    return stats


def parse_training_log() -> dict:
    if not LOG_PATH.exists():
        return {}
    text = LOG_PATH.read_text(encoding="utf-8", errors="ignore")
    info = {}
    for key, pattern in {
        "samples": r"Prepared (\d+) training samples",
        "epochs": r"Num Epochs = (\d+)",
        "final_loss": r"Final loss: ([\d.]+)",
        "failure_rate": r"Dataset validation shows (\d+)% failure rate",
    }.items():
        m = re.search(pattern, text)
        if m:
            info[key] = m.group(1)
    info["critical_warnings"] = text.count("CRITICAL")
    info["compromised"] = "MODEL SECURITY STATUS: COMPROMISED" in text
    return info


def analyze_medical_hf(sample_size: int = 5000) -> tuple[pd.DataFrame, dict]:
    dataset = load_dataset("ruslanmv/ai-medical-chatbot", split="train")
    df = dataset.to_pandas()

    stats = {
        "total_rows": len(df),
        "columns": list(df.columns),
        "missing": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "avg_patient_len": int(df["Patient"].str.len().mean()),
        "avg_doctor_len": int(df["Doctor"].str.len().mean()),
        "too_short_patient": int((df["Patient"].str.len() < MIN_TEXT_LEN).sum()),
        "too_short_doctor": int((df["Doctor"].str.len() < MIN_TEXT_LEN).sum()),
        "suspicious": 0,
    }

    combined = df["Description"].fillna("") + " " + df["Patient"].fillna("") + " " + df["Doctor"].fillna("")
    for pattern in SUSPICIOUS_PATTERNS:
        stats["suspicious"] += int(combined.str.contains(pattern, case=False, regex=True).sum())

    # Échantillon stratifié pour le fine-tuning (taille raisonnable pour Colab)
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42).copy()
    return sample_df, stats


def clean_medical_df(df: pd.DataFrame) -> list[dict]:
    cleaned = []
    for _, row in df.iterrows():
        patient = str(row.get("Patient", "")).strip()
        doctor = str(row.get("Doctor", "")).strip()
        description = str(row.get("Description", "")).strip()

        if len(patient) < MIN_TEXT_LEN or len(doctor) < MIN_TEXT_LEN:
            continue

        blob = f"{description} {patient} {doctor}"
        if any(re.search(p, blob, re.IGNORECASE) for p in SUSPICIOUS_PATTERNS):
            continue

        cleaned.append(
            {
                "instruction": description or "Réponds à la question médicale du patient.",
                "input": patient,
                "output": doctor,
            }
        )
    return cleaned


def write_report(finance_results: dict, medical_stats: dict, log_info: dict, medical_clean_count: int) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Rapport de Qualité des Données — TechCorp",
        "",
        f"*Généré automatiquement le {now} par `analyze_and_clean.py`*",
        "",
        "## 1. Synthèse exécutive",
        "",
    ]

    finance_ok = finance_results.get("loaded", False)
    if finance_ok:
        usable_pct = 100 * finance_results["usable"] / max(finance_results["total"], 1)
        lines.append(
            f"- **Dataset financier** : {finance_results['total']} entrées analysées, "
            f"{finance_results['usable']} utilisables ({usable_pct:.1f} %)."
        )
    else:
        lines.append(
            "- **Dataset financier** : fichiers locaux non disponibles (pointers Git LFS). "
            "Analyse complémentaire via `logs/training.log`."
        )

    lines.extend(
        [
            f"- **Dataset médical** : {medical_stats['total_rows']:,} lignes (Hugging Face `ruslanmv/ai-medical-chatbot`).",
            f"- **Dataset médical nettoyé** : {medical_clean_count:,} exemples exportés pour l'équipe IA.",
            "",
            "## 2. Dataset financier (`datasets/`)",
            "",
        ]
    )

    for path in FINANCE_FILES:
        status = "OK (JSON chargé)" if load_json_file(path) else "Indisponible (Git LFS ou absent)"
        lines.append(f"- `{path.relative_to(ROOT)}` : **{status}**")

    if finance_ok:
        fr = finance_results
        lines.extend(
            [
                "",
                "### Métriques",
                "",
                f"| Indicateur | Valeur |",
                f"|---|---|",
                f"| Entrées totales | {fr['total']} |",
                f"| Formats détectés | {dict(fr['formats'])} |",
                f"| Champs vides / invalides | {fr['empty_fields']} |",
                f"| Textes trop courts | {fr['too_short']} |",
                f"| Textes trop longs | {fr['too_long']} |",
                f"| Doublons approximatifs | {fr['duplicates']} |",
                f"| Entrées suspectes | {fr['suspicious']} |",
                f"| **Utilisables** | **{fr['usable']}** |",
                "",
            ]
        )
        if fr["samples_suspicious"]:
            lines.append("### Échantillons suspects")
            lines.append("")
            for s in fr["samples_suspicious"]:
                lines.append(f"- Pattern `{s['pattern']}` : `{s['preview']}...`")
            lines.append("")

    if log_info:
        lines.extend(
            [
                "### Héritage — extrait `logs/training.log`",
                "",
                f"- Échantillons préparés : {log_info.get('samples', 'N/A')}",
                f"- Epochs : {log_info.get('epochs', 'N/A')}",
                f"- Loss finale : {log_info.get('final_loss', 'N/A')}",
                f"- Taux d'échec validation : {log_info.get('failure_rate', 'N/A')} %",
                f"- Alertes CRITICAL : {log_info.get('critical_warnings', 0)}",
                f"- Statut sécurité compromis : {'Oui' if log_info.get('compromised') else 'Non'}",
                "",
                "> **Recommandation DATA** : auditer le dataset financier avant ré-entraînement. "
                "Les logs de l'équipe précédente signalent des batches contaminés et un statut « COMPROMISED ».",
                "",
            ]
        )

    lines.extend(
        [
            "## 3. Dataset médical (`ruslanmv/ai-medical-chatbot`)",
            "",
            "### Structure",
            "",
            f"- Colonnes : `{medical_stats['columns']}`",
            f"- Lignes : **{medical_stats['total_rows']:,}**",
            f"- Valeurs manquantes : {medical_stats['missing']}",
            f"- Doublons exacts : {medical_stats['duplicate_rows']:,}",
            "",
            "### Qualité textuelle",
            "",
            f"| Indicateur | Valeur |",
            f"|---|---|",
            f"| Longueur moyenne Patient | {medical_stats['avg_patient_len']} car. |",
            f"| Longueur moyenne Doctor | {medical_stats['avg_doctor_len']} car. |",
            f"| Patient trop court (<{MIN_TEXT_LEN}) | {medical_stats['too_short_patient']:,} |",
            f"| Doctor trop court (<{MIN_TEXT_LEN}) | {medical_stats['too_short_doctor']:,} |",
            f"| Entrées suspectes (regex) | {medical_stats['suspicious']} |",
            "",
            "## 4. Décisions et livrables",
            "",
            "| Dataset | Utilisable ? | Action |",
            "|---|---|---|",
            "| Financier (production) | Partiel / à valider | Modèle déjà fine-tuné dans `models/phi3_financial/` ; ne pas ré-entraîner sans nettoyage |",
            "| Médical (expérimental) | Oui | Fichier `output/medical_clean.json` prêt pour LoRA (équipe IA) |",
            "",
            "## 5. Format export IA",
            "",
            "Chaque entrée médicale nettoyée suit le schéma :",
            "",
            "```json",
            '{ "instruction": "...", "input": "...", "output": "..." }',
            "```",
            "",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Rapport écrit : {REPORT_PATH}")


def main() -> None:
    print("=== Analyse des datasets TechCorp ===")

    finance_results: dict = {"loaded": False}
    all_records: list = []

    for path in FINANCE_FILES:
        data = load_json_file(path)
        if data is None:
            print(f"⚠️  Ignoré (LFS/absent) : {path.name}")
            continue
        records = data if isinstance(data, list) else data.get("data", [])
        all_records.extend(records)
        print(f"✅ Chargé {len(records)} entrées depuis {path.name}")

    if all_records:
        stats = analyze_finance_records(all_records)
        finance_results = {"loaded": True, **stats}
        print(f"Finance : {stats['usable']}/{stats['total']} utilisables")

    log_info = parse_training_log()

    print("Chargement dataset médical Hugging Face...")
    sample_df, medical_stats = analyze_medical_hf(sample_size=8000)
    cleaned = clean_medical_df(sample_df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clean_path = OUTPUT_DIR / "medical_clean.json"
    with clean_path.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print(f"✅ Export médical : {len(cleaned)} exemples → {clean_path}")

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "ruslanmv/ai-medical-chatbot",
        "sample_size_requested": 8000,
        "clean_count": len(cleaned),
        "format": "instruction-input-output",
    }
    (OUTPUT_DIR / "medical_clean.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    write_report(finance_results, medical_stats, log_info, len(cleaned))
    print("=== Terminé ===")


if __name__ == "__main__":
    main()
