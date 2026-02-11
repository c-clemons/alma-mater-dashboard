"""
Management Dashboard - Client Presentation View
Comprehensive financial overview with actuals and projections
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np


def apply_dtc_adjustments(revenue, year):
    """Apply discounts and returns to DTC revenue"""
    # Discounts: 10% off revenue
    after_discount = revenue * 0.90
    
    # Returns: 20% for 2027+, 0% for 2026 (Matt factored it in)
    if year >= 2027:
        after_returns = after_discount * 0.80
    else:
        after_returns = after_discount
    
    return after_returns


def load_actuals():
    """Load 2025 actuals"""
    # 2025 Actuals from QBO
    actuals_2025 = {
        'Month': ['Jan 25', 'Feb 25', 'Mar 25', 'Apr 25', 'May 25', 'Jun 25', 
                  'Jul 25', 'Aug 25', 'Sep 25', 'Oct 25', 'Nov 25', 'Dec 25'],
        'DTC_Revenue': [4269.90, 2997.05, 1406.00, 4908.21, 4348.01, 5232.04, 
                        8912.02, 5228.85, 5504.82, 6270.06, 6044.05, 19407.51],
        'Wholesale_Revenue': [2433.00, 0, 0, 0, 1612.86, 0, 0, 0, 14688.31, 0, 6285.12, 1292.00],
        'COGS': [1494.65, 18212.83, 5012.17, 9558.23, 1582.81, 3235.61, 
                 5828.99, 3905.49, 979.12, 1383.98, 21838.11, 21752.95],
        'Sales_Marketing': [1200.00, 1200.00, 11319.01, 27200.00, 8741.00, 1200.00, 
                            7077.13, 7544.26, 15700.00, 15900.00, 8396.80, 27717.73],
        'Payroll': [0, 1483.75, 4473.02, 2000.00, 2411.90, 1552.50, 
                    1911.01, 2960.00, 4641.50, 2694.75, 2736.10, 2602.05],
        'Other_Expenses': [701.07, 2146.80, 672.47, 2108.27, 1754.80, 7947.23, 
                           180.23, 9592.98, 13735.48, 9714.85, 9727.07, 7357.56],
    }
    
    df = pd.DataFrame(actuals_2025)
    df['Total_Revenue'] = df['DTC_Revenue'] + df['Wholesale_Revenue']
    df['Gross_Profit'] = df['Total_Revenue'] - df['COGS']
    df['Total_OpEx'] = df['Sales_Marketing'] + df['Payroll'] + df['Other_Expenses']
    df['EBITDA'] = df['Gross_Profit'] - df['Total_OpEx']
    df['Period'] = 'Actual'
    
    return df


def load_projections():
    """Load 2026 projections from Matt's roadmap"""
    
    # Beta revenue
    beta_units = [10, 20, 30, 50, 100, 150, 200, 200, 200, 200, 200, 200]
    beta_aov = 250
    beta_revenue = [u * beta_aov for u in beta_units]
    
    # Alpha revenue (starts in Aug)
    alpha_units = [0, 0, 0, 0, 0, 0, 0, 0, 50, 100, 200, 300]
    alpha_aov = 450
    alpha_revenue = [u * alpha_aov for u in alpha_units]
    
    # Total DTC revenue
    dtc_revenue = [b + a for b, a in zip(beta_revenue, alpha_revenue)]
    
    # COGS (40% of revenue)
    cogs = [r * 0.40 for r in dtc_revenue]
    
    # Operating expenses from Matt's roadmap
    opex_monthly = [5900, 44300, 37300, 19340, 19340, 19340, 19340, 26340, 19340, 29340, 19340, 19340]
    
    # Performance marketing spend
    perf_marketing = [0, 0, 0, 15000, 15000, 15000, 15000, 15000, 25000, 25000, 25000, 30000]
    
    projections_2026 = {
        'Month': ['Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26',
                  'Jul 26', 'Aug 26', 'Sep 26', 'Oct 26', 'Nov 26', 'Dec 26'],
        'DTC_Revenue': dtc_revenue,
        'Wholesale_Revenue': [0] * 12,  # To be added via wholesale tracker
        'COGS': cogs,
        'Total_OpEx': opex_monthly,
        'Perf_Marketing': perf_marketing,
    }
    
    df = pd.DataFrame(projections_2026)
    df['Total_Revenue'] = df['DTC_Revenue'] + df['Wholesale_Revenue']
    df['Gross_Profit'] = df['Total_Revenue'] - df['COGS']
    df['EBITDA'] = df['Gross_Profit'] - df['Total_OpEx']
    df['Period'] = 'Forecast'
    
    return df


