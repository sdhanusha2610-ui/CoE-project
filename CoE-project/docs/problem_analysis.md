# Problem Analysis: Telemonitoring & Low-Value Readings in Older Adults

## Executive Summary

Older adults living alone with limited digital confidence frequently rely on remote monitoring devices to track vital signs. However, healthcare care teams managing these telemetry streams face a major operational bottleneck: **an overwhelming influx of low-value readings and alerts, which masks meaningful clinical changes.**

This problem analysis explores the drivers of alert overload, the risks of current triage paradigms, and the foundational design of a baseline-driven trend summariser.

---

## Why Care Teams Receive Too Many Low-Value Readings

1. **Frequent Home Measurements**
   - High-frequency daily or multi-daily home readings (heart rate, blood pressure, oxygen saturation, temperature) create high-volume time-series data.
   - Raw threshold-based alert systems treat every single data point independently.

2. **Isolated Abnormal Readings & Normal Individual Variation**
   - Transient events (e.g., minor exertion, transient anxiety, improper cuff placement, temporary ambient temperature variation) produce isolated abnormal spikes.
   - Individual vital signs naturally fluctuate throughout the day. Standard population-wide static thresholds fail to account for normal individual variation.

3. **Lack of Personal Baseline**
   - Without a historical personal baseline, a reading of Systolic BP = 138 mmHg might trigger a standard warning, even if that individual's normal resting baseline has consistently hovered around 135 mmHg for months.

4. **Lack of Temporal Context**
   - Single point-in-time readings lack temporal context. Care teams cannot determine whether a single elevated reading is an isolated spike or part of an emerging multi-day trend without manually cross-referencing past logs.

5. **Repeated Low-Value Alerts & Alert Fatigue**
   - Constant notification of benign, isolated deviations desensitizes care teams. Alert fatigue leads to delayed responses, cognitive overload, and the risk of missing genuine, meaningful clinical changes.

6. **Gradual Changes Hidden Among Raw Readings**
   - Progressive, subtle changes (such as a slow rise in blood pressure over two weeks) remain undetected when raw readings fluctuate within broad normal ranges or are buried in daily noisy logs.

---

## Proposed Solution Direction

To shift from reactive raw-reading alerts to proactive, meaningful pattern recognition, the proposed pipeline follows a transparent flow:

```
Individual readings
        ↓
Personal baseline
        ↓
Recent readings
        ↓
Change from baseline
        ↓
Basic trend detection & Alert Prioritisation
        ↓
Trend summary & Escalation Outcome
```

### Key Principles of the Prototype Foundation:
- **Prioritise Sustained Change Over Single Outliers**: Distinguish between isolated transient readings and sustained, persistent shifts.
- **Individual-Centric Baselines**: Measure deviations against each individual's median historical pattern rather than population static thresholds.
- **Human-Readable Summaries**: Provide clear, concise summaries describing the nature of the change without overwhelming care teams with raw data dumps.

---

## Scope Boundaries & Non-Goals

> [!IMPORTANT]
> **Prototype Boundaries (Review 2 Stage)**
> - **No Medical Diagnosis**: This prototype does NOT provide diagnosis or medical clinical assessments.
> - **No Treatment Recommendations**: The system does NOT suggest medication changes or medical interventions.
> - **No Autonomous Medical Escalation**: All output is strictly informational to assist human care team review; no automated clinical actions or triage escalations are performed by this software.
