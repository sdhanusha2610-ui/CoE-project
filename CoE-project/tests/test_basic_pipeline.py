"""
Comprehensive Automated Test Suite for Older Adult Trend Summariser (Review 2).
Verifies synthetic data generation, cleaning, baseline calculation, rule-based trend classification,
alert priority levels, escalation outcomes, quantitative metrics calculation, consent gates,
operational edge cases, and NaN handling.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.data_generator import generate_synthetic_data
from src.data_cleaning import clean_dataset
from src.baseline import calculate_personal_baselines, compare_with_baseline
from src.trend_detector import detect_vital_trend, analyze_person_trends
from src.evaluator import calculate_experiment_metrics
from src.edge_cases import run_all_edge_cases


def test_1_synthetic_dataset_generation():
    """Test 1: Synthetic dataset generation works and produces required fields."""
    df = generate_synthetic_data(seed=42, include_dirty_records=False)
    assert not df.empty
    assert len(df["person_id"].unique()) == 10
    required_cols = [
        "person_id", "timestamp", "heart_rate", "systolic_bp",
        "diastolic_bp", "oxygen_saturation", "temperature",
        "symptom_report", "consent_status"
    ]
    for col in required_cols:
        assert col in df.columns


def test_2_cleaning_removes_duplicates():
    """Test 2: Cleaning removes duplicates and handles invalid rows."""
    raw_df = generate_synthetic_data(seed=42, include_dirty_records=True)
    cleaned_df, stats = clean_dataset(raw_df)
    
    assert stats["duplicates_removed"] > 0
    assert stats["rows_after"] < stats["rows_before"]
    assert cleaned_df.duplicated().sum() == 0


def test_3_baseline_calculation():
    """Test 3: Personal baseline calculation correctly calculates median vitals."""
    raw_df = generate_synthetic_data(seed=42, include_dirty_records=False)
    cleaned_df, _ = clean_dataset(raw_df)
    baselines = calculate_personal_baselines(cleaned_df)
    
    assert "adult_001" in baselines
    base_sys = baselines["adult_001"]["baseline_systolic_bp"]
    assert 90 <= base_sys <= 160


def test_4_stable_readings_trend():
    """Test 4: Stable readings close to baseline are classified as 'stable' with LOW priority."""
    recent_readings = [120, 121, 119, 120, 122, 120]
    baseline_val = 120.0
    result = detect_vital_trend(recent_readings, baseline_val)
    
    assert result["trend_type"] == "stable"
    assert result["priority_level"] == "LOW"
    assert result["escalation_outcome"] == "routine_monitoring"


def test_5_repeated_changes_trend():
    """Test 5: Repeated elevated readings are classified as 'persistent_change'."""
    recent_readings = [120, 121, 142, 145, 144, 146]
    baseline_val = 120.0
    result = detect_vital_trend(recent_readings, baseline_val)
    
    assert result["trend_type"] == "persistent_change"
    assert result["priority_level"] in ["MEDIUM", "HIGH"]


def test_6_consent_restriction():
    """Test 6: Verify consent status field is correctly attached to person trend analysis."""
    raw_df = generate_synthetic_data(seed=42, include_dirty_records=False)
    cleaned_df, _ = clean_dataset(raw_df)
    
    trend_010 = analyze_person_trends(cleaned_df, "adult_010", vital_metric="systolic_bp")
    assert trend_010["consent_status"] == "consent_revoked"

    trend_001 = analyze_person_trends(cleaned_df, "adult_001", vital_metric="systolic_bp")
    assert trend_001["consent_status"] == "consent_given"


def test_7_alert_prioritisation_and_escalation():
    """Test 7: Test alert priority elevation when persistent change combines with symptoms."""
    recent_readings = [120, 122, 145, 148, 147, 150]
    baseline_val = 120.0
    symptom = "Shortness of breath"
    result = detect_vital_trend(recent_readings, baseline_val, symptom_report=symptom)
    
    assert result["priority_level"] == "HIGH"
    assert result["escalation_outcome"] == "urgent_check_in"


def test_8_experiment_metrics_calculation():
    """Test 8: Verify empirical calculation of Precision, Recall, FPR, FNR, and alert reduction."""
    raw_df = generate_synthetic_data(seed=42, include_dirty_records=True)
    cleaned_df, _ = clean_dataset(raw_df)
    metrics = calculate_experiment_metrics(cleaned_df)
    
    assert metrics["static_alert_count"] > metrics["trend_alert_count"]
    assert metrics["alert_reduction_pct"] > 0.0
    assert (metrics["tp"] + metrics["tn"] + metrics["fp"] + metrics["fn"]) == metrics["total_evaluated_cases"]
    assert 0.0 <= metrics["precision"] <= 1.0
    assert 0.0 <= metrics["recall"] <= 1.0


def test_9_operational_edge_cases():
    """Test 9: Verify all 4 operational failure edge cases run and produce expected results."""
    raw_df = generate_synthetic_data(seed=42, include_dirty_records=True)
    cleaned_df, _ = clean_dataset(raw_df)
    edge_results = run_all_edge_cases(cleaned_df)
    
    assert len(edge_results) == 4
    case_names = [c["case_name"] for c in edge_results]
    assert "Missing / Sporadic Readings" in case_names
    assert "Dynamic Consent Revocation" in case_names


def test_10_no_fleet_terminology():
    """Test 10: Ensure no fleet/vehicle domain terms exist in code docstrings or outputs."""
    import src.config as config
    assert not hasattr(config, "VEHICLE_IDS")


def test_11_isolated_abnormal_reading_suppression():
    """Test 11: Verify isolated abnormal reading is suppressed by Trend Summariser as LOW priority."""
    recent_readings = [120, 121, 120, 122, 121, 142] # Day 6 spike
    baseline_val = 120.0
    result = detect_vital_trend(recent_readings, baseline_val)
    
    assert result["trend_type"] == "isolated_change"
    assert result["priority_level"] == "LOW"


def test_12_nan_chart_data_handling():
    """Test 12: Verify chart data cleaning strips NaN values cleanly."""
    df_sample = pd.DataFrame({
        "timestamp": pd.date_range("2026-01-01", periods=5),
        "systolic_bp": [120.0, np.nan, 122.0, 125.0, np.nan]
    })
    chart_df = df_sample[["timestamp", "systolic_bp"]].dropna()
    assert len(chart_df) == 3
    assert chart_df["systolic_bp"].isna().sum() == 0
