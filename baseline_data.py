"""
Baseline Data Configuration
Hard-coded baseline team, OpEx, and wholesale data that loads for all users
"""

from datetime import date


# BASELINE TEAM MEMBERS (2026)
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
        'employment_type': 'Part-Time',
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
    {
        'first_name': 'Marty',
        'last_name': '',
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
]


# BASELINE OPEX (2026) - Additional fixed costs
BASELINE_OPEX = [
    {
        'expense_name': 'Travel & Entertainment',
        'category': 'Travel & Entertainment',
        'vendor': 'Various',
        'frequency': 'Annual',
        'monthly_amount': 25000 / 12,
        'annual_cost': 25000.00,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Fixed annual budget for 2026',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Phone Services',
        'category': 'Systems & Software',
        'vendor': 'Various Carriers',
        'frequency': 'Annual',
        'monthly_amount': 2000 / 12,
        'annual_cost': 2000.00,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Fixed annual budget for 2026',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Service Charges',
        'category': 'Professional Services',
        'vendor': 'Various',
        'frequency': 'Annual',
        'monthly_amount': 5000 / 12,
        'annual_cost': 5000.00,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Fixed annual budget for 2026',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Travel',
        'category': 'Travel & Entertainment',
        'vendor': 'Various',
        'frequency': 'Annual',
        'monthly_amount': 20000 / 12,
        'annual_cost': 20000.00,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Fixed annual budget for 2026',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Development & Innovation',
        'category': 'Research & Development',
        'vendor': 'Various',
        'frequency': 'Annual',
        'monthly_amount': 50000 / 12,
        'annual_cost': 50000.00,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Fixed annual budget for 2026',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Postage & Shipping',
        'category': 'Other',
        'vendor': 'USPS/FedEx/UPS',
        'frequency': 'Annual',
        'monthly_amount': 20000 / 12,
        'annual_cost': 20000.00,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Fixed annual budget for 2026',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Other Operating Expenses',
        'category': 'Other',
        'vendor': 'Various',
        'frequency': 'Annual',
        'monthly_amount': 10000 / 12,
        'annual_cost': 10000.00,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Fixed annual budget for 2026',
        'created_at': '2026-01-01T00:00:00',
    },
    # Systems costs from Matt's forecast
    {
        'expense_name': 'Shopify',
        'category': 'Systems & Software',
        'vendor': 'Shopify',
        'frequency': 'Monthly',
        'monthly_amount': 2850,
        'annual_cost': 34200,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'E-commerce platform - from Matt forecast',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Klaviyo (ESP/CRM)',
        'category': 'Systems & Software',
        'vendor': 'Klaviyo',
        'frequency': 'Monthly',
        'monthly_amount': 2500,
        'annual_cost': 30000,
        'start_date': '2026-01-01',
        'end_date': '2026-02-28',
        'growth_rate': 0.0,
        'notes': 'Migrating from Mailchimp to Klaviyo in Feb - from Matt forecast',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Klaviyo (ESP/CRM)',
        'category': 'Systems & Software',
        'vendor': 'Klaviyo',
        'frequency': 'Monthly',
        'monthly_amount': 250,
        'annual_cost': 2500,  # Feb-Dec = 11 months
        'start_date': '2026-03-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Post-migration cost - from Matt forecast',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Yotpo (Reviews)',
        'category': 'Systems & Software',
        'vendor': 'Yotpo',
        'frequency': 'Monthly',
        'monthly_amount': 100,
        'annual_cost': 1200,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Reviews platform - from Matt forecast',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'UpPromote',
        'category': 'Systems & Software',
        'vendor': 'UpPromote',
        'frequency': 'Annual',
        'monthly_amount': 3000 / 12,
        'annual_cost': 3000,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Affiliate platform - from Matt forecast',
        'created_at': '2026-01-01T00:00:00',
    },
    # Performance Marketing from Matt
    {
        'expense_name': 'Performance Marketing - Google/Meta',
        'category': 'Sales & Marketing',
        'vendor': 'Google/Meta',
        'frequency': 'Monthly',
        'monthly_amount': 10000,  # Starts at $10K, ramps to $25K
        'annual_cost': 160000,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.05,  # 5% monthly growth
        'notes': 'Digital advertising - ramping from $10K to $25K - from Matt forecast',
        'created_at': '2026-01-01T00:00:00',
    },
    {
        'expense_name': 'Affiliate Platform Costs',
        'category': 'Sales & Marketing',
        'vendor': 'Various Affiliates',
        'frequency': 'Monthly',
        'monthly_amount': 5000,  # Ramps up
        'annual_cost': 50000,
        'start_date': '2026-01-01',
        'end_date': None,
        'growth_rate': 0.0,
        'notes': 'Cost of affiliate commissions - from Matt forecast',
        'created_at': '2026-01-01T00:00:00',
    },
]


# RIPPLING BURDENS (Starting May 2026)
RIPPLING_BURDENS = {
    'start_month': 5,  # May
    'rippling': 137.00,  # Monthly per employee
    'healthcare': 697.91,  # Monthly (varies by employee)
    'futa': 3.50,  # Monthly
    'medicare': 0.0145,  # % of salary
    'soc_secur': 0.062,  # % of salary  
    'ca_ett': 0.001,  # % of salary (CA only)
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
    return BASELINE_TEAM.copy()


def get_baseline_opex():
    """Get baseline OpEx expenses"""
    return BASELINE_OPEX.copy()


def get_baseline_wholesale():
    """Get baseline wholesale deals"""
    return BASELINE_WHOLESALE.copy()


def get_rippling_burdens():
    """Get Rippling burden rates"""
    return RIPPLING_BURDENS.copy()
