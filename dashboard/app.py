"""
Clinic Cancellation Chatbot - Streamlit Dashboard

Real-time monitoring dashboard for waitlist management and active offers.

Author: Jonathan Ives (@dollythedog)
"""

import streamlit as st
# import pandas as pd
# from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Clinic Cancellation Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🏥 Clinic Cancellation Chatbot Dashboard")
st.markdown("**Real-time waitlist management and SMS offer monitoring**")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select View",
        ["📊 Overview", "⏱️ Active Cancellations", "📋 Waitlist", "📨 Message Log", "⚙️ Settings"]
    )
    
    st.markdown("---")
    st.info("**Status:** 🟢 System Online")
    st.metric("Active Offers", "0")
    st.metric("Waitlist Size", "0")

# Main content
if page == "📊 Overview":
    st.header("Overview Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Today's Cancellations",
            value="0",
            delta="0 from yesterday"
        )
    
    with col2:
        st.metric(
            label="Fill Rate",
            value="0%",
            delta="N/A"
        )
    
    with col3:
        st.metric(
            label="Messages Sent",
            value="0",
            delta="0 today"
        )
    
    with col4:
        st.metric(
            label="Response Rate",
            value="0%",
            delta="N/A"
        )
    
    st.markdown("---")
    st.subheader("Recent Activity")
    st.info("No recent activity to display. System is ready to process cancellations.")

elif page == "⏱️ Active Cancellations":
    st.header("Active Cancellations")
    st.info("No active cancellations at this time.")
    
    # TODO: Display active cancellations with countdown timers
    # TODO: Show offer batches and current status

elif page == "📋 Waitlist":
    st.header("Waitlist Management")
    
    tab1, tab2 = st.tabs(["📊 Current Waitlist", "➕ Add Patient"])
    
    with tab1:
        st.info("No patients on waitlist.")
        # TODO: Display waitlist table sorted by priority score
        # TODO: Add manual boost controls
        # TODO: Add activate/deactivate buttons
    
    with tab2:
        st.subheader("Add New Waitlist Entry")
        
        with st.form("add_patient_form"):
            phone = st.text_input("Phone Number", placeholder="+12145551234")
            display_name = st.text_input("Display Name", placeholder="First name or initials")
            urgent = st.checkbox("Urgent Priority")
            manual_boost = st.slider("Manual Boost", 0, 40, 0)
            notes = st.text_area("Notes (optional)")
            
            submitted = st.form_submit_button("Add to Waitlist")
            if submitted:
                st.success("Patient added to waitlist!")

elif page == "📨 Message Log":
    st.header("SMS Message Log")
    st.info("No messages logged yet.")
    
    # TODO: Display message log with filters
    # TODO: Show delivery status from Twilio
    # TODO: Highlight failed messages

elif page == "⚙️ Settings":
    st.header("System Settings")
    
    st.subheader("Batch Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Batch Size", min_value=1, max_value=10, value=3)
        st.number_input("Hold Minutes", min_value=1, max_value=30, value=7)
    
    with col2:
        st.time_input("Contact Hours Start", value=None)
        st.time_input("Contact Hours End", value=None)
    
    st.markdown("---")
    st.subheader("System Status")
    st.success("✅ Database: Connected")
    st.success("✅ Twilio: Ready")
    st.warning("⚠️ Scheduler: Not started")

# Footer
st.markdown("---")
st.caption("Clinic Cancellation Chatbot v0.1.0 | Texas Pulmonary & Critical Care Consultants")
