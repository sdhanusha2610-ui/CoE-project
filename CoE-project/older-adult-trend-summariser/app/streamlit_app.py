"""
Streamlit Prototype Application for Older Adult Trend Summariser (35% Milestone).
Implements Role-Based Access Control (Older Adult, Care Team, Administrator) and Privacy-by-Design.
"""

import sys
from pathlib import Path

# Add project root to path for module imports
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np

from src.data_cleaning import run_cleaning_pipeline
from src.baseline import calculate_personal_baselines, compare_with_baseline
from src.trend_detector import analyze_person_trends, detect_vital_trend
from src.config import PERSON_IDS


# Page Configuration
st.set_page_config(
    page_title="Older Adult Trend Summariser (35% Prototype)",
    page_icon="🏥",
    layout="wide"
)

# Load / Clean Data
@st.cache_data
def get_data():
    return run_cleaning_pipeline()

df = get_data()
baselines = calculate_personal_baselines(df)


# ---------------------------------------------------------
# SIDEBAR NAVIGATION & PRIVACY CONTROLS
# ---------------------------------------------------------
st.sidebar.title("🏥 System Access & Controls")

# Role Selection
role = st.sidebar.radio(
    "Select User Role:",
    ["Older Adult", "Care Team", "Administrator"],
    index=1
)

st.sidebar.divider()

# Privacy & Consent Controls
st.sidebar.subheader("🔒 Privacy Controls")
st.sidebar.warning("⚠️ **SYNTHETIC DATA ONLY**\nThis prototype does not use real patient data.")
st.sidebar.info("Information visibility is restricted strictly according to role and consent status.")

# Global or Per-User Consent Override (for interactive testing)
consent_override = st.sidebar.selectbox(
    "Consent Toggle (Simulation):",
    ["Use Profile Setting", "Force Consent Given", "Force Consent Not Given"]
)

st.sidebar.divider()
st.sidebar.caption("Project Milestone: 35% Foundation Stage")


# ---------------------------------------------------------
# VIEW 1: OLDER ADULT VIEW
# ---------------------------------------------------------
if role == "Older Adult":
    st.title("🏡 Older Adult Dashboard")
    st.caption("Personal Home Health Summary (Anonymous Self-View)")

    # Select Person ID
    selected_person = st.selectbox("Select Your Profile ID:", PERSON_IDS, index=0)
    person_data = df[df["person_id"] == selected_person].sort_values("timestamp")

    # Consent status
    raw_consent = person_data["consent_status"].iloc[-1]
    if consent_override == "Force Consent Given":
        effective_consent = "consent_given"
    elif consent_override == "Force Consent Not Given":
        effective_consent = "consent_not_given"
    else:
        effective_consent = raw_consent

    st.subheader("Your Sharing Preference")
    if effective_consent == "consent_given":
        st.success("✅ **Consent Provided**: Your trend summaries are shared with your designated care team.")
    else:
        st.error("🔒 **Consent Withheld**: Detailed trend summaries are currently restricted from care team view.")

    st.divider()

    # Trend Analysis for Primary Vital (Systolic BP)
    trend_info = analyze_person_trends(df, selected_person, vital_metric="systolic_bp")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Latest Systolic BP (mmHg)",
            value=trend_info["recent_value"],
            delta=trend_info["formatted_change"] if "formatted_change" in trend_info else f"{trend_info['absolute_change']:+g}"
        )
    with col2:
        st.metric(
            label="Personal Baseline (mmHg)",
            value=trend_info["baseline_value"]
        )
    with col3:
        st.metric(
            label="Trend Pattern Status",
            value=trend_info["trend_type"].replace("_", " ").title()
        )

    st.info(f"**Personal Summary**: {trend_info['summary']}")

    st.subheader("Your Recent Home Readings")
    st.dataframe(
        person_data[["timestamp", "heart_rate", "systolic_bp", "diastolic_bp", "oxygen_saturation", "temperature"]].tail(10),
        use_container_width=True
    )


# ---------------------------------------------------------
# VIEW 2: CARE TEAM VIEW
# ---------------------------------------------------------
elif role == "Care Team":
    st.title("🩺 Care Team Dashboard")
    st.caption("Authorised Trend Overview — Prioritising Meaningful Change Over Raw Alerts")

    selected_person = st.selectbox("Select Patient Profile (Anonymous ID):", PERSON_IDS, index=3)
    person_data = df[df["person_id"] == selected_person].sort_values("timestamp")

    # Evaluate Consent
    raw_consent = person_data["consent_status"].iloc[-1]
    if consent_override == "Force Consent Given":
        effective_consent = "consent_given"
    elif consent_override == "Force Consent Not Given":
        effective_consent = "consent_not_given"
    else:
        effective_consent = raw_consent

    # ENFORCE PRIVACY GATE
    if effective_consent != "consent_given":
        st.error("🔒 **Access Restricted**")
        st.warning("Detailed information is unavailable because consent has not been provided.")
    else:
        st.success("✅ **Consent Authorised for Care Team Access**")

        vital_selected = st.selectbox("Select Vital Sign Metric:", ["systolic_bp", "heart_rate", "oxygen_saturation"])
        trend_info = analyze_person_trends(df, selected_person, vital_metric=vital_selected)

        st.subheader("Personal Baseline Trend Summary")

        c1, c2, c3, c4 = st.columns(4)
        c1.write(f"**Person ID:** `{selected_person}`")
        c2.write(f"**Trend Pattern:** `{trend_info['trend_type']}`")
        c3.write(f"**Personal Baseline:** `{trend_info['baseline_value']}`")
        c4.write(f"**Recent Value:** `{trend_info['recent_value']}` (`{trend_info['absolute_change']:+g}`)")

        # Display Summary Block
        st.markdown(f"""
        > **Basic Trend Summary:**  
        > *"{trend_info['summary']}"*  
        >  
        > **Pattern Reasoning:**  
        > {trend_info['reason']}
        """)

        st.subheader("Historical vs Recent Readings Chart")
        person_chart_data = person_data[["timestamp", vital_selected]].set_index("timestamp")
        st.line_chart(person_chart_data)


# ---------------------------------------------------------
# VIEW 3: ADMINISTRATOR VIEW
# ---------------------------------------------------------
elif role == "Administrator":
    st.title("⚙️ Administrator System Overview")
    st.caption("High-Level Operational Metrics (No Unnecessary Vital Data Exposure)")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Synthetic Users", len(PERSON_IDS))
    c2.metric("Total Cleaned Readings", len(df))
    
    consent_given_count = (df.groupby("person_id")["consent_status"].last() == "consent_given").sum()
    c3.metric("Consent Authorised Count", f"{consent_given_count} / {len(PERSON_IDS)}")
    c4.metric("System Health Status", "Operational (35% Stage)")

    st.subheader("Aggregate Consent Distribution")
    consent_counts = df.groupby("person_id")["consent_status"].last().value_counts()
    st.bar_chart(consent_counts)

    st.subheader("System Data Log Info")
    st.json({
        "data_source": "data/processed/cleaned_home_readings.csv",
        "privacy_compliance": "Anonymous Person IDs Only",
        "ml_model_active": False,
        "autonomous_escalation_active": False
    })
