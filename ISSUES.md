# 🎯 ISSUES.md

**Project:** Clinic Cancellation Chatbot  
**Last Updated:** 2025-11-01  
**GitHub Project:** [Clinic Chatbot MVP](https://github.com/users/dollythedog/projects/1)

---

## 📊 Overview

Track project issues locally and sync with GitHub Issues. Use `make issues-sync` to update from GitHub.

**Current Status:** 🚧 Milestone 3 Complete - Moving to Milestone 4 (Hardening)  
**Progress:** 18/25 issues closed (72%) | 3/5 milestones complete (60%)

---

## ✅ Milestone 1: Bootstrap - COMPLETE

### 🔴 High Priority (DONE)
- [x] Initialize Git repository (@dollythedog) ✅
- [x] [#1](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/1) - Create project directory structure (@dollythedog) ✅
- [x] [#2](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/2) - Set up virtual environment and requirements.txt (@dollythedog) ✅
- [x] [#3](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/3) - Create .env.example with all config variables (@dollythedog) ✅

### 🟡 Medium Priority (DONE)
- [x] [#4](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/4) - Define database schema (schema.sql) (@dollythedog) ✅
- [x] [#5](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/5) - Set up Alembic for migrations (@dollythedog) ✅
- [x] [#6](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/6) - Implement time_utils.py (UTC/Central conversion) (@dollythedog) ✅
- [x] [#7](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/7) - Create basic FastAPI skeleton with health check (@dollythedog) ✅

---

## 📋 Milestone 2: Core Logic - COMPLETE

### 🔴 High Priority (DONE)
- [x] [#8](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/8) - Implement ORM models (models.py) (@dollythedog) ✅
- [x] [#9](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/9) - Build prioritizer.py with scoring algorithm (@dollythedog) ✅
- [x] [#10](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/10) - Create orchestrator.py (batch sending, hold timers) (@dollythedog) ✅
- [x] [#15](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/15) - Add race-safe reservation logic (SELECT FOR UPDATE) (@dollythedog) ✅

### 🟡 Medium Priority (DONE)
- [x] [#11](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/11) - Implement SMS webhook handler (/sms/inbound) (@dollythedog) ✅
- [x] [#12](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/12) - Implement status webhook handler (/twilio/status) (@dollythedog) ✅
- [x] [#13](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/13) - Build manual cancellation entry endpoint (/admin/cancel) (@dollythedog) ✅
- [x] [#14](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/14) - Set up APScheduler for hold timer expiration (@dollythedog) ✅

---

## 📋 Milestone 3: Dashboard - COMPLETE

### 🟡 Medium Priority (DONE)
- [x] [#16](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/16) - Create Streamlit dashboard app (@dollythedog) ✅
- [x] [#17](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/17) - Build active cancellations view (@dollythedog) ✅
- [x] [#18](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/18) - Add waitlist leaderboard (sorted by priority) (@dollythedog) ✅
- [x] Display active offers with countdown timers (@dollythedog) ✅
- [x] Implement message audit log viewer (@dollythedog) ✅
- [x] Add manual boost controls (@dollythedog) ✅
- [x] Add waitlist CRUD operations (@dollythedog) ✅

---

## 📋 Milestone 4: Hardening

### 🔴 High Priority (HIPAA Critical)
- [ ] [#19](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/19) - Implement STOP/HELP keyword handling (@dollythedog)
- [ ] [#20](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/20) - Add opt-out tracking in database (@dollythedog)
- [ ] [#21](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/21) - Create audit logging system (@dollythedog)
- [ ] [#22](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/22) - Add rate limiting to prevent spam (@dollythedog)
- [ ] Implement exception handling and error recovery (@dollythedog)

### 🟡 Medium Priority
- [ ] Write comprehensive test suite (@dollythedog)
- [ ] Create deployment documentation (@dollythedog)
- [ ] Write staff runbook and SOP (@dollythedog)

---

## 🔐 Security & Compliance Checklist

### 🔴 High Priority (Blocking Launch)
- [ ] [#23](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/23) - Sign Twilio BAA (@dollythedog)
- [ ] [#24](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/24) - Complete A2P 10DLC registration (@dollythedog)
- [ ] [#25](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/25) - Verify no PHI in SMS message bodies (@dollythedog)
- [ ] Enable database encryption at rest (@dollythedog)
- [ ] Implement TLS 1.2+ for all webhook connections (@dollythedog)
- [ ] Implement webhook signature verification (@dollythedog)

### 🟡 Medium Priority
- [ ] Create principle of least privilege DB user (@dollythedog)
- [ ] Document data retention policy (@dollythedog)
- [ ] Complete staff training (@dollythedog)

---

## 🚀 Milestone 5: Greenway Integration (Future)

### 🟢 Low Priority / Phase 2
- [ ] Evaluate Greenway API capabilities (@dollythedog)
- [ ] Choose integration approach (webhook/polling/CSV) (@dollythedog)
- [ ] Map Greenway fields to internal schema (@dollythedog)
- [ ] Build integration module (@dollythedog)
- [ ] Test end-to-end with production data (@dollythedog)
- [ ] Create monitoring and alerting (@dollythedog)

---

## 🐛 Bugs

_(None yet - will be added as discovered)_

---

## 💡 Enhancements

### 🟢 Low Priority / Phase 3
- [ ] Patient preference learning (ML-based)
- [ ] Multi-language support
- [ ] Integration with patient portal
- [ ] Predictive cancellation modeling

---

## 📝 Notes

**Labels Used:**
- `milestone-1-bootstrap`, `milestone-2-core`, `milestone-3-dashboard`, `milestone-4-hardening`, `milestone-5-greenway`
- `priority-high`, `priority-medium`, `priority-low`
- `bug`, `enhancement`, `documentation`, `security`, `hipaa-critical`

**Sync Command:**
```bash
make issues-sync
```

**Create Issue:**
```bash
gh issue create --title "Task name" --label "priority-high,milestone-1-bootstrap" --milestone "MVP"
```

---

## 🎯 Current Focus

**✅ Milestone 1 COMPLETE:** Bootstrap (Issues #1-#7) - 100% done  
**✅ Milestone 2 COMPLETE:** Core Logic (Issues #8-#15) - 100% done  
**✅ Milestone 3 COMPLETE:** Dashboard (Issues #16-#18) - 100% done  
**🔜 Next Session:** Start Milestone 4 - Hardening (Issues #19-#22)  
**Blocker:** None

**Recent Accomplishments (2025-11-01):**
- ✅ Fixed SQLAlchemy enum handling for Windows compatibility
- ✅ Fixed Windows date formatting issues (%-I format)
- ✅ Fixed dashboard infinite rerun loop
- ✅ Created seed_sample_data.py for easy testing
- ✅ **Added ntfy.sh integration for mock SMS testing**
- ✅ Mock Twilio client now sends push notifications to phone
- ✅ Dashboard fully functional with real-time monitoring
- ✅ All core logic implemented and tested

---

## 📈 Quick Stats

- **Total Issues Created:** 25
- **Open Issues:** 7
- **Closed Issues:** 18 ✅
- **Milestones Complete:** 3 of 5 (60%)
- **High Priority Remaining:** 2
- **HIPAA Critical:** 6
