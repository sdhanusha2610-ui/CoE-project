"""
Synthetic Data Generator for Older Adult Home Vital Readings.
Generates 10 synthetic profiles over 30 days demonstrating 5 clinical patterns.
Strictly synthetic data: uses anonymous IDs only (adult_001 to adult_010).
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from src.config import PERSON_IDS, DAYS_OF_READINGS, RAW_DATA_PATH


def generate_synthetic_data(seed: int = 42, include_dirty_records: bool = True) -> pd.DataFrame:
    """
    Generates synthetic home readings dataset for 10 older adults over 30 days.
    Implements 5 key clinical patterns across profiles:
      - Pattern 1: Stable (adult_001, adult_002)
      - Pattern 2: Natural variation (adult_003, adult_004)
      - Pattern 3: Isolated change (adult_005, adult_006)
      - Pattern 4: Persistent change (adult_007, adult_008)
      - Pattern 5: Gradual trend (adult_009, adult_010)
    """
    np.random.seed(seed)
    random.seed(seed)

    start_date = datetime(2026, 1, 1, 8, 0, 0)
    records = []

    # Map profiles to target patterns
    profile_patterns = {
        "adult_001": "stable",
        "adult_002": "stable",
        "adult_003": "natural_variation",
        "adult_004": "natural_variation",
        "adult_005": "isolated_change",
        "adult_006": "isolated_change",
        "adult_007": "persistent_change",
        "adult_008": "persistent_change",
        "adult_009": "gradual_trend",
        "adult_010": "gradual_trend",
    }

    # Baseline vitals per individual
    base_vitals = {
        pid: {
            "hr": int(np.random.normal(70, 4)),
            "sys_bp": int(np.random.normal(122, 5)),
            "dia_bp": int(np.random.normal(78, 4)),
            "spo2": int(np.random.normal(97, 1)),
            "temp": round(float(np.random.normal(36.6, 0.2)), 1),
            # Default consent: true for most, false for adult_010 to demonstrate consent logic
            "consent": "consent_given" if pid != "adult_010" else "consent_not_given"
        }
        for pid in PERSON_IDS
    }

    for day in range(DAYS_OF_READINGS):
        current_time = start_date + timedelta(days=day)
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        for pid in PERSON_IDS:
            pattern = profile_patterns[pid]
            base = base_vitals[pid]

            hr = base["hr"]
            sys_bp = base["sys_bp"]
            dia_bp = base["dia_bp"]
            spo2 = base["spo2"]
            temp = base["temp"]
            consent = base["consent"]

            # Symptom report (basic placeholder for 35% stage, e.g. None or simple string)
            symptom = "None"

            # Apply pattern logic
            if pattern == "stable":
                hr += int(np.random.choice([-1, 0, 1]))
                sys_bp += int(np.random.choice([-1, 0, 1]))
                dia_bp += int(np.random.choice([-1, 0, 1]))

            elif pattern == "natural_variation":
                hr += int(np.random.choice([-3, -2, -1, 0, 1, 2, 3]))
                sys_bp += int(np.random.choice([-4, -2, 0, 2, 4]))
                dia_bp += int(np.random.choice([-3, -1, 0, 1, 3]))

            elif pattern == "isolated_change":
                # Day 25 has an isolated spike/dip
                if day == 24:
                    sys_bp += 22
                    hr += 12
                    symptom = "Feeling slightly dizzy"
                else:
                    hr += int(np.random.choice([-1, 0, 1]))
                    sys_bp += int(np.random.choice([-2, 0, 2]))

            elif pattern == "persistent_change":
                # Days 24 to 29 show persistent elevation
                if day >= 24:
                    sys_bp += 18
                    hr += 10
                    symptom = "Feeling tired"
                else:
                    sys_bp += int(np.random.choice([-1, 0, 1]))

            elif pattern == "gradual_trend":
                # Days 15 to 29 demonstrate gradual upward movement
                if day >= 14:
                    sys_bp += (day - 14) * 1.5
                    hr += (day - 14) * 0.6

            # Bound vitals within sensible limits for raw generation
            hr = max(40, min(180, int(hr)))
            sys_bp = max(80, min(210, int(sys_bp)))
            dia_bp = max(50, min(120, int(dia_bp)))
            spo2 = max(85, min(100, int(spo2)))
            temp = round(max(35.0, min(40.0, float(temp))), 1)

            records.append({
                "person_id": pid,
                "timestamp": timestamp_str,
                "heart_rate": hr,
                "systolic_bp": sys_bp,
                "diastolic_bp": dia_bp,
                "oxygen_saturation": spo2,
                "temperature": temp,
                "symptom_report": symptom,
                "consent_status": consent
            })

    df = pd.DataFrame(records)

    if include_dirty_records:
        # Add a couple of synthetic duplicate rows and missing values for cleaning demonstration
        dup_row_1 = df.iloc[5].copy()
        dup_row_2 = df.iloc[20].copy()
        df = pd.concat([df, pd.DataFrame([dup_row_1, dup_row_2])], ignore_index=True)

        # Introduce a missing value and an invalid range value
        df.loc[12, "heart_rate"] = np.nan
        df.loc[45, "systolic_bp"] = 350  # Invalid range

    return df


def save_raw_dataset():
    """Generates synthetic dataset and saves it to data/raw/synthetic_home_readings.csv."""
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_data(include_dirty_records=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Generated {len(df)} synthetic records saved to {RAW_DATA_PATH}")


if __name__ == "__main__":
    save_raw_dataset()
