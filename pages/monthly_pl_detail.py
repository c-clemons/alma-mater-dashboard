"""
Monthly P&L Detail
Detailed month-by-month P&L with charts and data tables
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def load_monthly_actuals_2025():
    """Load 2025 monthly actuals"""
    # Data from QBO P&L
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # DTC Revenue by month
    dtc_revenue = [1406, 1819, 2075, 1739, 3319, 6158, 6367, 5841, 5937, 6788, 13671, 19408]
    
    # Wholesale Revenue by month (sporadic)
    wholesale_revenue = [2433, 0, 0, 0, 0, 1613, 0, 0, 14688, 0, 6285, 1292]
    
    # Total Revenue
    total_revenue = [d + w for d, w in zip(dtc_revenue, wholesale_revenue)]
    
    # COGS (94% of revenue - prototype phase)
    cogs = [r * 0.94 for r in total_revenue]
    
    # Gross Profit
    gross_profit = [r - c for r, c in zip(total_revenue, cogs)]
    
    # Operating Expenses (from QBO categories)
    # Sales & Marketing: $133,196 / 12 months (not evenly distributed)
    # Payroll: $29,358 / 12 months
    # Other: $65,747 / 12 months
    total_opex_annual = 133196 + 29358 + 65747
    opex_monthly = [total_opex_annual / 12] * 12  # Simplified - evenly distributed
    
    # EBITDA
    ebitda = [gp - opex for gp, opex in zip(gross_profit, opex_monthly)]
    
    return pd.DataFrame({
        'Month': months,
        'DTC Revenue': dtc_revenue,
        'Wholesale Revenue': wholesale_revenue,
        'Total Revenue': total_revenue,
        'COGS': cogs,
        'Gross Profit': gross_profit,
        'Gross Margin %': [(gp/r*100) if r > 0 else 0 for gp, r in zip(gross_profit, total_revenue)],
        'Operating Expenses': opex_monthly,
        'EBITDA': ebitda
    })


def load_monthly_forecast_2026():
    """Load 2026 monthly forecast"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Beta product (launch Q1): Ramp from 50 to 200 units/month
    # Alpha product (launch Q3): Ramp from 50 to 150 units/month
    beta_units = [50, 75, 100, 120, 140, 160, 170, 180, 190, 195, 200, 200]
    alpha_units = [0, 0, 0, 0, 0, 0, 50, 75, 100, 125, 150, 150]
    
    # AOV
    beta_aov = 250
    alpha_aov = 450
    
    # DTC Revenue
    dtc_revenue = [(b * beta_aov + a * alpha_aov) for b, a in zip(beta_units, alpha_units)]
    
    # Wholesale (assumed quarterly deals)
    wholesale_revenue = [0, 0, 15000, 0, 0, 20000, 0, 0, 25000, 0, 0, 30000]
    
    # Total Revenue
    total_revenue = [d + w for d, w in zip(dtc_revenue, wholesale_revenue)]
    
    # COGS (40% in production)
    cogs = [r * 0.40 for r in total_revenue]
    
    # Gross Profit
    gross_profit = [r - c for r, c in zip(total_revenue, cogs)]
    
    # Operating Expenses (from Matt's roadmap - $542K annually)
    opex_monthly = [542000 / 12] * 12  # ~$45K/month
    
    # EBITDA
    ebitda = [gp - opex for gp, opex in zip(gross_profit, opex_monthly)]
    
    return pd.DataFrame({
        'Month': months,
        'DTC Revenue': dtc_revenue,
        'Wholesale Revenue': wholesale_revenue,
        'Total Revenue': total_revenue,
        'COGS': cogs,
        'Gross Profit': gross_profit,
        'Gross Margin %': [(gp/r*100) if r > 0 else 0 for gp, r in zip(gross_profit, total_revenue)],
        'Operating Expenses': opex_monthly,
        'EBITDA': ebitda
    })


