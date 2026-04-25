from pathlib import Path
import pdfplumber
import pandas as pd


script_dir = Path(__file__).resolve().parent
pdf_file = script_dir / "MSK_ReeferManifest_FinalChangesToLoadListDeadline_IB7612E612EEGPSDTM.pdf"

with pdfplumber.open(pdf_file) as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables()

    print(f"Gefundene Tabellen auf Seite 1: {len(tables)}")

    for table_index, table in enumerate(tables, start=1):
        print(f"\n--- Tabelle {table_index} ---")
        for row_num, row in enumerate(table[:10], start=1):
            print(f"Zeile {row_num}: {len(row)} Spalten -> {row}")