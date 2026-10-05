"""
Synthetic Data Generator for Older Adult Home Vital Readings & Symptom Reports.
Generates 10 synthetic profiles over 30 days demonstrating realistic clinical patterns:
  - Pattern 1: Stable Normal (adult_001, adult_002)
  - Pattern 2: High Baseline Natural Variation (adult_003, adult_004) -> Generates static low-value alerts, suppressed by Trend Summariser.
  - Pattern 3: Isolated Abnormal Spikes (adult_005, adult_006) -> Generates static low-value alerts, suppressed by Trend Summariser.
  - Pattern 4: Persistent Shift (adult_007, adult_008) -> True Meaningful Change, detected by both.
  - Pattern 5: Gradual Trend (adult_009, adult_010) -> True Meaningful Change, detected by both.
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
    """
    np.random.seed(seed)
    random.seed(seed)

    start_date = datetime(2026, 1, 1, 8, 0, 0)
    records = []

    profile_patterns = {
        "adult_001": "stable",
        "adult_002": "stable",
        "adult_003": "high_baseline_variation",
        "adult_004": "high_baseline_variation",
        "adult_005": "isolated_spikes",
        "adult_006": "isolated_spikes",
        "adult_007": "persistent_change",
        "adult_008": "persistent_change",
        "adult_009": "gradual_trend",
        "adult_010": "gradual_trend",
    }

    base_vitals = {
        "adult_001": {"hr": 70, "sys_bp": 120, "dia_bp": 78, "spo2": 97, "temp": 36.6, "consent": "consent_given"},
        "adult_002": {"hr": 72, "sys_bp": 122, "dia_bp": 80, "spo2": 98, "temp": 36.5, "consent": "consent_given"},
        "adult_003": {"hr": 74, "sys_bp": 133, "dia_bp": 84, "spo2": 96, "temp": 36.7, "consent": "consent_given"},
        "adult_004": {"hr": 75, "sys_bp": 133, "dia_bp": 85, "spo2": 97, "temp": 36.6, "consent": "consent_given"},
        "adult_005": {"hr": 70, "sys_bp": 122, "dia_bp": 78, "spo2": 97, "temp": 36.6, "consent": "consent_given"},
        "adult_006": {"hr": 71, "sys_bp": 124, "dia_bp": 79, "spo2": 97, "temp": 36.6, "consent": "consent_given"},
        "adult_007": {"hr": 70, "sys_bp": 122, "dia_bp": 78, "spo2": 97, "temp": 36.6, "consent": "consent_given"},
        "adult_008": {"hr": 72, "sys_bp": 123, "dia_bp": 80, "spo2": 96, "temp": 36.7, "consent": "consent_given"},
        "adult_009": {"hr": 70, "sys_bp": 120, "dia_bp": 78, "spo2": 97, "temp": 36.6, "consent": "consent_given"},
        "adult_010": {"hr": 72, "sys_bp": 122, "dia_bp": 79, "spo2": 96, "temp": 36.6, "consent": "consent_revoked"},
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
            symptom = "None"
            ground_truth_event = "normal"

            if pattern == "stable":
                hr += int(np.random.choice([-1, 0, 1]))
                sys_bp += int(np.random.choice([-1, 0, 1]))
                dia_bp += int(np.random.choice([-1, 0, 1]))

            elif pattern == "high_baseline_variation":
                # High baseline (133 mmHg). Fluctuation (+2 to +4) causes static alert on ~8 days, but it is benign normal variation for this individual.
                fluct = int(np.random.choice([-1, 0, 2, 3, 4]))
                sys_bp += fluct
                if sys_bp > 135:
                    ground_truth_event = "benign_variation"

            elif pattern == "isolated_spikes":
                # Isolated abnormal spikes on days 8, 16, 24
                if day in [7, 15, 23]:
                    sys_bp += 18
                    hr += 10
                    symptom = "Feeling slightly dizzy after exertion"
                    ground_truth_event = "isolated_spike"
                else:
                    hr += int(np.random.choice([-1, 0, 1]))
                    sys_bp += int(np.random.choice([-2, 0, 2]))

            elif pattern == "persistent_change":
                # Persistent elevated BP on days 22-29 (8 days)
                if day >= 21:
                    sys_bp += 18
                    hr += 10
                    symptom = "Feeling persistently fatigued and lightheaded"
                    ground_truth_event = "meaningful_change"
                else:
                    sys_bp += int(np.random.choice([-1, 0, 1]))

            elif pattern == "gradual_trend":
                # Gradual trend upward over days 14-29
                if day >= 14:
                    sys_bp += int((day - 14) * 1.4)
                    hr += int((day - 14) * 0.5)
                    if day >= 21:
                        symptom = "Shortness of breath during routine daily activities"
                        ground_truth_event = "meaningful_change"

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
                "consent_status": consent,
                "ground_truth_event": ground_truth_event
            })

    df = pd.DataFrame(records)

    if include_dirty_records:
        # Insert intentional duplicate rows, missing value, and out of range value for data cleaning tests
        dup_row_1 = df.iloc[5].copy()
        dup_row_2 = df.iloc[20].copy()
        df = pd.concat([df, pd.DataFrame([dup_row_1, dup_row_2])], ignore_index=True)

        df.loc[12, "heart_rate"] = np.nan
        df.loc[45, "systolic_bp"] = 350  # Out of range

    return df


def save_raw_dataset():
    """Generates synthetic dataset and saves to data/raw/synthetic_home_readings.csv."""
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_data(include_dirty_records=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Generated {len(df)} synthetic records saved to {RAW_DATA_PATH}")


if __name__ == "__main__":
    save_raw_dataset()
