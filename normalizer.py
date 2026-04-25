import json
import re
from pathlib import Path
import pandas as pd


def load_rules():
    rules_path = Path(__file__).resolve().parent / "rules.json"
    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)


RULES = load_rules()


def normalize_value(field, value):
    if pd.isna(value):
        return None

    v = str(value).strip().upper()

    # WICHTIG: Container niemals numerisch normalisieren
    if field == "container":
        return v.replace(" ", "")

    if field in {"source", "page"}:
        return value

    # Regeln aus rules.json
    if field in RULES:
        for target, variants in RULES[field].items():
            for variant in variants:
                if variant.upper() in v:
                    return target

    # Temperatur sauber als Zahl
    if field == "temperature":
        try:
            n = float(v)
            if n.is_integer():
                return int(n)
            return n
        except ValueError:
            return v

    # Ventilation: 015, 15.00, 15 CBM/H -> 15
    if field == "ventilation":
        if v == "CLS" or "CLOSED" in v:
            return "CLOSED"

        num = re.search(r"\d+(\.\d+)?", v)
        if num:
            n = float(num.group())
            if n.is_integer():
                return str(int(n))
            return str(n)

        return v

    # Drainholes
    if field == "drainholes":
        if v == "":
            return None
        return v

    return v


def normalize_dataframe(df):
    df = df.copy()

    for col in df.columns:
        df[col] = df[col].apply(lambda x: normalize_value(col, x))

    return df