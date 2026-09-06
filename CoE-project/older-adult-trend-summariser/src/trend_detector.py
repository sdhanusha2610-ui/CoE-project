"""
Rule-Based Trend Detector and Human-Readable Summariser.
Classifies vital sign patterns into transparent, rule-based categories:
  - stable
  - isolated_change
  - persistent_change
  - gradual_trend
No machine learning, diagnosis, or treatment recommendations are provided.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.baseline import calculate_personal_baselines, compare_with_baseline


SUMMARY_TEMPLATES = {
    "stable": "No substantial change from the recent personal baseline.",
    "isolated_change": "One recent reading differs from the personal baseline, but surrounding readings do not show a continuing pattern.",
    "persistent_change": "Several recent readings show a consistent change compared with the personal baseline.",
    "gradual_trend": "Recent readings show a gradual directional change compared with the personal baseline."
}


def detect_vital_trend(
    recent_readings: List[float],
    baseline_value: float,
    threshold_pct: float = 8.0
) -> Dict[str, Any]:
    """
    Analyzes a sequence of recent readings (e.g. past 5-7 days) against a historical baseline value.
    
    Rule Logic:
    1. Stable: All recent readings within threshold deviation from baseline.
    2. Isolated Change: Only 1 recent reading deviates beyond threshold, while adjacent recent readings remain normal.
    3. Persistent Change: 3 or more recent readings deviate beyond threshold in the same direction.
    4. Gradual Trend: Monotonic or near-monotonic progressive movement over recent readings.
    """
    if not recent_readings:
        return {
            "trend_type": "stable",
            "baseline_value": baseline_value,
            "recent_value": baseline_value,
            "absolute_change": 0.0,
            "percentage_change": 0.0,
            "reason": "Insufficient recent reading data available.",
            "summary": SUMMARY_TEMPLATES["stable"]
        }

    recent_val = round(float(recent_readings[-1]), 1)
    abs_change = round(recent_val - baseline_value, 1)
    pct_change = round((abs_change / baseline_value) * 100, 1) if baseline_value != 0 else 0.0

    # Calculate deviations for recent sequence
    deviations = [(val - baseline_value) for val in recent_readings]
    pct_deviations = [(dev / baseline_value) * 100 if baseline_value != 0 else 0.0 for dev in deviations]

    outliers = [i for i, pct in enumerate(pct_deviations) if abs(pct) >= threshold_pct]

    # Rule evaluation
    if not outliers:
        trend_type = "stable"
        reason = f"All recent readings remain within {threshold_pct}% of the historical baseline ({baseline_value})."

    elif len(outliers) == 1 and outliers[0] == len(recent_readings) - 1:
        # Check if the single outlier is isolated (preceding reading was normal)
        trend_type = "isolated_change"
        reason = f"Single recent reading ({recent_val}) differs from baseline ({baseline_value}), but prior readings were normal."

    elif len(outliers) >= 3:
        # Check directionality of deviations
        directions = [np.sign(pct_deviations[i]) for i in outliers]
        if len(set(directions)) == 1:
            # All outliers in same direction
            trend_type = "persistent_change"
            dir_str = "elevated" if directions[0] > 0 else "reduced"
            reason = f"Several recent readings ({len(outliers)} observations) show a persistently {dir_str} pattern compared to baseline."
        else:
            trend_type = "isolated_change"
            reason = "Multiple fluctuations detected in mixed directions relative to baseline."

    else:
        # Check for gradual trend (consistently increasing or decreasing over sequence)
        diffs = np.diff(recent_readings)
        increasing = all(d >= -0.5 for d in diffs) and (recent_readings[-1] - recent_readings[0] > 5)
        decreasing = all(d <= 0.5 for d in diffs) and (recent_readings[0] - recent_readings[-1] > 5)

        if increasing or decreasing:
            trend_type = "gradual_trend"
            direction = "increasing" if increasing else "decreasing"
            reason = f"Readings demonstrate a progressive, gradual {direction} trend over recent observations."
        elif len(outliers) > 0:
            trend_type = "isolated_change"
            reason = f"Isolated reading variation detected relative to baseline ({baseline_value})."
        else:
            trend_type = "stable"
            reason = "Readings remain close to personal baseline."

    return {
        "trend_type": trend_type,
        "baseline_value": baseline_value,
        "recent_value": recent_val,
        "absolute_change": abs_change,
        "percentage_change": pct_change,
        "reason": reason,
        "summary": SUMMARY_TEMPLATES[trend_type]
    }


def analyze_person_trends(df: pd.DataFrame, person_id: str, vital_metric: str = "systolic_bp") -> Dict[str, Any]:
    """
    Analyzes personal trend for a specific person and vital metric.
    """
    baselines = calculate_personal_baselines(df)
    if person_id not in baselines:
        raise ValueError(f"Person ID {person_id} not found in dataset.")

    person_df = df[df["person_id"] == person_id].sort_values("timestamp")
    baseline_val = baselines[person_id][f"baseline_{vital_metric}"]

    # Use past 7 readings for recent window
    recent_vals = person_df[vital_metric].tail(7).tolist()

    analysis = detect_vital_trend(recent_vals, baseline_val)
    analysis["person_id"] = person_id
    analysis["vital_metric"] = vital_metric
    analysis["consent_status"] = person_df["consent_status"].iloc[-1]
    analysis["symptom_report"] = person_df["symptom_report"].iloc[-1]

    return analysis
