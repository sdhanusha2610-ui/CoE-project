"""
Data Cleaning Module for Home Vital Readings.
Performs timestamp conversion, datatype validation, duplicate detection/removal,
missing value analysis, and numeric range validation.
Saves cleaned dataset to data/processed/cleaned_home_readings.csv.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict
from src.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, VITAL_RANGES


def clean_dataset(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Cleans raw home readings dataframe and returns cleaned dataframe alongside cleaning statistics.
    
    Cleaning steps:
    1. Timestamp parsing & ISO conversion
    2. Datatype casting
    3. Exact duplicate identification and removal
    4. Numeric range validation against physiological limits
    5. Missing value logging (rows with missing required vitals are dropped rather than fabricated)
    """
    stats = {
        "rows_before": len(raw_df),
        "duplicates_removed": 0,
        "missing_values_found": 0,
        "invalid_records_removed": 0,
        "rows_after": 0
    }

    df = raw_df.copy()

    # 1. Duplicate detection and removal
    initial_len = len(df)
    df = df.drop_duplicates()
    stats["duplicates_removed"] = initial_len - len(df)

    # 2. Timestamp conversion & sorting
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # 3. Missing value analysis
    # Count missing values across key vital sign columns
    vital_cols = list(VITAL_RANGES.keys())
    missing_mask = df[vital_cols].isna().any(axis=1) | df["timestamp"].isna()
    stats["missing_values_found"] = int(missing_mask.sum())

    # We do NOT silently fabricate clinical values (e.g. median imputation for clinical data can mask baseline shifts).
    # Missing vitals rows are removed from processing and documented.
    df = df[~missing_mask].copy()

    # 4. Range validation
    invalid_mask = pd.Series(False, index=df.index)
    for col, (min_val, max_val) in VITAL_RANGES.items():
        if col in df.columns:
            out_of_range = (df[col] < min_val) | (df[col] > max_val)
            invalid_mask = invalid_mask | out_of_range

    stats["invalid_records_removed"] = int(invalid_mask.sum())
    df = df[~invalid_mask].copy()

    # Ensure numeric types
    for col in vital_cols:
        df[col] = pd.to_numeric(df[col])

    # Sort chronologically by person and timestamp
    df = df.sort_values(by=["person_id", "timestamp"]).reset_index(drop=True)
    stats["rows_after"] = len(df)

    return df, stats


def run_cleaning_pipeline() -> pd.DataFrame:
    """Loads raw dataset, cleans it, prints report, and saves to processed folder."""
    if not RAW_DATA_PATH.exists():
        from src.data_generator import save_raw_dataset
        save_raw_dataset()

    raw_df = pd.read_csv(RAW_DATA_PATH)
    cleaned_df, stats = clean_dataset(raw_df)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(PROCESSED_DATA_PATH, index=False)

    print("=== Data Cleaning Report ===")
    print(f"Rows before:            {stats['rows_before']}")
    print(f"Duplicates removed:     {stats['duplicates_removed']}")
    print(f"Missing values found:   {stats['missing_values_found']}")
    print(f"Invalid records removed:{stats['invalid_records_removed']}")
    print(f"Rows after:             {stats['rows_after']}")
    print(f"Cleaned dataset saved to {PROCESSED_DATA_PATH}")

    return cleaned_df


if __name__ == "__main__":
    run_cleaning_pipeline()
