# User and Workflow Mapping

## User Personas & Responsibilities

### 1. Older Adult
- **Profile**: Older adult living alone with limited digital confidence.
- **Responsibilities**:
  - Provide regular home vital readings (heart rate, blood pressure, oxygen saturation, temperature).
  - Provide qualitative symptom reports (e.g. feeling dizzy, fatigued, shortness of breath).
  - Explicitly manage (provide or revoke) consent for data sharing with care teams.

### 2. Care Team
- **Profile**: Clinicians, nurses, and care coordinators monitoring multiple older adults.
- **Responsibilities**:
  - Review authorised trend information for older adults who have granted consent.
  - Prioritise high/medium priority alerts and evaluate escalation outcomes (`routine_monitoring`, `care_team_review`, `urgent_check_in`).
  - Avoid wasting clinical time on isolated, benign fluctuations.

### 3. Administrator
- **Profile**: System administrator or technical manager oversight.
- **Responsibilities**:
  - Monitor system-level operational metrics (e.g., total registered profiles, active reading logs, aggregate consent distributions).
  - Manage general configuration without accessing individual clinical vital signs unnecessarily.

---

## Process Mapping

### Current Process (Baseline State)

```
Older Adult
     ↓
Takes reading
     ↓
Reading stored
     ↓
Individual abnormal reading triggers static alert
     ↓
Care team receives many readings/alerts
     ↓
Manual review
     ↓
Meaningful changes difficult to identify
```

### Proposed Process (Review 2 Stage)

```
Older Adult
     ↓
Synthetic home reading & Symptom Report
     ↓
Personal baseline calculation
     ↓
Trend detection & Alert Prioritisation
     ↓
Trend summary & Escalation Outcome
     ↓
Authorised care-team view
```
