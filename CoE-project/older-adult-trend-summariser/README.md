# A Field-Ready Prototype for Older Adults Living Alone with Limited Digital Confidence

## Current Progress Status

> [!IMPORTANT]
> **Current Milestone**: **Approximately 35% Completed**  
> This codebase represents the **first 35% foundation** of the project. The remaining 65% functionality (advanced machine learning, alert-reduction comparison experiment, escalation workflows, stakeholder validation, 3-minute video demo) is intentionally **not implemented yet** and is documented under [Future Implementation — Remaining 65%](#future-implementation--remaining-65).

---

## 1. Problem Statement

Older adults living alone with limited digital confidence rely on home telemonitoring devices to capture vital signs. However, care teams monitoring these feeds receive an overwhelming volume of **low-value readings** and isolated alerts, causing severe **alert fatigue** while risking that **meaningful clinical changes** remain hidden in raw noise.

---

## 2. Problem Analysis & Proposed Approach

### Why Care Teams Receive Too Many Low-Value Alerts
1. **High Frequency Data Streams**: Continuous daily readings generate high-volume noise.
2. **Isolated Spikes vs Normal Variation**: Individual fluctuations (e.g. minor exertion) trigger standard static alerts.
3. **Lack of Personal Baselines**: Static population thresholds ignore personal resting norms.
4. **Lack of Temporal Context**: Raw data points do not convey whether a shift is isolated or multi-day.
5. **Gradual Changes Hidden**: Slow progressive trends remain undetected beneath static thresholds.

### Proposed Pipeline Architecture (35% Stage)
```
Individual readings
        ↓
Personal baseline
        ↓
Recent readings
        ↓
Change from baseline
        ↓
Basic trend detection
        ↓
Trend summary
```

- **Non-Diagnostic Scope**: This prototype does NOT provide diagnosis, treatment recommendations, or autonomous medical decisions.

---

## 3. Dataset Description & Privacy by Design

### Synthetic Dataset
- **Profiles**: 10 synthetic older adult profiles (`adult_001` through `adult_010`).
- **Duration**: 30 days of daily readings per individual.
- **Fields**: `person_id`, `timestamp`, `heart_rate`, `systolic_bp`, `diastolic_bp`, `oxygen_saturation`, `temperature`, `symptom_report`, `consent_status`.
- **Patterns Demonstrated**:
  1. *Stable* (`adult_001`, `adult_002`)
  2. *Natural Variation* (`adult_003`, `adult_004`)
  3. *Isolated Change* (`adult_005`, `adult_006`)
  4. *Persistent Change* (`adult_007`, `adult_008`)
  5. *Gradual Trend* (`adult_009`, `adult_010`)

### Privacy Controls
- **Strictly Anonymous IDs**: No names, phone numbers, email addresses, or PII.
- **Consent-Driven Visibility**: Detailed care-team views are blocked unless consent is granted.
- **Role-Based Access**: Specialized interfaces for Older Adult, Care Team, and Administrator.
- **Prominent Synthetic Data Warnings**: Displayed prominently across the UI.

---

## 4. Technology Stack & Project Structure

### Technology Stack
- **Language**: Python 3.10+
- **Data & Analytics**: `pandas`, `numpy`
- **Visualization**: `matplotlib`
- **Dashboard Web App**: `streamlit`
- **Testing Framework**: `pytest`

### Project Structure
```
older-adult-trend-summariser/
│
├── data/
│   ├── raw/
│   │   └── synthetic_home_readings.csv
│   │
│   └── processed/
│       └── cleaned_home_readings.csv
│
├── notebooks/
│   └── 01_data_exploration.ipynb
│
├── src/
│   ├── __init__.py
│   ├── data_generator.py
│   ├── data_cleaning.py
│   ├── baseline.py
│   ├── trend_detector.py
│   └── config.py
│
├── app/
│   └── streamlit_app.py
│
├── tests/
│   └── test_basic_pipeline.py
│
├── docs/
│   ├── problem_analysis.md
│   └── workflow.md
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 5. Installation & Execution

### Setup Environment
```bash
# Clone or navigate to directory
cd older-adult-trend-summariser

# Install dependencies
pip install -r requirements.txt
```

### Run Data Pipeline & Clean Data
```bash
python -m src.data_generator
python -m src.data_cleaning
```

### Run Streamlit App
```bash
streamlit run app/streamlit_app.py
```

### Run Automated Unit Tests
```bash
pytest tests/test_basic_pipeline.py
```

---

## 6. Current Limitations (35% Stage)
- Rule-based trend detection uses simple statistical thresholds.
- Quantitative vitals are evaluated primarily; qualitative symptom integration is limited.
- Escalation outcomes and multi-stage alerting experiments are not enabled.

---

## 7. Future Implementation — Remaining 65%

> [!CAUTION]
> The following components belong strictly to the remaining 65% milestone and are **NOT** implemented in this initial stage:

### Remaining 20%
- Complete end-to-end trend summarisation including:
  - Symptom report integration & NLP matching
  - Multi-level escalation workflow outcomes
  - Richer temporal reasoning algorithms

### Remaining 15%
- Comparison Experiment:
  - Simple baseline alert method vs. Trend summariser
  - Metrics: Low-value alerts count, meaningful changes surfaced, false positive rate, false negative rate.

### Remaining 10%
- Realistic Failure and Edge Cases (at least 3 scenarios):
  - Missing or sporadic readings
  - Delayed sensor sync readings
  - Conflicting symptom and vital data
  - Dynamic consent withdrawal / modification mid-monitoring

### Remaining 10%
- Comprehensive Error Analysis:
  - False positive and false negative error classification
  - Missed trend investigation
  - Unnecessary alert reduction analysis

### Remaining 5%
- Stakeholder and user validation feedback
- Final comprehensive evaluation report
- Three-minute demonstration video
- Final production documentation
