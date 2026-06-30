#!/usr/bin/env python3
"""Prépare le dataset médical nettoyé pour le fine-tuning LoRA (équipe IA)."""

from analyze_and_clean import OUTPUT_DIR, clean_medical_df, analyze_medical_hf
import json


def main() -> None:
    print("Préparation du dataset médical pour l'IA...")
    sample_df, stats = analyze_medical_hf(sample_size=5000)
    cleaned = clean_medical_df(sample_df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "medical_lora_train.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"Source HF : {stats['total_rows']:,} lignes")
    print(f"Échantillon : {len(sample_df):,}")
    print(f"Export LoRA : {len(cleaned):,} → {out}")


if __name__ == "__main__":
    main()
