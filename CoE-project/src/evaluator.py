"""
Quantitative Evaluation & Comparison Experiment Module (Review 2 Requirement).
Compares Traditional Static Threshold Alerting vs. Proposed Personal Baseline Trend Summariser.
Calculates empirical metrics: TP, TN, FP, FN, Precision, Recall, FPR, FNR, and % Low-Value Alert Reduction.
Performs actual Error Analysis on generated evaluation data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.baseline import calculate_personal_baselines
from src.trend_detector import detect_vital_trend
from src.config import STATIC_THRESHOLDS


def evaluate_static_threshold_alerts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Simulates Traditional Static Threshold Alerting System.
    Triggers an alert on ANY single day where Systolic BP > 135 mmHg or HR > 85 bpm.
    """
    alerts = []
    sys_limit = STATIC_THRESHOLDS["systolic_bp_high"]

    for idx, row in df.iterrows():
        is_alert = bool(row["systolic_bp"] > sys_limit or row["heart_rate"] > STATIC_THRESHOLDS["heart_rate_high"])
        ground_truth = str(row.get("ground_truth_event", "normal"))
        is_true_meaningful = bool(ground_truth == "meaningful_change")

        alerts.append({
            "person_id": row["person_id"],
            "timestamp": row["timestamp"],
            "systolic_bp": row["systolic_bp"],
            "is_alert": is_alert,
            "ground_truth_event": ground_truth,
            "is_true_meaningful": is_true_meaningful
        })

    return alerts


def evaluate_trend_summariser_alerts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Simulates Proposed Personal Baseline Trend Summariser.
    Evaluates rolling 7-day windows against individual median baselines.
    Triggers an alert for persistent_change or gradual_trend patterns, or high priority status.
    """
    alerts = []
    baselines = calculate_personal_baselines(df)

    for person_id, group in df.groupby("person_id"):
        group_sorted = group.sort_values("timestamp").reset_index(drop=True)
        base_sys = baselines[person_id]["baseline_systolic_bp"]

        for i in range(len(group_sorted)):
            window = group_sorted.iloc[max(0, i - 6):i + 1]
            recent_vals = window["systolic_bp"].tolist()
            last_row = group_sorted.iloc[i]

            analysis = detect_vital_trend(
                recent_vals,
                base_sys,
                symptom_report=str(last_row["symptom_report"])
            )

            # Proposed trend alert condition
            is_alert = (
                (analysis["trend_type"] in ["persistent_change", "gradual_trend"]) or
                (analysis["priority_level"] == "HIGH")
            )

            ground_truth = str(last_row.get("ground_truth_event", "normal"))
            is_true_meaningful = bool(ground_truth == "meaningful_change")

            alerts.append({
                "person_id": person_id,
                "timestamp": last_row["timestamp"],
                "systolic_bp": last_row["systolic_bp"],
                "is_alert": is_alert,
                "trend_type": analysis["trend_type"],
                "priority_level": analysis["priority_level"],
                "ground_truth_event": ground_truth,
                "is_true_meaningful": is_true_meaningful
            })

    return alerts


def calculate_experiment_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates empirical confusion matrix (TP, TN, FP, FN), Precision, Recall, FPR, FNR,
    and % Reduction in Low-Value Alerts directly from evaluation data.
    """
    static_results = evaluate_static_threshold_alerts(df)
    trend_results = evaluate_trend_summariser_alerts(df)

    static_df = pd.DataFrame(static_results)
    trend_df = pd.DataFrame(trend_results)

    total_evaluated_cases = len(trend_df)
    static_alert_count = int(static_df["is_alert"].sum())
    trend_alert_count = int(trend_df["is_alert"].sum())

    # Low-Value Alert Reduction Percentage
    if static_alert_count > 0:
        alert_reduction_pct = round(((static_alert_count - trend_alert_count) / static_alert_count) * 100, 1)
    else:
        alert_reduction_pct = 0.0

    # Trend Summariser Confusion Matrix
    tp = int(((trend_df["is_alert"] == True) & (trend_df["is_true_meaningful"] == True)).sum())
    tn = int(((trend_df["is_alert"] == False) & (trend_df["is_true_meaningful"] == False)).sum())
    fp = int(((trend_df["is_alert"] == True) & (trend_df["is_true_meaningful"] == False)).sum())
    fn = int(((trend_df["is_alert"] == False) & (trend_df["is_true_meaningful"] == True)).sum())

    # Total Consistency Check Assertion
    assert (tp + tn + fp + fn) == total_evaluated_cases, "Confusion matrix sum must equal total cases."

    precision = round(tp / (tp + fp), 3) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 3) if (tp + fn) > 0 else 0.0
    fpr = round(fp / (fp + tn), 3) if (fp + tn) > 0 else 0.0
    fnr = round(fn / (fn + tp), 3) if (fn + tp) > 0 else 0.0

    # Actual Error Analysis Logs
    fp_examples = trend_df[(trend_df["is_alert"] == True) & (trend_df["is_true_meaningful"] == False)].head(3).to_dict("records")
    fn_examples = trend_df[(trend_df["is_alert"] == False) & (trend_df["is_true_meaningful"] == True)].head(3).to_dict("records")

    return {
        "total_evaluated_cases": total_evaluated_cases,
        "static_alert_count": static_alert_count,
        "trend_alert_count": trend_alert_count,
        "alert_reduction_pct": alert_reduction_pct,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "fpr": fpr,
        "fnr": fnr,
        "fp_examples": fp_examples,
        "fn_examples": fn_examples
    }
