"""
Cash Flow & Runway Calculator
Track current cash position, burn rate, and runway projections
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
from typing import Dict
from dateutil.relativedelta import relativedelta
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from financial_calcs import generate_monthly_pl


def get_monthly_funding(fundraising_rounds: list, year: int = 2026) -> Dict[int, float]:
    """Calculate monthly funding inflows from fundraising rounds for a given year."""
    monthly = {m: 0.0 for m in range(1, 13)}
    for rnd in (fundraising_rounds or []):
        rnd_year = rnd.get('year', 0)
        rnd_month = rnd.get('month', 0)
        amount = rnd.get('amount', 0)
        if rnd_year == year and 1 <= rnd_month <= 12 and amount > 0:
            monthly[rnd_month] += amount
    return monthly


def calculate_cash_runway(
    starting_cash: float,
    current_ap: float,
    current_ar: float,
    monthly_pl_df: pd.DataFrame,
    fundraising_rounds: list = None,
    year: int = 2026
) -> pd.DataFrame:
    """
    Calculate month-by-month cash runway

    Returns DataFrame with columns: Month, Revenue, OpEx, Net Cash Flow, Ending Cash, Days of Cash
    """
    # Starting position
    current_cash_assets = starting_cash + current_ar
    current_liabilities = current_ap
    net_cash = current_cash_assets - current_liabilities

    # Get monthly funding
    monthly_funding = get_monthly_funding(fundraising_rounds, year)

    runway_data = []
    cumulative_cash = net_cash
    cumulative_cash_no_fund = net_cash

    for idx, row in monthly_pl_df.iterrows():
        month_num = idx + 1
        month_name = row['Month']
        revenue = row['Total Revenue']
        cogs = row['Total COGS']
        opex = row['Total OpEx']
        funding = monthly_funding.get(month_num, 0)

        # Cash inflow (revenue + funding)
        cash_in = revenue + funding

        # Cash outflow (COGS + OpEx)
        cash_out = cogs + opex

        # Net cash flow
        net_flow = cash_in - cash_out
        net_flow_no_fund = (revenue - cash_out)

        # Update cumulative cash
        cumulative_cash += net_flow
        cumulative_cash_no_fund += net_flow_no_fund

        # Calculate monthly burn rate (negative net flow, excluding funding)
        burn_rate = -net_flow_no_fund if net_flow_no_fund < 0 else 0

        # Days of cash (if burning)
        if burn_rate > 0:
            daily_burn = burn_rate / 30
            days_of_cash = cumulative_cash / daily_burn if daily_burn > 0 else 999
        else:
            days_of_cash = 999  # Not burning

        runway_data.append({
            'Month': month_name,
            'Cash Inflow': cash_in,
            'Funding': funding,
            'Cash Outflow': cash_out,
            'Net Cash Flow': net_flow,
            'Ending Cash': cumulative_cash,
            'Ending Cash (No Funding)': cumulative_cash_no_fund,
            'Monthly Burn Rate': burn_rate,
            'Days of Cash': min(days_of_cash, 999)
        })

    return pd.DataFrame(runway_data)


def show():
    """Display cash flow and runway calculator"""
    
    st.markdown('<div class="main-header">Cash Flow & Runway Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Track cash position, burn rate, and runway projections</div>', unsafe_allow_html=True)
    
    st.info("💰 **Purpose:** Monitor your cash runway to ensure you have enough cash to reach profitability or your next funding milestone.")
    
    # Load data first
    team_members = st.session_state.get('team_members', [])
    opex_expenses = st.session_state.get('opex_expenses', [])
    wholesale_deals = st.session_state.get('wholesale_deals', [])
    
    # --- INPUT SECTION ---
    st.markdown("## Current Cash Position")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Use QBO cash balance if available
        qbo = st.session_state.get('qbo_actuals')
        default_cash = qbo.get('latest_cash', 41422.0) if qbo else 41422.0
        starting_cash = st.number_input(
            "Current Cash Balance ($)",
            min_value=0.0,
            value=default_cash,
            step=1000.0,
            help="Your current bank account balance (auto-populated from QBO if imported)"
        )
    
    with col2:
        current_ar = st.number_input(
            "Open Accounts Receivable ($)",
            min_value=0.0,
            value=0.0,  # From client screenshot
            step=100.0,
            help="Money owed to you by customers"
        )
    
    with col3:
        # Use QBO AP if available
        default_ap = qbo.get('latest_ap', 8414.0) if qbo else 8414.0
        current_ap = st.number_input(
            "Open Accounts Payable ($)",
            min_value=0.0,
            value=default_ap,
            step=100.0,
            help="Money you owe to vendors/employees (auto-populated from QBO if imported)"
        )
    
    # Calculate net cash position
    current_cash_assets = starting_cash + current_ar
    current_liabilities = current_ap
    net_cash = current_cash_assets - current_liabilities
    
    st.divider()
    
    # Display net position
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Cash Assets", f"${current_cash_assets:,.0f}")
    
    with col2:
        st.metric("Current Liabilities", f"${current_liabilities:,.0f}")
    
    with col3:
        st.metric(
            "Net Cash Position",
            f"${net_cash:,.0f}",
            delta="Available for operations"
        )
    
    with col4:
        # Calculate proper monthly burn from projections
        monthly_df = generate_monthly_pl(
            year=2026,
            team_members=team_members,
            opex_expenses=opex_expenses,
            wholesale_deals=wholesale_deals,
            dtc_discount_rate=0.0,
            dtc_return_rate=0.0
        )
        
        # Calculate ACTUAL burn rate from first 3 months (before wholesale kick in)
        first_three_months = monthly_df.head(3)
        avg_monthly_revenue = first_three_months['Total Revenue'].mean()
        avg_monthly_cogs = first_three_months['Total COGS'].mean()
        avg_monthly_opex = first_three_months['Total OpEx'].mean()
        
        # Net monthly burn = (COGS + OpEx) - Revenue
        monthly_cash_out = avg_monthly_cogs + avg_monthly_opex
        monthly_cash_in = avg_monthly_revenue
        net_monthly_burn = monthly_cash_out - monthly_cash_in
        
        if net_monthly_burn > 0:
            daily_burn = net_monthly_burn / 30
            days_of_cash = net_cash / daily_burn if daily_burn > 0 else 999
            st.metric(
                "Days of Cash",
                f"{days_of_cash:.0f} days",
                delta=f"{days_of_cash/30:.1f} months",
                delta_color="normal" if days_of_cash > 90 else "inverse"
            )
        else:
            st.metric("Days of Cash", "Cash Positive ✅")
    
    st.divider()
    
    # --- RUNWAY PROJECTION ---
    st.markdown("## 2026 Cash Runway Projection")
    
    # Get fundraising rounds
    fundraising_rounds = st.session_state.get('fundraising_rounds', [])

    # Calculate runway
    runway_df = calculate_cash_runway(
        starting_cash=starting_cash,
        current_ap=current_ap,
        current_ar=current_ar,
        monthly_pl_df=monthly_df,
        fundraising_rounds=fundraising_rounds,
        year=2026
    )
    
    # --- BURN BREAKDOWN ---
    st.markdown("### Monthly Burn Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average monthly breakdown for first half of year
        first_half = runway_df.head(6)
        
        avg_cash_in = first_half['Cash Inflow'].mean()
        avg_cash_out = first_half['Cash Outflow'].mean()
        avg_net_burn = first_half['Monthly Burn Rate'].mean()
        
        st.markdown("#### Average Monthly (First 6 Months)")
        st.metric("💰 Cash In (Revenue)", f"${avg_cash_in:,.0f}")
        st.metric("💸 Cash Out (COGS + OpEx)", f"${avg_cash_out:,.0f}")
        st.metric("🔥 Net Burn", f"${avg_net_burn:,.0f}", 
                 delta="Burning cash" if avg_net_burn > 0 else "Cash positive", 
                 delta_color="inverse" if avg_net_burn > 0 else "normal")
        
        # Calculate revenue offset percentage
        if avg_cash_out > 0:
            revenue_offset_pct = (avg_cash_in / avg_cash_out) * 100
            st.metric("📊 Revenue Covers", f"{revenue_offset_pct:.1f}%",
                     help="Percentage of expenses covered by revenue")
    
    with col2:
        # Burn composition breakdown using first month detail
        sample_pl = monthly_df.iloc[0]
        
        fig_burn = go.Figure(data=[
            go.Bar(
                x=['Team Costs', 'Other OpEx', 'COGS', 'Revenue'],
                y=[
                    sample_pl['Team Costs'],
                    sample_pl['Other OpEx'],
                    sample_pl['Total COGS'],
                    -sample_pl['Total Revenue']  # Negative to show offset
                ],
                marker_color=['#E63946', '#F4A261', '#E9C46A', '#00BA38']
            )
        ])
        
        fig_burn.update_layout(
            title=f'Cash Flow Components - {sample_pl["Month"]} (Example)',
            height=350,
            showlegend=False,
            yaxis_title="Amount ($)"
        )
        
        st.plotly_chart(fig_burn, use_container_width=True)
    
    st.divider()
    
    # --- CHARTS ---
    
    # Cash waterfall chart
    fig_waterfall = go.Figure(data=[
        go.Waterfall(
            name="Cash Flow",
            orientation="v",
            x=runway_df['Month'],
            textposition="outside",
            y=runway_df['Net Cash Flow'],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        )
    ])
    
    fig_waterfall.update_layout(
        title="Monthly Cash Flow Waterfall",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Ending cash balance projection
    fig_cash = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Projected Cash Balance', 'Monthly Burn Rate'),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # Cash balance line (with funding)
    colors_cash = ['#00BA38' if x >= 0 else '#F8766D' for x in runway_df['Ending Cash']]
    fig_cash.add_trace(
        go.Scatter(
            name='With Funding',
            x=runway_df['Month'],
            y=runway_df['Ending Cash'],
            mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=10, color=colors_cash),
            fill='tozeroy'
        ),
        row=1, col=1
    )

    # Cash balance line (without funding) - dashed
    if runway_df['Funding'].sum() > 0:
        fig_cash.add_trace(
            go.Scatter(
                name='Without Funding',
                x=runway_df['Month'],
                y=runway_df['Ending Cash (No Funding)'],
                mode='lines+markers',
                line=dict(color='#E63946', width=2, dash='dash'),
                marker=dict(size=6),
            ),
            row=1, col=1
        )
    
    # Zero line
    fig_cash.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
    
    # Burn rate
    fig_cash.add_trace(
        go.Bar(
            name='Monthly Burn',
            x=runway_df['Month'],
            y=runway_df['Monthly Burn Rate'],
            marker_color='#F8766D'
        ),
        row=2, col=1
    )
    
    fig_cash.update_layout(height=700, showlegend=True)
    fig_cash.update_yaxes(title_text="Cash Balance ($)", row=1, col=1)
    fig_cash.update_yaxes(title_text="Burn Rate ($)", row=2, col=1)
    
    st.plotly_chart(fig_cash, use_container_width=True)
    
    st.divider()
    
    # --- DATA TABLE ---
    st.markdown("### Monthly Cash Flow Detail")
    
    # Format for display
    display_df = runway_df.copy()
    for col in ['Cash Inflow', 'Funding', 'Cash Outflow', 'Net Cash Flow', 'Ending Cash', 'Ending Cash (No Funding)', 'Monthly Burn Rate']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    display_df['Days of Cash'] = display_df['Days of Cash'].apply(lambda x: f"{x:.0f}" if x < 999 else "∞")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Export
    csv = runway_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Cash Flow Data (CSV)",
        data=csv,
        file_name=f"alma_mater_cash_flow_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    st.divider()
    
    # --- KEY INSIGHTS ---
    st.markdown("### Key Insights")
    
    # Find cash-out month
    cash_out_month = None
    for idx, row in runway_df.iterrows():
        if row['Ending Cash'] < 0:
            cash_out_month = row['Month']
            break
    
    col1, col2 = st.columns(2)
    
    with col1:
        if cash_out_month:
            st.error(f"⚠️ **Cash Depletion Alert:** Projected to run out of cash in **{cash_out_month} 2026** without additional funding.")
        else:
            st.success("✅ **Cash Positive:** Projected to maintain positive cash through 2026!")
        
        # Calculate total funding need
        min_cash = runway_df['Ending Cash'].min()
        if min_cash < 0:
            funding_need = abs(min_cash)
            st.warning(f"💰 **Funding Recommendation:** Raise at least **${funding_need:,.0f}** to cover 2026 operations.")
    
    with col2:
        # Breakeven analysis
        breakeven_month = None
        for idx, row in runway_df.iterrows():
            if row['Net Cash Flow'] >= 0:
                breakeven_month = row['Month']
                break
        
        if breakeven_month:
            st.info(f"📈 **Cash Flow Positive:** First positive month projected in **{breakeven_month} 2026**")
        else:
            st.warning("📉 **Not Cash Positive:** No positive cash flow months projected in 2026")
    
    st.divider()

    # --- AP INFO ---
    st.markdown("### Accounts Payable")
    if qbo and qbo.get('latest_ap'):
        from qbo_parser import MONTHS as QBO_MONTHS
        lm = qbo.get('last_month', 0)
        ly = qbo.get('last_year', 0)
        st.metric("AP from QBO", f"${qbo['latest_ap']:,.2f}",
                  delta=f"As of {QBO_MONTHS[lm-1]} {ly}")
        st.caption("AP is auto-populated from your latest QBO import. You can override the value in the input above.")
    else:
        st.info("Upload a QBO file with a Balance Sheet tab to auto-populate AP.")
