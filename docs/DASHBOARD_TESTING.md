# Dashboard Testing Guide

**Project:** Clinic Cancellation Chatbot  
**Component:** Streamlit Dashboard  
**Version:** 0.3.0  
**Last Updated:** November 1, 2025

---

## 🎯 Overview

This guide provides instructions for testing the Streamlit dashboard to verify all Milestone 3 features are working correctly.

---

## 🔧 Prerequisites

1. **Database Setup:**
   - PostgreSQL server running
   - Database initialized with schema
   - `.env` file configured with DATABASE_URL

2. **Dependencies Installed:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Optional - Test Data:**
   - Run seed script to populate test data:
   ```powershell
   python scripts/seed_data.py
   ```

---

## 🚀 Starting the Dashboard

### Method 1: Using Makefile (Recommended)
```powershell
make run-dashboard
```

### Method 2: Using Run Script
```powershell
python run_dashboard.py
```

### Method 3: Direct Streamlit
```powershell
streamlit run dashboard/app.py
```

**Access:** http://localhost:8501

---

## ✅ Test Checklist

### 1. Dashboard View (Main)

**Active Cancellations Section:**
- [ ] Displays message when no cancellations exist
- [ ] Shows open cancellations with:
  - [ ] Provider name
  - [ ] Location
  - [ ] Slot time (in Central Time)
  - [ ] Time until slot
  - [ ] Time since created
  - [ ] Status badge
- [ ] Displays offers grouped by batch
- [ ] Shows offer state with colored indicators:
  - [ ] 🟡 Yellow for Pending
  - [ ] 🟢 Green for Accepted
  - [ ] ⚪ White for Declined
  - [ ] ⚫ Black for Expired
  - [ ] 🔴 Red for Failed
- [ ] Countdown timer shows minutes remaining for pending offers

**Active Offers Section:**
- [ ] Shows recent pending offers (up to 20)
- [ ] Displays patient name/phone (last 4 digits only)
- [ ] Shows appointment provider and time
- [ ] Hold timer countdown
- [ ] Offer state badges

### 2. Waitlist View

**Leaderboard Display:**
- [ ] Shows total active patient count
- [ ] Patients sorted by priority score (highest first)
- [ ] Top 5 entries expanded by default
- [ ] Others collapsed

**Patient Entry Cards:**
- [ ] Patient name/phone (privacy-protected)
- [ ] 🚨 URGENT badge appears when urgent_flag = true
- [ ] Priority breakdown shows:
  - [ ] Total score
  - [ ] Urgent flag contribution (+30)
  - [ ] Manual boost (0-40)
  - [ ] Days until next appointment
- [ ] Provider preferences displayed
- [ ] Provider type preference shown
- [ ] Days on waitlist calculated
- [ ] Notes displayed when present

### 3. Message Log View

**Message Display:**
- [ ] Shows last 50 messages by default
- [ ] Direction filter works (All/Outbound/Inbound)
- [ ] Phone filter works (last 4 digits)
- [ ] Messages show:
  - [ ] Direction icon (📤 outbound / 📥 inbound)
  - [ ] From/To phone (last 4 digits)
  - [ ] Status
  - [ ] Timestamps (created, sent, delivered)
  - [ ] Message body
  - [ ] Error messages when present

### 4. Admin Tools View

**Manual Boost Tab:**
- [ ] Dropdown shows active waitlist patients
- [ ] Current boost value displayed
- [ ] Slider allows 0-40 range
- [ ] "Update Boost" button works
- [ ] Success message appears
- [ ] Page refreshes with new value

**Add to Waitlist Tab:**
- [ ] Phone input accepts E.164 format
- [ ] Display name field works
- [ ] Urgent flag checkbox
- [ ] Manual boost slider (0-40)
- [ ] Provider type dropdown (Any/MD/DO/APP)
- [ ] Notes textarea
- [ ] "Add to Waitlist" button:
  - [ ] Validates phone required
  - [ ] Creates new patient if doesn't exist
  - [ ] Reuses existing patient if found
  - [ ] Creates waitlist entry
  - [ ] Shows success message
  - [ ] Refreshes page

