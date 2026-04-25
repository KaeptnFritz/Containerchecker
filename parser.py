from pathlib import Path
import re
import pdfplumber
import pandas as pd


def max3_parser(pdf_path: str) -> pd.DataFrame:
    rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = text.splitlines()

            for line in lines:
                line = line.strip()

                m = re.match(
                    r"^\d+\s+([A-Z]{4}\d{7})\s+[A-Z]{5}\s+[A-Z]{5}\s+(-?\d+(?:\.\d+)?)\s+(\S+)\s+[A-Z]{3}$",
                    line
                )
                if not m:
                    continue

                container = m.group(1)
                temperature = float(m.group(2))
                ventilation_raw = m.group(3)
                ventilation = ventilation_raw


                rows.append({
                    "container": container,
                    "temperature": temperature,
                    "ventilation": ventilation,
                    "drainholes": None,
                    "source": Path(pdf_path).name,
                    "page": page_num,
                })

    df = pd.DataFrame(rows)
    df = df.drop_duplicates(subset=["container"]).reset_index(drop=True)
    if df.empty:
        raise ValueError(f"HL parser found no containers in {pdf_path}")
    return df


def msk_parser(pdf_path: str) -> pd.DataFrame:
    all_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                df = pd.DataFrame(table)

                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)

                df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]

                try:
                    df_clean = df[[
                        "Container Number",
                        "Temp deg C",
                        "Ventilation",
                        "Drainholes"
                    ]].copy()
                except KeyError:
                    continue

                df_clean.columns = [
                    "container",
                    "temperature",
                    "ventilation",
                    "drainholes"
                ]

                df_clean["temperature"] = pd.to_numeric(df_clean["temperature"], errors="coerce")
                df_clean["source"] = Path(pdf_path).name
                df_clean["page"] = page_num

                all_rows.append(df_clean)

    if not all_rows:
        return pd.DataFrame(columns=["container", "temperature", "ventilation", "drainholes", "source", "page"])

    result = pd.concat(all_rows, ignore_index=True)
    result = result[result["container"].notna()]
    result = result.drop_duplicates(subset=["container"]).reset_index(drop=True)

    return result




def hl_parser(pdf_path: str) -> pd.DataFrame:
    rows = []

    container_pattern = re.compile(r"\b([A-Z]{4}\s?\d{7})\b")
    temp_pattern = re.compile(r"TEMP:\s*(?:PLUS|MINUS)?\s*([+-]?\d+\.?\d*)")
    vent_pattern = re.compile(r"FRESH AIR SUPPLY:\s*([A-Z0-9\s/]+)")

    current_container = None
    current_temp = None
    current_vent = None

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = text.splitlines()

            for line in lines:
                line = line.strip()

                # Container
                m_container = container_pattern.search(line)
                if m_container:
                    current_container = m_container.group(1).replace(" ", "")

                # Temperatur
                m_temp = temp_pattern.search(line)
                if m_temp:
                    current_temp = float(m_temp.group(1))

                # Ventilation
                m_vent = vent_pattern.search(line)
                if m_vent:
                    current_vent = m_vent.group(1).strip()

                # Wenn alles da → speichern
                if current_container and current_temp is not None:
                    rows.append({
                        "container": current_container,
                        "temperature": current_temp,
                        "ventilation": current_vent,
                        "drainholes": None,
                        "source": Path(pdf_path).name,
                        "page": page_num,
                    })

                    current_container = None
                    current_temp = None
                    current_vent = None

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df = df.drop_duplicates(subset=["container"]).reset_index(drop=True)
    return df

