"""
Baseline Data Configuration
Hard-coded baseline team, OpEx, and wholesale data that loads for all users.
Synced with Excel model (build_alma_mater_model.py) as of March 2026.
"""

from datetime import date


# ============================================================
# BASELINE TEAM MEMBERS (2026)
# Matches Excel model Team sheet exactly (9 active + 1 placeholder)
# ============================================================
BASELINE_TEAM = [
    {
        'first_name': 'Ryan',
        'last_name': 'Person',
        'title': 'Head of Golf',
        'department': 'Sales & Marketing',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 60000.00,
        'start_date': '2026-01-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Active',
        'notes': 'Current team member',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Jenny',
        'last_name': 'Champion',
        'title': 'Sales Rep',
        'department': 'Sales & Marketing',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 36000.00,
        'start_date': '2026-01-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Active',
        'notes': 'Current team member',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Michele',
        'last_name': 'Coffman',
        'title': 'Operations',
        'department': 'General & Administrative',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 24000.00,
        'start_date': '2026-01-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Active',
        'notes': 'Current team member - part time',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Sukhjit',
        'last_name': '',
        'title': 'Online Marketing',
        'department': 'Sales & Marketing',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 54000.00,
        'start_date': '2026-01-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Active',
        'notes': 'Current team member',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Marty',
        'last_name': 'Hackle',
        'title': 'Advisor',
        'department': 'General & Administrative',
        'employment_type': 'Contractor (1099)',
        'annual_salary': 48000.00,
        'start_date': '2026-01-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Active',
        'notes': 'Advisor - 1099',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Chandler',
        'last_name': 'Clemons',
        'title': 'Finance',
        'department': 'General & Administrative',
        'employment_type': 'Contractor (1099)',
        'annual_salary': 18000.00,
        'start_date': '2026-01-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Active',
        'notes': 'Fractional CFO - 1099 contractor',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Beth',
        'last_name': 'Hughes',
        'title': 'Accounting',
        'department': 'General & Administrative',
        'employment_type': 'Contractor (1099)',
        'annual_salary': 18000.00,
        'start_date': '2026-01-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Active',
        'notes': 'Accounting - 1099 contractor',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Nathan',
        'last_name': 'Brown',
        'title': 'CEO',
        'department': 'General & Administrative',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 60000.00,
        'start_date': '2026-06-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Projected',
        'notes': 'Starting June 1, 2026 (Congruity W2)',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Jay',
        'last_name': 'Nalbach',
        'title': 'Marketing Communications',
        'department': 'Sales & Marketing',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 60000.00,
        'start_date': '2026-06-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Projected',
        'notes': 'Starting June 1, 2026 (Congruity W2)',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'John',
        'last_name': 'Anderson',
        'title': 'Head of Sales',
        'department': 'Sales & Marketing',
        'employment_type': 'Contractor (1099)',
        'annual_salary': 60000.00,
        'start_date': '2026-06-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Projected',
        'notes': 'Fractional Head of Sales — $5k/mo starting Jun 1',
        'created_at': '2026-05-11T00:00:00',
    },
]


# ============================================================
# BASELINE OPEX (2026) - Monthly granularity from Matt Econ Roadmap
# Matches Excel model Assumptions tab exactly
# ============================================================

