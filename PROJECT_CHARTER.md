# 🏥 PROJECT_CHARTER.md

**Project Title:** *Automated Clinic Cancellation & Waitlist Chatbot*  
**Project Sponsor:** Jonathan Ives, Chief Strategy Officer  
**Department:** Texas Pulmonary & Critical Care Consultants (TPCCC)  
**Date:** October 2025

---

## 1. Project Goal

**Desired Outcome:**  
Develop a secure, automated SMS-based chatbot system that fills last-minute appointment cancellations by messaging patients from a managed waitlist in real time.

**Success Measures:**

* ≥80% of canceled appointments automatically filled within 2 hours.
* ≥95% accuracy in message delivery (Twilio delivery receipts).
* ≤5% manual intervention required for successful rescheduling.
* Full HIPAA-compliant data handling verified by internal audit.

---

## 2. Problem / Opportunity Definition

**Problem:**  
Manual backfilling of canceled appointments is inefficient, inconsistent, and labor-intensive. Staff must call or text patients individually, leading to unfilled slots, lost revenue, and administrative burnout.

**Opportunity:**  
Automating this workflow enables real-time outreach, improved access for patients seeking earlier visits, and optimized clinic utilization with minimal staff input.

---

## 3. Proposed Solution

**Solution Overview:**  
Implement a Python-based system hosted on the existing TPCCC Windows server, connected to PostgreSQL and Twilio's HIPAA-compliant messaging API.

The system will:

* Monitor cancellations (manually logged or via Greenway integration).
* Automatically message eligible patients from a structured waitlist.
* Prioritize by urgency, manual boost, and next scheduled visit date.
* Update an internal dashboard showing active offers, responses, and fill rates.

**Why this approach:**

* Leverages existing infrastructure (PostgreSQL, Windows server).
* Uses Twilio's proven, HIPAA-eligible communication platform.
* Reduces administrative burden while increasing clinic efficiency.

---

## 4. Alignment with Strategic Goals

* **Operational Efficiency:** Reduces staff time spent on rescheduling.
* **Patient Access:** Improves timely care, especially for urgent patients.
* **Technology Modernization:** Demonstrates TPCCC's commitment to innovation.
* **Data Governance:** Integrates seamlessly with TPCCC's internal data systems and HIPAA standards.

---

## 5. Selection Criteria

| Criteria | Description |
|---------|-------------|
| **Compliance / Regulatory** | Meets HIPAA standards via Twilio BAA and secure Postgres data handling. |
| **Efficiency / Cost Reduction** | Automates manual scheduling tasks, freeing staff time. |
| **Revenue Increase** | Reduces unfilled appointment slots. |
| **Patient Experience** | Provides faster access to care and simpler rescheduling. |

---

## 6. Cost / Benefit Analysis

### **Tangible Benefits**

| Benefit | Value & Probability | Assumptions |
|---------|---------------------|-------------|
| Increased appointment fill rate | $50,000/year, 90% | Average of 2 daily cancellations recovered, $100/visit margin. |
| Reduced staff scheduling time | $15,000/year, 95% | 1 hour/day reclaimed administrative time. |
| Improved provider utilization | Qualitative + Productivity KPIs | Fewer idle time gaps per schedule. |

### **Intangible Benefits**

| Benefit | Value & Probability | Assumptions |
|---------|---------------------|-------------|
| Enhanced patient satisfaction | High probability | Immediate outreach and flexibility. |
| Staff satisfaction and morale | High probability | Reduced stress from manual calling. |
| Demonstrated innovation | Moderate probability | Supports TPCCC's technology-forward identity. |

### **Cost Categories**

| Category | **Amount ($)** | Notes |
|---------|---------------|-------|
| Internal labor hours | TBD | Development & testing (~80–100 hrs). |
| External costs | <$250/month | Twilio HIPAA account, messaging fees. |
| Hardware/software | Minimal | Hosted on existing Windows server + PostgreSQL instance. |
| Other | TBD | Optional Cloudflare/Tailscale tunnel for webhook security. |

---

## 7. Scope

**In-Scope Activities:**

