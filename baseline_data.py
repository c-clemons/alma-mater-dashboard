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


def _build_opex_list():
    """Convert the monthly + annual OpEx items into the flat list format
    expected by the rest of the app (session state / data persistence)."""
    result = []
    for item in BASELINE_OPEX_MONTHLY:
        annual = sum(item['monthly_values'])
        result.append({
            'expense_name': item['expense_name'],
            'category': item['category'],
            'vendor': '',
            'frequency': 'Custom Monthly',
            'monthly_values': item['monthly_values'],
            'monthly_amount': annual / 12,  # average for display
            'annual_cost': annual,
            'start_date': '2026-01-01',
            'end_date': None,
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
            'end_date': None,
            'growth_rate': 0.0,
            'notes': item['notes'],
            'created_at': '2026-01-01T00:00:00',
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


# BASELINE WHOLESALE DEALS (2026 Projections from Client)
BASELINE_WHOLESALE = [
    {
        'customer_name': 'Total WS Spring 26',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 500,
        'wholesale_price': 144.00,
        'close_date': '2026-03-01',
        'delivery_date': '2026-03-15',
        'sales_commission': 0.00,
        'total_cost': 77770.00,  # From client data
        'units_produced': 1400,
        'doors': 33,
        'notes': 'Spring 2026 - 500 units @ 33 doors',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'customer_name': 'Total WS Fall 26',
        'product_type': 'Beta',
        'order_type': 'In-Line',
        'num_pairs': 1500,
        'wholesale_price': 144.00,
        'close_date': '2026-08-01',
        'delivery_date': '2026-08-15',
        'sales_commission': 0.00,
        'total_cost': 138875.00,  # From client data
        'units_produced': 2500,
        'doors': 80,
        'notes': 'Fall 2026 - 1,500 units @ 80 doors',
        'created_at': '2026-01-01T00:00:00',
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
    {"name": "Summer 2026 (Beta)", "product": "Beta", "pairs": 2000, "amount": 90000, "order_month": 2, "order_year": 2026},
    {"name": "Summer 2026 (Alpha)", "product": "Alpha", "pairs": 1000, "amount": 55000, "order_month": 2, "order_year": 2026},
    {"name": "Fall 2026 (Beta)", "product": "Beta", "pairs": 2000, "amount": 90000, "order_month": 4, "order_year": 2026},
    {"name": "Fall 2026 (Alpha)", "product": "Alpha", "pairs": 1000, "amount": 55000, "order_month": 4, "order_year": 2026},
    {"name": "Holiday 2026 (Beta)", "product": "Beta", "pairs": 1500, "amount": 67500, "order_month": 6, "order_year": 2026},
    {"name": "Holiday 2026 (Alpha)", "product": "Alpha", "pairs": 500, "amount": 27500, "order_month": 6, "order_year": 2026},
    {"name": "Spring 2027 (Beta)", "product": "Beta", "pairs": 3000, "amount": 135000, "order_month": 8, "order_year": 2026},
    {"name": "Spring 2027 (Alpha)", "product": "Alpha", "pairs": 2000, "amount": 110000, "order_month": 8, "order_year": 2026},
    {"name": "Summer 2027 (Beta)", "product": "Beta", "pairs": 4000, "amount": 180000, "order_month": 11, "order_year": 2026},
    {"name": "Summer 2027 (Alpha)", "product": "Alpha", "pairs": 2000, "amount": 110000, "order_month": 11, "order_year": 2026},
    {"name": "Fall 2027 (Beta)", "product": "Beta", "pairs": 4000, "amount": 180000, "order_month": 2, "order_year": 2027},
    {"name": "Fall 2027 (Alpha)", "product": "Alpha", "pairs": 3000, "amount": 165000, "order_month": 2, "order_year": 2027},
    {"name": "Holiday 2027 (Beta)", "product": "Beta", "pairs": 3000, "amount": 135000, "order_month": 5, "order_year": 2027},
    {"name": "Holiday 2027 (Alpha)", "product": "Alpha", "pairs": 2000, "amount": 110000, "order_month": 5, "order_year": 2027},
]

BASELINE_INVENTORY_CONFIG = {
    "lead_time_months": 4,
    "payment_terms_months": 5,
    "beg_inv_beta": 2500,
    "beg_inv_alpha": 500,
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