def show():
    """Display monthly P&L detail"""
    
    st.markdown('<div class="main-header">Monthly P&L Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Month-by-month financial performance with variance analysis</div>', unsafe_allow_html=True)
    
    # Load data
    df_2025 = load_monthly_actuals_2025()
    df_2026 = load_monthly_forecast_2026()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["2025 Actuals", "2026 Forecast", "Year Comparison", "Variance Analysis"])
    
    # --- 2025 ACTUALS ---
    with tab1:
        st.markdown("### 2025 Monthly Actuals")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", f"${df_2025['Total Revenue'].sum():,.0f}")
        
        with col2:
            st.metric("Avg Monthly Revenue", f"${df_2025['Total Revenue'].mean():,.0f}")
        
        with col3:
            st.metric("Avg Gross Margin", f"{df_2025['Gross Margin %'].mean():.1f}%")
        
        with col4:
            st.metric("Total EBITDA", f"${df_2025['EBITDA'].sum():,.0f}")
        
        st.divider()
        
        # Chart
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Revenue & COGS', 'EBITDA'),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4]
        )
        
        # Revenue and COGS
        fig.add_trace(
            go.Bar(name='DTC Revenue', x=df_2025['Month'], y=df_2025['DTC Revenue'],
                   marker_color='#2E86AB'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='Wholesale Revenue', x=df_2025['Month'], y=df_2025['Wholesale Revenue'],
                   marker_color='#A23B72'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(name='COGS', x=df_2025['Month'], y=df_2025['COGS'],
                      mode='lines+markers', line=dict(color='#F18F01', width=2)),
            row=1, col=1
        )
        
        # EBITDA
        colors = ['#00BA38' if x >= 0 else '#F8766D' for x in df_2025['EBITDA']]
        fig.add_trace(
            go.Bar(name='EBITDA', x=df_2025['Month'], y=df_2025['EBITDA'],
                   marker_color=colors, showlegend=False),
            row=2, col=1
        )
        
        fig.update_layout(height=700, showlegend=True, barmode='stack')
        fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
        fig.update_yaxes(title_text="EBITDA ($)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Data table
        st.markdown("### Monthly Data Table")
        
        # Format for display
        display_df = df_2025.copy()
        for col in ['DTC Revenue', 'Wholesale Revenue', 'Total Revenue', 'COGS', 'Gross Profit', 'Operating Expenses', 'EBITDA']:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
        display_df['Gross Margin %'] = display_df['Gross Margin %'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Export
        csv = df_2025.to_csv(index=False)
        st.download_button(
            label="Download 2025 Data (CSV)",
            data=csv,
            file_name="alma_mater_2025_monthly_pl.csv",
            mime="text/csv"
        )
    
    # --- 2026 FORECAST ---
    with tab2:
        st.markdown("### 2026 Monthly Forecast")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", f"${df_2026['Total Revenue'].sum():,.0f}")
        
        with col2:
            st.metric("Avg Monthly Revenue", f"${df_2026['Total Revenue'].mean():,.0f}")
        
        with col3:
            st.metric("Avg Gross Margin", f"{df_2026['Gross Margin %'].mean():.1f}%")
        
        with col4:
            st.metric("Total EBITDA", f"${df_2026['EBITDA'].sum():,.0f}")
        
        st.divider()
        
        # Chart
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Revenue & COGS', 'EBITDA'),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4]
        )
        
        # Revenue and COGS
        fig.add_trace(
            go.Bar(name='DTC Revenue', x=df_2026['Month'], y=df_2026['DTC Revenue'],
                   marker_color='#2E86AB'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(name='Wholesale Revenue', x=df_2026['Month'], y=df_2026['Wholesale Revenue'],
                   marker_color='#A23B72'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(name='COGS', x=df_2026['Month'], y=df_2026['COGS'],
                      mode='lines+markers', line=dict(color='#F18F01', width=2)),
            row=1, col=1
        )
        
        # EBITDA
        colors = ['#00BA38' if x >= 0 else '#F8766D' for x in df_2026['EBITDA']]
        fig.add_trace(
            go.Bar(name='EBITDA', x=df_2026['Month'], y=df_2026['EBITDA'],
                   marker_color=colors, showlegend=False),
            row=2, col=1
        )
        
        fig.update_layout(height=700, showlegend=True, barmode='stack')
        fig.update_yaxes(title_text="Amount ($)", row=1, col=1)
        fig.update_yaxes(title_text="EBITDA ($)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Data table
        st.markdown("### Monthly Data Table")
        
        # Format for display
        display_df = df_2026.copy()
        for col in ['DTC Revenue', 'Wholesale Revenue', 'Total Revenue', 'COGS', 'Gross Profit', 'Operating Expenses', 'EBITDA']:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
        display_df['Gross Margin %'] = display_df['Gross Margin %'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Export
        csv = df_2026.to_csv(index=False)
        st.download_button(
            label="Download 2026 Forecast (CSV)",
            data=csv,
            file_name="alma_mater_2026_forecast_monthly_pl.csv",
            mime="text/csv"
        )
    
    # --- YEAR COMPARISON ---
    with tab3:
        st.markdown("### Year-over-Year Comparison")
        
        # Side-by-side comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 2025 Actuals")
            st.metric("Total Revenue", f"${df_2025['Total Revenue'].sum():,.0f}")
            st.metric("Gross Margin", f"{df_2025['Gross Margin %'].mean():.1f}%")
            st.metric("EBITDA", f"${df_2025['EBITDA'].sum():,.0f}")
        
        with col2:
            st.markdown("#### 2026 Forecast")
            revenue_growth = (df_2026['Total Revenue'].sum() / df_2025['Total Revenue'].sum() - 1) * 100
            st.metric("Total Revenue", f"${df_2026['Total Revenue'].sum():,.0f}", delta=f"{revenue_growth:.0f}% YoY")
            margin_change = df_2026['Gross Margin %'].mean() - df_2025['Gross Margin %'].mean()
            st.metric("Gross Margin", f"{df_2026['Gross Margin %'].mean():.1f}%", delta=f"{margin_change:+.1f}pp")
            ebitda_change = df_2026['EBITDA'].sum() - df_2025['EBITDA'].sum()
            st.metric("EBITDA", f"${df_2026['EBITDA'].sum():,.0f}", delta=f"${ebitda_change:+,.0f}")
        
        st.divider()
        
        # Comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='2025 Actuals',
            x=df_2025['Month'],
            y=df_2025['Total Revenue'],
            marker_color='#619CFF'
        ))
        
        fig.add_trace(go.Bar(
            name='2026 Forecast',
            x=df_2026['Month'],
            y=df_2026['Total Revenue'],
            marker_color='#F8766D'
        ))
        
        fig.update_layout(
            title='Monthly Revenue: 2025 vs 2026',
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # --- VARIANCE ANALYSIS ---
    with tab4:
        st.markdown("### Variance Analysis")
        st.info("This feature will show Budget vs. Actual comparisons once you set budget targets. Coming soon!")
        
        # Placeholder for future variance tracking
        st.markdown("""
        **Planned features:**
        - Set monthly budget targets
        - Track actual vs. budget variance
        - Identify trends and anomalies
        - Forecast accuracy metrics
        """)

