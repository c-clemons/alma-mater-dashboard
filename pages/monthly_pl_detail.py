"""
Monthly P&L Detail
Detailed month-by-month P&L with charts, data tables, and assumption breakdowns
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from financial_calcs import generate_monthly_pl


def load_monthly_actuals_2025():
    """Load 2025 monthly actuals from QBO P&L"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Revenue from QBO (combining DTC channels)
    dtc_revenue = [1406, 1819, 2075, 1739, 3319, 6158, 6367, 5841, 5937, 6788, 13671, 19408]
    wholesale_revenue = [2433, 0, 0, 0, 0, 1613, 0, 0, 14688, 0, 6285, 1292]
    total_revenue = [d + w for d, w in zip(dtc_revenue, wholesale_revenue)]
    
    # COGS (94% of revenue - prototype phase)
    cogs = [r * 0.94 for r in total_revenue]
    gross_profit = [r - c for r, c in zip(total_revenue, cogs)]
    
    # Operating Expenses - ACTUAL monthly from P&L (Total for Expenses row)
    opex_monthly = [1901.07, 4830.55, 16464.50, 31308.27, 12907.70, 10699.73, 
                    9168.37, 20096.24, 34076.98, 28309.60, 20859.97, 37677.34]
    
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
    """Display monthly P&L detail with integrated data"""
    
    st.markdown('<div class="main-header">Monthly P&L Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Month-by-month financial performance with variance analysis</div>', unsafe_allow_html=True)
    
    # Get integrated 2026 data
    team_members = st.session_state.get('team_members', [])
    opex_expenses = st.session_state.get('opex_expenses', [])
    wholesale_deals = st.session_state.get('wholesale_deals', [])
    
    df_2026 = generate_monthly_pl(
        year=2026,
        team_members=team_members,
        opex_expenses=opex_expenses,
        wholesale_deals=wholesale_deals,
        dtc_discount_rate=0.0,
        dtc_return_rate=0.0
    )
    
    # Load 2025 actuals
    df_2025 = load_monthly_actuals_2025()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "2025 Actuals", 
        "2026 Forecast", 
        "Assumptions Breakdown",
        "Year Comparison", 
        "Variance Analysis"
    ])
    
    # --- TAB 1: 2025 ACTUALS ---
    with tab1:
        st.markdown("### 2025 Monthly Actuals")
        
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
        fig = go.Figure()
        fig.add_trace(go.Bar(name='DTC', x=df_2025['Month'], y=df_2025['DTC Revenue'], marker_color='#2E86AB'))
        fig.add_trace(go.Bar(name='Wholesale', x=df_2025['Month'], y=df_2025['Wholesale Revenue'], marker_color='#A23B72'))
        fig.add_trace(go.Scatter(name='COGS', x=df_2025['Month'], y=df_2025['COGS'], mode='lines+markers', marker_color='#E63946', line=dict(width=3)))
        fig.add_trace(go.Scatter(name='Operating Expenses', x=df_2025['Month'], y=df_2025['Operating Expenses'], mode='lines+markers', marker_color='#1D3557'))
        
        colors = ['#00BA38' if x >= 0 else '#F8766D' for x in df_2025['EBITDA']]
        fig.add_trace(go.Bar(name='EBITDA', x=df_2025['Month'], y=df_2025['EBITDA'], marker_color=colors))
        
        fig.update_layout(
            title='2025 Monthly Performance',
            hovermode='x unified',
            height=450
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Monthly Data Table")
        
        # Create transposed table with months as columns
        display_df = df_2025.copy()
        
        # Select key columns to transpose
        columns_to_show = ['DTC Revenue', 'Wholesale Revenue', 'Total Revenue', 'COGS', 
                          'Gross Profit', 'Operating Expenses', 'EBITDA']
        
        # Create transposed dataframe
        transposed_data = {}
        for col in columns_to_show:
            transposed_data[col] = display_df[col].values
        
        # Create DataFrame with months as columns
        transposed_df = pd.DataFrame(transposed_data, index=display_df['Month'].values).T
        
        # Format currency
        transposed_df = transposed_df.applymap(lambda x: f"${x:,.0f}")
        
        # Display with metric names as first column
        st.dataframe(transposed_df, use_container_width=True)
        
        csv = df_2025.to_csv(index=False)
        st.download_button("📥 Download 2025 Data (CSV)", csv, "2025_monthly_pl.csv", "text/csv")
    
    # --- TAB 2: 2026 FORECAST ---
    with tab2:
        st.markdown("### 2026 Monthly Forecast (Integrated)")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", f"${df_2026['Total Revenue'].sum():,.0f}")
        with col2:
            st.metric("Avg Monthly Revenue", f"${df_2026['Total Revenue'].mean():,.0f}")
        with col3:
            gross_margin = (df_2026['Gross Profit'].sum() / df_2026['Total Revenue'].sum() * 100)
            st.metric("Gross Margin", f"{gross_margin:.1f}%")
        with col4:
            st.metric("Total EBITDA", f"${df_2026['EBITDA'].sum():,.0f}")
        
        st.divider()
        
        # Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(name='DTC', x=df_2026['Month'], y=df_2026['DTC Revenue'], marker_color='#2E86AB'))
        fig.add_trace(go.Bar(name='Wholesale', x=df_2026['Month'], y=df_2026['Wholesale Revenue'], marker_color='#A23B72'))
        fig.add_trace(go.Scatter(name='COGS', x=df_2026['Month'], y=df_2026['Total COGS'], mode='lines+markers', marker_color='#E63946', line=dict(width=3)))
        fig.add_trace(go.Scatter(name='Team Costs', x=df_2026['Month'], y=df_2026['Team Costs'], mode='lines+markers', marker_color='#457B9D'))
        fig.add_trace(go.Scatter(name='Other OpEx', x=df_2026['Month'], y=df_2026['Other OpEx'], mode='lines+markers', marker_color='#1D3557'))
        
        colors = ['#00BA38' if x >= 0 else '#F8766D' for x in df_2026['EBITDA']]
        fig.add_trace(go.Bar(name='EBITDA', x=df_2026['Month'], y=df_2026['EBITDA'], marker_color=colors))
        
        fig.update_layout(
            title='2026 Monthly Performance',
            hovermode='x unified',
            height=450
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Monthly Data Table")
        
        # Create transposed table with months as columns
        display_df = df_2026.copy()
        
        # Select key columns to transpose
        columns_to_show = ['DTC Revenue', 'Wholesale Revenue', 'Total Revenue', 'Total COGS', 
                          'Gross Profit', 'Team Costs', 'Other OpEx', 'Total OpEx', 'EBITDA']
        
        # Create transposed dataframe
        transposed_data = {}
        for col in columns_to_show:
            transposed_data[col] = display_df[col].values
        
        # Create DataFrame with months as columns
        transposed_df = pd.DataFrame(transposed_data, index=display_df['Month'].values).T
        
        # Format currency
        transposed_df = transposed_df.applymap(lambda x: f"${x:,.0f}")
        
        # Display with metric names as first column
        st.dataframe(transposed_df, use_container_width=True)
        
        csv = df_2026.to_csv(index=False)
        st.download_button("📥 Download 2026 Data (CSV)", csv, "2026_monthly_pl.csv", "text/csv")
    
    # --- TAB 3: ASSUMPTIONS BREAKDOWN ---
    with tab3:
        st.markdown("### 2026 Assumptions & Drivers")
        
        st.info("💡 This shows all the baseline assumptions driving your 2026 projections")
        
        # Revenue Assumptions
        st.markdown("## Revenue Assumptions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### DTC Revenue")
            
            # V2 product
            st.markdown("**V2 (Beta) Product:**")
            v2_units = [10, 20, 30, 50, 100, 150, 200, 225, 250, 275, 300, 325]
            st.write(f"• Units per month: 10 → 325")
            st.write(f"• Total units: {sum(v2_units):,}")
            st.write(f"• AOV: $250")
            st.write(f"• Total Revenue: ${sum(v2_units) * 250:,.0f}")
            
            st.markdown("**Alpha Product:**")
            alpha_units = [0, 0, 0, 0, 0, 0, 50, 100, 200, 300, 300, 0]
            st.write(f"• Launch: July 2026")
            st.write(f"• Units per month: 50 → 300")
            st.write(f"• Total units: {sum(alpha_units):,}")
            st.write(f"• AOV: $450")
            st.write(f"• Total Revenue: ${sum(alpha_units) * 450:,.0f}")
            
            st.markdown("**Total DTC: ${:,.0f}**".format(sum(v2_units) * 250 + sum(alpha_units) * 450))
        
        with col2:
            st.markdown("### Wholesale Revenue")
            
            st.markdown("**Baseline Deals:**")
            st.write("• Spring 2026:")
            st.write("  - 500 units @ $144 = $72,000")
            st.write("  - Delivery: March 2026")
            st.write("  - Cost: $77,770")
            
            st.write("• Fall 2026:")
            st.write("  - 1,500 units @ $144 = $216,000")
            st.write("  - Delivery: August 2026")
            st.write("  - Cost: $138,875")
            
            st.markdown("**Total Wholesale: $288,000**")
            
            st.markdown("**Custom Deals:**")
            custom_ws_count = max(0, len(wholesale_deals) - 2)
            if custom_ws_count > 0:
                custom_ws_revenue = df_2026['Wholesale Revenue'].sum() - 288000
                st.write(f"• {custom_ws_count} additional deals")
                st.write(f"• Additional revenue: ${custom_ws_revenue:,.0f}")
            else:
                st.write("• No custom deals added")
        
        st.divider()
        
        # COGS Assumptions
        st.markdown("## COGS Assumptions")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Product Cost", "25%", help="Manufacturing and materials")
        with col2:
            st.metric("Warehousing", "6%", help="Storage and fulfillment")
        with col3:
            st.metric("Freight", "6%", help="Shipping and logistics")
        with col4:
            st.metric("Merchant Fees", "3%", help="Payment processing")
        
        st.markdown("**Total COGS Rate: 40%** of revenue")
        st.markdown(f"**2026 Total COGS: ${df_2026['Total COGS'].sum():,.0f}**")
        
        st.divider()
        
        # Team Assumptions
        st.markdown("## Team Cost Assumptions")
        
        st.markdown(f"**Total Team Members: {len(team_members)}** (Baseline: 7)")
        
        team_data = []
        for member in team_members[:7]:  # Show baseline
            name = f"{member.get('first_name', '')} {member.get('last_name', '')}"
            salary = member.get('annual_salary', 0)
            start_date = member.get('start_date', '')
            emp_type = member.get('employment_type', '')
            team_data.append({
                'Name': name,
                'Salary': f"${salary:,.0f}",
                'Type': emp_type,
                'Start Date': start_date
            })
        
        st.dataframe(pd.DataFrame(team_data), use_container_width=True, hide_index=True)
        
        st.markdown("**Rippling PEO Burdens (Starting May 2026):**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("• Platform: $137/month")
            st.write("• Healthcare: $697.91/month")
        with col2:
            st.write("• FUTA: $3.50/month")
            st.write("• Medicare: 1.45%")
        with col3:
            st.write("• Social Security: 6.2%")
            st.write("• CA ETT: 0.1%")
        
        st.markdown(f"**Total 2026 Team Costs: ${df_2026['Team Costs'].sum():,.0f}**")
        
        st.divider()
        
        # OpEx Assumptions
        st.markdown("## Operating Expense Assumptions")
        
        st.markdown(f"**Total OpEx Items: {len(opex_expenses)}** (Baseline: 13)")
        
        # Group by category
        opex_by_category = {}
        total_opex = 0
        
        for expense in opex_expenses[:13]:  # Show baseline
            category = expense.get('category', 'Other')
            amount = expense.get('annual_cost', 0)
            total_opex += amount
            
            if category not in opex_by_category:
                opex_by_category[category] = []
            
            opex_by_category[category].append({
                'Expense': expense.get('expense_name', ''),
                'Annual': f"${amount:,.0f}"
            })
        
        # Display by category
        for category, items in opex_by_category.items():
            with st.expander(f"**{category}**"):
                st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
        
        st.markdown(f"**Total 2026 Other OpEx: ${df_2026['Other OpEx'].sum():,.0f}**")
        
        st.divider()
        
        # Marketing Spend Breakdown
        st.markdown("## Marketing & Systems Spend")
        
        marketing_items = [
            ("Performance Marketing (Google/Meta)", "$160,000"),
            ("Affiliate Platform Costs", "$50,000"),
            ("Shopify", "$34,200"),
            ("Klaviyo (ESP/CRM)", "$32,500"),
            ("Yotpo (Reviews)", "$1,200"),
            ("UpPromote", "$3,000"),
        ]
        
        st.dataframe(
            pd.DataFrame(marketing_items, columns=['Item', 'Annual Cost']),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("**Total Marketing & Systems: $280,900**")
    
    # --- TAB 4: YEAR COMPARISON ---
    with tab4:
        st.markdown("### 2025 vs 2026 Comparison")
        
        # Summary comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            revenue_2025 = df_2025['Total Revenue'].sum()
            revenue_2026 = df_2026['Total Revenue'].sum()
            growth = ((revenue_2026 - revenue_2025) / revenue_2025 * 100) if revenue_2025 > 0 else 0
            st.metric("Revenue Growth", f"{growth:.0f}%", 
                     delta=f"${revenue_2026 - revenue_2025:,.0f}")
        
        with col2:
            ebitda_2025 = df_2025['EBITDA'].sum()
            ebitda_2026 = df_2026['EBITDA'].sum()
            st.metric("EBITDA Change", f"${ebitda_2026:,.0f}",
                     delta=f"${ebitda_2026 - ebitda_2025:,.0f}")
        
        with col3:
            margin_2025 = (df_2025['Gross Profit'].sum() / df_2025['Total Revenue'].sum() * 100)
            margin_2026 = (df_2026['Gross Profit'].sum() / df_2026['Total Revenue'].sum() * 100)
            st.metric("Gross Margin", f"{margin_2026:.1f}%",
                     delta=f"{margin_2026 - margin_2025:.1f}pp")
        
        st.divider()
        
        # Comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(name='2025 Revenue', x=df_2025['Month'], y=df_2025['Total Revenue'], marker_color='#A9A9A9'))
        fig.add_trace(go.Bar(name='2026 Revenue', x=df_2026['Month'], y=df_2026['Total Revenue'], marker_color='#2E86AB'))
        
        fig.update_layout(
            title='Monthly Revenue: 2025 vs 2026',
            barmode='group',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # --- TAB 5: VARIANCE ANALYSIS ---
    with tab5:
        st.markdown("### Budget vs Actual Tracking")
        st.info("🚧 This feature will track budget vs actual performance as 2026 progresses. Check back when you have actual data!")
