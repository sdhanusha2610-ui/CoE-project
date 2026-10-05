"""
Personal Baseline Calculation Engine.
Calculates historical personal vital baselines (using median) for individual profiles.
Computes absolute and percentage changes between current readings and historical norms.
Non-diagnostic and non-prescriptive by design.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from src.config import BASELINE_WINDOW_DAYS


def calculate_personal_baselines(df: pd.DataFrame, window_days: int = BASELINE_WINDOW_DAYS) -> Dict[str, Dict[str, float]]:
    """
    Calculates median historical baseline for each person across vital metrics.
    Prefers median over mean to minimize the impact of isolated outlier readings.
    """
    baselines = {}

    for person_id, group in df.groupby("person_id"):
        group_sorted = group.sort_values("timestamp")

        if len(group_sorted) > window_days:
            baseline_period = group_sorted.iloc[:window_days]
        else:
            baseline_period = group_sorted

        person_base = {
            "baseline_heart_rate": round(float(baseline_period["heart_rate"].median()), 1),
            "baseline_systolic_bp": round(float(baseline_period["systolic_bp"].median()), 1),
            "baseline_diastolic_bp": round(float(baseline_period["diastolic_bp"].median()), 1),
            "baseline_oxygen_saturation": round(float(baseline_period["oxygen_saturation"].median()), 1),
            "baseline_temperature": round(float(baseline_period["temperature"].median()), 1),
        }
        baselines[person_id] = person_base

    return baselines


def compare_with_baseline(
    current_value: float,
    baseline_value: float,
    vital_name: str = "vital"
) -> Dict[str, Any]:
    """
    Computes absolute change and percentage change from baseline for a vital measurement.
    """
    abs_change = round(current_value - baseline_value, 1)
    pct_change = round((abs_change / baseline_value) * 100, 1) if baseline_value != 0 else 0.0

    return {
        "vital_name": vital_name,
        "current_value": current_value,
        "baseline_value": baseline_value,
        "absolute_change": abs_change,
        "percentage_change": pct_change,
        "formatted_change": f"{'+' if abs_change > 0 else ''}{abs_change}"
    }
