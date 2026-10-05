"""
Rule-Based Trend Detector, Alert Prioritisation, and Escalation Outcome Engine.
Classifies vital sign patterns into transparent, rule-based categories:
  - stable
  - isolated_change
  - persistent_change
  - gradual_trend

Assigns Alert Priority Levels (LOW, MEDIUM, HIGH) and Escalation Outcomes:
  - routine_monitoring
  - care_team_review
  - urgent_check_in

Sanitizes all returned values against NaN or missing data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.baseline import calculate_personal_baselines


SUMMARY_TEMPLATES = {
    "stable": "No substantial change from recent personal baseline. Vitals remain within individual norms.",
    "isolated_change": "One recent reading differs from personal baseline, but surrounding readings remain stable without a continuing pattern.",
    "persistent_change": "Several recent readings show a consistent deviation compared with historical personal baseline.",
    "gradual_trend": "Recent readings demonstrate a progressive, directional drift compared with historical personal baseline."
}


def detect_vital_trend(
    recent_readings: List[float],
    baseline_value: float,
    symptom_report: str = "None reported",
    threshold_pct: float = 8.0
) -> Dict[str, Any]:
    """
    Analyzes a sequence of recent readings (e.g. past 7 days) against a historical baseline value.
    Combines quantitative vital deviations and qualitative symptom reports to assign alert priority
    and escalation outcome.
    """
    # Clean inputs against NaN
    clean_readings = [float(r) for r in recent_readings if pd.notna(r) and not np.isnan(r)]
    base_val = float(baseline_value) if (pd.notna(baseline_value) and not np.isnan(baseline_value)) else 120.0

    if not clean_readings:
        return {
            "trend_type": "stable",
            "priority_level": "LOW",
            "escalation_outcome": "routine_monitoring",
            "baseline_value": base_val,
            "recent_value": base_val,
            "absolute_change": 0.0,
            "percentage_change": 0.0,
            "reason": "Insufficient recent reading data available.",
            "summary": SUMMARY_TEMPLATES["stable"]
        }

    recent_val = round(float(clean_readings[-1]), 1)
    abs_change = round(recent_val - base_val, 1)
    pct_change = round((abs_change / base_val) * 100, 1) if base_val != 0 else 0.0

    deviations = [(val - base_val) for val in clean_readings]
    pct_deviations = [(dev / base_val) * 100 if base_val != 0 else 0.0 for dev in deviations]

    outliers = [i for i, pct in enumerate(pct_deviations) if abs(pct) >= threshold_pct]

    # Evaluate Pattern Type
    if not outliers:
        trend_type = "stable"
        reason = f"All recent readings remain within {threshold_pct}% of the personal baseline ({base_val})."

    elif len(outliers) == 1 and outliers[0] == len(clean_readings) - 1:
        trend_type = "isolated_change"
        reason = f"Single recent reading ({recent_val}) differs from baseline ({base_val}), but prior readings were normal."

    elif len(outliers) >= 3:
        directions = [np.sign(pct_deviations[i]) for i in outliers]
        if len(set(directions)) == 1:
            trend_type = "persistent_change"
            dir_str = "elevated" if directions[0] > 0 else "reduced"
            reason = f"Several recent readings ({len(outliers)} observations) show a persistently {dir_str} pattern compared to baseline."
        else:
            trend_type = "isolated_change"
            reason = "Multiple vital fluctuations detected in mixed directions relative to baseline."

    else:
        diffs = np.diff(clean_readings)
        increasing = all(d >= -0.5 for d in diffs) and (clean_readings[-1] - clean_readings[0] > 5)
        decreasing = all(d <= 0.5 for d in diffs) and (clean_readings[0] - clean_readings[-1] > 5)

        if increasing or decreasing:
            trend_type = "gradual_trend"
            direction = "increasing" if increasing else "decreasing"
            reason = f"Readings demonstrate a progressive, gradual {direction} trend over recent observations."
        elif len(outliers) > 0:
            trend_type = "isolated_change"
            reason = f"Isolated reading variation detected relative to baseline ({base_val})."
        else:
            trend_type = "stable"
            reason = "Readings remain close to personal baseline."

    # Priority Level & Escalation Outcome Assignment
    symptom_str = str(symptom_report) if pd.notna(symptom_report) else "None reported"
    if symptom_str.strip().lower() in ["nan", "none", "null", ""]:
        symptom_str = "None reported"

    has_severe_symptom = symptom_str != "None reported" and ("breath" in symptom_str.lower() or "dizzy" in symptom_str.lower())

    if trend_type == "stable":
        priority_level = "LOW"
        escalation_outcome = "routine_monitoring"
    elif trend_type == "isolated_change":
        if has_severe_symptom:
            priority_level = "MEDIUM"
            escalation_outcome = "care_team_review"
            reason += " Accompanied by reported symptoms."
        else:
            priority_level = "LOW"
            escalation_outcome = "routine_monitoring"
    elif trend_type == "persistent_change":
        if has_severe_symptom:
            priority_level = "HIGH"
            escalation_outcome = "urgent_check_in"
            reason += " High priority due to persistent vital change combined with active symptoms."
        else:
            priority_level = "MEDIUM"
            escalation_outcome = "care_team_review"
    elif trend_type == "gradual_trend":
        if has_severe_symptom:
            priority_level = "HIGH"
            escalation_outcome = "urgent_check_in"
        else:
            priority_level = "MEDIUM"
            escalation_outcome = "care_team_review"
    else:
        priority_level = "LOW"
        escalation_outcome = "routine_monitoring"

    return {
        "trend_type": trend_type,
        "priority_level": priority_level,
        "escalation_outcome": escalation_outcome,
        "baseline_value": base_val,
        "recent_value": recent_val,
        "absolute_change": abs_change,
        "percentage_change": pct_change,
        "reason": reason,
        "summary": SUMMARY_TEMPLATES[trend_type]
    }


def analyze_person_trends(df: pd.DataFrame, person_id: str, vital_metric: str = "systolic_bp") -> Dict[str, Any]:
    """
    Analyzes personal trend, alert priority, and escalation outcome for a person and vital metric.
    """
    baselines = calculate_personal_baselines(df)
    if person_id not in baselines:
        raise ValueError(f"Person ID {person_id} not found in dataset.")

    person_df = df[df["person_id"] == person_id].sort_values("timestamp")
    baseline_val = baselines[person_id][f"baseline_{vital_metric}"]

    recent_vals = person_df[vital_metric].tail(7).dropna().tolist()
    
    raw_symptom = person_df["symptom_report"].iloc[-1] if not person_df.empty else "None reported"
    if pd.isna(raw_symptom) or str(raw_symptom).strip().lower() in ["nan", "none", "null", ""]:
        last_symptom = "None reported"
    else:
        last_symptom = str(raw_symptom).strip()

    analysis = detect_vital_trend(recent_vals, baseline_val, symptom_report=last_symptom)
    analysis["person_id"] = person_id
    analysis["vital_metric"] = vital_metric
    analysis["consent_status"] = person_df["consent_status"].iloc[-1] if not person_df.empty else "consent_given"
    analysis["symptom_report"] = last_symptom

    return analysis
