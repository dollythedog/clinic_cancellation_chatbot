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
    /* Fix button sizing - make all buttons same height */
    div[data-testid="column"] button[kind="secondary"],
    div[data-testid="column"] button[kind="primary"] {
        height: 3.5rem !important;
        min-height: 3.5rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.2 !important;
        padding: 0.5rem !important;
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


# Main navigation with tab-style buttons
st.markdown("---")
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.get('view', 'Dashboard') == 'Dashboard' else "secondary"):
        st.session_state.view = 'Dashboard'
        st.rerun()

with col2:
    if st.button("📋 Waitlist", use_container_width=True, type="primary" if st.session_state.get('view') == 'Waitlist' else "secondary"):
        st.session_state.view = 'Waitlist'
        st.rerun()

with col3:
    if st.button("📨 Message Log", use_container_width=True, type="primary" if st.session_state.get('view') == 'Message Log' else "secondary"):
        st.session_state.view = 'Message Log'
        st.rerun()

with col4:
    if st.button("🔧 Admin Tools", use_container_width=True, type="primary" if st.session_state.get('view') == 'Admin Tools' else "secondary"):
        st.session_state.view = 'Admin Tools'
        st.rerun()

with col5:
    if st.button("➕ Add Cancellation", use_container_width=True, type="primary" if st.session_state.get('view') == 'Add Cancellation' else "secondary"):
        st.session_state.view = 'Add Cancellation'
        st.rerun()

with col6:
    if st.button("🆕 Add Patient", use_container_width=True, type="primary" if st.session_state.get('view') == 'Add Patient' else "secondary"):
        st.session_state.view = 'Add Patient'
        st.rerun()

with col7:
    if st.button("📸 Photo Guide", use_container_width=True, type="primary" if st.session_state.get('view') == 'Photo Guide' else "secondary"):
        st.session_state.view = 'Photo Guide'
        st.rerun()

# Initialize view if not set
if 'view' not in st.session_state:
    st.session_state.view = 'Dashboard'

view = st.session_state.view
st.markdown("---")


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
        
        # Admin action buttons
        st.markdown("---")
        action_col1, action_col2, action_col3 = st.columns([1, 1, 3])
        
        with action_col1:
            if st.button(f"🗑️ Delete", key=f"delete_cancel_{cancel.id}", help="Permanently delete this cancellation"):
                try:
                    # Delete related offers and messages first
                    db.query(Offer).filter(Offer.cancellation_id == cancel.id).delete()
                    db.query(CancellationEvent).filter(CancellationEvent.id == cancel.id).delete()
                    db.commit()
                    st.success("Cancellation deleted")
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error deleting: {e}")
        
        with action_col2:
            if st.button(f"❌ Void", key=f"void_cancel_{cancel.id}", help="Mark as cancelled (no longer available)"):
                try:
                    cancel.status = CancellationStatus.ABORTED
                    # Expire any pending offers
                    db.query(Offer).filter(
                        Offer.cancellation_id == cancel.id,
                        Offer.state == OfferState.PENDING
                    ).update({"state": OfferState.EXPIRED})
                    db.commit()
                    st.success("Cancellation voided")
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error voiding: {e}")


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
        
        # Add cancel button for pending offers
        if offer.state == OfferState.PENDING:
            if st.button("❌ Cancel", key=f"cancel_offer_{offer.id}", help="Cancel this pending offer"):
                try:
                    offer.state = OfferState.EXPIRED
                    db.commit()
                    st.success("Offer cancelled")
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error: {e}")
    
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
        
        # Admin action buttons
        st.markdown("---")
        action_col1, action_col2, action_col3, action_col4 = st.columns([1, 1, 1, 2])
        
        with action_col1:
            if st.button("✏️ Edit", key=f"edit_patient_{entry.id}", help="Edit patient details"):
                st.session_state.edit_patient_id = entry.id
                st.session_state.view = 'Admin Tools'
                st.rerun()
        
        with action_col2:
            if entry.active:
                if st.button("⏸️ Deactivate", key=f"deactivate_patient_{entry.id}", help="Remove from active waitlist"):
                    try:
                        with get_session() as action_db:
                            waitlist_entry = action_db.query(WaitlistEntry).filter(
                                WaitlistEntry.id == entry.id
                            ).first()
                            waitlist_entry.active = False
                            action_db.commit()
                            st.success("Patient deactivated")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with action_col3:
            if st.button("🗑️ Delete", key=f"delete_patient_{entry.id}", help="Permanently delete patient"):
                try:
                    with get_session() as action_db:
                        # Delete waitlist entry and patient if no other data
                        action_db.query(WaitlistEntry).filter(
                            WaitlistEntry.id == entry.id
                        ).delete()
                        # Check if patient has other entries or offers
                        has_offers = action_db.query(Offer).filter(
                            Offer.patient_id == patient.id
                        ).count() > 0
                        if not has_offers:
                            action_db.query(PatientContact).filter(
                                PatientContact.id == patient.id
                            ).delete()
                        action_db.commit()
                        st.success("Patient deleted")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")


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


