"""
Monthly P&L Detail
Detailed month-by-month P&L with charts, data tables, and variance analysis
Uses QBO actuals when available
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from financial_calcs import generate_monthly_pl
from qbo_parser import (
    deserialize_qbo_data, build_actuals_dataframe, actuals_to_pl_format, MONTHS
)


def get_2025_actuals():
    """Get 2025 actuals from QBO if available, otherwise use hard-coded fallback."""
    qbo_raw = st.session_state.get('qbo_actuals')
    if qbo_raw:
        parsed = deserialize_qbo_data(qbo_raw)
        if parsed:
            actuals = build_actuals_dataframe(parsed['pl_data'], 2025)
            rows = actuals_to_pl_format(actuals)
            return pd.DataFrame(rows), "QBO"

    # Fallback hard-coded 2025 (from original QBO data)
    months = MONTHS
    dtc_revenue = [0, 4269.90, 2997.05, 1406.00, 4908.21, 4348.01,
                   5232.04, 8912.02, 5228.85, 5504.82, 6270.06, 6044.05]
    wholesale_revenue = [0, 2433.00, 0, 0, 0, 1612.86, 0, 0, 0, 14688.31, 0, 6285.12]
    total_revenue = [d + w for d, w in zip(dtc_revenue, wholesale_revenue)]
    cogs = [0, 1494.65, 18212.83, 5012.17, 9558.23, 1582.81,
            3235.61, 5828.99, 3905.49, 979.12, 1383.98, 21838.11]
    gross_profit = [r - c for r, c in zip(total_revenue, cogs)]
    opex_monthly = [0, 1901.07, 7830.55, 11964.50, 31308.27, 12907.70,
                    10699.73, 9168.37, 20096.24, 34076.98, 28309.60, 20859.97]
    ebitda = [gp - opex for gp, opex in zip(gross_profit, opex_monthly)]

    data = []
    for m in range(12):
        data.append({
            'Month': months[m],
            'DTC Revenue': dtc_revenue[m],
            'Wholesale Revenue': wholesale_revenue[m],
            'Total Revenue': total_revenue[m],
            'Total COGS': cogs[m],
            'Gross Profit': gross_profit[m],
            'Gross Margin %': (gross_profit[m] / total_revenue[m] * 100) if total_revenue[m] > 0 else 0,
            'Total OpEx': opex_monthly[m],
            'EBITDA': ebitda[m],
            'EBITDA Margin %': (ebitda[m] / total_revenue[m] * 100) if total_revenue[m] > 0 else 0,
        })
    return pd.DataFrame(data), "Hard-coded"


def get_2026_actuals():
    """Get 2026 actuals from QBO if available. Returns (DataFrame, last_month) or (None, 0)."""
    qbo_raw = st.session_state.get('qbo_actuals')
    if not qbo_raw:
        return None, 0

    parsed = deserialize_qbo_data(qbo_raw)
    if not parsed:
        return None, 0

    # Check if we have any 2026 data
    max_26_month = 0
    for yr, mo in parsed['months_found']:
        if yr == 2026:
            max_26_month = max(max_26_month, mo)

    if max_26_month == 0:
        return None, 0

    actuals = build_actuals_dataframe(parsed['pl_data'], 2026, max_26_month)
    rows = actuals_to_pl_format(actuals)
    return pd.DataFrame(rows), max_26_month


def format_currency_table(df, cols):
    """Format columns as currency for display."""
    display = df.copy()
    for col in cols:
        if col in display.columns:
            display[col] = display[col].apply(lambda x: f"${x:,.0f}" if x != 0 else "-")
    return display


def make_pl_chart(df, title, has_team_costs=False):
    """Create standard P&L chart."""
    fig = go.Figure()
    fig.add_trace(go.Bar(name='DTC', x=df['Month'], y=df['DTC Revenue'], marker_color='#2E86AB'))
    fig.add_trace(go.Bar(name='Wholesale', x=df['Month'], y=df['Wholesale Revenue'], marker_color='#A23B72'))

    cogs_col = 'Total COGS' if 'Total COGS' in df.columns else 'COGS'
    fig.add_trace(go.Scatter(name='COGS', x=df['Month'], y=df[cogs_col],
                             mode='lines+markers', marker_color='#E63946', line=dict(width=3)))

    if has_team_costs and 'Team Costs' in df.columns:
        fig.add_trace(go.Scatter(name='Team Costs', x=df['Month'], y=df['Team Costs'],
                                 mode='lines+markers', marker_color='#457B9D'))
        fig.add_trace(go.Scatter(name='Other OpEx', x=df['Month'], y=df['Other OpEx'],
                                 mode='lines+markers', marker_color='#1D3557'))
    else:
        opex_col = 'Total OpEx' if 'Total OpEx' in df.columns else 'Operating Expenses'
        fig.add_trace(go.Scatter(name='OpEx', x=df['Month'], y=df[opex_col],
                                 mode='lines+markers', marker_color='#1D3557', line=dict(width=3)))

    colors = ['#00BA38' if x >= 0 else '#F8766D' for x in df['EBITDA']]
    fig.add_trace(go.Bar(name='EBITDA', x=df['Month'], y=df['EBITDA'], marker_color=colors))

    fig.update_layout(title=title, hovermode='x unified', height=450)
    return fig


def show():
    st.markdown('<div class="main-header">Monthly P&L Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Month-by-month financial performance with variance analysis</div>', unsafe_allow_html=True)

    # Get integrated 2026 forecast
    team_members = st.session_state.get('team_members', [])
    opex_expenses = st.session_state.get('opex_expenses', [])
    wholesale_deals = st.session_state.get('wholesale_deals', [])

    df_2026_forecast = generate_monthly_pl(
        year=2026,
        team_members=team_members,
        opex_expenses=opex_expenses,
        wholesale_deals=wholesale_deals,
        dtc_discount_rate=0.0,
        dtc_return_rate=0.0
    )

    # Get actuals
    df_2025, source_25 = get_2025_actuals()
    df_2026_actual, last_actual_month = get_2026_actuals()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "2025 Actuals",
        "2026 Forecast",
        "Variance Analysis",
        "Year Comparison",
        "Assumptions Breakdown",
    ])

    # --- TAB 1: 2025 ACTUALS ---
    with tab1:
        st.markdown("### 2025 Monthly Actuals")
        if source_25 == "QBO":
            st.caption("Source: QuickBooks Online import")
        else:
            st.caption("Source: Hard-coded baseline (upload QBO file to refresh)")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", f"${df_2025['Total Revenue'].sum():,.0f}")
        with col2:
            st.metric("Avg Monthly Revenue", f"${df_2025['Total Revenue'].mean():,.0f}")
        with col3:
            gm = df_2025['Gross Margin %'].mean()
            st.metric("Avg Gross Margin", f"{gm:.1f}%")
        with col4:
            st.metric("Total EBITDA", f"${df_2025['EBITDA'].sum():,.0f}")

        st.divider()
        st.plotly_chart(make_pl_chart(df_2025, '2025 Monthly Performance'), use_container_width=True)

        st.markdown("### Monthly Data Table")
        key_cols = ['DTC Revenue', 'Wholesale Revenue', 'Total Revenue',
                    'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']
        available_cols = [c for c in key_cols if c in df_2025.columns]
        transposed = df_2025.set_index('Month')[available_cols].T
        transposed_fmt = transposed.applymap(lambda x: f"${x:,.0f}")
        st.dataframe(transposed_fmt, use_container_width=True)

        csv = df_2025.to_csv(index=False)
        st.download_button("Download 2025 Data (CSV)", csv, "2025_monthly_pl.csv", "text/csv")

    # --- TAB 2: 2026 FORECAST ---
    with tab2:
        st.markdown("### 2026 Monthly Forecast (Integrated)")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", f"${df_2026_forecast['Total Revenue'].sum():,.0f}")
        with col2:
            st.metric("Avg Monthly Revenue", f"${df_2026_forecast['Total Revenue'].mean():,.0f}")
        with col3:
            gm = (df_2026_forecast['Gross Profit'].sum() / df_2026_forecast['Total Revenue'].sum() * 100)
            st.metric("Gross Margin", f"{gm:.1f}%")
        with col4:
            st.metric("Total EBITDA", f"${df_2026_forecast['EBITDA'].sum():,.0f}")

        st.divider()
        st.plotly_chart(
            make_pl_chart(df_2026_forecast, '2026 Monthly Performance', has_team_costs=True),
            use_container_width=True
        )

        st.markdown("### Monthly Data Table")
        key_cols_26 = ['DTC Revenue', 'Wholesale Revenue', 'Total Revenue', 'Total COGS',
                       'Gross Profit', 'Team Costs', 'Other OpEx', 'Total OpEx', 'EBITDA']
        transposed_26 = df_2026_forecast.set_index('Month')[key_cols_26].T
        transposed_26_fmt = transposed_26.applymap(lambda x: f"${x:,.0f}")
        st.dataframe(transposed_26_fmt, use_container_width=True)

        csv = df_2026_forecast.to_csv(index=False)
        st.download_button("Download 2026 Data (CSV)", csv, "2026_monthly_pl.csv", "text/csv")

    # --- TAB 3: VARIANCE ANALYSIS ---
    with tab3:
        st.markdown("### 2026 Actual vs Forecast Variance")

        if df_2026_actual is None or last_actual_month == 0:
            st.warning(
                "No 2026 actuals available yet. Upload a QBO file with 2026 data "
                "on the **QBO Import** page to enable variance tracking."
            )
        else:
            st.success(
                f"Showing variance for closed months: **Jan - {MONTHS[last_actual_month - 1]} 2026**"
            )

            # Build variance for key metrics
            variance_metrics = ['Total Revenue', 'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']

            # Summary metrics for closed months
            col1, col2, col3 = st.columns(3)
            actual_rev = df_2026_actual['Total Revenue'].iloc[:last_actual_month].sum()
            forecast_rev = df_2026_forecast['Total Revenue'].iloc[:last_actual_month].sum()
            var_rev = actual_rev - forecast_rev

            with col1:
                st.metric("YTD Actual Revenue", f"${actual_rev:,.0f}")
            with col2:
                st.metric("YTD Forecast Revenue", f"${forecast_rev:,.0f}")
            with col3:
                pct = (var_rev / forecast_rev * 100) if forecast_rev != 0 else 0
                st.metric("Revenue Variance", f"${var_rev:,.0f}",
                          delta=f"{pct:+.1f}%",
                          delta_color="normal" if var_rev >= 0 else "inverse")

            st.divider()

            # Detailed variance table
            st.markdown("#### Monthly Variance Detail")

            for metric in variance_metrics:
                with st.expander(f"**{metric}**", expanded=(metric in ['Total Revenue', 'EBITDA'])):
                    var_data = []
                    for m in range(last_actual_month):
                        actual_col = metric if metric in df_2026_actual.columns else None
                        forecast_col = metric if metric in df_2026_forecast.columns else None

                        if actual_col and forecast_col:
                            act_val = df_2026_actual[actual_col].iloc[m]
                            fc_val = df_2026_forecast[forecast_col].iloc[m]
                            var_val = act_val - fc_val
                            var_pct = (var_val / fc_val * 100) if fc_val != 0 else 0
                        else:
                            act_val = fc_val = var_val = var_pct = 0

                        var_data.append({
                            'Month': MONTHS[m],
                            'Actual': act_val,
                            'Forecast': fc_val,
                            'Variance $': var_val,
                            'Variance %': var_pct,
                        })

                    var_df = pd.DataFrame(var_data)

                    # Add totals row
                    totals = {
                        'Month': 'YTD Total',
                        'Actual': var_df['Actual'].sum(),
                        'Forecast': var_df['Forecast'].sum(),
                        'Variance $': var_df['Variance $'].sum(),
                        'Variance %': (var_df['Variance $'].sum() / var_df['Forecast'].sum() * 100)
                        if var_df['Forecast'].sum() != 0 else 0,
                    }
                    var_df = pd.concat([var_df, pd.DataFrame([totals])], ignore_index=True)

                    # Format
                    display_var = var_df.copy()
                    for col in ['Actual', 'Forecast', 'Variance $']:
                        display_var[col] = display_var[col].apply(lambda x: f"${x:,.0f}")
                    display_var['Variance %'] = display_var['Variance %'].apply(lambda x: f"{x:+.1f}%")

                    st.dataframe(display_var, use_container_width=True, hide_index=True)

            st.divider()

            # Variance chart
            st.markdown("#### Actual vs Forecast Chart")

            fig = go.Figure()

            # Only show closed months
            closed_months = MONTHS[:last_actual_month]
            actual_rev = df_2026_actual['Total Revenue'].iloc[:last_actual_month].values
            forecast_rev = df_2026_forecast['Total Revenue'].iloc[:last_actual_month].values

            fig.add_trace(go.Bar(
                name='Actual', x=closed_months, y=actual_rev,
                marker_color='#2E86AB'
            ))
            fig.add_trace(go.Bar(
                name='Forecast', x=closed_months, y=forecast_rev,
                marker_color='#A9A9A9', opacity=0.7
            ))

            # Add variance line
            variance = actual_rev - forecast_rev
            fig.add_trace(go.Scatter(
                name='Variance', x=closed_months, y=variance,
                mode='lines+markers', marker_color='#E63946',
                yaxis='y2'
            ))

            fig.update_layout(
                title='Revenue: Actual vs Forecast',
                barmode='group',
                height=400,
                yaxis=dict(title='Revenue ($)'),
                yaxis2=dict(title='Variance ($)', overlaying='y', side='right'),
            )

            st.plotly_chart(fig, use_container_width=True)

            # EBITDA variance chart
            actual_ebitda = df_2026_actual['EBITDA'].iloc[:last_actual_month].values
            forecast_ebitda = df_2026_forecast['EBITDA'].iloc[:last_actual_month].values

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name='Actual EBITDA', x=closed_months, y=actual_ebitda,
                                  marker_color=['#00BA38' if x >= 0 else '#F8766D' for x in actual_ebitda]))
            fig2.add_trace(go.Bar(name='Forecast EBITDA', x=closed_months, y=forecast_ebitda,
                                  marker_color='#A9A9A9', opacity=0.5))
            fig2.update_layout(title='EBITDA: Actual vs Forecast', barmode='group', height=350)
            st.plotly_chart(fig2, use_container_width=True)

    # --- TAB 4: YEAR COMPARISON ---
    with tab4:
        st.markdown("### 2025 vs 2026 Comparison")

        col1, col2, col3 = st.columns(3)
        revenue_2025 = df_2025['Total Revenue'].sum()
        revenue_2026 = df_2026_forecast['Total Revenue'].sum()
        growth = ((revenue_2026 - revenue_2025) / revenue_2025 * 100) if revenue_2025 > 0 else 0

        with col1:
            st.metric("Revenue Growth", f"{growth:.0f}%",
                      delta=f"${revenue_2026 - revenue_2025:,.0f}")
        with col2:
            ebitda_2025 = df_2025['EBITDA'].sum()
            ebitda_2026 = df_2026_forecast['EBITDA'].sum()
            st.metric("EBITDA Change", f"${ebitda_2026:,.0f}",
                      delta=f"${ebitda_2026 - ebitda_2025:,.0f}")
        with col3:
            gp_25 = df_2025['Gross Profit'].sum()
            gp_26 = df_2026_forecast['Gross Profit'].sum()
            margin_2025 = (gp_25 / revenue_2025 * 100) if revenue_2025 > 0 else 0
            margin_2026 = (gp_26 / revenue_2026 * 100) if revenue_2026 > 0 else 0
            st.metric("Gross Margin", f"{margin_2026:.1f}%",
                      delta=f"{margin_2026 - margin_2025:.1f}pp")

        st.divider()

        fig = go.Figure()
        fig.add_trace(go.Bar(name='2025 Revenue', x=df_2025['Month'],
                             y=df_2025['Total Revenue'], marker_color='#A9A9A9'))
        fig.add_trace(go.Bar(name='2026 Revenue', x=df_2026_forecast['Month'],
                             y=df_2026_forecast['Total Revenue'], marker_color='#2E86AB'))
        fig.update_layout(title='Monthly Revenue: 2025 vs 2026', barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 5: ASSUMPTIONS BREAKDOWN ---
    with tab5:
        st.markdown("### 2026 Assumptions & Drivers")
        st.info("This shows all the baseline assumptions driving your 2026 projections")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### DTC Revenue")
            v2_units = [10, 20, 30, 50, 100, 150, 200, 225, 250, 275, 300, 325]
            alpha_units = [0, 0, 0, 0, 0, 0, 50, 100, 200, 300, 300, 0]
            st.markdown("**V2 (Beta) Product:**")
            st.write(f"Units per month: 10 -> 325 | Total: {sum(v2_units):,} | AOV: $250")
            st.write(f"Total Revenue: ${sum(v2_units) * 250:,.0f}")
            st.markdown("**Alpha Product:**")
            st.write(f"Launch: July 2026 | Units: 50 -> 300 | Total: {sum(alpha_units):,} | AOV: $450")
            st.write(f"Total Revenue: ${sum(alpha_units) * 450:,.0f}")
            st.markdown(f"**Total DTC: ${sum(v2_units) * 250 + sum(alpha_units) * 450:,.0f}**")

        with col2:
            st.markdown("### Wholesale Revenue")
            st.write("Spring 2026: 500 units @ $144 = $72,000 (Cost: $77,770)")
            st.write("Fall 2026: 1,500 units @ $144 = $216,000 (Cost: $138,875)")
            st.markdown("**Total Wholesale: $288,000**")

        st.divider()

        st.markdown("## COGS: 40% Total")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Product Cost", "25%")
        with col2:
            st.metric("Warehousing", "6%")
        with col3:
            st.metric("Freight", "6%")
        with col4:
            st.metric("Merchant Fees", "3%")

        st.divider()

        st.markdown("## Team Costs")
        st.write(f"**{len(st.session_state.get('team_members', []))}** team members")
        st.write("Rippling PEO starting May 2026: $137 + $697.91 healthcare + payroll taxes")

        st.divider()

        st.markdown("## OpEx")
        st.write(f"**{len(st.session_state.get('opex_expenses', []))}** expense items")
        st.write(f"Total 2026 Other OpEx: ${df_2026_forecast['Other OpEx'].sum():,.0f}")