**Remove from Waitlist Tab:**
- [ ] Dropdown shows active entries
- [ ] "Remove from Waitlist" button works
- [ ] Sets active = false
- [ ] Shows success message
- [ ] Refreshes page

### 5. Sidebar

**Quick Stats:**
- [ ] Active Cancellations count
- [ ] Waitlist Size count
- [ ] Pending Offers count
- [ ] Counts update on refresh

**Controls:**
- [ ] Auto-refresh toggle works
- [ ] View selection radio buttons work
- [ ] Database errors handled gracefully

### 6. General UI/UX

**Layout:**
- [ ] Wide layout fills screen
- [ ] Columns sized appropriately
- [ ] Expanders work correctly
- [ ] Tabs switch properly

**Styling:**
- [ ] Custom CSS loads
- [ ] Badge colors display correctly
- [ ] Icons render properly
- [ ] Emoji unicode displays

**Error Handling:**
- [ ] Database connection errors show user-friendly message
- [ ] Query errors don't crash app
- [ ] Empty states display helpful messages

**Performance:**
- [ ] Page loads quickly (<2 seconds)
- [ ] Auto-refresh doesn't lag
- [ ] Large waitlists render smoothly

---

## 🐛 Common Issues & Solutions

### Issue: "Database error: could not connect"
**Solution:** 
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env` is correct
- Test connection: `python -c "from app.infra.db import check_db_connection; print(check_db_connection())"`

### Issue: "No module named 'streamlit'"
**Solution:** 
```powershell
pip install streamlit
```

### Issue: "ImportError: cannot import name 'get_session'"
**Solution:** 
- Ensure you're running from project root
- Check Python path includes project directory

### Issue: Auto-refresh not working
**Solution:** 
- This is normal for Streamlit
- Auto-refresh re-runs entire script every 30s
- Can be CPU intensive with large datasets

### Issue: Phone numbers not displaying
**Solution:** 
- Ensure patient_contact.phone_e164 has values
- Check display format: `***{phone[-4:]}`

---

## 📊 Test Data Requirements

For comprehensive testing, database should have:

**Minimum:**
- 1 provider (provider_reference)
- 3 patients (patient_contact)
- 3 waitlist entries (different priority scores)
- 1 cancellation event (status = 'open')
- 3 offers (1 per patient, same cancellation)
- 5 message logs (mix of inbound/outbound)

**Recommended:**
- 5+ providers (different types: MD/DO, APP)
- 10+ patients (some with opt_out = true)
- 10+ waitlist entries (varied priorities)
- 3+ cancellation events (different statuses)
- 10+ offers (varied states)
- 20+ message logs

**Use seed script:**
```powershell
python scripts/seed_data.py
```

---

## 🎯 Acceptance Criteria

Dashboard is considered complete when:

✅ All views load without errors  
✅ Real-time data displays correctly  
✅ All CRUD operations work (add/update/remove)  
✅ Privacy protection enforced (last 4 digits only)  
✅ Countdown timers update properly  
✅ Filters work in message log  
✅ Error states handled gracefully  
✅ Mobile/responsive layout works  
✅ Auto-refresh functions without crashes  

---

## 📝 Testing Notes

**Date:** _____________  
**Tester:** _____________  
**Build Version:** 0.3.0  

**Issues Found:**
1. _________________________________
2. _________________________________
3. _________________________________

**Sign-off:**
- [ ] All critical features working
- [ ] No blocking bugs
- [ ] Ready for user acceptance testing

---

## 🔗 Related Documentation

- [README.md](../README.md) - Project overview
- [PROJECT_PLAN.md](../PROJECT_PLAN.md) - Technical specifications
- [SESSION_SUMMARY.md](../SESSION_SUMMARY.md) - Implementation details
- [RUNBOOK.md](./RUNBOOK.md) - Operations guide (future)

---

**Questions or Issues?**  
Contact: Jonathan Ives (@dollythedog)