def show_add_cancellation():
    """Display form to manually add a cancellation event"""
    
    st.header("➕ Add Cancellation")
    st.caption("Manually log a cancellation to trigger waitlist offers")
    
    try:
        with get_session() as db:
            # Get list of providers
            providers = db.query(ProviderReference).filter(
                ProviderReference.active == True
            ).order_by(ProviderReference.provider_name).all()
            
            if not providers:
                st.error("No active providers found in the database. Please add providers first.")
                return
            
            provider_options = {
                f"{p.provider_name} ({p.provider_type})": p.id
                for p in providers
            }
            
            with st.form("add_cancellation_form"):
                st.subheader("Appointment Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_provider_name = st.selectbox(
                        "Provider *",
                        options=list(provider_options.keys()),
                        help="Select the provider for this appointment"
                    )
                    
                    location = st.text_input(
                        "Location *",
                        placeholder="Main Clinic",
                        help="Clinic location name"
                    )
                    
                    reason = st.selectbox(
                        "Reason for Cancellation",
                        options=[
                            "Patient cancelled",
                            "Provider schedule change",
                            "Emergency",
                            "No-show",
                            "Other"
                        ]
                    )
                
                with col2:
                    slot_date = st.date_input(
                        "Appointment Date *",
                        value=datetime.now().date(),
                        min_value=datetime.now().date()
                    )
                    
                    slot_time = st.time_input(
                        "Appointment Time *",
                        value=datetime.now().time()
                    )
                    
                    duration_minutes = st.number_input(
                        "Duration (minutes) *",
                        min_value=15,
                        max_value=240,
                        value=30,
                        step=15
                    )
                
                notes = st.text_area(
                    "Notes (optional)",
                    placeholder="Additional information about this cancellation..."
                )
                
                st.markdown("**Required fields marked with ***")
                
                submit_button = st.form_submit_button("🚀 Create Cancellation & Send Offers", type="primary")
                
                if submit_button:
                    if not location:
                        st.error("Location is required")
                    else:
                        try:
                            import requests
                            
                            provider_id = provider_options[selected_provider_name]
                            
                            # Combine date and time to create datetime
                            slot_start = datetime.combine(slot_date, slot_time)
                            slot_end = slot_start + timedelta(minutes=duration_minutes)
                            
                            # Convert to UTC (assuming local is Central Time)
                            from utils.time_utils import make_aware, to_utc
                            slot_start_aware = make_aware(slot_start)
                            slot_end_aware = make_aware(slot_end)
                            slot_start_utc = to_utc(slot_start_aware)
                            slot_end_utc = to_utc(slot_end_aware)
                            
                            # Call API to create cancellation (triggers orchestrator automatically)
                            api_url = "http://localhost:8000/admin/cancel"
                            payload = {
                                "provider_id": provider_id,
                                "location": location,
                                "slot_start_at": slot_start_utc.isoformat(),
                                "slot_end_at": slot_end_utc.isoformat(),
                                "reason": reason,
                                "notes": notes
                            }
                            
                            response = requests.post(api_url, json=payload, timeout=10)
                            response.raise_for_status()
                            
                            result = response.json()
                            
                            st.success(f"✅ Cancellation created successfully! (ID: {result['id']})")
                            st.info(f"📨 Sent {result['offers_sent']} SMS offer(s) to waitlist patients")
                                
                                # Show summary
                                st.markdown("**Cancellation Summary:**")
                                st.write(f"- Provider: {selected_provider_name}")
                                st.write(f"- Location: {location}")
                                st.write(f"- Time: {slot_start.strftime('%b %d, %Y at %I:%M %p')} CT")
                                st.write(f"- Duration: {duration_minutes} minutes")
                                st.write(f"- Reason: {reason}")
                                
                                # Set flag to show view dashboard button
                                st.session_state.show_dashboard_button = True
                                
                        except Exception as e:
                            st.error(f"Error creating cancellation: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
            
            # Show dashboard button outside form if cancellation was created
            if st.session_state.get('show_dashboard_button', False):
                if st.button("📊 View on Dashboard"):
                    st.session_state.view = 'Dashboard'
                    st.session_state.show_dashboard_button = False
                    st.rerun()
        
    except Exception as e:
        st.error(f"Error loading form: {e}")


def show_add_patient():
    """Display form to add a patient to the waitlist"""
    
    st.header("🆕 Add Patient to Waitlist")
    st.caption("Add a new patient or reactivate an existing patient on the waitlist")
    
    with st.form("add_patient_form"):
        st.subheader("Patient Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            phone = st.text_input(
                "Phone Number (E.164 format) *",
                placeholder="+12145551234",
                help="Format: +1 followed by 10-digit number"
            )
            
            display_name = st.text_input(
                "Display Name *",
                placeholder="John D.",
                help="Patient's name (first name + last initial for privacy)"
            )
            
            current_appt_date = st.date_input(
                "Current Appointment Date (if scheduled)",
                value=None,
                min_value=datetime.now().date(),
                help="If patient already has an appointment, enter the date"
            )
        
        with col2:
            provider_type_pref = st.selectbox(
                "Provider Type Preference",
                options=["Any", "MD/DO", "APP"],
                help="Patient's preference for provider type"
            )
            
            urgent = st.checkbox(
                "🚨 Urgent Flag",
                help="Check if patient needs urgent/priority access (+30 priority points)"
            )
            
            manual_boost = st.slider(
                "Manual Boost",
                min_value=0,
                max_value=40,
                value=0,
                help="Additional priority points (0-40)"
            )
        
        st.subheader("Additional Details")
        
        notes = st.text_area(
            "Notes (optional)",
            placeholder="Reason for waitlist, special requirements, etc.",
            help="Internal notes about this patient (not sent in SMS)"
        )
        
        st.markdown("**Required fields marked with ***")
        
        submit_button = st.form_submit_button("✅ Add to Waitlist", type="primary")
        
        if submit_button:
            # Validation
            errors = []
            if not phone:
                errors.append("Phone number is required")
            elif not phone.startswith("+1") or len(phone) != 12:
                errors.append("Phone must be in E.164 format: +12145551234")
            
            if not display_name:
                errors.append("Display name is required")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    with get_session() as add_db:
                        # Check if patient already exists
                        patient = add_db.query(PatientContact).filter(
                            PatientContact.phone_e164 == phone
                        ).first()
                        
                        if patient:
                            st.info(f"ℹ️ Patient {phone} already exists in database")
                            # Update display name if different
                            if display_name and patient.display_name != display_name:
                                patient.display_name = display_name
                        else:
                            # Create new patient
                            patient = PatientContact(
                                phone_e164=phone,
                                display_name=display_name,
                                consent_source="manual_entry",
                                opt_out=False
                            )
                            add_db.add(patient)
                            add_db.flush()  # Get patient ID
                            st.success(f"✅ New patient created: {display_name}")
                        
                        # Check for existing active waitlist entry
                        existing_entry = add_db.query(WaitlistEntry).filter(
                            WaitlistEntry.patient_id == patient.id,
                            WaitlistEntry.active == True
                        ).first()
                        
                        if existing_entry:
                            st.warning(f"⚠️ Patient already has an active waitlist entry (ID: {existing_entry.id})")
                            st.write("Update the entry instead?")
                        else:
                            # Convert current_appt_date to datetime if provided
                            current_appt_datetime = None
                            if current_appt_date:
                                current_appt_datetime = datetime.combine(
                                    current_appt_date,
                                    datetime.min.time()
                                )
                                from utils.time_utils import local_to_utc
                                current_appt_datetime = local_to_utc(current_appt_datetime)
                            
                            # Create waitlist entry
                            entry = WaitlistEntry(
                                patient_id=patient.id,
                                urgent_flag=urgent,
                                manual_boost=manual_boost,
                                provider_type_preference=provider_type_pref if provider_type_pref != "Any" else None,
                                current_appt_at=current_appt_datetime,
                                notes=notes,
                                active=True
                            )
                            add_db.add(entry)
                            add_db.commit()
                            add_db.refresh(entry)
                            
                            st.success(f"✅ {display_name} added to waitlist! (Entry ID: {entry.id})")
                            
                            # Show summary
                            st.markdown("**Waitlist Entry Summary:**")
                            st.write(f"- Patient: {display_name}")
                            st.write(f"- Phone: {phone}")
                            st.write(f"- Urgent: {'Yes 🚨' if urgent else 'No'}")
                            st.write(f"- Manual Boost: {manual_boost}")
                            st.write(f"- Provider Type: {provider_type_pref}")
                            if current_appt_date:
                                st.write(f"- Current Appointment: {current_appt_date.strftime('%b %d, %Y')}")
                            
                            # Button to view waitlist
                            if st.button("📋 View Waitlist"):
                                st.session_state.view = 'Waitlist'
                                st.rerun()
                            
                except Exception as e:
                    st.error(f"Error adding patient: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


def show_admin_tools():
    """Display admin controls for waitlist management"""
    
    st.header("🔧 Admin Tools")
    st.warning("⚠️ Admin actions will modify the database")
    
    # Check if we're in edit mode for a specific patient
    if st.session_state.get('edit_patient_id'):
        show_edit_patient_form(st.session_state.edit_patient_id)
        return
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Manual Boost", 
        "Remove from Waitlist", 
        "Bulk Operations",
        "Cancellation Management",
        "System Cleanup"
    ])
    
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
    
    with tab3:
        st.subheader("📦 Bulk Operations")
        st.caption("Perform bulk actions on multiple records")
        
        bulk_col1, bulk_col2 = st.columns(2)
        
        with bulk_col1:
            st.markdown("**Expire Old Offers**")
            st.write("Expire all pending offers older than X hours")
            hours_threshold = st.number_input("Hours", min_value=1, max_value=72, value=24)
            if st.button("⏱️ Expire Old Offers"):
                try:
                    with get_session() as bulk_db:
                        cutoff_time = now_utc() - timedelta(hours=hours_threshold)
                        result = bulk_db.query(Offer).filter(
                            Offer.state == OfferState.PENDING,
                            Offer.offer_sent_at < cutoff_time
                        ).update({"state": OfferState.EXPIRED})
                        bulk_db.commit()
                        st.success(f"✅ Expired {result} old offers")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with bulk_col2:
            st.markdown("**Reactivate Inactive Patients**")
            st.write("Reactivate all inactive waitlist entries")
            if st.button("▶️ Reactivate All"):
                try:
                    with get_session() as bulk_db:
                        result = bulk_db.query(WaitlistEntry).filter(
                            WaitlistEntry.active == False
                        ).update({"active": True})
                        bulk_db.commit()
                        st.success(f"✅ Reactivated {result} patients")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab4:
        st.subheader("🗓️ Cancellation Management")
        st.caption("View and manage all cancellations")
        
        try:
            with get_session() as db:
                # Filter options
                status_filter = st.selectbox(
                    "Status",
                    ["All", "OPEN", "FILLED", "ABORTED", "EXPIRED"]
                )
                
                query = db.query(CancellationEvent).order_by(desc(CancellationEvent.created_at))
                
                if status_filter != "All":
                    query = query.filter(
                        CancellationEvent.status == CancellationStatus[status_filter]
                    )
                
                cancellations = query.limit(50).all()
                
                if cancellations:
                    st.write(f"Showing {len(cancellations)} cancellation(s)")
                    
                    for cancel in cancellations:
                        provider_name = cancel.provider.provider_name if cancel.provider else "Unknown"
                        slot_time = to_local(cancel.slot_start_at).strftime("%b %d at %I:%M %p")
                        
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{provider_name}**")
                        with col2:
                            st.write(slot_time)
                        with col3:
                            st.write(cancel.status.value)
                        with col4:
                            if st.button("🗑️", key=f"admin_del_{cancel.id}"):
                                try:
                                    db.query(Offer).filter(Offer.cancellation_id == cancel.id).delete()
                                    db.query(CancellationEvent).filter(CancellationEvent.id == cancel.id).delete()
                                    db.commit()
                                    st.success("Deleted")
                                    st.rerun()
                                except Exception as e:
                                    db.rollback()
                                    st.error(f"Error: {e}")
                        with col5:
                            if cancel.status == CancellationStatus.OPEN:
                                if st.button("❌", key=f"admin_void_{cancel.id}"):
                                    try:
                                        cancel.status = CancellationStatus.ABORTED
                                        db.commit()
                                        st.success("Voided")
                                        st.rerun()
                                    except Exception as e:
                                        db.rollback()
                                        st.error(f"Error: {e}")
                        
                        st.divider()
                else:
                    st.info("No cancellations found")
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab5:
        st.subheader("🧼 System Cleanup")
        st.caption("⚠️ Use with caution - these actions delete data permanently")
        
        cleanup_col1, cleanup_col2 = st.columns(2)
        
        with cleanup_col1:
            st.markdown("**Delete All Test Data**")
            st.write("Remove all cancellations, offers, and messages")
            confirm_test = st.checkbox("I understand this will delete all test data")
            if st.button("🧽 Clear All Data", disabled=not confirm_test):
                try:
                    with get_session() as cleanup_db:
                        msg_count = cleanup_db.query(MessageLog).delete()
                        offer_count = cleanup_db.query(Offer).delete()
                        cancel_count = cleanup_db.query(CancellationEvent).delete()
                        cleanup_db.commit()
                        st.success(f"✅ Deleted {cancel_count} cancellations, {offer_count} offers, {msg_count} messages")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with cleanup_col2:
            st.markdown("**Delete Old Messages**")
            st.write("Remove message logs older than X days")
            days_threshold = st.number_input("Days", min_value=1, max_value=365, value=30)
            if st.button("🗑️ Delete Old Messages"):
                try:
                    with get_session() as cleanup_db:
                        cutoff_date = now_utc() - timedelta(days=days_threshold)
                        result = cleanup_db.query(MessageLog).filter(
                            MessageLog.created_at < cutoff_date
                        ).delete()
                        cleanup_db.commit()
                        st.success(f"✅ Deleted {result} old messages")
                except Exception as e:
                    st.error(f"Error: {e}")