# Items with custom monthly schedules (from Matt Econ Roadmap)
# Format: expense_name, category, monthly_values[Jan..Dec]
BASELINE_OPEX_MONTHLY = [
    # 2026 OpEx restructured May 21 to mirror Matt's new 2026 Budget file
    # (AM Marketing_Ecom Budget.xlsx). Compromise 16-line structure: one row per
    # (Section × Cost Type) subtotal. Jan-Apr are Q1 actuals from Matt; May-Dec is
    # Plan. Closed-month overrides still flow from QBO actuals. Total: $463,469/yr
    {
        'expense_name': 'Brand Creative — Creative',
        'category': 'Sales & Marketing',
        'monthly_values': [375, 8750, 3325, 17175, 0, 0, 0, 0, 0, 0, 0, 0],
        'notes': 'Brand Creative / Production — photo/video, copy, design (Matt 2026 Budget)',
    },
    {
        'expense_name': 'Marketing Channels — Mgmt',
        'category': 'Sales & Marketing',
        'monthly_values': [14150, 12375, 11323, 21525, 22333.75, 19600, 22280, 22280, 22280, 20680, 20680, 20680],
        'notes': 'Brand/GTM/CMM/Email/SEO/Organic Social/Perf Mkt mgmt (Matt 2026 Budget R76)',
    },
    {
        'expense_name': 'Marketing Channels — Creative',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 0, 1425, 1000, 1600, 4540, 5040, 4540, 5040, 4540, 5040, 4540],
        'notes': 'Email/SEO/Perf Mkt creative production (Matt 2026 Budget R77)',
    },
    {
        'expense_name': 'Marketing Channels — Spend',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 0, 0, 0, 0, 10640, 15768, 15896, 10896, 8768, 21152, 21152],
        'notes': 'Performance media buy + Direct Mail send costs (Matt 2026 Budget R78)',
    },
    {
        'expense_name': 'Marketing Channels — Systems',
        'category': 'Systems & Software',
        'monthly_values': [0, 0, 0, 0, 0, 90, 90, 90, 90, 90, 90, 90],
        'notes': 'PostPilot system fee (Matt 2026 Budget R79)',
    },
    {
        'expense_name': 'Channel — Mgmt',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 6100, 4750, 3291, 2250, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
        'notes': 'Website management (Matt 2026 Budget R90)',
    },
    {
        'expense_name': 'Channel — Creative',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 0, 3900, 3125, 1100, 1100, 1100, 1100, 0, 0, 0, 0],
        'notes': 'Website digital design + copy (Matt 2026 Budget R91)',
    },
    {
        'expense_name': 'Channel — Systems',
        'category': 'Systems & Software',
        'monthly_values': [0, 2200, 150, 2403, 1600, 100, 100, 100, 100, 100, 100, 100],
        'notes': 'Website development + Yotpo + A/B testing (Matt 2026 Budget R92)',
    },
    {
        'expense_name': 'General Systems — Loop+Yotpo',
        'category': 'Systems & Software',
        'monthly_values': [0, 0, 0, 509, 509, 509, 509, 509, 509, 509, 509, 509],
        'notes': 'Loop Returns ($340) + Yotpo ($169) Apr-Dec (Matt 2026 Budget R101+R102)',
    },
    {
        'expense_name': 'General Systems — Shopify (old assumption)',
        'category': 'Systems & Software',
        'monthly_values': [2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850],
        'notes': 'Using our $2,850/mo flat — Matt 2026 Budget showed $2,500 Mar-Aug only ($15K). Confirm with Matt.',
    },
]

# Items with flat annual amounts spread evenly (annual / 12 each month)
BASELINE_OPEX_ANNUAL = [
    {
        'expense_name': 'Travel & Entertainment',
        'category': 'Travel & Entertainment',
        'annual_cost': 25000.00,
        'notes': 'Fixed annual budget for 2026',
    },
    {
        'expense_name': 'Development & Innovation',
        'category': 'Research & Development',
        'annual_cost': 50000.00,
        'notes': 'Fixed annual budget for 2026',
    },
    {
        'expense_name': 'Postage & Shipping',
        'category': 'Other',
        'annual_cost': 20000.00,
        'notes': 'Fixed annual budget for 2026',
    },
    {
        'expense_name': 'Service Charges',
        'category': 'Professional Services',
        'annual_cost': 5000.00,
        'notes': 'Fixed annual budget for 2026',
    },
    {
        'expense_name': 'Phone Services',
        'category': 'Systems & Software',
        'annual_cost': 2000.00,
        'notes': 'Fixed annual budget for 2026',
    },
    {
        'expense_name': 'Other Operating',
        'category': 'Other',
        'annual_cost': 10000.00,
        'notes': 'Fixed annual budget for 2026',
    },
]


# ============================================================
# 2027 BASELINE OPEX — Phase 3 (May 21, 2026)
# Source: Matt's monthly file (AM 26-28 Marketing_Ecom Budget_Monthly.xlsx)
# Aggregated to 7-line Section × Cost Type structure
# ============================================================
BASELINE_OPEX_MONTHLY_2027 = [
    # CORRECTED May 21: Phase 3 originally used Matt's Budget tab cols 20-31 which
    # are labeled 2028 (per row-1 headers). Cols 5-16 are the correct 2027 monthly.
    # Total: $985,781 (vs original incorrect $1,262,781)
    {
        'expense_name': 'Brand Creative — Creative',
        'category': 'Sales & Marketing',
        'monthly_values': [34000, 12500, 12500, 29000, 12500, 12500, 14000, 12500, 27500, 14000, 12500, 12500],
        'notes': 'Photo/Video, UGC, Copywriting, Image Proc, Digital Design (Matt 2027 file cols 5-16, R30-R37)',
    },
    {
        'expense_name': 'Marketing Channels — Mgmt',
        'category': 'Sales & Marketing',
        'monthly_values': [34000] * 12,
        'notes': '7 agency mgmt roles ($34K/mo): Creative Lead $5K + Marketing Lead $5K + CRM $5K + SEO/AIO $3K + Organic Social $6K + Perf Mkt $6K + Community $4K (Matt 2027 R13-R21)',
    },
    {
        'expense_name': 'Marketing Channels — Spend',
        'category': 'Sales & Marketing',
        'monthly_values': [10000, 13000, 16000, 21000, 26000, 26000, 26000, 20000, 20000, 13000, 32000, 32000],
        'notes': 'Performance Marketing $195k + PostPilot $60k (Matt 2027 R48+R51)',
    },
    {
        'expense_name': 'Channel — Mgmt',
        'category': 'Sales & Marketing',
        'monthly_values': [4000] * 12,
        'notes': 'eCommerce Mgmt $4K/mo (Matt 2027 R23)',
    },
    {
        'expense_name': 'Channel — Creative+Systems',
        'category': 'Sales & Marketing',
        'monthly_values': [1000, 4000, 1000, 4000, 1000, 4000, 1000, 4000, 1000, 4000, 1000, 4000],
        'notes': 'UX Design $12K + Development $18K (Matt 2027 R63+R64)',
    },
    {
        'expense_name': 'General Systems — Loop+Yotpo',
        'category': 'Systems & Software',
        'monthly_values': [0, 0, 0, 509, 509, 509, 509, 509, 509, 509, 509, 509],
        'notes': 'Carry-forward from 2026 (Matt did not update for 2027)',
    },
    {
        'expense_name': 'General Systems — Shopify (old assumption)',
        'category': 'Systems & Software',
        'monthly_values': [2850] * 12,
        'notes': 'Our $2,850/mo flat — pending Matt confirmation on his Mar-Aug pattern',
    },
]


