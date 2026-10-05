# A Field-Ready Prototype for Older Adults Living Alone with Limited Digital Confidence

## Overview & Progress Status

> [!NOTE]
> **Milestone Status**: **Review 2 Full Prototype Implementation**  
> This repository presents an end-to-end working prototype designed for **older adults living alone with limited digital confidence**. It prioritises **sustained personal baseline trends** over noisy individual readings, drastically reducing care-team alert fatigue.

---

## 1. Problem Statement

Older adults living alone with limited digital confidence rely on home telemonitoring devices to capture vital signs. However, healthcare care teams monitoring these telemetry feeds receive an overwhelming volume of **low-value readings** and isolated alerts, causing severe **alert fatigue** while risking that **meaningful clinical changes** remain hidden in raw noise.

---

## 2. Solution Architecture & Proposed Approach

### Proposed Pipeline Flow
```
Individual Home Readings & Symptom Reports
        ↓
Personal Median Baseline Calculation
        ↓
Rolling Recent Window (7 Days)
        ↓
Deviation Analysis & Trend Detection
        ↓
Alert Prioritisation (LOW / MEDIUM / HIGH)
        ↓
Escalation Outcomes & Privacy-Gated Dashboard
```

- **Non-Diagnostic Scope**: This prototype does NOT provide clinical diagnosis, medical treatment recommendations, or autonomous emergency dispatch.

---

## 3. Synthetic Dataset & Privacy by Design

### Synthetic Dataset
- **Profiles**: 10 synthetic older adult profiles (`adult_001` through `adult_010`).
- **Duration**: 30 days of daily readings per profile.
- **Fields**: `person_id`, `timestamp`, `heart_rate`, `systolic_bp`, `diastolic_bp`, `oxygen_saturation`, `temperature`, `symptom_report`, `consent_status`, `ground_truth_event`.
- **Clinical Patterns**: Stable, Natural Variation, Isolated Change, Persistent Change, Gradual Trend.

### Privacy & Security Controls
- **Anonymous IDs**: Only `adult_001` to `adult_010` are used. No names, phone numbers, or PII.
- **Consent Revocation Gate**: Care Team view is immediately blocked if consent is revoked.
- **Role-Based Access Control**: Specialized UI modes for Older Adult, Care Team, and Administrator.
- **Prominent Warnings**: Synthetic data notices displayed across all UI views.

---

## 4. Project Structure

```
CoE-project/
│
├── data/
│   ├── raw/
│   │   └── synthetic_home_readings.csv
│   └── processed/
│       └── cleaned_home_readings.csv
│
├── notebooks/
│   └── 01_data_exploration.ipynb
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data_generator.py
│   ├── data_cleaning.py
│   ├── baseline.py
│   ├── trend_detector.py
│   ├── evaluator.py
│   └── edge_cases.py
│
├── app/
│   └── streamlit_app.py
│
├── tests/
│   └── test_basic_pipeline.py
│
├── docs/
│   ├── problem_analysis.md
│   ├── workflow.md
│   └── evaluation_report.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 5. Installation & Execution

### Setup Environment
```bash
# Navigate to project root
cd CoE-project

# Install dependencies
pip install -r requirements.txt
```

### Run Data Pipeline & Data Cleaning
```bash
python3 -m src.data_generator
python3 -m src.data_cleaning
```

### Run Automated Unit Test Suite
```bash
python3 -m pytest tests/test_basic_pipeline.py
```

### Launch Interactive Streamlit Prototype
```bash
streamlit run app/streamlit_app.py
```

---

## 6. 3-Minute Demonstration Guide

1. **Minute 1: Problem & Individual Baseline (0:00 - 1:00)**
   - Open **Tab 1 (Live Role-Based Dashboard)** as Older Adult. Select `adult_001` and `adult_003`. Note how personal baselines differ (120 mmHg vs 135 mmHg).
2. **Minute 2: Priority Queue & Escalation (1:00 - 2:00)**
   - Switch role to Care Team. Select `adult_007`. Observe how a 5-day persistent BP shift generates a **HIGH Priority / Urgent Check-In** escalation outcome.
3. **Minute 3: Consent Gate & Empirical Metrics (2:00 - 3:00)**
   - Toggle consent to `Force Consent Revoked` for `adult_010` to observe the privacy gate.
   - Switch to **Tab 2 (Alert Reduction Experiment)** to view empirical metrics (**>65% reduction in low-value alerts**, confusion matrix, Precision, Recall, FPR, FNR).

---

## 7. Current System Limitations
- Rule-based trend detection relies on transparent statistical thresholds rather than deep neural models.
- Symptom processing uses keyword matching rather than complex medical NLP engines.
- Clinical emergency dispatch is intentionally excluded to ensure safe, human-in-the-loop operation.
