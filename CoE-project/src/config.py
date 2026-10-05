"""
Configuration parameters for data generation, validation, alert thresholds, and file paths.
"""
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "synthetic_home_readings.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "cleaned_home_readings.csv"

# Anonymous Person IDs (10 synthetic profiles)
PERSON_IDS = [f"adult_{i:03d}" for i in range(1, 11)]

# Observation Window Parameters
DAYS_OF_READINGS = 30
BASELINE_WINDOW_DAYS = 20
RECENT_WINDOW_DAYS = 7

# Physiological Ranges for Cleaning Validation
VITAL_RANGES = {
    "heart_rate": (30, 200),           # bpm
    "systolic_bp": (70, 240),          # mmHg
    "diastolic_bp": (40, 140),         # mmHg
    "oxygen_saturation": (70, 100),    # %
    "temperature": (34.0, 42.0),       # °C
}

# Static Threshold Limits (Traditional Alert System for Baseline Comparison)
STATIC_THRESHOLDS = {
    "systolic_bp_high": 135,           # mmHg
    "heart_rate_high": 85,              # bpm
    "oxygen_saturation_low": 94,        # %
    "temperature_high": 37.5            # °C
}

# Priority Levels & Escalation Outcomes
PRIORITY_LEVELS = ["LOW", "MEDIUM", "HIGH"]
ESCALATION_OUTCOMES = ["routine_monitoring", "care_team_review", "urgent_check_in"]