# 2027 annual-input items (from Excel R145-R150)
BASELINE_OPEX_ANNUAL_2027 = [
    {
        'expense_name': 'Travel & Entertainment',
        'category': 'Travel & Entertainment',
        'annual_cost': 40000.00,
        'notes': 'Fixed annual budget for 2027',
    },
    {
        'expense_name': 'Development & Innovation',
        'category': 'Research & Development',
        'annual_cost': 50000.00,
        'notes': 'Fixed annual budget for 2027',
    },
    {
        'expense_name': 'Postage & Shipping',
        'category': 'Other',
        'annual_cost': 40000.00,
        'notes': 'Fixed annual budget for 2027',
    },
    {
        'expense_name': 'Service Charges',
        'category': 'Professional Services',
        'annual_cost': 7500.00,
        'notes': 'Fixed annual budget for 2027',
    },
    {
        'expense_name': 'Phone Services',
        'category': 'Systems & Software',
        'annual_cost': 2000.00,
        'notes': 'Fixed annual budget for 2027',
    },
    {
        'expense_name': 'Other Operating',
        'category': 'Other',
        'annual_cost': 15000.00,
        'notes': 'Fixed annual budget for 2027',
    },
]


# ============================================================
# 2028 BASELINE OPEX — Phase 4 (May 21, 2026)
# Source: Matt's monthly file (AM 26-28 Marketing_Ecom Budget with 2028 budget.xlsx)
# Budget tab cols 20-31 (labeled 2028 per row 1 headers)
# Note: $8K drift vs annual file (Matt updated annual but not all monthly cells)
# Annual-input items: 2027 values held flat as placeholder (no Matt 2028 guidance)
# ============================================================
BASELINE_OPEX_MONTHLY_2028 = [
    {
        'expense_name': 'Brand Creative — Creative',
        'category': 'Sales & Marketing',
        'monthly_values': [18500, 32000, 17000, 18500, 32000, 17000, 18500, 32000, 17000, 33500, 17000, 17000],
        'notes': 'Photo/Video, UGC, Copywriting, Image Proc, Digital Design (Matt 2028 R30-R37)',
    },
    {
        'expense_name': 'Marketing Channels — Mgmt',
        'category': 'Sales & Marketing',
        'monthly_values': [40000] * 12,
        'notes': '7 agency mgmt roles ($40K/mo): Creative Lead $5K + Marketing Lead $6K + CRM $6K + SEO/AIO $4K + Organic Social $7K + Perf Mkt $7K + Community $5K (Matt 2028 R13-R21)',
    },
    {
        'expense_name': 'Marketing Channels — Spend',
        'category': 'Sales & Marketing',
        'monthly_values': [15000, 20000, 26000, 33000, 38000, 38000, 38000, 31000, 31000, 20000, 44000, 44000],
        'notes': 'Performance Marketing $299k + PostPilot $79k (Matt 2028 R48+R51)',
    },
    {
        'expense_name': 'Channel — Mgmt',
        'category': 'Sales & Marketing',
        'monthly_values': [5000] * 12,
        'notes': 'eCommerce Mgmt $5K/mo (Matt 2028 R23)',
    },
    {
        'expense_name': 'Channel — Creative+Systems',
        'category': 'Sales & Marketing',
        'monthly_values': [2000, 4000, 2000, 4000, 2000, 4000, 2000, 4000, 2000, 4000, 2000, 4000],
        'notes': 'UX Design $12K + Development $24K (Matt 2028 R63+R64)',
    },
    {
        'expense_name': 'General Systems — Loop+Yotpo',
        'category': 'Systems & Software',
        'monthly_values': [0, 0, 0, 509, 509, 509, 509, 509, 509, 509, 509, 509],
        'notes': 'Carry-forward from 2026 (Matt did not update for 2028)',
    },
    {
        'expense_name': 'General Systems — Shopify (old assumption)',
        'category': 'Systems & Software',
        'monthly_values': [2850] * 12,
        'notes': 'Our $2,850/mo flat — pending Matt confirmation',
    },
]


