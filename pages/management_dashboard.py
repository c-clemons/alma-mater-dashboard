"""
Management Dashboard - Fully Integrated Version
Shows complete 2026 financials with baseline + custom data
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from financial_calcs import generate_monthly_pl, get_cogs_breakdown


def show():
    """Display integrated management dashboard"""
    
    st.markdown('<div class="main-header">Management Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">2026 Financial Overview - Integrated View</div>', unsafe_allow_html=True)
    
    # Get integrated data
    team_members = st.session_state.get('team_members', [])
    opex_expenses = st.session_state.get('opex_expenses', [])
    wholesale_deals = st.session_state.get('wholesale_deals', [])
    
    # Generate monthly P&L with all integrated data
    df_2026 = generate_monthly_pl(
        year=2026,
        team_members=team_members,
        opex_expenses=opex_expenses,
        wholesale_deals=wholesale_deals,
        dtc_discount_rate=0.0,  # No discounts in 2026
        dtc_return_rate=0.0  # No returns in 2026
    )
    
    # Calculate annual totals
    annual_dtc_revenue = df_2026['DTC Revenue'].sum()
    annual_ws_revenue = df_2026['Wholesale Revenue'].sum()
    annual_total_revenue = df_2026['Total Revenue'].sum()
    annual_cogs = df_2026['Total COGS'].sum()
    annual_gross_profit = df_2026['Gross Profit'].sum()
    annual_team_costs = df_2026['Team Costs'].sum()
    annual_other_opex = df_2026['Other OpEx'].sum()
    annual_total_opex = df_2026['Total OpEx'].sum()
    annual_ebitda = df_2026['EBITDA'].sum()
    
    gross_margin = (annual_gross_profit / annual_total_revenue * 100) if annual_total_revenue > 0 else 0
    ebitda_margin = (annual_ebitda / annual_total_revenue * 100) if annual_total_revenue > 0 else 0
    
    # --- EXECUTIVE SUMMARY ---
    st.markdown("## Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${annual_total_revenue:,.0f}",
            help="DTC + Wholesale revenue for 2026"
        )
    
    with col2:
        st.metric(
            "Gross Profit",
            f"${annual_gross_profit:,.0f}",
            delta=f"{gross_margin:.1f}% margin"
        )
    
    with col3:
        st.metric(
            "Total OpEx",
            f"${annual_total_opex:,.0f}",
            help="Team costs + Other operating expenses"
        )
    
    with col4:
        st.metric(
            "EBITDA",
            f"${annual_ebitda:,.0f}",
            delta=f"{ebitda_margin:.1f}% margin",
            delta_color="normal" if annual_ebitda >= 0 else "inverse"
        )
    
    st.divider()
    
    # --- REVENUE BREAKDOWN ---
    st.markdown("## Revenue Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by channel
        fig_revenue = go.Figure(data=[
            go.Pie(
                labels=['DTC', 'Wholesale'],
                values=[annual_dtc_revenue, annual_ws_revenue],
                hole=0.4,
                marker=dict(colors=['#2E86AB', '#A23B72'])
            )
        ])
        fig_revenue.update_layout(
            title='Revenue by Channel',
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Revenue metrics
        st.metric("DTC Revenue", f"${annual_dtc_revenue:,.0f}")
        st.metric("Wholesale Revenue", f"${annual_ws_revenue:,.0f}")
    
    with col2:
        # Monthly revenue trend
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Bar(
            name='DTC',
            x=df_2026['Month'],
            y=df_2026['DTC Revenue'],
            marker_color='#2E86AB'
        ))
        
        fig_trend.add_trace(go.Bar(
            name='Wholesale',
            x=df_2026['Month'],
            y=df_2026['Wholesale Revenue'],
            marker_color='#A23B72'
        ))
        
        fig_trend.update_layout(
            title='Monthly Revenue Trend',
            barmode='stack',
            height=300,
            showlegend=True
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.divider()
    
    # --- COGS BREAKDOWN ---
    st.markdown("## Cost of Goods Sold")
    
    # Get COGS breakdown
    cogs_breakdown = get_cogs_breakdown(annual_total_revenue, year=2026, channel='DTC')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # COGS components pie chart
        fig_cogs = go.Figure(data=[
            go.Pie(
                labels=['Product Cost', 'Warehousing', 'Freight', 'Merchant Fees'],
                values=[
                    cogs_breakdown['product'],
                    cogs_breakdown['warehousing'],
                    cogs_breakdown['freight'],
                    cogs_breakdown['merchant']
                ],
                hole=0.4,
                marker=dict(colors=['#E63946', '#F18F01', '#F4A261', '#E9C46A'])
            )
        ])
        fig_cogs.update_layout(
            title='COGS Breakdown',
            height=300
        )
        st.plotly_chart(fig_cogs, use_container_width=True)
    
    with col2:
        st.markdown("### COGS Components")
        
        # Display breakdown table
        cogs_data = pd.DataFrame({
            'Component': ['Product Cost', 'Warehousing', 'Freight', 'Merchant Fees', 'Total COGS'],
            'Amount': [
                cogs_breakdown['product'],
                cogs_breakdown['warehousing'],
                cogs_breakdown['freight'],
                cogs_breakdown['merchant'],
                cogs_breakdown['total']
            ],
            '% of Revenue': [
                25.0, 6.0, 6.0, 3.0, 40.0
            ]
        })
        
        # Format for display
        cogs_data['Amount'] = cogs_data['Amount'].apply(lambda x: f"${x:,.0f}")
        cogs_data['% of Revenue'] = cogs_data['% of Revenue'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(cogs_data, use_container_width=True, hide_index=True)
        
        st.info(f"**Total COGS:** ${annual_cogs:,.0f} (40% of revenue)")
    
    st.divider()
    
# --- OPERATING EXPENSES ---
    st.markdown("## Operating Expenses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # OpEx breakdown pie chart
        fig_opex = go.Figure(data=[
            go.Pie(
                labels=['Team Costs', 'Other OpEx'],
                values=[annual_team_costs, annual_other_opex],
                hole=0.4,
                marker=dict(colors=['#457B9D', '#1D3557'])
            )
        ])
        fig_opex.update_layout(
            title='OpEx Breakdown',
            height=300
        )
        st.plotly_chart(fig_opex, use_container_width=True)
        
        st.metric("Team Costs", f"${annual_team_costs:,.0f}", 
                 help="Salaries + Rippling burdens (starting May)")
        st.metric("Other OpEx", f"${annual_other_opex:,.0f}",
                 help="All other operating expenses")
    
    with col2:
        st.markdown("### OpEx Components")
        
        # Calculate major expense categories from baseline
        performance_marketing = 160000
        affiliate = 50000
        shopify = 34200
        klaviyo = 32500  # Migration cost included
        other_systems = 1200 + 3000  # Yotpo + UpPromote
        original_opex = 132000  # Travel, development, shipping, etc.
        
        # Display breakdown table
        opex_data = pd.DataFrame({
            'Component': [
                'Performance Marketing',
                'Affiliate Platform',
                'Shopify',
                'Klaviyo (ESP/CRM)',
                'Other Systems',
                'Original OpEx',
                'Team Costs',
                'Total OpEx'
            ],
            'Amount': [
                performance_marketing,
                affiliate,
                shopify,
                klaviyo,
                other_systems,
                original_opex,
                annual_team_costs,
                annual_total_opex
            ],
            '% of Revenue': [
                (performance_marketing / annual_total_revenue * 100),
                (affiliate / annual_total_revenue * 100),
                (shopify / annual_total_revenue * 100),
                (klaviyo / annual_total_revenue * 100),
                (other_systems / annual_total_revenue * 100),
                (original_opex / annual_total_revenue * 100),
                (annual_team_costs / annual_total_revenue * 100),
                (annual_total_opex / annual_total_revenue * 100)
            ]
        })
        
        # Format for display
        opex_data['Amount'] = opex_data['Amount'].apply(lambda x: f"${x:,.0f}")
        opex_data['% of Revenue'] = opex_data['% of Revenue'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(opex_data, use_container_width=True, hide_index=True)
        
        st.info(f"**Total OpEx:** ${annual_total_opex:,.0f} (54% of revenue)")
    
    # Monthly OpEx trend
    st.markdown("### Monthly OpEx Trend")
    fig_opex_trend = go.Figure()
    
    fig_opex_trend.add_trace(go.Bar(
        name='Team Costs',
        x=df_2026['Month'],
        y=df_2026['Team Costs'],
        marker_color='#457B9D'
    ))
    
    fig_opex_trend.add_trace(go.Bar(
        name='Other OpEx',
        x=df_2026['Month'],
        y=df_2026['Other OpEx'],
        marker_color='#1D3557'
    ))
    
    fig_opex_trend.update_layout(
        title='Monthly OpEx by Category',
        barmode='stack',
        height=350,
        showlegend=True
    )
    
    st.plotly_chart(fig_opex_trend, use_container_width=True)
    
    st.divider()
    
    # --- PROFITABILITY ---
    st.markdown("## Profitability Analysis")
    
    # Monthly profitability chart
    fig_profit = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Monthly Gross Profit', 'Monthly EBITDA'),
        vertical_spacing=0.15,
        row_heights=[0.5, 0.5]
    )
    
    # Gross Profit
    fig_profit.add_trace(
        go.Bar(
            name='Gross Profit',
            x=df_2026['Month'],
            y=df_2026['Gross Profit'],
            marker_color='#00BA38'
        ),
        row=1, col=1
    )
    
    # EBITDA
    colors = ['#00BA38' if x >= 0 else '#F8766D' for x in df_2026['EBITDA']]
    fig_profit.add_trace(
        go.Bar(
            name='EBITDA',
            x=df_2026['Month'],
            y=df_2026['EBITDA'],
            marker_color=colors
        ),
        row=2, col=1
    )
    
    fig_profit.update_layout(height=600, showlegend=False)
    fig_profit.update_yaxes(title_text="Amount ($)", row=1, col=1)
    fig_profit.update_yaxes(title_text="Amount ($)", row=2, col=1)
    
    st.plotly_chart(fig_profit, use_container_width=True)
    
    st.divider()
    
    # --- DATA SOURCES ---
    st.markdown("## Data Sources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Team")
        st.write(f"**{len(team_members)}** team members")
        st.write(f"Baseline: 7 members")
        st.write(f"Custom: {max(0, len(team_members) - 7)}")
        st.write(f"Total Annual: ${annual_team_costs:,.0f}")
    
    with col2:
        st.markdown("### OpEx")
        st.write(f"**{len(opex_expenses)}** expense items")
        st.write(f"Baseline: 13 items (~$387K)")
        st.write(f"Custom: {max(0, len(opex_expenses) - 13)}")
        st.write(f"Total Annual: ${annual_other_opex:,.0f}")
    
    with col3:
        st.markdown("### Wholesale")
        st.write(f"**{len(wholesale_deals)}** deals")
        st.write(f"Baseline: 2 deals ($288K)")
        st.write(f"Custom: {max(0, len(wholesale_deals) - 2)}")
        st.write(f"Total Annual: ${annual_ws_revenue:,.0f}")
    
    # Quick links
    st.divider()
    st.info("💡 **Tip:** Use Team Tracker, OpEx Tracker, and Wholesale Tracker to add custom data on top of the baseline.")
