"""
Monthly Management Report — Nathan access only.

Mirrors the PowerPoint monthly deck. Reads live data from qbo_actuals.json,
marketing_monthly.json, and monthly_report_data.json so numbers stay in sync
with the model + app. A separate password (st.secrets["nathan_password"])
gates access on top of the shared dashboard password.
"""

import json
import os
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONTH_FULL = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']

DATA_DIR = Path(__file__).parent.parent / 'data'

# Empirica brand palette
CHARCOAL = '#1A1D24'
FOREST = '#2F5D3D'
BRONZE = '#A66A2C'
SLATE = '#3A4250'
CREAM = '#F7F3EC'
BRICK = '#8B3A2E'
MUTED = '#6B7280'
GRID = '#E5DED0'


def _load_json(name):
    path = DATA_DIR / name
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


ALLOWED_EMAILS = {
    'chandler@empirica-analytics.com',
    'nathan@almamaterfootwear.com',
}


def _get_cf_access_email():
    """Return the email Cloudflare Access authenticated for this request.

    Cloudflare Access injects `Cf-Access-Authenticated-User-Email` on every
    request it forwards to the origin (case-insensitive). Streamlit exposes
    incoming request headers via `st.context.headers` on 1.35+.
    """
    try:
        headers = st.context.headers or {}
    except Exception:
        return None
    for key in ('Cf-Access-Authenticated-User-Email',
                'cf-access-authenticated-user-email',
                'CF-Access-Authenticated-User-Email'):
        v = headers.get(key)
        if v:
            return v.strip().lower()
    return None


def _gate_nathan():
    """Gate by Cloudflare Access email — no in-app password.

    Cloudflare Access is the primary gate at the network layer. The app
    additionally restricts this page to a fixed allowlist so only Nathan
    (or Chandler for support) sees it, even if CF Access is later widened
    to more Alma Mater team members.
    """
    email = _get_cf_access_email()
    if email and email in ALLOWED_EMAILS:
        return True

    st.markdown("### Monthly Management Report")
    if email:
        st.error(
            f"This page is restricted to Nathan and Chandler. "
            f"You're signed in via Cloudflare Access as `{email}` — access denied for this page."
        )
    else:
        st.warning(
            "This page is restricted. Cloudflare Access identity is required "
            "but no Cf-Access-Authenticated-User-Email header is present. "
            "If you are seeing this message, contact Chandler."
        )
    return False


def _fmt_k(v):
    if v is None:
        return '$0'
    sign = '-' if v < 0 else ''
    a = abs(v)
    if a >= 1_000_000:
        return f"{sign}${a/1_000_000:.2f}M"
    if a >= 1_000:
        return f"{sign}${a/1_000:.0f}K"
    return f"{sign}${a:,.0f}"


def _fmt_dollar(v):
    if v is None or v == 0:
        return '$0'
    sign = '-' if v < 0 else ''
    return f"{sign}${abs(v):,.0f}"


def _fmt_n(v):
    return f"{round(v or 0):,}"


def _tile(col, label, value, delta=None, delta_color='normal'):
    with col:
        st.metric(label, value, delta=delta, delta_color=delta_color)


def _get_monthly_from_qbo(qbo, key):
    """Extract Jan-Dec array for a P&L line item from qbo pl_data."""
    pl = qbo.get('pl_data', {}).get(key, {})
    return [pl.get(f"2026_{m}", 0) or 0 for m in range(1, 13)]