# 2028 annual-input items — PLACEHOLDER using 2027 values; Matt did not provide
BASELINE_OPEX_ANNUAL_2028 = [
    {
        'expense_name': 'Travel & Entertainment',
        'category': 'Travel & Entertainment',
        'annual_cost': 40000.00,
        'notes': '2028 placeholder = 2027 value (Matt did not provide; review)',
    },
    {
        'expense_name': 'Development & Innovation',
        'category': 'Research & Development',
        'annual_cost': 50000.00,
        'notes': '2028 placeholder = 2027 value (Matt did not provide; review)',
    },
    {
        'expense_name': 'Postage & Shipping',
        'category': 'Other',
        'annual_cost': 40000.00,
        'notes': '2028 placeholder = 2027 value (Matt did not provide; review)',
    },
    {
        'expense_name': 'Service Charges',
        'category': 'Professional Services',
        'annual_cost': 7500.00,
        'notes': '2028 placeholder = 2027 value (Matt did not provide; review)',
    },
    {
        'expense_name': 'Phone Services',
        'category': 'Systems & Software',
        'annual_cost': 2000.00,
        'notes': '2028 placeholder = 2027 value (Matt did not provide; review)',
    },
    {
        'expense_name': 'Other Operating',
        'category': 'Other',
        'annual_cost': 15000.00,
        'notes': '2028 placeholder = 2027 value (Matt did not provide; review)',
    },
]


def _build_opex_list():
    """Convert the monthly + annual OpEx items into the flat list format
    expected by the rest of the app (session state / data persistence).

    Each item is tagged with `applies_to_year` (2026 or 2027). The OpEx
    calculator in financial_calcs.py filters by this when generating a
    year-specific P&L. Items without `applies_to_year` are treated as
    universal (legacy/user custom items).
    """
    result = []
    # 2026 items
    for item in BASELINE_OPEX_MONTHLY:
        annual = sum(item['monthly_values'])
        result.append({
            'expense_name': item['expense_name'],
            'category': item['category'],
            'vendor': '',
            'frequency': 'Custom Monthly',
            'monthly_values': item['monthly_values'],
            'monthly_amount': annual / 12,
            'annual_cost': annual,
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'applies_to_year': 2026,
            'growth_rate': 0.0,
            'notes': item['notes'],
            'created_at': '2026-01-01T00:00:00',
        })
    for item in BASELINE_OPEX_ANNUAL:
        result.append({
            'expense_name': item['expense_name'],
            'category': item['category'],
            'vendor': '',
            'frequency': 'Annual',
            'monthly_amount': item['annual_cost'] / 12,
            'annual_cost': item['annual_cost'],
            'start_date': '2026-01-01',
            'end_date': '2026-12-31',
            'applies_to_year': 2026,
            'growth_rate': 0.0,
            'notes': item['notes'],
            'created_at': '2026-01-01T00:00:00',
        })
    # 2027 items (Phase 3 — Matt's monthly file)
    for item in BASELINE_OPEX_MONTHLY_2027:
        annual = sum(item['monthly_values'])
        result.append({
            'expense_name': item['expense_name'],
            'category': item['category'],
            'vendor': '',
            'frequency': 'Custom Monthly',
            'monthly_values': item['monthly_values'],
            'monthly_amount': annual / 12,
            'annual_cost': annual,
            'start_date': '2027-01-01',
            'end_date': '2027-12-31',
            'applies_to_year': 2027,
            'growth_rate': 0.0,
            'notes': item['notes'],
            'created_at': '2026-05-21T00:00:00',
        })
    for item in BASELINE_OPEX_ANNUAL_2027:
        result.append({
            'expense_name': item['expense_name'],
            'category': item['category'],
            'vendor': '',
            'frequency': 'Annual',
            'monthly_amount': item['annual_cost'] / 12,
            'annual_cost': item['annual_cost'],
            'start_date': '2027-01-01',
            'end_date': '2027-12-31',
            'applies_to_year': 2027,
            'growth_rate': 0.0,
            'notes': item['notes'],
            'created_at': '2026-05-21T00:00:00',
        })
    # 2028 items (Phase 4)
    for item in BASELINE_OPEX_MONTHLY_2028:
        annual = sum(item['monthly_values'])
        result.append({
            'expense_name': item['expense_name'],
            'category': item['category'],
            'vendor': '',
            'frequency': 'Custom Monthly',
            'monthly_values': item['monthly_values'],
            'monthly_amount': annual / 12,
            'annual_cost': annual,
            'start_date': '2028-01-01',
            'end_date': '2028-12-31',
            'applies_to_year': 2028,
            'growth_rate': 0.0,
            'notes': item['notes'],
            'created_at': '2026-05-21T00:00:00',
        })
    for item in BASELINE_OPEX_ANNUAL_2028:
        result.append({
            'expense_name': item['expense_name'],
            'category': item['category'],
            'vendor': '',
            'frequency': 'Annual',
            'monthly_amount': item['annual_cost'] / 12,
            'annual_cost': item['annual_cost'],
            'start_date': '2028-01-01',
            'end_date': '2028-12-31',
            'applies_to_year': 2028,
            'growth_rate': 0.0,
            'notes': item['notes'],
            'created_at': '2026-05-21T00:00:00',
        })
    return result