* Design and deploy a Python-based chatbot using Twilio and PostgreSQL.
* Develop FastAPI backend and Streamlit dashboard.
* Build and test prioritization logic (urgent, manual boost, next appointment).
* Integrate basic Greenway cancellation import or manual entry form.

**Out-of-Scope but Critical Activities:**

* Advanced AI triage or voice calling functions.
* Direct EHR write-back integration (future phase).
* Multi-language support or patient portal synchronization.

---

## 8. Major Project Activities

| **Description** | **Who is Responsible** | **Target Date** |
|----------------|----------------------|----------------|
| Define schema and enums (incl. provider integration) | Jonathan Ives | Nov 2025 |
| Build API endpoints (FastAPI) | Jonathan Ives | Dec 2025 |
| Configure Twilio + webhook tunneling | Jonathan Ives | Dec 2025 |
| Develop orchestration logic & hold timers | Jonathan Ives | Jan 2026 |
| Design Streamlit dashboard (scoreboard view) | Jonathan Ives | Jan 2026 |
| Test end-to-end workflow (MVP) | Jonathan Ives + Staff | Feb 2026 |
| Evaluate Greenway integration options | Jonathan Ives | Q2 2026 |

---

## 9. Out-of-Scope Activities Critical to Success

* Staff training for dashboard usage.
* Establishing Twilio BAA and compliance verification.
* Scheduling system governance and change control.

---

## 10. Deliverables

| **Deliverable** | **Description / Use** |
|----------------|----------------------|
| **PostgreSQL schema.sql** | Defines tables, fields, and enums. |
| **FastAPI backend** | Core orchestration, API endpoints, and webhook handlers. |
| **Twilio integration module** | Secure SMS messaging and delivery logging. |
| **Streamlit dashboard** | Real-time scoreboard and message audit. |
| **Runbook & SOP** | Operational documentation for staff. |

---

## 11. Major Obstacles

* Integration limitations with Greenway API (no direct cancellation webhook).
* Potential SMS opt-outs reducing reach.
* Staff adoption of new process during rollout.
* Real-time webhook exposure through firewalls (may need Cloudflare/Tailscale).

---

## 12. Risks & Mitigation

| **Risk** | **Mitigation Strategy** |
|---------|------------------------|
| SMS delivery failures | Monitor Twilio status callbacks; automated retry logic. |
| HIPAA compliance breach | Use Twilio BAA, minimal PHI, audit logging, and encryption. |
| Provider mismatch or prioritization errors | Validation via test patients and manual override. |
| Low patient uptake | Continuous optimization of messaging templates. |

---

## 13. Schedule Overview

### **Major Milestones**

| **Milestone** | **Date** |
|--------------|---------|
| Repository initialized & schema approved | Nov 2025 |
| Twilio setup complete | Dec 2025 |
| Core messaging logic operational | Jan 2026 |
| Dashboard deployed (MVP) | Feb 2026 |
| Staff training & internal launch | Mar 2026 |

### **External Milestones Affecting the Project**

| **Milestone** | **Date** |
|--------------|---------|
| Twilio BAA approval | Dec 2025 |
| Greenway API availability | TBD 2026 |

**Impact of Late Delivery:**  
Delays will result in continued manual scheduling workload, unfilled cancellations, and missed patient engagement opportunities.

---

## 14. Collaboration Needs

| **Collaborator** | **Role** | **Timing / Deliverable** |
|-----------------|---------|-------------------------|
| Front Desk Supervisor | Identify workflow & test cases | Before internal pilot |
| IT Support | Assist with Windows server permissions, tunnels | During setup |
| Compliance Officer | Review message templates & BAA | Before production |
| Provider Group | Approve priority and provider matching logic | Pre-launch |
| Jonathan Ives (Sponsor) | Final review and sign-off | Throughout project |

---

## ✅ Summary

This project will replace a repetitive manual process with an automated, compliant, and patient-friendly communication system. By leveraging your existing server infrastructure and database, it balances efficiency, compliance, and innovation—an ideal pilot for broader workflow automation at TPCCC.
