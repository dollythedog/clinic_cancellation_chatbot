"""
Clinic Cancellation Chatbot - Streamlit Dashboard

Real-time monitoring dashboard for staff to view:
- Active cancellations with countdown timers
- Waitlist leaderboard sorted by priority
- Active offers and message history
- Admin controls for manual boost and waitlist management

Author: Jonathan Ives (@dollythedog)
"""

import streamlit as st
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
from sqlalchemy.orm import Session
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infra.db import get_session
from app.infra.models import (
    CancellationEvent, CancellationStatus,
    WaitlistEntry, PatientContact, ProviderReference,
    Offer, OfferState, MessageLog, MessageDirection
)
from utils.time_utils import (
    now_utc, to_local, format_timedelta, minutes_until, 
    time_until, format_for_sms
)

# Page configuration
st.set_page_config(
    page_title="TPCCC Cancellation Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .urgent-flag {
        background-color: #ff4b4b;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .offer-pending {
        background-color: #ffa726;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .offer-accepted {
        background-color: #66bb6a;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .offer-declined {
        background-color: #9e9e9e;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .countdown-timer {
        font-size: 24px;
        font-weight: bold;
        color: #ff4b4b;
    }
    .priority-score {
        font-size: 28px;
        font-weight: bold;
        color: #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("🏥 TPCCC Cancellation Chatbot Dashboard")
st.markdown("**Real-time waitlist management and appointment filling**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()
    
    st.divider()
    
    # Navigation
    st.header("📊 View")
    view = st.radio(
        "Select view:",
        ["Dashboard", "Waitlist", "Message Log", "Admin Tools"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Quick stats
    st.header("📈 Quick Stats")
    
    try:
        with get_session() as db:
            active_cancellations = db.query(CancellationEvent).filter(
                CancellationEvent.status == CancellationStatus.OPEN
            ).count()
            
            active_waitlist = db.query(WaitlistEntry).join(PatientContact).filter(
                WaitlistEntry.active == True,
                PatientContact.opt_out == False
            ).count()
            
            pending_offers = db.query(Offer).filter(
                Offer.state == OfferState.PENDING
            ).count()
        
        st.metric("Active Cancellations", active_cancellations)
        st.metric("Waitlist Size", active_waitlist)
        st.metric("Pending Offers", pending_offers)
    except Exception as e:
        st.error(f"Database error: {e}")
        st.metric("Active Cancellations", "Error")
        st.metric("Waitlist Size", "Error")
        st.metric("Pending Offers", "Error")


def show_dashboard():
    """Display main dashboard with active cancellations and offers"""
    
    st.header("🚨 Active Cancellations")
    
    try:
        with get_session() as db:
            # Get open cancellations
            cancellations = db.query(CancellationEvent).filter(
                CancellationEvent.status == CancellationStatus.OPEN
            ).order_by(CancellationEvent.slot_start_at).all()
            
            if not cancellations:
                st.info("✅ No active cancellations - all slots filled!")
            else:
                for cancel in cancellations:
                    show_cancellation_card(cancel, db)
    except Exception as e:
        st.error(f"Error loading cancellations: {e}")
    
    st.divider()
    
    # Active offers section
    st.header("📱 Active Offers")
    
    try:
        with get_session() as db:
            active_offers = db.query(Offer).filter(
                Offer.state == OfferState.PENDING
            ).order_by(desc(Offer.offer_sent_at)).limit(20).all()
            
            if not active_offers:
                st.info("No pending offers at this time.")
            else:
                for offer in active_offers:
                    show_offer_card(offer, db)
    except Exception as e:
        st.error(f"Error loading offers: {e}")


def show_cancellation_card(cancel: CancellationEvent, db: Session):
    """Display a single cancellation event card"""
    
    provider_name = cancel.provider.provider_name if cancel.provider else "Unknown"
    slot_time_local = to_local(cancel.slot_start_at)
    created_local = to_local(cancel.created_at)
    
    # Calculate time metrics
    time_since_created = now_utc() - cancel.created_at
    time_until_slot = cancel.slot_start_at - now_utc()
    
    with st.expander(
        f"🔴 {provider_name} - {slot_time_local.strftime('%b %d at %I:%M %p')} ({cancel.location})",
        expanded=True
    ):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Provider", provider_name)
            st.metric("Location", cancel.location)
        
        with col2:
            st.metric("Slot Time", slot_time_local.strftime("%I:%M %p CT"))
            st.metric("Time Until Slot", format_timedelta(time_until_slot, short=True))
        
        with col3:
            st.metric("Created", format_timedelta(time_since_created, short=True) + " ago")
            st.metric("Status", cancel.status.value.upper())
        
        # Get offers for this cancellation
        offers = db.query(Offer).filter(
            Offer.cancellation_id == cancel.id
        ).order_by(Offer.batch_number, desc(Offer.offer_sent_at)).all()
        
        if offers:
            st.markdown(f"**Offers Sent:** {len(offers)}")
            
            # Group by batch
            batches = {}
            for offer in offers:
                if offer.batch_number not in batches:
                    batches[offer.batch_number] = []
                batches[offer.batch_number].append(offer)
            
            for batch_num in sorted(batches.keys()):
                batch_offers = batches[batch_num]
                st.markdown(f"**Batch {batch_num}:**")
                
                batch_cols = st.columns(len(batch_offers))
                for idx, offer in enumerate(batch_offers):
                    with batch_cols[idx]:
                        patient_name = offer.patient.display_name or offer.patient.phone_e164[-4:]
                        state_color = {
                            OfferState.PENDING: "🟡",
                            OfferState.ACCEPTED: "🟢",
                            OfferState.DECLINED: "⚪",
                            OfferState.EXPIRED: "⚫",
                            OfferState.FAILED: "🔴"
                        }.get(offer.state, "⚪")
                        
                        st.markdown(f"{state_color} {patient_name}")
                        st.caption(f"{offer.state.value}")
                        
                        if offer.state == OfferState.PENDING and offer.hold_expires_at:
                            mins_left = minutes_until(offer.hold_expires_at)
                            if mins_left > 0:
                                st.markdown(f"⏰ {mins_left:.1f}m left")
        else:
            st.warning("No offers sent yet")


def show_offer_card(offer: Offer, db: Session):
    """Display a single offer card"""
    
    patient_name = offer.patient.display_name or f"***{offer.patient.phone_e164[-4:]}"
    cancel = offer.cancellation
    provider_name = cancel.provider.provider_name if cancel.provider else "Unknown"
    
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        st.markdown(f"**Patient:** {patient_name}")
        # Get priority from waitlist entry
        waitlist_entry = db.query(WaitlistEntry).filter(
            WaitlistEntry.patient_id == offer.patient_id,
            WaitlistEntry.active == True
        ).first()
        priority_score = waitlist_entry.priority_score if waitlist_entry else "N/A"
        st.caption(f"Priority: {priority_score}")
    
    with col2:
        st.markdown(f"**Appointment:** {provider_name}")
        st.caption(format_for_sms(cancel.slot_start_at))
    
    with col3:
        if offer.hold_expires_at:
            mins_left = minutes_until(offer.hold_expires_at)
            if mins_left > 0:
                st.markdown(f"⏰ **Expires in:** {mins_left:.1f} min")
            else:
                st.markdown("⏰ **Status:** Expired")
        else:
            st.markdown("⏰ **Status:** No timer")
    
    with col4:
        state_badge = {
            OfferState.PENDING: "🟡 Pending",
            OfferState.ACCEPTED: "🟢 Accepted",
            OfferState.DECLINED: "⚪ Declined"
        }.get(offer.state, offer.state.value)
        st.markdown(state_badge)
    
    st.divider()


def show_waitlist():
    """Display waitlist leaderboard sorted by priority"""
    
    st.header("📋 Waitlist Leaderboard")
    st.caption("Sorted by priority score (higher = more urgent)")
    
    try:
        with get_session() as db:
            waitlist_entries = db.query(WaitlistEntry).join(
                PatientContact
            ).filter(
                WaitlistEntry.active == True,
                PatientContact.opt_out == False
            ).order_by(
                desc(WaitlistEntry.priority_score),
                WaitlistEntry.joined_at
            ).all()
            
            if not waitlist_entries:
                st.info("Waitlist is empty")
            else:
                st.markdown(f"**Total Active Patients:** {len(waitlist_entries)}")
                
                # Display as cards
                for idx, entry in enumerate(waitlist_entries, 1):
                    show_waitlist_entry_card(entry, idx)
    except Exception as e:
        st.error(f"Error loading waitlist: {e}")


def show_waitlist_entry_card(entry: WaitlistEntry, rank: int):
    """Display a single waitlist entry"""
    
    patient = entry.patient
    patient_name = patient.display_name or f"***{patient.phone_e164[-4:]}"
    
    with st.expander(
        f"#{rank} - {patient_name} (Priority: {entry.priority_score or 0})",
        expanded=(rank <= 5)
    ):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Patient Info**")
            st.write(f"Name: {patient_name}")
            st.write(f"Phone: ***{patient.phone_e164[-4:]}")
            
            if entry.urgent_flag:
                st.markdown('<span class="urgent-flag">🚨 URGENT</span>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Priority Breakdown**")
            st.write(f"**Total Score:** {entry.priority_score or 0}")
            st.write(f"Urgent Flag: +{30 if entry.urgent_flag else 0}")
            st.write(f"Manual Boost: +{entry.manual_boost}")
            
            if entry.current_appt_at:
                days_until = (entry.current_appt_at - now_utc()).days
                st.write(f"Next Appt: {days_until} days away")
            else:
                st.write("Next Appt: None scheduled")
        
        with col3:
            st.markdown("**Preferences**")
            if entry.provider_preference:
                st.write(f"Providers: {', '.join(entry.provider_preference)}")
            else:
                st.write("Providers: Any")
            
            st.write(f"Type: {entry.provider_type_preference or 'Any'}")
            
            days_on_waitlist = (now_utc() - entry.joined_at).days
            st.write(f"On waitlist: {days_on_waitlist} days")
        
        if entry.notes:
            st.info(f"**Notes:** {entry.notes}")


def show_message_log():
    """Display recent message history"""
    
    st.header("📨 Message Log")
    st.caption("Recent SMS messages (last 50)")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        direction_filter = st.selectbox(
            "Direction",
            ["All", "Outbound", "Inbound"],
            index=0
        )
    
    with col2:
        phone_filter = st.text_input("Filter by phone (last 4 digits)", "")
    
    try:
        with get_session() as db:
            query = db.query(MessageLog).order_by(desc(MessageLog.created_at))
            
            # Apply filters
            if direction_filter != "All":
                query = query.filter(
                    MessageLog.direction == MessageDirection[direction_filter.upper()]
                )
            
            if phone_filter:
                query = query.filter(
                    or_(
                        MessageLog.from_phone.like(f"%{phone_filter}"),
                        MessageLog.to_phone.like(f"%{phone_filter}")
                    )
                )
            
            messages = query.limit(50).all()
            
            if not messages:
                st.info("No messages found")
            else:
                for msg in messages:
                    show_message_card(msg)
    except Exception as e:
        st.error(f"Error loading messages: {e}")


def show_message_card(msg: MessageLog):
    """Display a single message log entry"""
    
    direction_icon = "📤" if msg.direction == MessageDirection.OUTBOUND else "📥"
    created_local = to_local(msg.created_at)
    
    with st.expander(
        f"{direction_icon} {msg.direction.value.upper()} - {created_local.strftime('%b %d %I:%M %p')}",
        expanded=False
    ):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Details**")
            st.write(f"From: ***{msg.from_phone[-4:]}")
            st.write(f"To: ***{msg.to_phone[-4:]}")
            st.write(f"Status: {msg.status.value if msg.status else 'N/A'}")
        
        with col2:
            st.markdown("**Timing**")
            st.write(f"Created: {created_local.strftime('%b %d %I:%M:%S %p')}")
            if msg.sent_at:
                st.write(f"Sent: {to_local(msg.sent_at).strftime('%b %d %I:%M:%S %p')}")
            if msg.delivered_at:
                st.write(f"Delivered: {to_local(msg.delivered_at).strftime('%b %d %I:%M:%S %p')}")
        
        st.markdown("**Message Body:**")
        st.text(msg.body)
        
        if msg.error_message:
            st.error(f"Error: {msg.error_message} (Code: {msg.error_code})")


def show_admin_tools():
    """Display admin controls for waitlist management"""
    
    st.header("🔧 Admin Tools")
    st.warning("⚠️ Admin actions will modify the database")
    
    tab1, tab2, tab3 = st.tabs(["Manual Boost", "Add to Waitlist", "Remove from Waitlist"])
    
    with tab1:
        st.subheader("📈 Manual Boost")
        st.caption("Increase priority for urgent patients (0-40 points)")
        
        try:
            with get_session() as db:
                active_entries = db.query(WaitlistEntry).join(
                    PatientContact
                ).filter(
                    WaitlistEntry.active == True,
                    PatientContact.opt_out == False
                ).order_by(
                    desc(WaitlistEntry.priority_score)
                ).all()
                
                if active_entries:
                    entry_options = {
                        f"{entry.patient.display_name or entry.patient.phone_e164[-4:]} (ID: {entry.id})": entry.id
                        for entry in active_entries
                    }
                    
                    selected_entry_name = st.selectbox("Select patient", list(entry_options.keys()))
                    selected_entry_id = entry_options[selected_entry_name]
                    
                    # Get current entry
                    current_entry = next(e for e in active_entries if e.id == selected_entry_id)
                    
                    st.info(f"Current boost: {current_entry.manual_boost}")
                    
                    new_boost = st.slider("New boost value", 0, 40, current_entry.manual_boost)
                    
                    if st.button("Update Boost"):
                        with get_session() as update_db:
                            entry = update_db.query(WaitlistEntry).get(selected_entry_id)
                            entry.manual_boost = new_boost
                            update_db.commit()
                            st.success(f"✅ Boost updated to {new_boost}")
                            st.rerun()
                else:
                    st.info("No active waitlist entries")
        except Exception as e:
            st.error(f"Error loading waitlist entries: {e}")
    
    with tab2:
        st.subheader("➕ Add Patient to Waitlist")
        st.caption("Add a new patient or activate existing patient")
        
        phone = st.text_input("Phone (E.164 format)", placeholder="+12145551234")
        display_name = st.text_input("Display Name", placeholder="John D.")
        
        col1, col2 = st.columns(2)
        with col1:
            urgent = st.checkbox("Urgent Flag")
            manual_boost = st.slider("Manual Boost", 0, 40, 0)
        
        with col2:
            provider_type = st.selectbox("Provider Type", ["Any", "MD/DO", "APP"])
        
        notes = st.text_area("Notes")
        
        if st.button("Add to Waitlist"):
            if not phone:
                st.error("Phone number required")
            else:
                try:
                    with get_session() as add_db:
                        # Check if patient exists
                        patient = add_db.query(PatientContact).filter(
                            PatientContact.phone_e164 == phone
                        ).first()
                        
                        if not patient:
                            # Create new patient
                            patient = PatientContact(
                                phone_e164=phone,
                                display_name=display_name,
                                consent_source="manual_entry"
                            )
                            add_db.add(patient)
                            add_db.flush()
                        
                        # Create waitlist entry
                        entry = WaitlistEntry(
                            patient_id=patient.id,
                            urgent_flag=urgent,
                            manual_boost=manual_boost,
                            provider_type_preference=provider_type if provider_type != "Any" else None,
                            notes=notes,
                            active=True
                        )
                        add_db.add(entry)
                        add_db.commit()
                        
                        st.success(f"✅ {display_name or phone} added to waitlist")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab3:
        st.subheader("➖ Remove from Waitlist")
        st.caption("Deactivate a patient from the waitlist")
        
        try:
            with get_session() as db:
                active_entries = db.query(WaitlistEntry).join(
                    PatientContact
                ).filter(
                    WaitlistEntry.active == True
                ).order_by(
                    desc(WaitlistEntry.priority_score)
                ).all()
                
                if active_entries:
                    entry_options = {
                        f"{entry.patient.display_name or entry.patient.phone_e164[-4:]} (ID: {entry.id})": entry.id
                        for entry in active_entries
                    }
                    
                    selected_entry_name = st.selectbox("Select patient to remove", list(entry_options.keys()))
                    selected_entry_id = entry_options[selected_entry_name]
                    
                    if st.button("Remove from Waitlist", type="primary"):
                        with get_session() as remove_db:
                            entry = remove_db.query(WaitlistEntry).get(selected_entry_id)
                            entry.active = False
                            remove_db.commit()
                            st.success("✅ Patient removed from waitlist")
                            st.rerun()
                else:
                    st.info("No active waitlist entries")
        except Exception as e:
            st.error(f"Error loading waitlist entries: {e}")


# Main content area
if view == "Dashboard":
    show_dashboard()
elif view == "Waitlist":
    show_waitlist()
elif view == "Message Log":
    show_message_log()
elif view == "Admin Tools":
    show_admin_tools()


# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%b %d, %Y at %I:%M:%S %p')} | Auto-refresh: {'ON' if auto_refresh else 'OFF'}")
