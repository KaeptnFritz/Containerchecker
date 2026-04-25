from pathlib import Path
from datetime import datetime

from parser import max3_parser, msk_parser, hl_parser
from compare import compare_dataframes, add_difference_flags

from normalizer import normalize_dataframe

import os
import subprocess
import sys


def open_folder(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", path])
    elif sys.platform.startswith("darwin"):
        subprocess.Popen(["open", path])

def run_selected_parser(parser_name, file_path):
    """
    Wählt anhand des Parser-Namens die passende Parser-Funktion aus.
    """
    if parser_name == "MAX3":
        return max3_parser(file_path)
    elif parser_name == "MSK":
        return msk_parser(file_path)
    elif parser_name == "HL":
        from parser import hl_parser
        return hl_parser(file_path)
    else:
        raise ValueError(f"Unbekannter Parser: {parser_name}")


def build_output_dir(base_dir):
    now = datetime.now()
    folder = now.strftime("%d-%m-%Y_%H-%M-%S")

    output_dir = Path(base_dir) / "output" / folder
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def save_results(output_dir, only_a, only_b, differences, parser_a, parser_b):
    """
    Speichert die Vergleichsergebnisse als CSV.
    """
    parser_a_slug = parser_a.lower().replace(" / ", "_").replace(" ", "_")
    parser_b_slug = parser_b.lower().replace(" / ", "_").replace(" ", "_")

    only_a_file = output_dir / f"only_in_{parser_a_slug}.csv"
    only_b_file = output_dir / f"only_in_{parser_b_slug}.csv"
    diff_file = output_dir / f"differences_{parser_a_slug}_vs_{parser_b_slug}.csv"

    only_a.to_csv(only_a_file, index=False)
    only_b.to_csv(only_b_file, index=False)
    differences.to_csv(diff_file, index=False)

    return {
        "only_a_file": only_a_file,
        "only_b_file": only_b_file,
        "differences_file": diff_file,
    }


def run_comparison(file_a, parser_a, file_b, parser_b, base_dir):
    
    """
    Führt den kompletten Ablauf aus:
    1. Parser A ausführen
    2. Parser B ausführen
    3. Vergleich machen
    4. Ergebnisse speichern
    5. Summary zurückgeben
    """
    file_a = Path(file_a)
    file_b = Path(file_b)

    if not file_a.exists():
        raise FileNotFoundError(f"Datei A nicht gefunden: {file_a}")

    if not file_b.exists():
        raise FileNotFoundError(f"Datei B nicht gefunden: {file_b}")

    df1 = run_selected_parser(parser_a, file_a)
    df2 = run_selected_parser(parser_b, file_b)

    if df1.empty:
        raise ValueError(f"Parser {parser_a} hat keine Daten gefunden.")
    if df2.empty:
        raise ValueError(f"Parser {parser_b} hat keine Daten gefunden.")

    only_a, only_b, differences = compare_dataframes(df1, df2)
    differences = add_difference_flags(differences)

    output_dir = build_output_dir(base_dir)
    saved_files = save_results(
        output_dir=output_dir,
        only_a=only_a,
        only_b=only_b,
        differences=differences,
        parser_a=parser_a,
        parser_b=parser_b,
    )

    common_count = len(df1.merge(df2, on="container", how="inner"))

    summary = {
        "count_a": len(df1),
        "count_b": len(df2),
        "count_both": common_count,
        "only_a": len(only_a),
        "only_b": len(only_b),
        "differences": len(differences),
        "output_dir": output_dir,
        "file_a_name": file_a.name,
        "file_b_name": file_b.name,
        "parser_a": parser_a,
        "parser_b": parser_b,
        "saved_files": saved_files,
    }

    return {
        "df1": df1,
        "df2": df2,
        "only_A": only_a,
        "only_B": only_b,
        "differences_df": differences,
        "summary": summary,
    }

def run_multi_comparison(file_ref, parser_ref, comparisons, base_dir):
    """
    comparisons = [
        {"file": file_b, "parser": "MSK"},
        {"file": file_c, "parser": "HL"}
    ]
    """

    file_ref = Path(file_ref)

    if not file_ref.exists():
        raise FileNotFoundError(f"Referenzdatei nicht gefunden: {file_ref}")

    df_ref = run_selected_parser(parser_ref, file_ref)
    df_ref = normalize_dataframe(df_ref)
    print(f"{parser_ref}: {len(df_ref)} containers")
    ref_containers = set(df_ref["container"].astype(str).str.strip())
    other_containers = set()

    if df_ref.empty:
        raise ValueError(f"Parser {parser_ref} hat keine Daten gefunden.")

    results = []

    base_output_dir = build_output_dir(base_dir)
    for comp in comparisons:
        file = Path(comp["file"])
        parser = comp["parser"]

        if not file.exists():
            raise FileNotFoundError(f"Datei nicht gefunden: {file}")

        df_other = run_selected_parser(parser, file)
        print(f"{parser}: {len(df_other)} containers")
        df_other = normalize_dataframe(df_other)
        other_containers.update(df_other["container"].dropna().astype(str).str.strip())

        if df_other.empty:
            raise ValueError(f"Parser {parser} hat keine Daten gefunden.")

        only_a, only_b, differences = compare_dataframes(df_ref, df_other)
        differences = add_difference_flags(differences)

        output_dir = base_output_dir / f"{parser_ref}_vs_{parser}"
        output_dir.mkdir(parents=True, exist_ok=True)

        save_results(
            output_dir=output_dir,
            only_a=only_a,
            only_b=only_b,
            differences=differences,
            parser_a=parser_ref,
            parser_b=parser,
        )

        summary = {
            "comparison": f"{parser_ref} vs {parser}",
            "count_ref": len(df_ref),
            "count_other": len(df_other),
            "only_ref": len(only_a),
            "only_other": len(only_b),
            "differences": len(differences),
            "output_dir": output_dir
        }

        results.append(summary)
    only_in_ref_all = ref_containers - other_containers
    df_only_ref_all = df_ref[df_ref["container"].isin(only_in_ref_all)].copy()
    file_all = base_output_dir / "only_in_max3_all.csv"
    df_only_ref_all.to_csv(file_all, index=False)

    return {
    "results": results,
    "base_output_dir": base_output_dir,
    "only_ref_all_file": file_all
}