# Legacy flat format used by session state
BASELINE_OPEX = _build_opex_list()


# CONGRUITY PEO BURDENS (Starting June 2026)
RIPPLING_BURDENS = {
    'start_month': 6,  # June
    'rippling': 166.67,    # Congruity platform: $10k/yr ÷ 12 ÷ 5 employees
    'healthcare': 666.67,  # $40k/yr ÷ 12 ÷ 5 employees
    'futa': 3.50,
    'medicare': 0.0145,
    'soc_secur': 0.062,
    'ca_ett': 0.001,
    'pre_rippling_rate': 0.185,  # Pre-Congruity flat burden Jan-May
}


# BASELINE WHOLESALE DEALS (2026-2028)
# 2026: synced with Excel May 26, 2026 — blended ASP $149 (5% Alpha mix)
# 2027-2028: Nate WS forecast 6Jun26 (territory build with John Anderson).
#   Email guidance: "everything is forecast off an average wholesale price of $144"
#   → ASP forced to flat $144 for 2027/2028 (overrides Alpha-blend convention).
#   Nate's adjustments vs John's raw forecast: 50% of '27, dropped "B" territories in '28,
#   full forecast for '29.  Totals: $1,447,200 (2027) / $3,330,000 (2028).
#   Spring/Fall split mirrors Excel GG monthly shape → 37.5% Spring / 62.5% Fall.
# All entries are 'Beta' product_type (wholesale unit consumption pool).
BASELINE_WHOLESALE = [
    # ---- 2026 ----
    {
        'customer_name': 'Total WS Spring 26',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 500,
        'wholesale_price': 149.00,  # blended @ 5% Alpha mix
        'close_date': '2026-03-01',
        'delivery_date': '2026-03-15',
        'sales_commission': 0.00,
        'total_cost': 77770.00,
        'units_produced': 1400,
        'doors': 33,
        'notes': 'Spring 2026 - 500 units @ 33 doors (blended ASP)',
        'created_at': '2026-01-01T00:00:00',
    },
    # ---- Fall 2026 (Jun-Dec) — Nate bell curve 16Jun26 — 1,500u total @ $149 blended ASP ----
    # Replaces single Aug-1 Fall 26 deal. Peak Aug, lowest Dec (~5%), all months populated.
    # Per-unit cost basis preserved: $92.58/u; doors scale proportionally (~0.053 doors/u).
    {
        'customer_name': 'WS Jun 26',
        'product_type': 'Beta', 'order_type': 'In-Line',
        'num_pairs': 127, 'wholesale_price': 149.00,
        'close_date': '2026-06-01', 'delivery_date': '2026-06-15',
        'sales_commission': 0.00, 'total_cost': 11758.13,
        'units_produced': 0, 'doors': 7,
        'notes': 'Jun 2026 — bell curve allocation (127u @ $149 = $18,923)',
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Jul 26',
        'product_type': 'Beta', 'order_type': 'In-Line',
        'num_pairs': 268, 'wholesale_price': 149.00,
        'close_date': '2026-07-01', 'delivery_date': '2026-07-15',
        'sales_commission': 0.00, 'total_cost': 24811.94,
        'units_produced': 0, 'doors': 14,
        'notes': 'Jul 2026 — bell curve allocation (268u @ $149 = $39,932)',
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Aug 26',
        'product_type': 'Beta', 'order_type': 'In-Line',
        'num_pairs': 345, 'wholesale_price': 149.00,
        'close_date': '2026-08-01', 'delivery_date': '2026-08-15',
        'sales_commission': 0.00, 'total_cost': 31941.25,
        'units_produced': 0, 'doors': 18,
        'notes': 'Aug 2026 — bell curve peak (345u @ $149 = $51,405)',
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Sep 26',
        'product_type': 'Beta', 'order_type': 'In-Line',
        'num_pairs': 312, 'wholesale_price': 149.00,
        'close_date': '2026-09-01', 'delivery_date': '2026-09-15',
        'sales_commission': 0.00, 'total_cost': 28886.21,
        'units_produced': 0, 'doors': 17,
        'notes': 'Sep 2026 — bell curve allocation (312u @ $149 = $46,488)',
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Oct 26',
        'product_type': 'Beta', 'order_type': 'In-Line',
        'num_pairs': 233, 'wholesale_price': 149.00,
        'close_date': '2026-10-01', 'delivery_date': '2026-10-15',
        'sales_commission': 0.00, 'total_cost': 21571.21,
        'units_produced': 0, 'doors': 12,
        'notes': 'Oct 2026 — bell curve allocation (233u @ $149 = $34,717)',
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Nov 26',
        'product_type': 'Beta', 'order_type': 'In-Line',
        'num_pairs': 143, 'wholesale_price': 149.00,
        'close_date': '2026-11-01', 'delivery_date': '2026-11-15',
        'sales_commission': 0.00, 'total_cost': 13239.42,
        'units_produced': 0, 'doors': 8,
        'notes': 'Nov 2026 — bell curve allocation (143u @ $149 = $21,307)',
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Dec 26',
        'product_type': 'Beta', 'order_type': 'In-Line',
        'num_pairs': 72, 'wholesale_price': 149.00,
        'close_date': '2026-12-01', 'delivery_date': '2026-12-15',
        'sales_commission': 0.00, 'total_cost': 6666.00,
        'units_produced': 0, 'doors': 4,
        'notes': 'Dec 2026 — bell curve allocation (72u @ $149 = $10,728)',
        'created_at': '2026-06-16T00:00:00',
    },
    # ---- 2027 — Nate WS forecast 16Jun26 bell curve ($10,050u @ $144 ASP). All 12 months populated, ~5% min, peaks Mar/Aug ----
    {
        'customer_name': 'WS Jan 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 663,
        'wholesale_price': 144.00,
        'close_date': '2027-01-01',
        'delivery_date': '2027-01-15',
        'sales_commission': 11456.64,
        'total_cost': 25498.98,
        'units_produced': 0,
        'doors': 33,
        'notes': "Jan 2027 — bell curve allocation (663u @ $144 = $95,472)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Feb 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1403,
        'wholesale_price': 144.00,
        'close_date': '2027-02-01',
        'delivery_date': '2027-02-15',
        'sales_commission': 24243.84,
        'total_cost': 53959.38,
        'units_produced': 0,
        'doors': 70,
        'notes': "Feb 2027 — bell curve allocation (1,403u @ $144 = $202,032)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Mar 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1801,
        'wholesale_price': 144.00,
        'close_date': '2027-03-01',
        'delivery_date': '2027-03-15',
        'sales_commission': 31121.28,
        'total_cost': 69266.46,
        'units_produced': 0,
        'doors': 90,
        'notes': "Mar 2027 — bell curve allocation (1,801u @ $144 = $259,344)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Apr 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1491,
        'wholesale_price': 144.00,
        'close_date': '2027-04-01',
        'delivery_date': '2027-04-15',
        'sales_commission': 25764.48,
        'total_cost': 57343.86,
        'units_produced': 0,
        'doors': 75,
        'notes': "Apr 2027 — bell curve allocation (1,491u @ $144 = $214,704)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS May 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 846,
        'wholesale_price': 144.00,
        'close_date': '2027-05-01',
        'delivery_date': '2027-05-15',
        'sales_commission': 14618.88,
        'total_cost': 32537.16,
        'units_produced': 0,
        'doors': 42,
        'notes': "May 2027 — bell curve allocation (846u @ $144 = $121,824)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Jun 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 329,
        'wholesale_price': 144.00,
        'close_date': '2027-06-01',
        'delivery_date': '2027-06-15',
        'sales_commission': 5685.12,
        'total_cost': 12653.34,
        'units_produced': 0,
        'doors': 16,
        'notes': "Jun 2027 — bell curve allocation (329u @ $144 = $47,376)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Jul 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 687,
        'wholesale_price': 144.00,
        'close_date': '2027-07-01',
        'delivery_date': '2027-07-15',
        'sales_commission': 11871.36,
        'total_cost': 85194.87,
        'units_produced': 0,
        'doors': 34,
        'notes': "Jul 2027 — bell curve allocation (687u @ $144 = $98,928)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Aug 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 882,
        'wholesale_price': 144.00,
        'close_date': '2027-08-01',
        'delivery_date': '2027-08-15',
        'sales_commission': 15240.96,
        'total_cost': 109376.82,
        'units_produced': 0,
        'doors': 44,
        'notes': "Aug 2027 — bell curve allocation (882u @ $144 = $127,008)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Sep 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 800,
        'wholesale_price': 144.00,
        'close_date': '2027-09-01',
        'delivery_date': '2027-09-15',
        'sales_commission': 13824.0,
        'total_cost': 99208.0,
        'units_produced': 0,
        'doors': 40,
        'notes': "Sep 2027 — bell curve allocation (800u @ $144 = $115,200)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Oct 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 597,
        'wholesale_price': 144.00,
        'close_date': '2027-10-01',
        'delivery_date': '2027-10-15',
        'sales_commission': 10316.16,
        'total_cost': 74033.97,
        'units_produced': 0,
        'doors': 30,
        'notes': "Oct 2027 — bell curve allocation (597u @ $144 = $85,968)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Nov 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 366,
        'wholesale_price': 144.00,
        'close_date': '2027-11-01',
        'delivery_date': '2027-11-15',
        'sales_commission': 6324.48,
        'total_cost': 45387.66,
        'units_produced': 0,
        'doors': 18,
        'notes': "Nov 2027 — bell curve allocation (366u @ $144 = $52,704)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Dec 27',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 185,
        'wholesale_price': 144.00,
        'close_date': '2027-12-01',
        'delivery_date': '2027-12-15',
        'sales_commission': 3196.8,
        'total_cost': 22941.85,
        'units_produced': 0,
        'doors': 9,
        'notes': "Dec 2027 — bell curve allocation (185u @ $144 = $26,640)",
        'created_at': '2026-06-16T00:00:00',
    },
    # ---- 2028 — Nate WS forecast 16Jun26 bell curve ($23,125u @ $144 ASP). All 12 months populated, ~5% min, peaks Mar/Aug ----
    {
        'customer_name': 'WS Jan 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1525,
        'wholesale_price': 144.00,
        'close_date': '2028-01-01',
        'delivery_date': '2028-01-15',
        'sales_commission': 26352.0,
        'total_cost': 58651.5,
        'units_produced': 0,
        'doors': 76,
        'notes': "Jan 2028 — bell curve allocation (1,525u @ $144 = $219,600)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Feb 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 3228,
        'wholesale_price': 144.00,
        'close_date': '2028-02-01',
        'delivery_date': '2028-02-15',
        'sales_commission': 55779.84,
        'total_cost': 124148.88,
        'units_produced': 0,
        'doors': 161,
        'notes': "Feb 2028 — bell curve allocation (3,228u @ $144 = $464,832)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Mar 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 4145,
        'wholesale_price': 144.00,
        'close_date': '2028-03-01',
        'delivery_date': '2028-03-15',
        'sales_commission': 71625.6,
        'total_cost': 159416.7,
        'units_produced': 0,
        'doors': 207,
        'notes': "Mar 2028 — bell curve allocation (4,145u @ $144 = $596,880)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Apr 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 3431,
        'wholesale_price': 144.00,
        'close_date': '2028-04-01',
        'delivery_date': '2028-04-15',
        'sales_commission': 59287.68,
        'total_cost': 131956.26,
        'units_produced': 0,
        'doors': 172,
        'notes': "Apr 2028 — bell curve allocation (3,431u @ $144 = $494,064)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS May 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1946,
        'wholesale_price': 144.00,
        'close_date': '2028-05-01',
        'delivery_date': '2028-05-15',
        'sales_commission': 33626.88,
        'total_cost': 74843.16,
        'units_produced': 0,
        'doors': 97,
        'notes': "May 2028 — bell curve allocation (1,946u @ $144 = $280,224)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Jun 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 756,
        'wholesale_price': 144.00,
        'close_date': '2028-06-01',
        'delivery_date': '2028-06-15',
        'sales_commission': 13063.68,
        'total_cost': 29075.76,
        'units_produced': 0,
        'doors': 38,
        'notes': "Jun 2028 — bell curve allocation (756u @ $144 = $108,864)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Jul 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1581,
        'wholesale_price': 144.00,
        'close_date': '2028-07-01',
        'delivery_date': '2028-07-15',
        'sales_commission': 27319.68,
        'total_cost': 196059.81,
        'units_produced': 0,
        'doors': 79,
        'notes': "Jul 2028 — bell curve allocation (1,581u @ $144 = $227,664)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Aug 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 2029,
        'wholesale_price': 144.00,
        'close_date': '2028-08-01',
        'delivery_date': '2028-08-15',
        'sales_commission': 35061.12,
        'total_cost': 251616.29,
        'units_produced': 0,
        'doors': 101,
        'notes': "Aug 2028 — bell curve allocation (2,029u @ $144 = $292,176)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Sep 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1841,
        'wholesale_price': 144.00,
        'close_date': '2028-09-01',
        'delivery_date': '2028-09-15',
        'sales_commission': 31812.48,
        'total_cost': 228302.41,
        'units_produced': 0,
        'doors': 92,
        'notes': "Sep 2028 — bell curve allocation (1,841u @ $144 = $265,104)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Oct 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1374,
        'wholesale_price': 144.00,
        'close_date': '2028-10-01',
        'delivery_date': '2028-10-15',
        'sales_commission': 23742.72,
        'total_cost': 170389.74,
        'units_produced': 0,
        'doors': 69,
        'notes': "Oct 2028 — bell curve allocation (1,374u @ $144 = $197,856)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Nov 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 843,
        'wholesale_price': 144.00,
        'close_date': '2028-11-01',
        'delivery_date': '2028-11-15',
        'sales_commission': 14567.04,
        'total_cost': 104540.43,
        'units_produced': 0,
        'doors': 42,
        'notes': "Nov 2028 — bell curve allocation (843u @ $144 = $121,392)",
        'created_at': '2026-06-16T00:00:00',
    },
    {
        'customer_name': 'WS Dec 28',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 426,
        'wholesale_price': 144.00,
        'close_date': '2028-12-01',
        'delivery_date': '2028-12-15',
        'sales_commission': 7361.28,
        'total_cost': 52828.26,
        'units_produced': 0,
        'doors': 21,
        'notes': "Dec 2028 — bell curve allocation (426u @ $144 = $61,344)",
        'created_at': '2026-06-16T00:00:00',
    },
]


