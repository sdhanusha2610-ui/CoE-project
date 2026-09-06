"""
Configuration parameters for data generation, validation, and file paths.
"""
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "synthetic_home_readings.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "cleaned_home_readings.csv"

# Person IDs (10 synthetic profiles)
PERSON_IDS = [f"adult_{i:03d}" for i in range(1, 11)]

# Reading Parameters
DAYS_OF_READINGS = 30

# Realistic Vital Ranges for Validation
VITAL_RANGES = {
    "heart_rate": (30, 200),           # bpm
    "systolic_bp": (70, 240),          # mmHg
    "diastolic_bp": (40, 140),         # mmHg
    "oxygen_saturation": (70, 100),    # %
    "temperature": (34.0, 42.0),       # °C
}
