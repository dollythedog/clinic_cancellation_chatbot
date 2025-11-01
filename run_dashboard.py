"""
Run script for Streamlit dashboard

Usage:
    python run_dashboard.py

Author: Jonathan Ives (@dollythedog)
"""

import sys
import os

# Ensure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard", "app.py")
    
    sys.argv = [
        "streamlit",
        "run",
        dashboard_path,
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ]
    
    sys.exit(stcli.main())
