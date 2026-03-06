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
        'title': 'Operations',
        'department': 'General & Administrative',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 48000.00,
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
        'title': 'Marketing',
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
        'title': 'Admin',
        'department': 'General & Administrative',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 12000.00,
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
        'title': 'Product Development',
        'department': 'Research & Development',
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
        'title': 'W9 Contractor',
        'department': 'General & Administrative',
        'employment_type': 'Contractor (1099)',
        'annual_salary': 48000.00,
        'start_date': '2026-01-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Active',
        'notes': 'W9 contractor - no burdens',
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
        'title': 'Sales',
        'department': 'Sales & Marketing',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 30000.00,
        'start_date': '2026-05-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Projected',
        'notes': 'Starting May 2026',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'first_name': 'Jay',
        'last_name': 'Nalbach',
        'title': 'Operations',
        'department': 'General & Administrative',
        'employment_type': 'Full-Time Employee (FTE)',
        'annual_salary': 30000.00,
        'start_date': '2026-05-01',
        'termination_date': None,
        'location': 'USA',
        'status': 'Projected',
        'notes': 'Starting May 2026',
        'created_at': '2026-01-01T00:00:00',
    },
]


# ============================================================
# BASELINE OPEX (2026) - Monthly granularity from Matt Econ Roadmap
# Matches Excel model Assumptions tab exactly
# ============================================================

# Items with custom monthly schedules (from Matt Econ Roadmap)
# Format: expense_name, category, monthly_values[Jan..Dec]
BASELINE_OPEX_MONTHLY = [
    {
        'expense_name': 'FSG Strategy & Ops',
        'category': 'Professional Services',
        'monthly_values': [5900, 11000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000],
        'notes': 'FSG strategic & ops consulting - Matt Econ Roadmap',
    },
    {
        'expense_name': 'FSG Marketing Mgmt',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 12000, 12000, 7940, 7940, 7940, 7940, 7940, 7940, 7940, 7940, 7940],
        'notes': 'FSG marketing management - Matt Econ Roadmap',
    },
    {
        'expense_name': 'FSG Creative',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 15000, 13000, 3000, 3000, 3000, 3000, 10000, 3000, 13000, 3000, 3000],
        'notes': 'FSG creative services - Matt Econ Roadmap',
    },
    {
        'expense_name': 'FSG Channel',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 6300, 6300, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400, 2400],
        'notes': 'FSG channel/ecom management - Matt Econ Roadmap',
    },
    {
        'expense_name': 'Perf. Marketing (Ad Spend)',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 0, 0, 10000, 10000, 10000, 10000, 10000, 20000, 20000, 20000, 25000],
        'notes': 'Google/Meta ad spend - ramps through year',
    },
    {
        'expense_name': 'Affiliate Costs',
        'category': 'Sales & Marketing',
        'monthly_values': [0, 0, 0, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000],
        'notes': 'Affiliate platform commissions - starts Apr',
    },
    {
        'expense_name': 'Shopify',
        'category': 'Systems & Software',
        'monthly_values': [2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850, 2850],
        'notes': 'E-commerce platform',
    },
    {
        'expense_name': 'Klaviyo',
        'category': 'Systems & Software',
        'monthly_values': [2500, 2500, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250],
        'notes': 'ESP/CRM - migrates from Mailchimp in Mar (cost drops)',
    },
    {
        'expense_name': 'Yotpo',
        'category': 'Systems & Software',
        'monthly_values': [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
        'notes': 'Reviews platform',
    },
    {
        'expense_name': 'UpPromote',
        'category': 'Systems & Software',
        'monthly_values': [250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250, 250],
        'notes': 'Affiliate platform',
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


# RIPPLING BURDENS (Starting May 2026)
RIPPLING_BURDENS = {
    'start_month': 5,  # May
    'rippling': 137.00,  # Monthly per employee
    'healthcare': 697.91,  # Monthly (varies by employee)
    'futa': 3.50,  # Monthly
    'medicare': 0.0145,  # % of salary
    'soc_secur': 0.062,  # % of salary
    'ca_ett': 0.001,  # % of salary (CA only)
    'pre_rippling_rate': 0.185,  # 18.5% flat burden Jan-Apr
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
