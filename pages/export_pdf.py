"""
PDF Export - Monthly Management Report
Generates a professional multi-page PDF report with:
  Page 1: Executive Summary (cash, runway, KPIs, alerts)
  Page 2: P&L Detail with MoM changes, forecast variance, and projections
  Page 3: Cash Flow & Balance Sheet
  Page 4: Operational Metrics (revenue mix, headcount, wholesale pipeline)
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, date
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from financial_calcs import generate_monthly_pl
from qbo_parser import (
    deserialize_qbo_data, build_actuals_dataframe, actuals_to_pl_format, MONTHS
)


# ---------------------------------------------------------------------------
# Helpers for pulling actuals & forecast data
# ---------------------------------------------------------------------------

def _get_report_period():
    """Determine the report month from QBO data."""
    qbo_raw = st.session_state.get('qbo_actuals')
    if not qbo_raw:
        return None, None, None
    last_yr = qbo_raw.get('last_year', 0)
    last_mo = qbo_raw.get('last_month', 0)
    if last_yr == 0 or last_mo == 0:
        return None, None, None
    return last_yr, last_mo, f"{MONTHS[last_mo - 1]} {last_yr}"


def _get_actuals_for_year(year, max_month=12):
    """Return list-of-dicts P&L rows for *year* up to *max_month* from QBO."""
    qbo_raw = st.session_state.get('qbo_actuals')
    if not qbo_raw:
        return None
    parsed = deserialize_qbo_data(qbo_raw)
    if not parsed:
        return None
    actuals = build_actuals_dataframe(parsed['pl_data'], year, max_month)
    return actuals_to_pl_format(actuals)


def _get_forecast_df():
    """Generate the 2026 forecast DataFrame."""
    return generate_monthly_pl(
        year=2026,
        team_members=st.session_state.get('team_members', []),
        opex_expenses=st.session_state.get('opex_expenses', []),
        wholesale_deals=st.session_state.get('wholesale_deals', []),
        dtc_discount_rate=0.0,
        dtc_return_rate=0.0,
    )


def _safe_pct(numerator, denominator):
    if denominator == 0:
        return 0.0
    return numerator / denominator * 100


def _fmt(val, prefix="$", decimals=0):
    """Format a number as currency or plain."""
    if prefix == "$":
        return f"${val:,.{decimals}f}"
    if prefix == "%":
        return f"{val:+.1f}%"
    return f"{val:,.{decimals}f}"


# ---------------------------------------------------------------------------
# PDF Generation
# ---------------------------------------------------------------------------

def generate_pdf_report():
    """Build the full management report PDF and return a BytesIO buffer."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
            PageBreak, KeepTogether,
        )
        from reportlab.lib import colors
    except ImportError:
        st.error("reportlab is required. Add it to requirements.txt.")
        return None

    # ------------------------------------------------------------------
    # Collect data
    # ------------------------------------------------------------------
    report_yr, report_mo, report_label = _get_report_period()
    has_actuals = report_yr is not None

    forecast_df = _get_forecast_df()

    # Actuals rows (list of dicts, one per month)
    actuals_rows_26 = _get_actuals_for_year(2026, report_mo) if has_actuals and report_yr == 2026 else None
    actuals_rows_25 = _get_actuals_for_year(2025)

    # Determine which year's actuals to use for the "last month" section
    if actuals_rows_26 and report_yr == 2026:
        last_mo_idx = report_mo - 1
        current_row = actuals_rows_26[last_mo_idx]
        if last_mo_idx > 0:
            prior_row = actuals_rows_26[last_mo_idx - 1]
        elif actuals_rows_25:
            # Jan 2026 → prior month is Dec 2025
            prior_row = actuals_rows_25[11]
        else:
            prior_row = None
    elif actuals_rows_25 and report_yr == 2025:
        last_mo_idx = report_mo - 1
        current_row = actuals_rows_25[last_mo_idx]
        prior_row = actuals_rows_25[last_mo_idx - 1] if last_mo_idx > 0 else None
    else:
        current_row = None
        prior_row = None

    # Forecast row for the report month (always 2026 forecast)
    forecast_mo_idx = (report_mo - 1) if has_actuals else 0
    forecast_row = forecast_df.iloc[forecast_mo_idx].to_dict() if has_actuals else None

    # QBO raw data
    qbo_raw = st.session_state.get('qbo_actuals', {})
    latest_cash = qbo_raw.get('latest_cash', 0) if qbo_raw else 0

    # Cash data from QBO balance sheet
    cash_data = {}
    if qbo_raw:
        parsed_full = deserialize_qbo_data(qbo_raw)
        if parsed_full:
            cash_data = parsed_full.get('cash_data', {})

    # Team, wholesale, fundraising from session
    team_members = st.session_state.get('team_members', [])
    wholesale_deals = st.session_state.get('wholesale_deals', [])
    fundraising_rounds = st.session_state.get('fundraising_rounds', [])

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.5 * inch, bottomMargin=0.5 * inch,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()

    brand_blue = colors.HexColor('#1a3a5c')
    brand_light = colors.HexColor('#e8eef4')
    green = colors.HexColor('#2d8a4e')
    red = colors.HexColor('#c0392b')
    grey_bg = colors.HexColor('#f5f5f5')
    dark_header = colors.HexColor('#2c3e50')

    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'], fontSize=22,
        textColor=brand_blue, spaceAfter=4, leading=26,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'], fontSize=11,
        textColor=colors.HexColor('#666666'), spaceAfter=16,
    )
    section_style = ParagraphStyle(
        'Section', parent=styles['Heading2'], fontSize=14,
        textColor=brand_blue, spaceBefore=12, spaceAfter=8,
    )
    subsection_style = ParagraphStyle(
        'Subsection', parent=styles['Heading3'], fontSize=11,
        textColor=brand_blue, spaceBefore=8, spaceAfter=4,
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'], fontSize=9, leading=12,
    )
    small_style = ParagraphStyle(
        'Small', parent=styles['Normal'], fontSize=8, leading=10,
        textColor=colors.HexColor('#888888'),
    )
    right_style = ParagraphStyle(
        'Right', parent=body_style, alignment=TA_RIGHT,
    )
    center_style = ParagraphStyle(
        'Center', parent=body_style, alignment=TA_CENTER,
    )

    def _table_style(header_color=dark_header):
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, grey_bg]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, header_color),
        ])

    def _highlight_row_style(row_idx, bg=brand_light):
        """Return extra style commands to highlight a specific row."""
        return [
            ('BACKGROUND', (0, row_idx), (-1, row_idx), bg),
            ('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
        ]

    story = []

    # ------------------------------------------------------------------
    # PAGE 1 — Executive Summary
    # ------------------------------------------------------------------
    report_title = "Monthly Management Report"
    if report_label:
        report_title = f"{report_label} Management Report"

    story.append(Paragraph("Alma Mater Inc.", title_style))
    story.append(Paragraph(report_title, subtitle_style))
    story.append(Paragraph(
        f"Prepared {datetime.now().strftime('%B %d, %Y')} | Confidential",
        small_style,
    ))
    story.append(Spacer(1, 0.15 * inch))

    # --- KPI Cards (as a table) ---
    story.append(Paragraph("Key Performance Indicators", section_style))

    # Calculate KPIs
    if current_row:
        rev = current_row.get('Total Revenue', 0)
        gp = current_row.get('Gross Profit', 0)
        gm_pct = _safe_pct(gp, rev)
        ebitda = current_row.get('EBITDA', 0)
        ebitda_margin = _safe_pct(ebitda, rev)
        net_income = current_row.get('Net Income', ebitda)
    else:
        rev = gp = gm_pct = ebitda = ebitda_margin = net_income = 0

    # Burn rate (trailing 3-month average from forecast as proxy)
    first_3 = forecast_df.head(max(report_mo, 3) if has_actuals else 3)
    avg_burn = (first_3['Total COGS'].mean() + first_3['Total OpEx'].mean()) - first_3['Total Revenue'].mean()
    monthly_burn = max(avg_burn, 0)
    days_runway = (latest_cash / (monthly_burn / 30)) if monthly_burn > 0 else 999
    months_runway = days_runway / 30

    kpi_data = [
        ['Metric', 'Value'],
        ['Closing Cash Balance', _fmt(latest_cash)],
        ['Days of Cash Runway', f"{min(days_runway, 999):.0f} days ({months_runway:.1f} months)"],
        ['Monthly Burn Rate (Avg)', _fmt(monthly_burn)],
        [f'Revenue ({report_label or "Latest"})', _fmt(rev)],
        ['Gross Margin %', f"{gm_pct:.1f}%"],
        ['EBITDA', _fmt(ebitda)],
        ['Net Income', _fmt(net_income)],
    ]

    kpi_table = Table(kpi_data, colWidths=[3.0 * inch, 3.5 * inch])
    ts = _table_style()
    kpi_table.setStyle(ts)
    story.append(kpi_table)
    story.append(Spacer(1, 0.2 * inch))

    # --- Alerts / Flags ---
    story.append(Paragraph("Key Variances & Alerts", section_style))

    alerts = []
    if has_actuals and forecast_row and current_row:
        for metric in ['Total Revenue', 'Total COGS', 'Total OpEx', 'EBITDA']:
            act = current_row.get(metric, 0)
            fc = forecast_row.get(metric, 0)
            if fc != 0:
                var_pct = (act - fc) / abs(fc) * 100
                if abs(var_pct) > 10:
                    direction = "over" if var_pct > 0 else "under"
                    flag = "Favorable" if (
                        (metric in ['Total Revenue', 'EBITDA'] and var_pct > 0) or
                        (metric in ['Total COGS', 'Total OpEx'] and var_pct < 0)
                    ) else "Unfavorable"
                    alerts.append(
                        f"{metric}: {_fmt(act)} actual vs {_fmt(fc)} forecast "
                        f"({var_pct:+.1f}% {direction}) - {flag}"
                    )

    if days_runway < 90:
        alerts.append(f"CASH ALERT: Only {days_runway:.0f} days of runway remaining")

    if not alerts:
        alerts.append("All key metrics within 10% of forecast. No alerts.")

    for a in alerts:
        story.append(Paragraph(f"  {a}", body_style))
    story.append(Spacer(1, 0.15 * inch))

    # --- YTD Summary ---
    if has_actuals and actuals_rows_26 and report_yr == 2026:
        story.append(Paragraph("Year-to-Date Summary (2026)", section_style))

        ytd_data = [['Metric', 'YTD Actual', 'YTD Forecast', 'Variance $', 'Variance %']]
        for metric in ['Total Revenue', 'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']:
            ytd_act = sum(r.get(metric, 0) for r in actuals_rows_26[:report_mo])
            ytd_fc = forecast_df[metric].iloc[:report_mo].sum()
            var_d = ytd_act - ytd_fc
            var_p = _safe_pct(var_d, abs(ytd_fc))
            ytd_data.append([
                metric, _fmt(ytd_act), _fmt(ytd_fc),
                _fmt(var_d), f"{var_p:+.1f}%",
            ])

        ytd_table = Table(ytd_data, colWidths=[1.6*inch, 1.3*inch, 1.3*inch, 1.2*inch, 1.1*inch])
        ytd_table.setStyle(_table_style())
        story.append(ytd_table)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # PAGE 2 — P&L Detail
    # ------------------------------------------------------------------
    story.append(Paragraph("Profit & Loss Detail", title_style))
    story.append(Spacer(1, 0.1 * inch))

    # --- Last Month Detail Table ---
    if current_row:
        story.append(Paragraph(
            f"Monthly Detail: {report_label}", section_style
        ))

        # Build comparison table
        pl_metrics = [
            ('DTC Revenue', 'DTC Revenue'),
            ('Wholesale Revenue', 'Wholesale Revenue'),
            ('Total Revenue', 'Total Revenue'),
            ('Total COGS', 'Total COGS'),
            ('Gross Profit', 'Gross Profit'),
            ('Total OpEx', 'Total OpEx'),
            ('EBITDA', 'EBITDA'),
            ('Net Income', 'Net Income'),
        ]

        header = ['Line Item', 'Actual', 'Prior Mo', 'MoM $', 'MoM %',
                   'Forecast', 'Var $', 'Var %']
        pl_data = [header]

        for label, key in pl_metrics:
            act = current_row.get(key, 0)
            prior = prior_row.get(key, 0) if prior_row else 0
            mom_d = act - prior
            mom_p = _safe_pct(mom_d, abs(prior)) if prior != 0 else 0
            fc = forecast_row.get(key, 0) if forecast_row else 0
            var_d = act - fc
            var_p = _safe_pct(var_d, abs(fc)) if fc != 0 else 0

            pl_data.append([
                label,
                _fmt(act), _fmt(prior),
                _fmt(mom_d), f"{mom_p:+.1f}%",
                _fmt(fc), _fmt(var_d), f"{var_p:+.1f}%",
            ])

        col_widths = [1.2*inch, 0.8*inch, 0.8*inch, 0.75*inch, 0.6*inch,
                      0.8*inch, 0.75*inch, 0.6*inch]
        pl_table = Table(pl_data, colWidths=col_widths)
        ts = _table_style()
        pl_table.setStyle(ts)

        # Highlight total rows
        for i, (label, _) in enumerate(pl_metrics):
            if label in ('Total Revenue', 'Gross Profit', 'EBITDA', 'Net Income'):
                for cmd in _highlight_row_style(i + 1):
                    pl_table.setStyle(TableStyle([cmd]))

        story.append(pl_table)
        story.append(Spacer(1, 0.2 * inch))

    # --- Forward Projections (1, 3, 6 month) ---
    story.append(Paragraph("Forward Projections", section_style))

    if has_actuals:
        proj_header = ['Metric', '1-Mo Proj', '3-Mo Proj', '6-Mo Proj']
        proj_data = [proj_header]

        for label in ['Total Revenue', 'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']:
            vals_1 = vals_3 = vals_6 = 0
            for offset in range(1, 7):
                idx = report_mo - 1 + offset  # 0-indexed
                if idx < 12:
                    val = forecast_df[label].iloc[idx]
                    if offset <= 1:
                        vals_1 += val
                    if offset <= 3:
                        vals_3 += val
                    vals_6 += val

            proj_data.append([label, _fmt(vals_1), _fmt(vals_3), _fmt(vals_6)])

        proj_table = Table(proj_data, colWidths=[1.8*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        proj_table.setStyle(_table_style())
        story.append(proj_table)
    else:
        # No actuals — show full year forecast summary
        story.append(Paragraph("Upload QBO data for period-specific projections.", body_style))
        annual_data = [['Metric', 'Full Year 2026 Forecast']]
        for label in ['Total Revenue', 'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']:
            annual_data.append([label, _fmt(forecast_df[label].sum())])
        ann_table = Table(annual_data, colWidths=[2.5*inch, 3.0*inch])
        ann_table.setStyle(_table_style())
        story.append(ann_table)

    story.append(Spacer(1, 0.2 * inch))

    # --- OpEx Breakdown ---
    if current_row:
        story.append(Paragraph("Operating Expense Breakdown", subsection_style))

        opex_items = [
            ('Sales & Marketing', 'Sales & Marketing'),
            ('Payroll', 'Payroll'),
            ('Software', 'Software'),
            ('Professional Fees', 'Professional Fees'),
            ('Travel', 'Travel'),
            ('Rent & Lease', 'Rent & Lease'),
            ('Insurance', 'Insurance'),
        ]
        opex_header = ['Category', 'Actual', 'Prior Mo', 'Change']
        opex_data = [opex_header]
        for label, key in opex_items:
            act = current_row.get(key, 0)
            prior = prior_row.get(key, 0) if prior_row else 0
            if act != 0 or prior != 0:
                opex_data.append([label, _fmt(act), _fmt(prior), _fmt(act - prior)])

        if len(opex_data) > 1:
            opex_tbl = Table(opex_data, colWidths=[2.0*inch, 1.3*inch, 1.3*inch, 1.3*inch])
            opex_tbl.setStyle(_table_style())
            story.append(opex_tbl)

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # PAGE 3 — Cash Flow & Balance Sheet
    # ------------------------------------------------------------------
    story.append(Paragraph("Cash Flow & Balance Sheet", title_style))
    story.append(Spacer(1, 0.1 * inch))

    # --- Cash Waterfall ---
    story.append(Paragraph("Cash Position", section_style))

    if cash_data and has_actuals:
        cash_header = ['Period', 'Cash Balance']
        cash_rows = [cash_header]
        sorted_periods = sorted(cash_data.keys())

        opening_cash = 0
        for yr, mo in sorted_periods:
            bal = cash_data[(yr, mo)]
            cash_rows.append([f"{MONTHS[mo-1]} {yr}", _fmt(bal, "$", 2)])
            if (yr, mo) == sorted_periods[0]:
                opening_cash = bal

        closing_cash = cash_data.get(sorted_periods[-1], 0) if sorted_periods else 0

        cash_tbl = Table(cash_rows, colWidths=[2.5*inch, 3.0*inch])
        cash_tbl.setStyle(_table_style())
        story.append(cash_tbl)
        story.append(Spacer(1, 0.15 * inch))

        # Cash movement summary
        if len(sorted_periods) >= 2:
            first_period = sorted_periods[0]
            last_period = sorted_periods[-1]
            opening = cash_data[first_period]
            closing = cash_data[last_period]
            net_change = closing - opening

            move_data = [
                ['Cash Movement', 'Amount'],
                ['Opening Balance', _fmt(opening, "$", 2)],
                ['Net Change', _fmt(net_change, "$", 2)],
                ['Closing Balance', _fmt(closing, "$", 2)],
            ]
            move_tbl = Table(move_data, colWidths=[2.5*inch, 3.0*inch])
            ts = _table_style()
            move_tbl.setStyle(ts)
            for cmd in _highlight_row_style(3):
                move_tbl.setStyle(TableStyle([cmd]))
            story.append(move_tbl)
    else:
        story.append(Paragraph(
            "Cash balance data not available. Import QBO Balance Sheet to populate.",
            body_style,
        ))

    story.append(Spacer(1, 0.2 * inch))

    # --- Runway Projection ---
    story.append(Paragraph("Cash Runway Projection", section_style))

    # Get monthly funding from fundraising rounds
    from pages.cash_runway import get_monthly_funding
    fundraising_rounds_for_runway = st.session_state.get('fundraising_rounds', [])
    monthly_funding = get_monthly_funding(fundraising_rounds_for_runway, 2026)
    has_funding = sum(monthly_funding.values()) > 0

    if has_funding:
        runway_header = ['Month', 'Revenue', 'Funding', 'COGS + OpEx', 'Net Flow', 'Cash']
    else:
        runway_header = ['Month', 'Revenue', 'COGS + OpEx', 'Net Flow', 'Cash']
    runway_data = [runway_header]

    starting_cash_val = latest_cash if latest_cash > 0 else st.session_state.get(
        'assumptions', {}
    ).get('starting_cash_2026', 41422)
    cumulative = starting_cash_val
    start_idx = report_mo if has_actuals else 0

    for idx in range(start_idx, 12):
        row = forecast_df.iloc[idx]
        month_num = idx + 1
        funding = monthly_funding.get(month_num, 0)
        net = row['Total Revenue'] + funding - row['Total COGS'] - row['Total OpEx']
        cumulative += net
        if has_funding:
            runway_data.append([
                row['Month'],
                _fmt(row['Total Revenue']),
                _fmt(funding) if funding > 0 else '-',
                _fmt(row['Total COGS'] + row['Total OpEx']),
                _fmt(net),
                _fmt(cumulative),
            ])
        else:
            runway_data.append([
                row['Month'],
                _fmt(row['Total Revenue']),
                _fmt(row['Total COGS'] + row['Total OpEx']),
                _fmt(net),
                _fmt(cumulative),
            ])

    if len(runway_data) > 1:
        if has_funding:
            col_widths = [0.8*inch, 1.0*inch, 0.9*inch, 1.1*inch, 1.0*inch, 1.1*inch]
        else:
            col_widths = [1.0*inch, 1.2*inch, 1.3*inch, 1.2*inch, 1.3*inch]
        rw_tbl = Table(runway_data, colWidths=col_widths)
        rw_tbl.setStyle(_table_style())
        story.append(rw_tbl)

    story.append(Spacer(1, 0.2 * inch))

    # --- AP / AR ---
    story.append(Paragraph("Accounts Payable & Receivable", section_style))

    ap_val = qbo_raw.get('latest_ap', 0) if qbo_raw else 0
    ar_val = 0.0
    ap_source = f"from QBO ({report_label})" if (qbo_raw and ap_val) else "not available from QBO"

    story.append(Paragraph(
        f"AP {ap_source}. AR manually tracked — update on the Cash Flow page.",
        small_style,
    ))

    apar_data = [
        ['Item', 'Balance'],
        ['Accounts Receivable', _fmt(ar_val)],
        ['Accounts Payable', _fmt(ap_val)],
        ['Net Working Capital (AR - AP)', _fmt(ar_val - ap_val)],
    ]
    apar_tbl = Table(apar_data, colWidths=[3.0*inch, 2.5*inch])
    apar_tbl.setStyle(_table_style())
    story.append(apar_tbl)

    story.append(Spacer(1, 0.2 * inch))

    # --- Fundraising / Financing Activities ---
    story.append(Paragraph("Fundraising & Financing", section_style))

    fundraising_rounds = st.session_state.get('fundraising_rounds', [])
    assumptions = st.session_state.get('assumptions', {})
    safe_raised = assumptions.get('safe_notes_raised', 308000.0)

    if fundraising_rounds:
        fund_data = [['Round', 'Amount', 'Timing', 'Status']]
        total_planned = 0
        for rnd in fundraising_rounds:
            amt = rnd.get('amount', 0)
            mo = rnd.get('month', 1)
            yr = rnd.get('year', 2026)
            fund_data.append([
                rnd.get('name', ''),
                _fmt(amt),
                f"{MONTHS[mo - 1]} {yr}",
                rnd.get('status', 'TBD'),
            ])
            total_planned += amt
        fund_data.append(['Total Planned', _fmt(total_planned), '', ''])

        fund_tbl = Table(fund_data, colWidths=[2.0*inch, 1.3*inch, 1.2*inch, 1.0*inch])
        ts = _table_style()
        fund_tbl.setStyle(ts)
        for cmd in _highlight_row_style(len(fund_data) - 1):
            fund_tbl.setStyle(TableStyle([cmd]))
        story.append(fund_tbl)
        story.append(Spacer(1, 0.1 * inch))

        prior_data = [
            ['Prior Capital', 'Amount'],
            ['SAFE Notes Raised', _fmt(safe_raised)],
            ['Total Capital (Raised + Planned)', _fmt(safe_raised + total_planned)],
        ]
        prior_tbl = Table(prior_data, colWidths=[3.0*inch, 2.5*inch])
        prior_tbl.setStyle(_table_style())
        for cmd in _highlight_row_style(2):
            prior_tbl.setStyle(TableStyle([cmd]))
        story.append(prior_tbl)
    else:
        story.append(Paragraph(
            f"SAFE Notes Raised: {_fmt(safe_raised)}. "
            "No additional fundraising rounds planned. "
            "Add rounds on the Fundraising page.",
            body_style,
        ))

    story.append(PageBreak())

    # ------------------------------------------------------------------
    # PAGE 4 — Operational Metrics
    # ------------------------------------------------------------------
    story.append(Paragraph("Operational Metrics", title_style))
    story.append(Spacer(1, 0.1 * inch))

    # --- Revenue Mix ---
    story.append(Paragraph("Revenue Mix: DTC vs Wholesale", section_style))

    if current_row:
        dtc = current_row.get('DTC Revenue', 0)
        ws = current_row.get('Wholesale Revenue', 0)
        total = dtc + ws
        mix_data = [
            ['Channel', 'Amount', '% of Total'],
            ['DTC', _fmt(dtc), f"{_safe_pct(dtc, total):.1f}%"],
            ['Wholesale', _fmt(ws), f"{_safe_pct(ws, total):.1f}%"],
            ['Total', _fmt(total), '100.0%'],
        ]
        mix_tbl = Table(mix_data, colWidths=[2.0*inch, 1.5*inch, 1.5*inch])
        mix_tbl.setStyle(_table_style())
        for cmd in _highlight_row_style(3):
            mix_tbl.setStyle(TableStyle([cmd]))
        story.append(mix_tbl)

        # YTD mix if we have 2026 actuals
        if actuals_rows_26 and report_mo > 1:
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph("YTD Revenue Mix", subsection_style))
            ytd_dtc = sum(r.get('DTC Revenue', 0) for r in actuals_rows_26[:report_mo])
            ytd_ws = sum(r.get('Wholesale Revenue', 0) for r in actuals_rows_26[:report_mo])
            ytd_total = ytd_dtc + ytd_ws
            ytd_mix = [
                ['Channel', 'YTD Amount', '% of Total'],
                ['DTC', _fmt(ytd_dtc), f"{_safe_pct(ytd_dtc, ytd_total):.1f}%"],
                ['Wholesale', _fmt(ytd_ws), f"{_safe_pct(ytd_ws, ytd_total):.1f}%"],
                ['Total', _fmt(ytd_total), '100.0%'],
            ]
            ytd_mix_tbl = Table(ytd_mix, colWidths=[2.0*inch, 1.5*inch, 1.5*inch])
            ytd_mix_tbl.setStyle(_table_style())
            for cmd in _highlight_row_style(3):
                ytd_mix_tbl.setStyle(TableStyle([cmd]))
            story.append(ytd_mix_tbl)
    else:
        story.append(Paragraph("Revenue mix data not available without QBO import.", body_style))

    story.append(Spacer(1, 0.2 * inch))

    # --- Headcount & Payroll ---
    story.append(Paragraph("Headcount & Payroll", section_style))

    if team_members:
        total_headcount = len(team_members)
        total_salary = sum(m.get('annual_salary', 0) for m in team_members)
        total_annual_cost = sum(
            m.get('total_cost', m.get('annual_salary', 0) * 1.185)
            for m in team_members
        )
        monthly_payroll = total_annual_cost / 12

        team_data = [
            ['Metric', 'Value'],
            ['Total Headcount', str(total_headcount)],
            ['Total Annual Salaries', _fmt(total_salary)],
            ['Total Annual Cost (incl. burdens)', _fmt(total_annual_cost)],
            ['Monthly Payroll Burden', _fmt(monthly_payroll)],
        ]

        # Department breakdown
        dept_counts = {}
        for m in team_members:
            dept = m.get('department', 'Other')
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        team_data.append(['', ''])
        team_data.append(['Department', 'Headcount'])
        for dept, count in sorted(dept_counts.items()):
            team_data.append([f"  {dept}", str(count)])

        team_tbl = Table(team_data, colWidths=[3.5*inch, 2.0*inch])
        team_tbl.setStyle(_table_style())
        story.append(team_tbl)
    else:
        story.append(Paragraph("No team members loaded.", body_style))

    story.append(Spacer(1, 0.2 * inch))

    # --- Wholesale Pipeline ---
    story.append(Paragraph("Wholesale Pipeline", section_style))

    if wholesale_deals:
        def _deal_rev(d):
            if 'revenue' in d:
                return d['revenue']
            return d.get('num_pairs', 0) * d.get('wholesale_price', 0)

        def _deal_pairs(d):
            return d.get('pairs', d.get('num_pairs', 0))

        ws_header = ['Customer', 'Pairs', 'Revenue', 'Delivery']
        ws_data = [ws_header]
        total_ws_rev = 0
        total_ws_pairs = 0

        for d in wholesale_deals:
            name = d.get('club_name', d.get('customer_name', ''))
            pairs = _deal_pairs(d)
            rev = _deal_rev(d)
            delivery = d.get('delivery_date', d.get('close_date', ''))
            ws_data.append([name, str(pairs), _fmt(rev), str(delivery)])
            total_ws_rev += rev
            total_ws_pairs += pairs

        ws_data.append(['TOTAL', str(total_ws_pairs), _fmt(total_ws_rev), ''])

        ws_tbl = Table(ws_data, colWidths=[2.2*inch, 0.8*inch, 1.3*inch, 1.2*inch])
        ws_tbl.setStyle(_table_style())
        for cmd in _highlight_row_style(len(ws_data) - 1):
            ws_tbl.setStyle(TableStyle([cmd]))
        story.append(ws_tbl)
    else:
        story.append(Paragraph("No wholesale deals loaded.", body_style))

    story.append(Spacer(1, 0.3 * inch))

    # --- Footer ---
    story.append(Paragraph(
        "This report is generated from the Alma Mater Financial Dashboard. "
        "Data sources: QuickBooks Online actuals, integrated forecast model, "
        "and manually entered team/OpEx/wholesale data.",
        small_style,
    ))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | "
        "Empirica Financial | Confidential",
        small_style,
    ))

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    doc.build(story)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------------------------
# Streamlit Page
# ---------------------------------------------------------------------------

