"""
Unit Tests for Basic Pipeline (35% Milestone).
Verifies synthetic generation, duplicate cleaning, baseline median computation,
rule-based trend classification, and consent privacy controls.
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
    """Test 4: Stable readings close to baseline are classified as 'stable'."""
    recent_readings = [120, 121, 119, 120, 122, 120]
    baseline_val = 120.0
    result = detect_vital_trend(recent_readings, baseline_val)
    
    assert result["trend_type"] == "stable"
    assert "No substantial change" in result["summary"]


def test_5_repeated_changes_trend():
    """Test 5: Repeated elevated readings are classified as 'persistent_change'."""
    # Baseline is 120, recent readings jump to 142+ for 4 observations
    recent_readings = [120, 121, 142, 145, 144, 146]
    baseline_val = 120.0
    result = detect_vital_trend(recent_readings, baseline_val)
    
    assert result["trend_type"] == "persistent_change"
    assert "consistent change" in result["summary"]


def test_6_consent_restriction():
    """Test 6: Verify consent status field is correctly attached to person trend analysis."""
    raw_df = generate_synthetic_data(seed=42, include_dirty_records=False)
    cleaned_df, _ = clean_dataset(raw_df)
    
    # adult_010 was generated with consent_not_given
    trend_010 = analyze_person_trends(cleaned_df, "adult_010", vital_metric="systolic_bp")
    assert trend_010["consent_status"] == "consent_not_given"

    trend_001 = analyze_person_trends(cleaned_df, "adult_001", vital_metric="systolic_bp")
    assert trend_001["consent_status"] == "consent_given"
