# User and Workflow Mapping

## User Personas & Responsibilities

### 1. Older Adult
- **Profile**: Older adult living alone with limited digital confidence.
- **Responsibilities**:
  - Provide regular home vital readings (e.g., heart rate, blood pressure, oxygen saturation, temperature).
  - Optionally provide qualitative symptom reports (*Future Work / Remaining 65%*).
  - Explicitly manage (provide or withdraw) consent for data sharing with care teams.

### 2. Care Team
- **Profile**: Clinicians, nurses, and care coordinators monitoring multiple older adults.
- **Responsibilities**:
  - Review authorised trend information for older adults who have granted consent.
  - Evaluate potentially meaningful directional changes highlighted by trend summaries.
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
Individual abnormal reading may trigger attention
     ↓
Care team receives many readings/alerts
     ↓
Manual review
     ↓
Meaningful changes may be difficult to identify
```

### Proposed Process (35% Milestone Stage)

```
Older Adult
     ↓
Synthetic home reading
     ↓
Personal baseline
     ↓
Basic trend detection
     ↓
Basic trend summary
     ↓
Authorised care-team view
```

> [!NOTE]
> **Future Extensions (Remaining 65%)**:
> - Integrated qualitative symptom reports alongside quantitative vital trends.
> - Multi-tier escalation workflows and alert-reduction performance experiments.