# ============================================================
# BASELINE FUNDRAISING ROUNDS
# Matches Excel model Assumptions tab (rows 58-60)
# ============================================================
BASELINE_FUNDRAISING = [
    {
        'name': '1st SAFE Round',
        'amount': 323000.0,
        'month': 1,
        'year': 2026,
        'status': 'Closed',
        'notes': 'Pre-existing SAFE — received before 2026',
    },
    {
        'name': '2nd SAFE Round',
        'amount': 555000.0,
        'month': 4,
        'year': 2026,
        'status': 'Closed',
        'notes': 'Closed April 2026 — funds in bank',
    },
]


def get_baseline_fundraising():
    """Get baseline fundraising rounds"""
    return [r.copy() for r in BASELINE_FUNDRAISING]


# ============================================================
# BASELINE PURCHASE ORDERS & INVENTORY CONFIG
# Matches Excel model Assumptions tab PO section
# ============================================================
BASELINE_PO_DATA = [
    # Recalibrated 8Jun26 — Nathan note: 2028 POs were too aggressive (inventory ballooned).
    # Slimmed to land end-2028 ~8K units. WS reshaped 65% Spring / 35% Fall.
    # Lead time 4 months; arrival = order_month + 4.
    {"name": "Holiday 2026 (Beta)",      "product": "Beta", "pairs": 1500,  "amount": 67500,  "order_month": 5,  "order_year": 2026},
    {"name": "Spring 2027 (Beta)",       "product": "Beta", "pairs": 2000,  "amount": 90000,  "order_month": 8,  "order_year": 2026},
    {"name": "Summer 2027 (Beta)",       "product": "Beta", "pairs": 7000,  "amount": 315000, "order_month": 11, "order_year": 2026},  # bigger to cover Mar'27 4.4K WS ship
    {"name": "Fall 2027 (Beta)",         "product": "Beta", "pairs": 6000,  "amount": 270000, "order_month": 2,  "order_year": 2027},
    {"name": "Holiday 2027 (Beta)",      "product": "Beta", "pairs": 5000,  "amount": 225000, "order_month": 5,  "order_year": 2027},  # reverted Sep arrival
    {"name": "Q4 2027 Stocker (Beta)",   "product": "Beta", "pairs": 3000,  "amount": 135000, "order_month": 8,  "order_year": 2027},
    {"name": "Spring 2028 (Beta)",       "product": "Beta", "pairs": 12000, "amount": 540000, "order_month": 11, "order_year": 2027},  # cover Mar'28 10K WS ship
    {"name": "Summer 2028 (Beta)",       "product": "Beta", "pairs": 7000,  "amount": 315000, "order_month": 2,  "order_year": 2028},  # trimmed from 12K
    {"name": "Fall 2028 (Beta)",         "product": "Beta", "pairs": 7000,  "amount": 315000, "order_month": 4,  "order_year": 2028},  # trimmed from 14K; Aug arrival
    {"name": "Q4 2028 Stocker (Beta)",   "product": "Beta", "pairs": 4000,  "amount": 180000, "order_month": 8,  "order_year": 2028},
    # Total: 10 Beta POs, 54,500 pairs, $2,452,500 (down from 66,500 pairs / $2,992,500)
]

BASELINE_INVENTORY_CONFIG = {
    "lead_time_months": 4,
    "payment_terms_months": 5,
    # Synced with Excel Inventory tab R7/R17 (actual Shopify Jan 2026 beginning balance)
    # was 2500/500 (programmatic estimate); updated to 4433/132 (Shopify reality)
    "beg_inv_beta": 4433,
    "beg_inv_alpha": 132,
}


def get_baseline_po_data():
    """Get baseline purchase orders"""
    return [d.copy() for d in BASELINE_PO_DATA]


def get_baseline_inventory_config():
    """Get baseline inventory configuration"""
    return BASELINE_INVENTORY_CONFIG.copy()


def get_baseline_team():
    """Get baseline team members"""
    return [m.copy() for m in BASELINE_TEAM]


def get_baseline_opex():
    """Get baseline OpEx expenses"""
    return [e.copy() for e in BASELINE_OPEX]


def get_baseline_wholesale():
    """Get baseline wholesale deals"""
    return [d.copy() for d in BASELINE_WHOLESALE]


def get_rippling_burdens():
    """Get Rippling burden rates"""
    return RIPPLING_BURDENS.copy()