def show_edit_patient_form(entry_id: int):
    """Edit patient details"""
    st.header("✏️ Edit Patient")
    
    try:
        with get_session() as db:
            entry = db.query(WaitlistEntry).filter(WaitlistEntry.id == entry_id).first()
            
            if not entry:
                st.error("Patient not found")
                if st.button("← Back to Admin Tools"):
                    st.session_state.edit_patient_id = None
                    st.rerun()
                return
            
            patient = entry.patient
            
            st.write(f"**Patient:** {patient.display_name or patient.phone_e164}")
            
            with st.form("edit_patient_form"):
                display_name = st.text_input("Display Name", value=patient.display_name or "")
                urgent_flag = st.checkbox("Urgent Flag", value=entry.urgent_flag)
                manual_boost = st.slider("Manual Boost", 0, 40, entry.manual_boost)
                notes = st.text_area("Notes", value=entry.notes or "")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("✅ Save Changes", type="primary")
                with col2:
                    cancel = st.form_submit_button("❌ Cancel")
                
                if submit:
                    try:
                        with get_session() as update_db:
                            update_entry = update_db.query(WaitlistEntry).filter(
                                WaitlistEntry.id == entry_id
                            ).first()
                            update_patient = update_entry.patient
                            
                            update_patient.display_name = display_name
                            update_entry.urgent_flag = urgent_flag
                            update_entry.manual_boost = manual_boost
                            update_entry.notes = notes
                            
                            update_db.commit()
                            st.success("✅ Patient updated successfully")
                            st.session_state.edit_patient_id = None
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error updating patient: {e}")
                
                if cancel:
                    st.session_state.edit_patient_id = None
                    st.rerun()
    
    except Exception as e:
        st.error(f"Error loading patient: {e}")
        if st.button("← Back to Admin Tools"):
            st.session_state.edit_patient_id = None
            st.rerun()


