import pandas as pd



def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame):

    merged = df1.merge(
        df2,
        on="container",
        how="outer",
        suffixes=("_A", "_B"),
        indicator=True
    )

    only_A = merged[merged["_merge"] == "left_only"].copy()
    only_B = merged[merged["_merge"] == "right_only"].copy()

    both = merged["_merge"] == "both"

    temp_diff = (
        both &
        (merged["temperature_A"] != merged["temperature_B"])
    )

    vent_diff = (
        both &
        (merged["ventilation_A"] != merged["ventilation_B"])
    )

    drain_diff = (
        both &
        merged["drainholes_A"].notna() &
        merged["drainholes_B"].notna() &
        (merged["drainholes_A"] != merged["drainholes_B"])
    )

    differences = merged[temp_diff | vent_diff | drain_diff].copy()
    print("DEBUG ventilation A:", repr(merged["ventilation_A"].iloc[0]), type(merged["ventilation_A"].iloc[0]))
    print("DEBUG ventilation B:", repr(merged["ventilation_B"].iloc[0]), type(merged["ventilation_B"].iloc[0]))

    return only_A, only_B, differences


def add_difference_flags(differences: pd.DataFrame) -> pd.DataFrame:
    differences = differences.copy()

    both = differences["_merge"] == "both"

    differences["temp_diff"] = (
        both &
        (differences["temperature_A"] != differences["temperature_B"])
    )

    differences["vent_diff"] = (
        both &
        (differences["ventilation_A"] != differences["ventilation_B"])
    )

    both_have_drain = (
        both &
        differences["drainholes_A"].notna() &
        differences["drainholes_B"].notna()
    )

    differences["drain_diff"] = (
        both_have_drain &
        (differences["drainholes_A"] != differences["drainholes_B"])
    )

    return differences