"""
Monthly P&L Detail
Detailed month-by-month P&L with charts
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def show():
    """Display monthly P&L detail"""
    
    st.markdown('<div class="main-header">Monthly P&L Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Month-by-month financial performance</div>', unsafe_allow_html=True)
    
    st.info("This page is under construction. Coming soon: Monthly P&L table and time series charts.")
    
    st.markdown("### Planned Features")
    st.markdown("""
    - Monthly P&L data table (2025 Actual & 2026 Forecast)
    - Time series bar chart (Revenue, COGS, OpEx, EBITDA)
    - Toggle between actual and forecast views
    - Export to CSV functionality
    - Variance analysis (Actual vs Forecast)
    """)