def show():
    """Display management dashboard"""
    
    st.markdown('<div class="main-header">📊 Management Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Financial Performance & Projections</div>', unsafe_allow_html=True)
    
    # Load data
    actuals = load_actuals()
    projections = load_projections()
    
    # Combine for charts
    combined = pd.concat([actuals, projections], ignore_index=True)
    
    # --- EXECUTIVE SUMMARY ---
    st.markdown("### 📈 Executive Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 2025 Actual Results")
        st.metric("Total Revenue", f"${actuals['Total_Revenue'].sum():,.0f}")
        st.metric("Gross Profit", f"${actuals['Gross_Profit'].sum():,.0f}")
        st.metric("EBITDA", f"${actuals['EBITDA'].sum():,.0f}")
        st.metric("Ending Cash", "$93,412", help="As of 12/31/2025")
    
    with col2:
        st.markdown("#### 2026 Projected")
        st.metric("Total Revenue", f"${projections['Total_Revenue'].sum():,.0f}")
        st.metric("Gross Profit", f"${projections['Gross_Profit'].sum():,.0f}")
        st.metric("EBITDA", f"${projections['EBITDA'].sum():,.0f}")
        st.metric("Year-End Cash", "TBD", help="Depends on funding")
    
    with col3:
        st.markdown("#### Growth Metrics")
        rev_growth = ((projections['Total_Revenue'].sum() - actuals['Total_Revenue'].sum()) / 
                     actuals['Total_Revenue'].sum() * 100)
        st.metric("Revenue Growth", f"{rev_growth:.0f}%", delta=f"{rev_growth:.0f}% YoY")
        
        gm_2025 = actuals['Gross_Profit'].sum() / actuals['Total_Revenue'].sum() * 100
        gm_2026 = projections['Gross_Profit'].sum() / projections['Total_Revenue'].sum() * 100
        st.metric("2026 Gross Margin", f"{gm_2026:.1f}%", delta=f"{gm_2026-gm_2025:.1f}pp")
        
        st.metric("Cash Needed", "$100-150K", delta="Q1 2026", delta_color="inverse")
    
    st.divider()
    
    # --- REVENUE TRENDS ---
    st.markdown("### 💰 Revenue Performance")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Revenue trend chart
        fig_revenue = go.Figure()
        
        # Actuals
        fig_revenue.add_trace(go.Bar(
            x=actuals['Month'],
            y=actuals['Total_Revenue'],
            name='2025 Actual',
            marker_color='#2E86AB',
            text=actuals['Total_Revenue'].apply(lambda x: f'${x/1000:.0f}K'),
            textposition='outside'
        ))
        
        # Forecast
        fig_revenue.add_trace(go.Bar(
            x=projections['Month'],
            y=projections['Total_Revenue'],
            name='2026 Forecast',
            marker_color='#A23B72',
            text=projections['Total_Revenue'].apply(lambda x: f'${x/1000:.0f}K'),
            textposition='outside'
        ))
        
        fig_revenue.update_layout(
            title="Monthly Revenue: Actual vs Forecast",
            xaxis_title="Month",
            yaxis_title="Revenue ($)",
            height=400,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Revenue split pie chart for 2026
        st.markdown("#### 2026 Revenue Mix")
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Beta Product', 'Alpha Product', 'Wholesale'],
            values=[
                sum([10, 20, 30, 50, 100, 150, 200, 200, 200, 200, 200, 200]) * 250,
                sum([50, 100, 200, 300]) * 450,
                0
            ],
            hole=0.4,
            marker=dict(colors=['#2E86AB', '#A23B72', '#F18F01'])
        )])
        
        fig_pie.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # --- P&L TABLE ---
    st.markdown("### 📋 Profit & Loss Summary")
    
    # Create summary table
    pl_data = []
    
    for period, df in [('2025 Actual', actuals), ('2026 Forecast', projections)]:
        pl_data.append({
            'Period': period,
            'Revenue': df['Total_Revenue'].sum(),
            'COGS': df['COGS'].sum(),
            'Gross Profit': df['Gross_Profit'].sum(),
            'Gross Margin %': (df['Gross_Profit'].sum() / df['Total_Revenue'].sum() * 100) if df['Total_Revenue'].sum() > 0 else 0,
            'Operating Expenses': df['Total_OpEx'].sum(),
            'EBITDA': df['EBITDA'].sum(),
            'EBITDA Margin %': (df['EBITDA'].sum() / df['Total_Revenue'].sum() * 100) if df['Total_Revenue'].sum() > 0 else 0,
        })
    
    pl_df = pd.DataFrame(pl_data)
    
    # Format for display
    display_df = pl_df.copy()
    currency_cols = ['Revenue', 'COGS', 'Gross Profit', 'Operating Expenses', 'EBITDA']
    for col in currency_cols:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
    
    pct_cols = ['Gross Margin %', 'EBITDA Margin %']
    for col in pct_cols:
        display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # --- CASH FLOW ---
    st.markdown("### 💵 Cash Flow & Runway")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calculate cash flow
        starting_cash = 93412
        monthly_cf = projections['EBITDA'].values
        cumulative_cf = np.cumsum(monthly_cf)
        cash_balance = starting_cash + cumulative_cf
        
        fig_cash = go.Figure()
        
        fig_cash.add_trace(go.Scatter(
            x=projections['Month'],
            y=cash_balance,
            mode='lines+markers',
            name='Cash Balance',
            line=dict(color='#2E86AB', width=3),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 171, 0.2)'
        ))
        
        # Add zero line
        fig_cash.add_hline(y=0, line_dash="dash", line_color="red", 
                          annotation_text="Cash Zero")
        
        # Mark negative territory
        if (cash_balance < 0).any():
            fig_cash.add_hrect(
                y0=cash_balance.min(), y1=0,
                fillcolor="red", opacity=0.1,
                line_width=0
            )
        
        fig_cash.update_layout(
            title="2026 Cash Balance Projection",
            xaxis_title="Month",
            yaxis_title="Cash Balance ($)",
            height=400
        )
        
        st.plotly_chart(fig_cash, use_container_width=True)
    
    with col2:
        st.markdown("#### Cash Requirements")
        
        min_cash = cash_balance.min()
        months_negative = sum(1 for c in cash_balance if c < 0)
        
        if min_cash < 0:
            capital_needed = abs(min_cash) + 50000  # Add buffer
            st.error(f"⚠️ **Cash goes negative by ${abs(min_cash):,.0f}**")
            st.metric("Capital Required", f"${capital_needed:,.0f}", help="Includes $50K buffer")
            st.metric("Months Negative", f"{months_negative}")
            
            # Find when cash goes negative
            first_negative = next((i for i, c in enumerate(cash_balance) if c < 0), None)
            if first_negative:
                st.warning(f"💡 **Need funding by {projections['Month'].iloc[first_negative]}**")
        else:
            st.success("✅ Cash remains positive through 2026")
            st.metric("Ending Cash", f"${cash_balance[-1]:,.0f}")
        
        st.markdown("#### Recommended Action")
        st.info("🎯 **Raise $100-150K in Q1 2026**\n\n"
                "This provides:\n"
                "- 6+ months runway\n"
                "- Marketing scale-up capital\n"
                "- Product development buffer")
    
    st.divider()
    
    # --- EXPENSE BREAKDOWN ---
    st.markdown("### 💼 Operating Expense Breakdown")
    
    # Expense categories from Matt's roadmap
    expense_categories = {
        'Ops & Strategic': 82900,
        'Marketing Management': 103400,
        'Creative': 75000,
        'Channel/Ecommerce': 36600,
        'Systems': 34200,
        'Performance Marketing': 160000,
        'Affiliate': 50000,
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Expense breakdown pie
        fig_exp = go.Figure(data=[go.Pie(
            labels=list(expense_categories.keys()),
            values=list(expense_categories.values()),
            hole=0.4
        )])
        
        fig_exp.update_layout(
            title="2026 OpEx by Category",
            height=400
        )
        
        st.plotly_chart(fig_exp, use_container_width=True)
    
    with col2:
        # Top expense categories table
        exp_df = pd.DataFrame([
            {'Category': k, 'Annual Budget': v, '% of Total': v/sum(expense_categories.values())*100}
            for k, v in expense_categories.items()
        ])
        exp_df = exp_df.sort_values('Annual Budget', ascending=False)
        
        display_exp = exp_df.copy()
        display_exp['Annual Budget'] = display_exp['Annual Budget'].apply(lambda x: f"${x:,.0f}")
        display_exp['% of Total'] = display_exp['% of Total'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(display_exp, use_container_width=True, hide_index=True, height=400)
    
    st.divider()
    
    # --- KEY INSIGHTS ---
    st.markdown("### 💡 Key Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Revenue")
        st.write("**2026 Target:** $867K (+760% YoY)")
        st.write("**Q1 Critical:** Beta launch & validation")
        st.write("**Q3 Milestone:** Alpha product launch")
        st.write("**Unit Economics:** $250 Beta, $450 Alpha")
    
    with col2:
        st.markdown("#### 💰 Profitability")
        st.write("**Gross Margin:** 60% target (vs 6% in 2025)")
        st.write("**EBITDA:** Path to breakeven by Q4 2026")
        st.write("**Burn Rate:** $30-40K/month average")
        st.write("**Break-even:** ~$50K monthly revenue")
    
    with col3:
        st.markdown("#### 🚀 Action Items")
        st.write("**Immediate:** Raise $100-150K Q1 2026")
        st.write("**Q1:** Launch Beta, validate pricing")
        st.write("**Q2:** Scale marketing to $15K/month")
        st.write("**Q3:** Alpha launch, expand wholesale")