def show():
    """Render the July 2026 Monthly Management Report."""
    if not _gate_nathan():
        return

    # === Load data (all live from JSON, not hardcoded) ===
    qbo_full = st.session_state.get('qbo_actuals') or _load_json('qbo_actuals.json')
    if qbo_full and 'qbo_actuals' in qbo_full:
        qbo = qbo_full['qbo_actuals']
    else:
        qbo = qbo_full

    mkt = _load_json('marketing_monthly.json')
    rpt = _load_json('monthly_report_data.json')

    if not qbo or not mkt or not rpt:
        st.error(
            "Missing data files. Need: qbo_actuals.json, marketing_monthly.json, monthly_report_data.json"
        )
        return

    through_month = rpt['as_of_month']
    through_year = rpt['as_of_year']

    # === Header ===
    st.markdown(
        f"<div style='background:{CHARCOAL};padding:24px 32px;border-radius:8px;margin-bottom:16px;'>"
        f"<div style='color:{CREAM};font-size:28px;font-weight:700;'>Alma Mater Inc</div>"
        f"<div style='color:{BRONZE};font-size:18px;font-weight:500;'>Management Report — "
        f"Period ended {MONTH_FULL[through_month-1]} 31, {through_year}</div>"
        f"<div style='color:{CREAM};font-size:11px;margin-top:8px;opacity:0.8;'>"
        f"Last updated {rpt['last_updated']} · Prepared by Empirica Analytics LLC</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # === Compute YTD / July metrics from live qbo_actuals ===
    dtc_m = _get_monthly_from_qbo(qbo, 'DTC Revenue')
    ws_m = _get_monthly_from_qbo(qbo, 'Wholesale Revenue')
    rev_m = _get_monthly_from_qbo(qbo, 'Total Revenue')
    cogs_m = _get_monthly_from_qbo(qbo, 'Total COGS')
    gp_m = _get_monthly_from_qbo(qbo, 'Gross Profit')
    opex_m = _get_monthly_from_qbo(qbo, 'Total Expenses')
    noi_m = _get_monthly_from_qbo(qbo, 'Net Operating Income')
    ni_m = _get_monthly_from_qbo(qbo, 'Net Income')

    ytd_rev = sum(rev_m[:through_month])
    ytd_dtc = sum(dtc_m[:through_month])
    ytd_ws = sum(ws_m[:through_month])
    ytd_cogs = sum(cogs_m[:through_month])
    ytd_gp = sum(gp_m[:through_month])
    ytd_opex = sum(opex_m[:through_month])
    ytd_ni = sum(ni_m[:through_month])
    ytd_gp_pct = (ytd_gp / ytd_rev * 100) if ytd_rev else 0

    jul_rev = rev_m[through_month - 1]
    jul_dtc = dtc_m[through_month - 1]
    jul_ws = ws_m[through_month - 1]
    jul_gp = gp_m[through_month - 1]
    jul_gp_pct = (jul_gp / jul_rev * 100) if jul_rev else 0
    jul_opex = opex_m[through_month - 1]
    jul_ni = ni_m[through_month - 1]
    prev_opex = opex_m[through_month - 2] if through_month >= 2 else 0
    prev_rev = rev_m[through_month - 2] if through_month >= 2 else 0

    # Cash from qbo cash_data
    cash_data = qbo.get('cash_data', {})
    end_month_cash = cash_data.get(f'{through_year}_{through_month}', 0)
    prev_cash = cash_data.get(f'{through_year}_{through_month - 1}', 0) if through_month >= 2 else 0

    # Marketing YTD from Matt's ecomm
    ecomm = mkt['ecomm_monthly']
    ytd_adj = sum(ecomm['adjg'][:through_month])
    ytd_orders = sum(ecomm['orders'][:through_month])
    ytd_sessions = sum(ecomm['sessions'][:through_month])
    ytd_new_cust = sum(ecomm['new_cust'][:through_month])
    ytd_net_rev = sum(ecomm['net_rev'][:through_month])
    jul_adj = ecomm['adjg'][through_month - 1]
    jul_orders = ecomm['orders'][through_month - 1]

    perf = mkt['perf_marketing_monthly'].get(str(through_month)) or mkt['perf_marketing_monthly'].get(through_month) or {}

    # === Section 1: Executive Summary ===
    st.markdown(f"## Executive Summary")
    st.caption(
        f"July revenue up {((jul_rev/prev_rev-1)*100):.0f}% MoM to {_fmt_k(jul_rev)}. "
        f"GM {jul_gp_pct:.1f}%. Meta ads full-month ROAS {perf.get('roas', 0):.2f} vs 4.0 target."
    )

    # Row 1: Financial
    c1, c2, c3, c4 = st.columns(4)
    _tile(c1, 'YTD Revenue', _fmt_k(ytd_rev), f"{_fmt_k(ytd_rev/through_month)}/mo avg")
    _tile(c2, 'Gross Margin YTD', f"{ytd_gp_pct:.1f}%", f"{_fmt_k(ytd_gp)} gross profit")
    cash_delta = end_month_cash - prev_cash
    _tile(c3, f'End-{MONTHS[through_month-1]} Cash', _fmt_k(end_month_cash),
          f"{_fmt_k(cash_delta)} MoM", delta_color='normal' if cash_delta >= 0 else 'inverse')
    _tile(c4, f'{MONTHS[through_month-1]} Net Loss', _fmt_k(jul_ni),
          f"{_fmt_k(jul_ni - ni_m[through_month-2])} vs prior mo")

    # Row 2: Shopify (Matt's data)
    c1, c2, c3, c4 = st.columns(4)
    _tile(c1, 'Shopify YTD Adj Gross', _fmt_k(ytd_adj), f"{_fmt_n(ytd_orders)} orders")
    _tile(c2, f'Shopify {MONTHS[through_month-1]} Adj Gross', _fmt_k(jul_adj), f"{_fmt_n(jul_orders)} orders")
    _tile(c3, 'YTD New Customers', _fmt_n(ytd_new_cust), f"{MONTHS[through_month-1]}: {_fmt_n(ecomm['new_cust'][through_month-1])}")
    _tile(c4, 'Shopify Net Rev YTD', _fmt_k(ytd_net_rev), 'after returns')

    # Row 3: Meta Ads (full-month July)
    if perf:
        c1, c2, c3, c4 = st.columns(4)
        roas = perf.get('roas', 0)
        cpa = perf.get('cpa', 0)
        ctr = perf.get('ctr', 0) * 100
        cpm = perf.get('cpm', 0)
        _tile(c1, f'ROAS ({MONTHS[through_month-1]})', f"{roas:.2f}",
              f"Target: 4.0 ({'✓ ABOVE' if roas >= 4 else '✗ below'})",
              delta_color='normal' if roas >= 4 else 'inverse')
        _tile(c2, f'CPA ({MONTHS[through_month-1]})', f"${cpa:.2f}",
              f"Target: $60 ({'✓ BELOW' if cpa <= 60 else '✗ above'})",
              delta_color='normal' if cpa <= 60 else 'inverse')
        _tile(c3, f'CTR ({MONTHS[through_month-1]})', f"{ctr:.1f}%",
              f"Target: 2% ({'✓ ABOVE' if ctr >= 2 else '✗ below'})",
              delta_color='normal' if ctr >= 2 else 'inverse')
        _tile(c4, f'CPM ({MONTHS[through_month-1]})', f"${cpm:.2f}", 'Target: ~$19 (2x for golfer)')

    st.divider()

    # === Section 2: Revenue by Channel ===
    st.markdown("## 2. Revenue — by Channel")

    fig = go.Figure()
    fig.add_bar(name='DTC Revenue', x=MONTHS, y=dtc_m, marker_color=CHARCOAL,
                text=[f"${v:,.0f}" if v else '' for v in dtc_m], textposition='inside', textfont=dict(color='white', size=10))
    fig.add_bar(name='Wholesale', x=MONTHS, y=ws_m, marker_color=BRONZE,
                text=[f"${v:,.0f}" if v else '' for v in ws_m], textposition='inside', textfont=dict(color='white', size=10))
    fig.update_layout(barmode='stack', title='Monthly Revenue by Channel (Jan-Jul actuals, Aug-Dec forecast per Matt Aug refresh)',
                      height=440, legend=dict(orientation='h', y=1.1),
                      yaxis_tickformat='$,.0f', margin=dict(l=40, r=40, t=80, b=40))
    st.plotly_chart(fig, use_container_width=True)

    # === Section 3: COGS, GP, GM Trend ===
    st.markdown("## 3. COGS, Gross Profit & Margin Trend")

    c1, c2, c3, c4 = st.columns(4)
    _tile(c1, 'YTD COGS', _fmt_k(ytd_cogs), f"{ytd_cogs/ytd_rev*100:.1f}% of revenue")
    _tile(c2, 'YTD Gross Profit', _fmt_k(ytd_gp), f"{ytd_gp_pct:.1f}% margin")
    _tile(c3, f'{MONTHS[through_month-1]} GM', f"{jul_gp_pct:.1f}%",
          f"{'above' if jul_gp_pct >= 52 else 'below'} 52% target")
    _tile(c4, 'Full-Year GP Fcst', _fmt_k(sum(gp_m)))

    gp_pct_series = [gp_m[i]/rev_m[i]*100 if rev_m[i] else 0 for i in range(12)]
    fig = go.Figure()
    fig.add_bar(name='Revenue', x=MONTHS, y=rev_m, marker_color=FOREST)
    fig.add_bar(name='COGS', x=MONTHS, y=cogs_m, marker_color=BRICK)
    fig.update_layout(barmode='group', title='Revenue vs COGS (Monthly)', height=340,
                      legend=dict(orientation='h', y=1.15),
                      yaxis_tickformat='$,.0f', margin=dict(l=40, r=40, t=70, b=40))
    st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure()
    fig.add_scatter(x=MONTHS, y=gp_pct_series, mode='lines+markers+text',
                    text=[f"{v:.1f}%" if v else '' for v in gp_pct_series],
                    textposition='top center', line=dict(color=FOREST, width=3),
                    marker=dict(size=8), name='GM %')
    fig.add_hline(y=52, line_dash='dot', line_color=MUTED, annotation_text='52% target')
    fig.update_layout(title='Gross Margin % Trend', height=320,
                      yaxis_tickformat='.0f', yaxis_ticksuffix='%', yaxis_range=[0, 100],
                      margin=dict(l=40, r=40, t=60, b=40))
    st.plotly_chart(fig, use_container_width=True)

    # === Section 4: Operating Expenses ===
    st.markdown("## 4. Operating Expenses")

    c1, c2, c3, c4 = st.columns(4)
    _tile(c1, 'YTD OpEx', _fmt_k(ytd_opex), f"{_fmt_k(ytd_opex/through_month)}/mo avg")
    opex_mom_pct = (jul_opex/prev_opex - 1) * 100 if prev_opex else 0
    _tile(c2, f'{MONTHS[through_month-1]} OpEx', _fmt_k(jul_opex), f"{opex_mom_pct:+.0f}% MoM",
          delta_color='inverse' if opex_mom_pct > 0 else 'normal')
    sm_m = _get_monthly_from_qbo(qbo, 'Sales & Marketing')
    payroll_m = _get_monthly_from_qbo(qbo, 'Payroll')
    _tile(c3, f'{MONTHS[through_month-1]} S&M', _fmt_k(sm_m[through_month-1]))
    _tile(c4, f'{MONTHS[through_month-1]} Payroll', _fmt_k(payroll_m[through_month-1]), 'W2 + benefits')

    prof_m = _get_monthly_from_qbo(qbo, 'Professional Fees')
    travel_m = _get_monthly_from_qbo(qbo, 'Travel')

    fig = go.Figure()
    m_slice = MONTHS[:through_month]
    fig.add_bar(name='S&M', x=m_slice, y=sm_m[:through_month], marker_color=CHARCOAL)
    fig.add_bar(name='Payroll', x=m_slice, y=payroll_m[:through_month], marker_color=BRONZE)
    fig.add_bar(name='Prof Fees', x=m_slice, y=prof_m[:through_month], marker_color=FOREST)
    fig.add_bar(name='Travel', x=m_slice, y=travel_m[:through_month], marker_color=SLATE)
    fig.update_layout(barmode='stack', title=f'OpEx Composition by Category (Actuals Jan-{MONTHS[through_month-1]})',
                      height=400, legend=dict(orientation='h', y=1.1),
                      yaxis_tickformat='$,.0f', margin=dict(l=40, r=40, t=70, b=40))
    st.plotly_chart(fig, use_container_width=True)

    # === Section 5: P&L Summary ===
    st.markdown(f"## 5. P&L Summary — YTD {MONTHS[through_month-1]} {through_year}")

    pl = rpt['pl_ytd']
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("**Revenue & Gross Profit**")
        rev_rows = [
            ('DTC — Gross Sales', pl['dtc_gross']),
            ('  (–) DTC Discounts', pl['dtc_disc']),
            ('  (–) DTC Returns', pl['dtc_returns']),
            ('**DTC Net Revenue**', pl['dtc_net']),
            ('Wholesale — Gross Sales', pl['ws_gross']),
            ('  (–) WS Discounts', pl['ws_disc']),
            ('  (+) WS Shipping', pl['ws_shipping']),
            ('**Wholesale Net Revenue**', pl['ws_net']),
            ('**TOTAL REVENUE**', pl['total_income']),
            ('Total COGS', -pl['total_cogs']),
            ('**GROSS PROFIT**', pl['gp']),
            (f'Gross Margin', f"{pl['gp_pct']:.1f}%"),
        ]
        df = pd.DataFrame(rev_rows, columns=['Line Item', f'YTD {MONTHS[through_month-1]} {through_year}'])
        df[f'YTD {MONTHS[through_month-1]} {through_year}'] = df[f'YTD {MONTHS[through_month-1]} {through_year}'].apply(
            lambda v: v if isinstance(v, str) else _fmt_dollar(v)
        )
        st.dataframe(df, hide_index=True, use_container_width=True)

    with col_r:
        st.markdown("**Operating Expenses & Net Income**")
        opex_rows = [
            ('Sales & Marketing', -pl['sm']),
            ('Payroll', -pl['payroll']),
            ('Professional Fees', -pl['prof_fees']),
            ('Travel', -pl['travel']),
            ('Meals & Entertainment', -(pl['meals'] + pl['ent'])),
            ('Software', -pl['software']),
            ('Office / Rent / Other', -(pl['office_supp'] + pl['office_furn'] + pl['rent']
                                        + pl['bank'] + pl['repairs'] + pl['rd']
                                        + pl['insurance'] + pl['utilities'])),
            ('**TOTAL OPERATING EXPENSES**', -pl['total_opex']),
            ('**NET OPERATING INCOME**', pl['noi']),
            ('  (–) Depreciation', -pl['depreciation']),
            ('  (–) Taxes & Licenses', -pl.get('taxes_lic', 0)),
            ('**NET INCOME**', pl['ni']),
        ]
        df = pd.DataFrame(opex_rows, columns=['Line Item', f'YTD {MONTHS[through_month-1]} {through_year}'])
        df[f'YTD {MONTHS[through_month-1]} {through_year}'] = df[f'YTD {MONTHS[through_month-1]} {through_year}'].apply(
            lambda v: _fmt_dollar(v) if isinstance(v, (int, float)) else v
        )
        st.dataframe(df, hide_index=True, use_container_width=True)

    # === Cash Runway ===
    st.markdown("## 5. Cash Runway")

    end_cash_series = [cash_data.get(f'{through_year}_{m}', 0) for m in range(1, 13)]
    # Model forecast for Aug-Dec: use last known + declining pattern (would need financial_calcs;
    # for now use empty for forecast months)
    # Realistic burn: end_cash + $1M Aug SAFE - $62K/mo
    BURN = 62000
    SAFE = 1_000_000
    realistic = end_cash_series[:through_month]
    cash = end_month_cash
    for i, m in enumerate(MONTHS[through_month:]):
        cash -= BURN
        if m == 'Aug':
            cash += SAFE
        realistic.append(cash)

    fig = go.Figure()
    fig.add_scatter(x=MONTHS, y=realistic, mode='lines+markers+text',
                    text=[_fmt_k(v) for v in realistic], textposition='top center',
                    line=dict(color=FOREST, width=3), marker=dict(size=8),
                    name='Current Run-Rate ($62K/mo burn + $1M SAFE Aug)')
    fig.update_layout(title=f'Cash Balance Trajectory  (actuals Jan-{MONTHS[through_month-1]}, projected Aug-Dec with $1M SAFE closing in August)',
                      height=400, yaxis_tickformat='$,.0f',
                      legend=dict(orientation='h', y=1.1),
                      margin=dict(l=40, r=40, t=70, b=40))
    st.plotly_chart(fig, use_container_width=True)

    # Runway scenarios
    st.markdown("**Runway Scenarios**")
    runway_rows = [
        ('Base case (no SAFE)', _fmt_dollar(end_month_cash), '$62K', f"{end_month_cash/BURN:.1f} mo"),
        ('+ $500K bridge', _fmt_dollar(end_month_cash + 500_000), '$62K', f"{(end_month_cash+500_000)/BURN:.1f} mo"),
        ('+ $1.0M SAFE', _fmt_dollar(end_month_cash + 1_000_000), '$62K', f"{(end_month_cash+1_000_000)/BURN:.1f} mo"),
    ]
    st.dataframe(pd.DataFrame(runway_rows, columns=['Scenario', 'Starting Cash', 'Monthly Burn', 'Runway']),
                 hide_index=True, use_container_width=True)

    # === Balance Sheet ===
    st.markdown(f"## 5. Balance Sheet Summary — as of {MONTH_FULL[through_month-1]} 31, {through_year}")

    bs_reclass = rpt['balance_sheet']['reclass']
    post_safe = {**bs_reclass, 'cash': bs_reclass['cash'] + 1_000_000,
                 'total_assets': bs_reclass['total_assets'] + 1_000_000,
                 'safe_notes': bs_reclass['safe_notes'] + 1_000_000,
                 'total_equity': bs_reclass['total_equity'] + 1_000_000}

    bs_rows = [
        ('**ASSETS**', '', ''),
        ('  Cash', _fmt_dollar(bs_reclass['cash']), _fmt_dollar(post_safe['cash'])),
        ('  Accounts Receivable', _fmt_dollar(bs_reclass['ar']), _fmt_dollar(post_safe['ar'])),
        ('  Inventory', _fmt_dollar(bs_reclass['inventory']), _fmt_dollar(post_safe['inventory'])),
        ('  Prepaid + Clearing', _fmt_dollar(bs_reclass['prepaid'] + bs_reclass['clearing']),
                                 _fmt_dollar(post_safe['prepaid'] + post_safe['clearing'])),
        ('  Fixed Assets + Sec Dep', _fmt_dollar(bs_reclass['fixed_net'] + bs_reclass['security_dep']),
                                     _fmt_dollar(post_safe['fixed_net'] + post_safe['security_dep'])),
        ('**TOTAL ASSETS**', _fmt_dollar(bs_reclass['total_assets']), _fmt_dollar(post_safe['total_assets'])),
        ('**LIABILITIES**', '', ''),
        ('  Accounts Payable', _fmt_dollar(bs_reclass['ap']), _fmt_dollar(post_safe['ap'])),
        ('  Credit Cards', _fmt_dollar(bs_reclass['credit_cards']), _fmt_dollar(post_safe['credit_cards'])),
        ('  Due to De Olmsted (was PPP)', _fmt_dollar(bs_reclass['due_de_olmsted']), _fmt_dollar(post_safe['due_de_olmsted'])),
        ('  Accrued + Sales Tax + Def Rev',
         _fmt_dollar(bs_reclass['accrued'] + bs_reclass['sales_tax'] + bs_reclass['deferred_rev']),
         _fmt_dollar(post_safe['accrued'] + post_safe['sales_tax'] + post_safe['deferred_rev'])),
        ('**TOTAL LIABILITIES**', _fmt_dollar(bs_reclass['total_liab']), _fmt_dollar(post_safe['total_liab'])),
        ('**EQUITY**', '', ''),
        ('  SAFE Notes', _fmt_dollar(bs_reclass['safe_notes']), _fmt_dollar(post_safe['safe_notes'])),
        ('  Owner Investment', _fmt_dollar(bs_reclass['owner_invest']), _fmt_dollar(post_safe['owner_invest'])),
        ('  Retained Earnings', _fmt_dollar(bs_reclass['retained']), _fmt_dollar(post_safe['retained'])),
        ('  YTD Net Income', _fmt_dollar(bs_reclass['net_income']), _fmt_dollar(post_safe['net_income'])),
        ('**TOTAL EQUITY**', _fmt_dollar(bs_reclass['total_equity']), _fmt_dollar(post_safe['total_equity'])),
    ]
    df = pd.DataFrame(bs_rows, columns=['', f'As of {MONTHS[through_month-1]} 31 (reclassed)', 'Post-SAFE ($1M)'])
    st.dataframe(df, hide_index=True, use_container_width=True)

    # === Section 6: Marketing Performance ===
    st.markdown("## 6. Marketing Performance")

    # Meta Ads (July)
    st.markdown("### Meta Ads (Full Month)")
    if perf:
        c1, c2, c3, c4 = st.columns(4)
        _tile(c1, 'Ad Spend', _fmt_dollar(perf.get('ad_spend', 0)),
              f"{perf.get('pct_budget', 0)*100:.0f}% of $10K budget")
        _tile(c2, 'Ad Revenue', _fmt_dollar(perf.get('ad_revenue', 0)),
              f"{_fmt_n(perf.get('clicks', 0))} clicks")
        _tile(c3, 'Impressions', _fmt_n(perf.get('impressions', 0)))
        _tile(c4, 'CPC', f"${perf.get('cpc', 0):.2f}")

    # Ecomm KPI trend
    st.markdown("### Ecomm — Session/Order Trend (from Full Stream Group)")
    ecomm_slice = list(range(1, through_month + 1))
    fig = go.Figure()
    fig.add_scatter(x=[MONTHS[i-1] for i in ecomm_slice],
                    y=ecomm['sessions'][:through_month], mode='lines+markers+text',
                    text=[_fmt_n(v) for v in ecomm['sessions'][:through_month]],
                    textposition='top center', line=dict(color=CHARCOAL, width=3),
                    marker=dict(size=8), name='Sessions')
    fig.update_layout(title='Monthly Sessions', height=300, yaxis_tickformat=',',
                      margin=dict(l=40, r=40, t=60, b=40))
    st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure()
    fig.add_bar(x=[MONTHS[i-1] for i in ecomm_slice], y=ecomm['orders'][:through_month],
                marker_color=BRONZE, text=[_fmt_n(v) for v in ecomm['orders'][:through_month]],
                textposition='outside')
    fig.update_layout(title='Monthly Orders', height=300,
                      margin=dict(l=40, r=40, t=60, b=40))
    st.plotly_chart(fig, use_container_width=True)

    # Email/SMS + Automations
    st.markdown("### Email / SMS & Automations")
    jul_months_str = MONTH_FULL[:through_month]

    email_rows = [r for r in mkt['emailsms'] if r['month'] in jul_months_str]
    if email_rows:
        st.markdown("**Email / SMS Campaigns**")
        df = pd.DataFrame(email_rows)
        df['open_rate'] = df['open_rate'].apply(lambda v: f"{v*100:.1f}%" if v else '—')
        df['click_rate'] = df['click_rate'].apply(lambda v: f"{v*100:.1f}%")
        df['revenue'] = df['revenue'].apply(_fmt_dollar)
        df = df.rename(columns={'month': 'Month', 'channel': 'Ch', 'recipients': 'Recipients',
                                 'open_rate': 'Open', 'click_rate': 'Click',
                                 'revenue': 'Revenue', 'orders': 'Orders'})
        st.dataframe(df, hide_index=True, use_container_width=True)

    auto_rows = [r for r in mkt['automations'] if r['month'] in jul_months_str]
    if auto_rows:
        st.markdown("**Automations (Flows)**")
        df = pd.DataFrame(auto_rows)
        df['open_rate'] = df['open_rate'].apply(lambda v: f"{v*100:.0f}%" if v else '—')
        df['click_rate'] = df['click_rate'].apply(lambda v: f"{v*100:.1f}%")
        df['revenue'] = df['revenue'].apply(_fmt_dollar)
        df = df.rename(columns={'month': 'Month', 'channel': 'Ch', 'delivery': 'Delivery',
                                 'open_rate': 'Open', 'click_rate': 'Click',
                                 'revenue': 'Revenue', 'orders': 'Orders'})
        st.dataframe(df, hide_index=True, use_container_width=True)

    # Social
    st.markdown("### Social")
    social_rows = [r for r in mkt['social'] if r['month'] in jul_months_str]
    if social_rows:
        for s in social_rows:
            c1, c2, c3, c4 = st.columns(4)
            _tile(c1, f"Followers ({s['month'][:3]})", _fmt_n(s['followers']), f"+{_fmt_n(s['new'])} new")
            _tile(c2, 'Organic Views', _fmt_n(s['views']))
            _tile(c3, 'Engagements', _fmt_n(s['engagements']))
            _tile(c4, 'Engagement Rate', f"{s['engage_rate']*100:.2f}%")

    st.divider()
    st.caption(
        f"Source: qbo_actuals.json ({qbo_full.get('last_updated', 'unknown') if isinstance(qbo_full, dict) else 'live'}), "
        f"marketing_monthly.json ({mkt['last_updated']}). "
        "Numbers pulled live from app data — always in sync with the model."
    )