def show():
    """Display PDF export page."""
    st.markdown('<div class="main-header">Export Management Report</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Generate a professional PDF management report</div>',
        unsafe_allow_html=True,
    )

    # Show what will be included
    report_yr, report_mo, report_label = _get_report_period()

    if report_label:
        st.success(f"Report period: **{report_label}** (from QBO actuals)")
    else:
        st.warning(
            "No QBO actuals loaded. The report will use forecast data only. "
            "Import QBO data on the **QBO Import** page for actuals + variance analysis."
        )

    st.markdown("""
### Report Contents

**Page 1 - Executive Summary**
- Cash balance and days of runway
- Key financial KPIs (revenue, margins, EBITDA, net income)
- Variance alerts (any metric >10% off forecast)
- Year-to-date actual vs forecast summary

**Page 2 - P&L Detail**
- Last month actuals with prior month comparison (MoM change)
- Forecast variance (actual vs plan)
- Forward projections: 1-month, 3-month, 6-month outlook
- Operating expense category breakdown

**Page 3 - Cash Flow & Balance Sheet**
- Historical cash balances from QBO Balance Sheet
- Forward cash runway projection (includes fundraising events)
- Accounts payable (auto-populated from QBO) and receivable
- Fundraising schedule with amounts, timing, and status

**Page 4 - Operational Metrics**
- Revenue mix (DTC vs Wholesale) with percentages
- Headcount and payroll summary by department
- Wholesale deal pipeline with delivery dates
    """)

    st.divider()

    if st.button("Generate Management Report PDF", type="primary", use_container_width=True):
        with st.spinner("Building PDF report..."):
            pdf_buffer = generate_pdf_report()

            if pdf_buffer:
                st.success("Report generated successfully!")

                timestamp = datetime.now().strftime('%Y%m%d')
                filename = f"alma_mater_mgmt_report_{timestamp}.pdf"
                if report_label:
                    period_slug = report_label.replace(' ', '_').lower()
                    filename = f"alma_mater_mgmt_report_{period_slug}.pdf"

                st.download_button(
                    label="Download PDF Report",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
