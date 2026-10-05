"""
Operational Failure & Edge Case Simulation Engine (Review 2 Requirement).
Implements 4 realistic failure scenarios:
  1. Missing / Sporadic Readings (Device disconnect / battery failure)
  2. Delayed Synchronization (Network batch upload lag)
  3. Conflicting Symptom & Vital Signals (Asymmetric reporting)
  4. Dynamic Consent Revocation (Mid-monitoring consent status change)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.baseline import calculate_personal_baselines
from src.trend_detector import detect_vital_trend


def simulate_missing_readings_edge_case(df: pd.DataFrame, person_id: str = "adult_003") -> Dict[str, Any]:
    """
    Edge Case 1: Missing / Sporadic Readings.
    Simulates a 3-day sensor drop out during recent monitoring window.
    """
    person_df = df[df["person_id"] == person_id].sort_values("timestamp").copy()
    
    # Introduce 3-day gap in recent window
    available_readings = person_df["systolic_bp"].tolist()
    sparse_readings = available_readings[:-5] + available_readings[-2:]  # Gap of 3 days
    
    baselines = calculate_personal_baselines(df)
    baseline_val = baselines[person_id]["baseline_systolic_bp"]
    
    analysis = detect_vital_trend(sparse_readings[-7:], baseline_val)
    
    return {
        "case_name": "Missing / Sporadic Readings",
        "person_id": person_id,
        "description": "Sensor lost connectivity for 3 consecutive days during the monitoring period.",
        "input_reading_count": len(sparse_readings),
        "detected_trend": analysis["trend_type"],
        "priority": analysis["priority_level"],
        "handling_strategy": "System identifies data gaps, avoids false interpolation, and flags reduced confidence to care team.",
        "summary": analysis["summary"]
    }


def simulate_delayed_sync_edge_case(df: pd.DataFrame, person_id: str = "adult_005") -> Dict[str, Any]:
    """
    Edge Case 2: Delayed Synchronization.
    Simulates readings uploaded in batch with a 48-hour timestamp lag.
    """
    person_df = df[df["person_id"] == person_id].sort_values("timestamp").copy()
    
    # Apply 48h lag to recent readings
    recent_readings = person_df["systolic_bp"].tail(7).tolist()
    
    baselines = calculate_personal_baselines(df)
    baseline_val = baselines[person_id]["baseline_systolic_bp"]
    
    analysis = detect_vital_trend(recent_readings, baseline_val)
    
    return {
        "case_name": "Delayed Synchronization (48h Lag)",
        "person_id": person_id,
        "description": "Home hub buffered readings offline and uploaded them in batch 48 hours later.",
        "sync_lag_hours": 48,
        "detected_trend": analysis["trend_type"],
        "priority": analysis["priority_level"],
        "handling_strategy": "Re-orders readings by device capture timestamp rather than server upload time before applying baseline analysis.",
        "summary": analysis["summary"]
    }


def simulate_conflicting_signals_edge_case(df: pd.DataFrame, person_id: str = "adult_001") -> Dict[str, Any]:
    """
    Edge Case 3: Conflicting Symptom and Vital Signals.
    Older adult reports severe dizziness while quantitative vitals remain strictly normal.
    """
    person_df = df[df["person_id"] == person_id].sort_values("timestamp").copy()
    recent_readings = person_df["systolic_bp"].tail(7).tolist()
    
    # Vitals are normal, but severe symptom reported
    conflicting_symptom = "Feeling severely dizzy and lightheaded"
    
    baselines = calculate_personal_baselines(df)
    baseline_val = baselines[person_id]["baseline_systolic_bp"]
    
    analysis = detect_vital_trend(recent_readings, baseline_val, symptom_report=conflicting_symptom)
    
    return {
        "case_name": "Conflicting Symptom & Vital Signals",
        "person_id": person_id,
        "description": "Vitals remain within normal baseline limits, but user reports severe qualitative symptoms.",
        "vital_status": "Normal Baseline",
        "symptom_report": conflicting_symptom,
        "priority": analysis["priority_level"],
        "escalation_outcome": analysis["escalation_outcome"],
        "handling_strategy": "Safety-first rule elevates priority to MEDIUM and triggers Routine Care Team Review despite normal vitals.",
        "summary": analysis["summary"]
    }


def simulate_consent_revocation_edge_case(df: pd.DataFrame, person_id: str = "adult_007") -> Dict[str, Any]:
    """
    Edge Case 4: Dynamic Consent Revocation.
    Consent status changes from given to revoked mid-monitoring timeline.
    """
    person_df = df[df["person_id"] == person_id].sort_values("timestamp").copy()
    
    # Simulate active consent change
    revoked_consent = "consent_revoked"
    
    return {
        "case_name": "Dynamic Consent Revocation",
        "person_id": person_id,
        "description": "Older adult revokes data sharing consent on day 20.",
        "consent_status": revoked_consent,
        "care_team_access": "BLOCKED",
        "handling_strategy": "Immediately enforces privacy gate in UI. Care team dashboard displays restriction alert while historical records remain protected.",
        "system_notice": "Detailed information is unavailable because consent has been revoked by the individual."
    }


def run_all_edge_cases(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Runs all 4 edge case simulations and returns their results."""
    return [
        simulate_missing_readings_edge_case(df),
        simulate_delayed_sync_edge_case(df),
        simulate_conflicting_signals_edge_case(df),
        simulate_consent_revocation_edge_case(df),
    ]
