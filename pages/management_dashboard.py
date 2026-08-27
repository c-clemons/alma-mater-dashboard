"""
Management Dashboard - 2026 Financial Health at a Glance
Blends YTD actuals (from QBO) with remaining-year forecast.
Designed to show financial health in 60 seconds.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from financial_calcs import generate_monthly_pl, get_cogs_breakdown
from shopify_client import get_shopify_data, is_configured as shopify_configured


MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

ACTUAL_COLOR = '#1B4332'
FORECAST_COLOR = '#95D5B2'
NEGATIVE_COLOR = '#E63946'
POSITIVE_COLOR = '#2D6A4F'
ACCENT_BLUE = '#2E86AB'
ACCENT_PURPLE = '#A23B72'


def _get_2026_actuals_from_qbo():
    """Extract 2026 monthly actuals from QBO data. Returns dict of lists and metadata."""
    qbo = st.session_state.get('qbo_actuals')
    if not qbo:
        return None

    pl = qbo.get('pl_data', {})
    cash = qbo.get('cash_data', {})
    ap = qbo.get('ap_data', {})
    last_month = qbo.get('last_month', 0)
    last_year = qbo.get('last_year', 0)

    if last_year < 2026:
        return None

    n_actual = last_month if last_year == 2026 else 12

    def _get_monthly(key):
        vals = []
        for m in range(1, n_actual + 1):
            vals.append(pl.get(key, {}).get(f'2026_{m}', 0))
        return vals

    return {
        'n_months': n_actual,
        'dtc_revenue': _get_monthly('DTC Revenue'),
        'wholesale_revenue': _get_monthly('Wholesale Revenue'),
        'total_revenue': _get_monthly('Total Revenue'),
        'total_cogs': _get_monthly('Total COGS'),
        'gross_profit': _get_monthly('Gross Profit'),
        'total_opex': _get_monthly('Total Expenses'),
        'net_income': _get_monthly('Net Income'),
        'latest_cash': qbo.get('latest_cash', 0),
        'latest_ap': qbo.get('latest_ap', 0),
        'cash_history': {m: v for m, v in cash.items() if m.startswith('2026_')},
    }


def _build_blended_2026(actuals, df_forecast):
    """Build blended 2026: YTD actuals + remaining forecasted months."""
    n_actual = actuals['n_months'] if actuals else 0
    rows = []

    for m in range(12):
        if m < n_actual and actuals:
            rows.append({
                'Month': MONTHS[m],
                'DTC Revenue': actuals['dtc_revenue'][m],
                'Wholesale Revenue': actuals['wholesale_revenue'][m],
                'Total Revenue': actuals['total_revenue'][m],
                'Total COGS': actuals['total_cogs'][m],
                'Gross Profit': actuals['gross_profit'][m],
                'Total OpEx': actuals['total_opex'][m],
                'EBITDA': actuals['gross_profit'][m] - actuals['total_opex'][m],
                'Source': 'Actual',
            })
        else:
            fc = df_forecast.iloc[m]
            rows.append({
                'Month': MONTHS[m],
                'DTC Revenue': fc['DTC Revenue'],
                'Wholesale Revenue': fc['Wholesale Revenue'],
                'Total Revenue': fc['Total Revenue'],
                'Total COGS': fc['Total COGS'],
                'Gross Profit': fc['Gross Profit'],
                'Total OpEx': fc['Total OpEx'],
                'EBITDA': fc['EBITDA'],
                'Source': 'Forecast',
            })

    return pd.DataFrame(rows)


def _fmt_k(v):
    """Compact K/M formatter used by the exec summary tiles."""
    if v is None:
        return '$0'
    sign = '-' if v < 0 else ''
    a = abs(v)
    if a >= 1_000_000:
        return f"{sign}${a/1_000_000:.2f}M"
    if a >= 1_000:
        return f"{sign}${a/1_000:.0f}K"
    return f"{sign}${a:,.0f}"


def _fmt_n(v):
    return f"{round(v or 0):,}"


def _load_marketing_snapshot():
    """Load Full Stream Group monthly snapshot (marketing_monthly.json)."""
    import json
    from pathlib import Path
    p = Path(__file__).parent.parent / 'data' / 'marketing_monthly.json'
    if not p.exists():
        return None
    with open(p) as f:
        return json.load(f)


def _render_executive_summary(actuals, n_actual):
    """3-row KPI block: financial YTD + Shopify YTD + Meta Ads (current month).

    Reads live from qbo_actuals (session_state) and marketing_monthly.json.
    Mirrors the block on the Monthly Report page so both stay in sync as
    monthly closes and Matt's snapshots land.
    """
    if not actuals or n_actual == 0:
        return

    mkt = _load_marketing_snapshot()
    m = n_actual  # 1-indexed current month
    month_name = MONTHS[m - 1]

    # Pull monthly arrays for computed metrics
    qbo_full = st.session_state.get('qbo_actuals') or {}
    qbo = qbo_full.get('qbo_actuals', qbo_full)
    pl = qbo.get('pl_data', {})

    def month_series(key):
        item = pl.get(key, {})
        return [item.get(f"2026_{i}", 0) or 0 for i in range(1, 13)]

    rev_m = month_series('Total Revenue')
    gp_m = month_series('Gross Profit')
    ni_m = month_series('Net Income')

    ytd_rev = sum(rev_m[:m])
    ytd_gp = sum(gp_m[:m])
    ytd_gp_pct = (ytd_gp / ytd_rev * 100) if ytd_rev else 0

    cash_data = qbo.get('cash_data', {})
    end_cash = cash_data.get(f'2026_{m}', 0)
    prev_cash = cash_data.get(f'2026_{m-1}', 0) if m >= 2 else 0
    cash_delta = end_cash - prev_cash

    mo_rev = rev_m[m - 1]
    prev_rev = rev_m[m - 2] if m >= 2 else 0
    mo_ni = ni_m[m - 1]
    prev_ni = ni_m[m - 2] if m >= 2 else 0
    mo_gp_pct = (gp_m[m - 1] / mo_rev * 100) if mo_rev else 0

    st.markdown("## Executive Summary")
    if mkt and mo_rev and prev_rev:
        perf = mkt.get('perf_marketing_monthly', {}).get(str(m)) or mkt.get('perf_marketing_monthly', {}).get(m) or {}
        st.caption(
            f"{month_name} revenue {((mo_rev/prev_rev-1)*100):+.0f}% MoM to {_fmt_k(mo_rev)}. "
            f"GM {mo_gp_pct:.1f}%. "
            + (f"Meta ads full-month ROAS {perf.get('roas', 0):.2f} vs 4.0 target." if perf else "")
        )

    # Row 1 — Financial YTD + current month
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("YTD Revenue", _fmt_k(ytd_rev), f"{_fmt_k(ytd_rev/m)}/mo avg")
    with c2:
        st.metric("Gross Margin YTD", f"{ytd_gp_pct:.1f}%", f"{_fmt_k(ytd_gp)} gross profit")
    with c3:
        st.metric(f"End-{month_name} Cash", _fmt_k(end_cash),
                  f"{_fmt_k(cash_delta)} MoM",
                  delta_color='normal' if cash_delta >= 0 else 'inverse')
    with c4:
        st.metric(f"{month_name} Net Loss", _fmt_k(mo_ni),
                  f"{_fmt_k(mo_ni - prev_ni)} vs prior mo")

    # Row 2 — Shopify (Matt's snapshot)
    if mkt:
        ecomm = mkt.get('ecomm_monthly', {})
        adjg = ecomm.get('adjg', [])
        orders = ecomm.get('orders', [])
        new_cust = ecomm.get('new_cust', [])
        net_rev = ecomm.get('net_rev', [])
        ytd_adj = sum(adjg[:m]) if adjg else 0
        ytd_orders = sum(orders[:m]) if orders else 0
        ytd_new = sum(new_cust[:m]) if new_cust else 0
        ytd_net = sum(net_rev[:m]) if net_rev else 0
        mo_adj = adjg[m - 1] if len(adjg) >= m else 0
        mo_orders = orders[m - 1] if len(orders) >= m else 0
        mo_new = new_cust[m - 1] if len(new_cust) >= m else 0
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Shopify YTD Adj Gross", _fmt_k(ytd_adj), f"{_fmt_n(ytd_orders)} orders")
        with c2:
            st.metric(f"Shopify {month_name} Adj Gross", _fmt_k(mo_adj), f"{_fmt_n(mo_orders)} orders")
        with c3:
            st.metric("YTD New Customers", _fmt_n(ytd_new), f"{month_name}: {_fmt_n(mo_new)}")
        with c4:
            st.metric("Shopify Net Rev YTD", _fmt_k(ytd_net), "after returns")

        # Row 3 — Meta Ads (current month)
        perf = mkt.get('perf_marketing_monthly', {}).get(str(m)) or mkt.get('perf_marketing_monthly', {}).get(m) or {}
        if perf:
            roas = perf.get('roas', 0) or 0
            cpa = perf.get('cpa', 0) or 0
            ctr = (perf.get('ctr', 0) or 0) * 100
            cpm = perf.get('cpm', 0) or 0
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric(f"ROAS ({month_name})", f"{roas:.2f}",
                          "Target: 4.0" + (" ✓" if roas >= 4 else " ✗"),
                          delta_color='normal' if roas >= 4 else 'inverse')
            with c2:
                st.metric(f"CPA ({month_name})", f"${cpa:.2f}",
                          "Target: $60" + (" ✓" if cpa <= 60 else " ✗"),
                          delta_color='normal' if cpa <= 60 else 'inverse')
            with c3:
                st.metric(f"CTR ({month_name})", f"{ctr:.1f}%",
                          "Target: 2%" + (" ✓" if ctr >= 2 else " ✗"),
                          delta_color='normal' if ctr >= 2 else 'inverse')
            with c4:
                st.metric(f"CPM ({month_name})", f"${cpm:.2f}", "Target ~$19 (2x golfer)")

    st.divider()


def show():
    """Display management dashboard — financial health in 60 seconds."""

    st.markdown('<div class="main-header">Management Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">2026 Financial Health — YTD Actuals + Forecast</div>',
        unsafe_allow_html=True
    )

    # ---------- data setup ----------
    team_members = st.session_state.get('team_members', [])
    opex_expenses = st.session_state.get('opex_expenses', [])
    wholesale_deals = st.session_state.get('wholesale_deals', [])

    df_forecast = generate_monthly_pl(
        year=2026,
        team_members=team_members,
        opex_expenses=opex_expenses,
        wholesale_deals=wholesale_deals,
        dtc_discount_rate=0.0,
        dtc_return_rate=0.0,
    )

    actuals = _get_2026_actuals_from_qbo()
    df_blended = _build_blended_2026(actuals, df_forecast)
    n_actual = actuals['n_months'] if actuals else 0

    # Pre-compute blended annual totals (used in multiple sections)
    annual_revenue = df_blended['Total Revenue'].sum()
    annual_cogs = df_blended['Total COGS'].sum()
    annual_gp = df_blended['Gross Profit'].sum()
    annual_opex = df_blended['Total OpEx'].sum()
    annual_ebitda = df_blended['EBITDA'].sum()
    gp_margin = (annual_gp / annual_revenue * 100) if annual_revenue > 0 else 0
    ebitda_margin = (annual_ebitda / annual_revenue * 100) if annual_revenue > 0 else 0

    # Pre-compute YTD actuals (used in multiple sections)
    ytd_actual_ebitda = 0
    avg_monthly_burn = 0
    net_cash = 0
    if actuals and n_actual > 0:
        ytd_actual_rev = sum(actuals['total_revenue'][:n_actual])
        ytd_actual_gp = sum(actuals['gross_profit'][:n_actual])
        ytd_actual_opex = sum(actuals['total_opex'][:n_actual])
        ytd_actual_ebitda = ytd_actual_gp - ytd_actual_opex
        avg_monthly_burn = abs(ytd_actual_ebitda / n_actual) if ytd_actual_ebitda < 0 else 0
        net_cash = actuals['latest_cash'] - actuals['latest_ap']

    # ================================================================
    # EXECUTIVE SUMMARY (mirrors Monthly Report page — auto-updates from
    # qbo_actuals + marketing_monthly.json each month)
    # ================================================================
    _render_executive_summary(actuals, n_actual)

    # ================================================================
    # ROW 1: CASH POSITION BANNER
    # ================================================================
    if actuals and n_actual > 0:
        latest_cash = actuals['latest_cash']
        latest_ap = actuals['latest_ap']

        # Days of cash calculations
        if avg_monthly_burn > 0:
            daily_burn = avg_monthly_burn / 30
            days_of_cash_net = int(net_cash / daily_burn) if net_cash > 0 else 0
            months_of_cash_net = round(net_cash / avg_monthly_burn, 1) if net_cash > 0 else 0
            days_of_cash_gross = int(latest_cash / daily_burn)
            months_of_cash_gross = round(latest_cash / avg_monthly_burn, 1)
        else:
            days_of_cash_net = 999
            months_of_cash_net = 99
            days_of_cash_gross = 999
            months_of_cash_gross = 99

        # Next month forecast burn (from blended)
        next_month_idx = n_actual  # 0-indexed, so this is the next forecast month
        next_month_burn = abs(df_blended['EBITDA'].iloc[next_month_idx]) if next_month_idx < 12 else 0
        next_month_name = MONTHS[next_month_idx] if next_month_idx < 12 else "N/A"

        st.caption(
            f"QBO actuals through **{MONTHS[n_actual-1]} 2026** | "
            f"Updated {st.session_state.get('qbo_actuals', {}).get('last_updated', 'N/A')}"
        )

        # First row: core cash metrics
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Current Cash Assets", f"${latest_cash:,.0f}")
        with c2:
            st.metric("Current Liabilities", f"${latest_ap:,.0f}")
        with c3:
            cash_label = "Available for operations" if net_cash > 0 else "Negative — action needed"
            st.metric("Net Cash Position", f"${net_cash:,.0f}")
            st.caption(cash_label)
        with c4:
            st.metric("Days of Cash (without investment)", f"{days_of_cash_net} days")

        # Second row: additional burn/runway metrics
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.metric("Days of Cash (excl. liabilities)", f"{days_of_cash_gross} days")
            st.caption(f"{months_of_cash_gross} months")
        with c6:
            st.metric(
                "Avg Monthly Burn (2026 Actuals)",
                f"${avg_monthly_burn:,.0f}",
                help=f"Average monthly EBITDA loss from {n_actual} months of actuals"
            )
        with c7:
            st.metric(
                f"Next Month Burn ({next_month_name})",
                f"${next_month_burn:,.0f}",
                help="Forecasted EBITDA loss for the next month"
            )
        with c8:
            # Placeholder for symmetry or additional metric
            opex_pct = (annual_opex / annual_revenue * 100) if annual_revenue > 0 else 0
            st.metric(
                "OpEx % of Revenue",
                f"{opex_pct:.0f}%",
                help="Full-year blended OpEx / Revenue"
            )

        st.divider()
    else:
        st.info("No QBO actuals loaded. Showing forecast only. Import via **QBO Import** page.")

    # ================================================================
    # SHOPIFY LIVE METRICS (YTD from Shopify API)
    # ================================================================
    shopify_data = None
    if shopify_configured():
        try:
            shopify_data = get_shopify_data(2026)
        except Exception as e:
            st.warning(f"Shopify data unavailable: {e}")

    if shopify_data:
        st.markdown("## Shopify Sales (Live YTD)")
        so = shopify_data['orders']
        inv = shopify_data['inventory']

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        # Adjusted Gross = Gross Sales − Discounts = subtotal_price (post-discount,
        # pre-tax/shipping/returns). Matches Matt's BI tool "Adjusted Gross (calc'd)"
        # hero column. Gifting orders have $0 Adjusted Gross by definition.
        dtc = so['channel'].get('DTC', {})
        gift = so['channel'].get('Gifting', {})
        ws = so['channel'].get('Wholesale', {})
        dtc_units_combined = dtc.get('units', 0) + gift.get('units', 0)
        dtc_orders_combined = dtc.get('orders', 0) + gift.get('orders', 0)
        dtc_adjg_combined = dtc.get('net', 0) + gift.get('net', 0)  # gift.net == 0
        with c1:
            st.metric("Units Sold (Total)", f"{so['total_units']:,}")
        with c2:
            st.metric("Units Sold (DTC)", f"{dtc_units_combined:,}",
                      help="Includes Gifting (seeded $0-payment) orders")
            st.caption(f"{dtc_orders_combined} orders (incl. {gift.get('orders', 0)} gifting)")
        with c3:
            st.metric("Units Sold (Wholesale)", f"{ws.get('units', 0):,}")
            st.caption(f"{ws.get('orders', 0)} orders")
        with c4:
            st.metric("DTC Adjusted Gross", f"${dtc_adjg_combined:,.0f}",
                      help="Gross Sales − Discounts (pre-tax, pre-shipping, pre-returns). Matches Matt's reporting hero metric.")
        with c5:
            st.metric("Wholesale Adjusted Gross", f"${ws.get('net', 0):,.0f}")
        with c6:
            st.metric("Inventory on Hand", f"{inv['total_units']:,}")
            st.caption(f"{inv['in_stock']} of {inv['total_products']} SKUs in stock")

        # ---- Monthly Adjusted Gross by Channel chart ----
        # Adjusted Gross = subtotal_price (Gross Sales - Discounts, pre-tax/shipping/returns).
        # Matches Matt's BI tool hero metric.
        months_with_data = [m for m in so['monthly'] if m['orders'] > 0]
        if months_with_data:
            m_df = pd.DataFrame(months_with_data)
            totals = m_df['dtc_net'] + m_df['ws_net']

            fig_shop = go.Figure()
            fig_shop.add_trace(go.Bar(
                name='DTC Adj Gross', x=m_df['month_name'], y=m_df['dtc_net'],
                marker_color=ACCENT_BLUE,
            ))
            fig_shop.add_trace(go.Bar(
                name='Wholesale Adj Gross', x=m_df['month_name'], y=m_df['ws_net'],
                marker_color=ACCENT_PURPLE,
            ))
            # Column-top totals (DTC + Wholesale)
            fig_shop.add_trace(go.Scatter(
                x=m_df['month_name'], y=totals,
                mode='text',
                text=[f"${v:,.0f}" for v in totals],
                textposition='top center',
                textfont=dict(size=12, color='#111'),
                showlegend=False,
                hoverinfo='skip',
            ))
            fig_shop.update_layout(
                title='Monthly Adjusted Gross by Channel',
                barmode='stack', height=320, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis_tickformat='$,.0f', margin=dict(t=60, b=30),
                yaxis=dict(range=[0, float(totals.max()) * 1.15]) if len(totals) else None,
            )
            st.plotly_chart(fig_shop, use_container_width=True)

        # ---- Last 7 days vs prior 7 days ----
        if so['daily']:
            from datetime import date, timedelta as td
            today = date.today()
            # Last 7 full days = yesterday back 7 days
            end_recent = today - td(days=1)
            start_recent = end_recent - td(days=6)
            end_prior = start_recent - td(days=1)
            start_prior = end_prior - td(days=6)

            def _sum_period(daily, start, end):
                dtc_units = 0; ws_units = 0; dtc_net = 0; ws_net = 0; orders = 0
                # We need order-level data for channel split; use daily totals as proxy
                # Recompute from raw orders in shopify_data
                return None  # Will use order-level below

            # Recompute from raw order analysis monthly data — but we need daily
            # channel split. Let's compute from the daily + monthly data.
            # Better: iterate orders directly from the cached data
            import shopify_client as sc
            all_orders = None
            try:
                cache_key = 'shopify_raw_orders_2026'
                if cache_key in st.session_state:
                    all_orders = st.session_state[cache_key]
                else:
                    all_orders = sc.fetch_orders_ytd(2026)
                    st.session_state[cache_key] = all_orders
            except Exception:
                pass

            if all_orders:
                def _period_stats(orders_list, start_dt, end_dt):
                    # Net Revenue = subtotal_price (dollars paid for product, pre-tax/shipping).
                    # Gifting orders have $0 net by definition; we still count their units in
                    # DTC unit totals because they ARE units shipped, but they add $0 to revenue.
                    stats = {'dtc_units': 0, 'ws_units': 0,
                             'dtc_net': 0, 'ws_net': 0,
                             'gift_units': 0, 'orders': 0}
                    for o in orders_list:
                        created = o.get('created_at', '')[:10]
                        if not created:
                            continue
                        try:
                            od = date.fromisoformat(created)
                        except ValueError:
                            continue
                        if od < start_dt or od > end_dt:
                            continue
                        stats['orders'] += 1
                        otype = sc.classify_order(o)
                        units = sum(li.get('quantity', 0) for li in o.get('line_items', []))
                        net = float(o.get('subtotal_price', 0) or 0)
                        if otype == 'DTC':
                            stats['dtc_units'] += units
                            stats['dtc_net'] += net
                        elif otype == 'Wholesale':
                            stats['ws_units'] += units
                            stats['ws_net'] += net
                        else:
                            # Gifting: net is $0 by definition (100% discount). Roll units into DTC.
                            stats['gift_units'] += units
                            stats['dtc_units'] += units
                    return stats

                recent = _period_stats(all_orders, start_recent, end_recent)
                prior = _period_stats(all_orders, start_prior, end_prior)

                st.markdown(
                    f"#### Last 7 Days ({start_recent.strftime('%b %d')} – {end_recent.strftime('%b %d')}) "
                    f"vs Prior 7 Days ({start_prior.strftime('%b %d')} – {end_prior.strftime('%b %d')})"
                )

                def _delta_str_units(val):
                    """Format unit delta: '+12 vs prior 7d' or '-37 vs prior 7d'"""
                    return f"{val:+,} vs prior 7d"

                def _delta_str_rev(val):
                    """Format revenue delta with sign before $: '+$1,234' or '-$5,678'"""
                    sign = '+' if val >= 0 else '-'
                    return f"{sign}${abs(val):,.0f} vs prior 7d"

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    delta_u = recent['dtc_units'] - prior['dtc_units']
                    st.metric("DTC Units", f"{recent['dtc_units']:,}",
                              delta=_delta_str_units(delta_u),
                              delta_color="normal")
                with c2:
                    delta_r = recent['dtc_net'] - prior['dtc_net']
                    st.metric("DTC Adjusted Gross", f"${recent['dtc_net']:,.0f}",
                              delta=_delta_str_rev(delta_r),
                              delta_color="normal")
                with c3:
                    delta_wu = recent['ws_units'] - prior['ws_units']
                    st.metric("Wholesale Units", f"{recent['ws_units']:,}",
                              delta=_delta_str_units(delta_wu),
                              delta_color="normal")
                with c4:
                    delta_wr = recent['ws_net'] - prior['ws_net']
                    st.metric("Wholesale Adjusted Gross", f"${recent['ws_net']:,.0f}",
                              delta=_delta_str_rev(delta_wr),
                              delta_color="normal")

        st.divider()

    # ================================================================
    # ROW 2: KEY RATIOS
    # ================================================================
    st.markdown("## Key Ratios")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gross Margin", f"{gp_margin:.1f}%",
                  help="(Revenue - COGS) / Revenue — blended year")
    with col2:
        opex_pct_r = (annual_opex / annual_revenue * 100) if annual_revenue > 0 else 0
        st.metric("OpEx % of Revenue", f"{opex_pct_r:.1f}%",
                  help="Total OpEx / Revenue — blended year")
    with col3:
        st.metric("EBITDA Margin", f"{ebitda_margin:.1f}%",
                  delta_color="normal" if ebitda_margin >= 0 else "inverse")
    with col4:
        if n_actual > 0 and avg_monthly_burn > 0:
            st.metric("Monthly Burn Rate (Actual)", f"${avg_monthly_burn:,.0f}",
                      help=f"Avg monthly EBITDA loss from {n_actual} months of actuals")
        else:
            fc_burn = abs(annual_ebitda / 12) if annual_ebitda < 0 else 0
            st.metric("Monthly Burn Rate (Est)", f"${fc_burn:,.0f}")

    st.divider()

    # ================================================================
    # CASH RUNWAY PROJECTION (with $1M SAFE closing October)
    # ================================================================
    if actuals and n_actual > 0:
        st.divider()
        st.markdown("## Cash Runway Projection")
        st.caption(
            "Projection assumes a **$1M SAFE note closes in October**. "
            "Both scenarios (with and without the raise) are shown."
        )

        cash_hist = actuals.get('cash_history', {})
        actual_cash = [cash_hist.get(f'2026_{m}', None) for m in range(1, n_actual + 1)]
        actual_cash = [c for c in actual_cash if c is not None]

        # Baseline projection (no new capital)
        projected_no_safe = [net_cash]
        for m in range(n_actual, 12):
            projected_no_safe.append(projected_no_safe[-1] + df_blended['EBITDA'].iloc[m])

        # With $1M SAFE in October (Oct = index 9)
        SAFE_AMOUNT = 1_000_000
        SAFE_MONTH_IDX = 9  # October (0-indexed)
        projected_with_safe = [net_cash]
        for m in range(n_actual, 12):
            step = projected_with_safe[-1] + df_blended['EBITDA'].iloc[m]
            if m == SAFE_MONTH_IDX:
                step += SAFE_AMOUNT
            projected_with_safe.append(step)

        fig_cash = go.Figure()
        if actual_cash:
            fig_cash.add_trace(go.Scatter(
                x=MONTHS[:len(actual_cash)], y=actual_cash,
                mode='lines+markers', name='Actual Cash',
                line=dict(color=ACTUAL_COLOR, width=3), marker=dict(size=8),
            ))
        proj_months = MONTHS[n_actual - 1:12]
        fig_cash.add_trace(go.Scatter(
            x=proj_months, y=projected_no_safe,
            mode='lines+markers', name='Projected — no new capital',
            line=dict(color=FORECAST_COLOR, width=2, dash='dash'), marker=dict(size=6),
        ))
        fig_cash.add_trace(go.Scatter(
            x=proj_months, y=projected_with_safe,
            mode='lines+markers', name='Projected — with $1M SAFE (Oct)',
            line=dict(color=POSITIVE_COLOR, width=2.5), marker=dict(size=7),
        ))
        fig_cash.add_hline(y=0, line_dash="dot", line_color="red",
                           annotation_text="Zero Cash", annotation_position="bottom right")
        fig_cash.update_layout(
            height=380, showlegend=True,
            yaxis_title="Cash ($)", yaxis_tickformat="$,.0f",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_cash, use_container_width=True)

        # End-year comparison + break points
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("End-Dec (no SAFE)", f"${projected_no_safe[-1]:,.0f}")
        with c2:
            st.metric("End-Dec (with SAFE)", f"${projected_with_safe[-1]:,.0f}",
                      delta=f"+${SAFE_AMOUNT:,.0f} raise")
        with c3:
            zero_month = next(
                (proj_months[i] for i, v in enumerate(projected_no_safe) if v <= 0),
                None
            )
            st.metric("Zero-cash month (no SAFE)", zero_month if zero_month else "Not reached in 2026")

    # ================================================================
    # BLENDED P&L SUMMARY TABLE
    # ================================================================
    st.divider()
    st.markdown("## 2026 Blended P&L")

    display_df = df_blended.copy()
    for col in ['DTC Revenue', 'Wholesale Revenue', 'Total Revenue',
                'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']:
        display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")

    st.dataframe(
        display_df[['Month', 'Source', 'Total Revenue', 'Total COGS',
                     'Gross Profit', 'Total OpEx', 'EBITDA']],
        use_container_width=True, hide_index=True,
    )

    st.markdown(
        f"**Full Year (Blended):** Revenue ${annual_revenue:,.0f} | "
        f"Gross Profit ${annual_gp:,.0f} ({gp_margin:.0f}%) | "
        f"OpEx ${annual_opex:,.0f} | "
        f"EBITDA ${annual_ebitda:,.0f} ({ebitda_margin:.0f}%)"
    )

    # ================================================================
    # DATA SOURCES FOOTER
    # ================================================================
    st.divider()
    with st.expander("Data Sources & Notes"):
        if n_actual > 0:
            st.write(f"**Actual months:** Jan-{MONTHS[n_actual-1]} 2026 from QuickBooks Online")
            st.write(f"**Forecast months:** {MONTHS[n_actual]}-Dec 2026 from model assumptions")
        else:
            st.write("**All months:** Forecast from model assumptions")
        st.write(f"**Team members:** {len(team_members)}")
        st.write(f"**OpEx items:** {len(opex_expenses)}")
        st.write(f"**Wholesale deals:** {len(wholesale_deals)}")
        st.caption("Tip: Import latest QBO data via the **QBO Import** page to update actuals.")