def show_photo_guide():
    """Display photo upload guide with link to presentation"""
    
    st.header("📸 Photo Upload Guide")
    st.markdown("Learn how to add screenshots and images to any slide in the executive presentation.")
    
    # Presentation link
    presentation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'executive_presentation.html'))
    presentation_url = f"file:///{presentation_path.replace(os.sep, '/')}"
    
    st.markdown(f"""
    ### 📋 Dynamic Image Gallery System
    
    The presentation has a **fully dynamic** image loading system. Just drop files into the `docs/images/` folder
    and they automatically appear on the corresponding slide!
    
    #### Naming Convention
    
    ```
    image<NUMBER>-slide-<H>-<V>.<extension>
    ```
    
    Where:
    - `<NUMBER>` = Image number (1, 2, 3, etc.)
    - `<H>` = Horizontal slide number (check top-right of presentation)
    - `<V>` = Vertical slide number
    - `<extension>` = png, jpg, or jpeg
    
    #### Examples
    
    - **Slide 5.3**: `image1-slide-5-3.png`, `image2-slide-5-3.png`
    - **Slide 2.3**: `image1-slide-2-3.png`, `image2-slide-2-3.jpg`
    - **Slide 7.1**: `image1-slide-7-1.png`
    
    #### How to Find Slide Numbers
    
    1. Open the presentation (button below)
    2. Navigate to the slide you want
    3. Look at the **top-right corner** for the slide number (e.g., "5/3")
    4. Use that number in your filename: `5/3` → `image1-slide-5-3.png`
    
    #### Supported Formats
    - PNG (recommended for screenshots)
    - JPG/JPEG (smaller file size)
    
    #### Best Practices
    - Keep file sizes under 2MB
    - Use sequential numbering (1, 2, 3...)
    - PNG gives better quality for text/screenshots
    - Images appear in a responsive grid with lightbox
    
    #### View Full Presentation
    
    Click below to open the presentation:
    """)
    
    # Create a link that opens in browser
    st.markdown(f'<a href="{presentation_url}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">🎯 Open Full Presentation</button></a>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show current images in docs/images folder
    st.subheader("📁 Current Images")
    
    images_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'images')
    
    if os.path.exists(images_path):
        # Get all image files
        all_image_files = [f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg')) and 'slide-' in f.lower()]
        
        if all_image_files:
            # Group by slide
            import re
            slides_dict = {}
            for img_file in all_image_files:
                match = re.search(r'slide-(\d+)-(\d+)', img_file.lower())
                if match:
                    slide_id = f"{match.group(1)}-{match.group(2)}"
                    if slide_id not in slides_dict:
                        slides_dict[slide_id] = []
                    slides_dict[slide_id].append(img_file)
            
            st.write(f"Found {len(all_image_files)} image(s) across {len(slides_dict)} slide(s):")
            
            # Display by slide
            for slide_id in sorted(slides_dict.keys()):
                with st.expander(f"🖼️ Slide {slide_id.replace('-', '.')} ({len(slides_dict[slide_id])} images)", expanded=True):
                    image_files = slides_dict[slide_id]
                    cols_per_row = 3
                    for i in range(0, len(image_files), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, col in enumerate(cols):
                            if i + j < len(image_files):
                                img_file = image_files[i + j]
                                with col:
                                    st.image(os.path.join(images_path, img_file), caption=img_file, use_container_width=True)
        else:
            st.info("📸 No images found yet. Add screenshots to `docs/images/` folder with naming pattern: `image1-slide-X-Y.png`")
    else:
        st.warning(f"Images folder not found: {images_path}")
    
    st.markdown("---")
    st.caption("For more information, see: `docs/images/README.md`")


# Main content area
if view == "Dashboard":
    show_dashboard()
elif view == "Waitlist":
    show_waitlist()
elif view == "Message Log":
    show_message_log()
elif view == "Admin Tools":
    show_admin_tools()
elif view == "Add Cancellation":
    show_add_cancellation()
elif view == "Add Patient":
    show_add_patient()
elif view == "Photo Guide":
    show_photo_guide()


# Footer
st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%b %d, %Y at %I:%M:%S %p')} | Auto-refresh: {'ON' if auto_refresh else 'OFF'}")
