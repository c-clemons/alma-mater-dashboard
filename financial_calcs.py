"""
Financial Calculations Module
Integrates team costs, OpEx, wholesale, and DTC revenue
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Tuple
from baseline_data import get_rippling_burdens


def calculate_team_costs_monthly(team_members: List[Dict], year: int = 2026) -> Dict[int, float]:
    """
    Calculate monthly team costs including Rippling burdens starting May 2026.
    Matches Excel model Team Costs tab formula logic exactly.

    Returns: Dict of {month: total_cost}
    """
    monthly_costs = {month: 0.0 for month in range(1, 13)}
    rippling = get_rippling_burdens()
    pre_rippling_rate = rippling.get('pre_rippling_rate', 0.185)

    for member in team_members:
        if not member.get('annual_salary'):
            continue

        monthly_salary = member['annual_salary'] / 12

        # Parse start date
        start_date_str = member.get('start_date', f'{year}-01-01')
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except:
            start_date = date(year, 1, 1)

        # Parse end date if exists
        end_date = None
        if member.get('termination_date'):
            try:
                end_date = datetime.strptime(member['termination_date'], '%Y-%m-%d').date()
            except:
                pass

        # Calculate active months
        for month in range(1, 13):
            month_date = date(year, month, 1)

            # Check if employee is active this month
            if month_date.year == start_date.year and month_date.month < start_date.month:
                continue
            if end_date and month_date > end_date:
                continue

            # Base salary
            cost = monthly_salary

            # Add burdens (matches Excel formula exactly)
            if member.get('employment_type') == 'Contractor (1099)':
                # No burdens for 1099 contractors
                pass
            else:
                # W2 employees get burdens
                if month >= rippling['start_month']:
                    # Rippling PEO starts in May
                    cost += rippling['rippling']      # $137/month
                    cost += rippling['healthcare']     # $697.91/month
                    cost += rippling['futa']           # $3.50/month
                    cost += monthly_salary * rippling['medicare']   # 1.45%
                    cost += monthly_salary * rippling['soc_secur']  # 6.2%
                    cost += monthly_salary * rippling['ca_ett']     # 0.1%
                else:
                    # Pre-Rippling: flat 18.5% burden rate
                    cost += monthly_salary * pre_rippling_rate

            monthly_costs[month] += cost

    return monthly_costs


def calculate_opex_monthly(opex_expenses: List[Dict], year: int = 2026) -> Dict[int, float]:
    """
    Calculate monthly OpEx costs.
    Supports 'Custom Monthly' items with per-month values (from Matt Econ Roadmap)
    as well as Monthly, Quarterly, Annual, and One-Time frequencies.

    Returns: Dict of {month: total_cost}
    """
    monthly_costs = {month: 0.0 for month in range(1, 13)}

    for expense in opex_expenses:
        frequency = expense.get('frequency', 'Monthly')

        # Custom Monthly: each month has its own value (from baseline_data)
        if frequency == 'Custom Monthly':
            monthly_vals = expense.get('monthly_values', [])
            for month in range(1, 13):
                if month - 1 < len(monthly_vals):
                    monthly_costs[month] += monthly_vals[month - 1]
            continue

        amount = expense.get('monthly_amount', 0) or expense.get('annual_cost', 0) / 12

        # Parse start date
        start_date_str = expense.get('start_date', f'{year}-01-01')
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except:
            start_date = date(year, 1, 1)

        # Parse end date if exists
        end_date = None
        if expense.get('end_date'):
            try:
                end_date = datetime.strptime(expense['end_date'], '%Y-%m-%d').date()
            except:
                pass

        # Allocate to months based on frequency
        if frequency == 'Monthly':
            for month in range(1, 13):
                month_date = date(year, month, 1)
                if month_date.year == start_date.year and month_date.month >= start_date.month:
                    if not end_date or month_date <= end_date:
                        monthly_costs[month] += amount

        elif frequency == 'Quarterly':
            for month in [3, 6, 9, 12]:
                month_date = date(year, month, 1)
                if month_date >= start_date:
                    if not end_date or month_date <= end_date:
                        monthly_costs[month] += amount * 3

        elif frequency == 'Annual':
            annual_amount = expense.get('annual_cost', amount * 12)
            for month in range(1, 13):
                month_date = date(year, month, 1)
                if month_date >= start_date:
                    if not end_date or month_date <= end_date:
                        monthly_costs[month] += annual_amount / 12

        elif frequency == 'One-Time':
            if start_date.year == year:
                monthly_costs[start_date.month] += amount

    return monthly_costs


def calculate_wholesale_revenue_monthly(deals: List[Dict], year: int = 2026) -> Tuple[Dict[int, float], Dict[int, float]]:
    """
    Calculate monthly wholesale revenue and COGS
    
    Returns: (revenue_dict, cogs_dict) where each is {month: amount}
    """
    monthly_revenue = {month: 0.0 for month in range(1, 13)}
    monthly_cogs = {month: 0.0 for month in range(1, 13)}
    
    for deal in deals:
        # Parse delivery date (revenue recognition date)
        delivery_date_str = deal.get('delivery_date') or deal.get('close_date')
        if not delivery_date_str:
            continue
        
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
        except:
            continue
        
        if delivery_date.year != year:
            continue
        
        # Calculate revenue
        num_pairs = deal.get('num_pairs', 0)
        wholesale_price = deal.get('wholesale_price', 0)
        revenue = num_pairs * wholesale_price
        
        # Calculate COGS
        if 'total_cost' in deal:
            # Use client-provided total cost
            cogs = deal['total_cost']
        else:
            # Calculate from COGS components
            cogs_product = deal.get('cogs_product', 0.25)
            cogs_warehousing = deal.get('cogs_warehousing', 0.06)
            cogs_freight = deal.get('cogs_freight', 0.06)
            cogs_merchant = deal.get('cogs_merchant', 0.03)
            
            total_cogs_rate = cogs_product + cogs_warehousing + cogs_freight + cogs_merchant
            cogs = revenue * total_cogs_rate
        
        # Add to month
        month = delivery_date.month
        monthly_revenue[month] += revenue
        monthly_cogs[month] += cogs
    
    return monthly_revenue, monthly_cogs


def calculate_dtc_revenue_monthly(year: int = 2026, discount_rate: float = 0.0, return_rate: float = 0.0) -> Tuple[Dict[int, float], Dict[int, float]]:
    """
    Calculate monthly DTC revenue and COGS
    Includes discounts and returns for 2027+
    
    Returns: (revenue_dict, cogs_dict)
    """
    monthly_revenue = {month: 0.0 for month in range(1, 13)}
    monthly_cogs = {month: 0.0 for month in range(1, 13)}
    
    if year == 2026:
        # 2026 Forecast from Matt's updated roadmap (Screenshot 2/11/26)
        # V2 (Beta) product - units sold per month
        v2_units = [10, 20, 30, 50, 100, 150, 200, 225, 250, 275, 300, 325]
        v2_aov = 250  # $250 AOV
        
        # Alpha product - starts later in year
        alpha_units = [0, 0, 0, 0, 0, 0, 50, 100, 200, 300, 300, 0]
        alpha_aov = 450  # $450 AOV
        
        cogs_rate = 0.40  # 40% in production
        
        for month in range(1, 13):
            gross_revenue = (v2_units[month-1] * v2_aov + alpha_units[month-1] * alpha_aov)
            
            # Apply discount
            net_revenue = gross_revenue * (1 - discount_rate)
            
            # Apply returns (reduce revenue further)
            final_revenue = net_revenue * (1 - return_rate)
            
            monthly_revenue[month] = final_revenue
            monthly_cogs[month] = gross_revenue * cogs_rate  # COGS on gross
    
    elif year == 2027:
        # 2027 projections (with discounts and returns)
        # Scale up from 2026 - build to 1,000 pairs/month
        # Apply 10% discount and 20% returns
        v2_units = [350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900]
        v2_aov = 250
        
        alpha_units = [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850]
        alpha_aov = 450
        
        cogs_rate = 0.40
        
        for month in range(1, 13):
            gross_revenue = (v2_units[month-1] * v2_aov + alpha_units[month-1] * alpha_aov)
            
            # Apply 10% discount
            net_revenue = gross_revenue * (1 - discount_rate)
            
            # Apply 20% returns
            final_revenue = net_revenue * (1 - return_rate)
            
            monthly_revenue[month] = final_revenue
            monthly_cogs[month] = gross_revenue * cogs_rate
    
    return monthly_revenue, monthly_cogs


def get_cogs_breakdown(revenue: float, year: int = 2026, channel: str = 'DTC') -> Dict[str, float]:
    """
    Get COGS breakdown by component
    
    Returns: Dict with keys: product, warehousing, freight, merchant, total
    """
    if channel == 'DTC':
        if year == 2026:
            # Production scale
            return {
                'product': revenue * 0.25,  # 25% product cost
                'warehousing': revenue * 0.06,  # 6% warehousing
                'freight': revenue * 0.06,  # 6% freight
                'merchant': revenue * 0.03,  # 3% merchant fees
                'total': revenue * 0.40  # 40% total
            }
        else:
            return {
                'product': revenue * 0.25,
                'warehousing': revenue * 0.06,
                'freight': revenue * 0.06,
                'merchant': revenue * 0.03,
                'total': revenue * 0.40
            }
    
    elif channel == 'Wholesale':
        # From deal-specific rates
        return {
            'product': revenue * 0.25,
            'warehousing': revenue * 0.06,
            'freight': revenue * 0.06,
            'merchant': revenue * 0.03,
            'total': revenue * 0.40
        }
    
    return {}


# ============================================================
# INVENTORY & PO CALCULATIONS
# ============================================================

def get_dtc_demand_units(year: int = 2026) -> Dict[str, List[int]]:
    """Get raw DTC demand units by product for a given year."""
    if year == 2026:
        return {
            "Beta": [10, 20, 30, 50, 100, 150, 200, 225, 250, 275, 300, 325],
            "Alpha": [0, 0, 0, 0, 0, 0, 50, 100, 200, 300, 300, 0],
        }
    elif year == 2027:
        return {
            "Beta": [350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900],
            "Alpha": [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850],
        }
    return {"Beta": [0]*12, "Alpha": [0]*12}


def calculate_po_arrivals(po_data: List[Dict], lead_time: int, year: int) -> Dict[str, Dict[int, int]]:
    """Calculate monthly PO arrivals by product for a given year.
    Returns {"Beta": {1:0, 2:2000, ...}, "Alpha": {1:0, ...}}
    """
    arrivals = {"Beta": {m: 0 for m in range(1, 13)}, "Alpha": {m: 0 for m in range(1, 13)}}
    year_offset = (year - 2026) * 12  # 0 for 2026, 12 for 2027

    for po in po_data:
        pairs = po.get('pairs', 0)
        if pairs <= 0:
            continue
        arrival_abs = (po['order_year'] - 2026) * 12 + po['order_month'] + lead_time
        # Check if arrival falls in target year (1-12 for 2026, 13-24 for 2027)
        month_in_year = arrival_abs - year_offset
        if 1 <= month_in_year <= 12:
            product = po.get('product', 'Beta')
            if product in arrivals:
                arrivals[product][month_in_year] += pairs

    return arrivals


def calculate_ws_shipments(wholesale_deals: List[Dict], year: int) -> Dict[str, Dict[int, int]]:
    """Calculate monthly wholesale shipments by product for a given year."""
    shipments = {"Beta": {m: 0 for m in range(1, 13)}, "Alpha": {m: 0 for m in range(1, 13)}}

    for deal in wholesale_deals:
        delivery_str = deal.get('delivery_date') or deal.get('close_date')
        if not delivery_str:
            continue
        try:
            delivery_date = datetime.strptime(delivery_str, '%Y-%m-%d').date()
        except:
            continue
        if delivery_date.year != year:
            continue

        pairs = deal.get('num_pairs', 0)
        product = deal.get('product_type', 'Beta')
        if product in shipments:
            shipments[product][delivery_date.month] += pairs

    return shipments


def calculate_inventory_balance(
    po_data: List[Dict],
    wholesale_deals: List[Dict],
    lead_time: int,
    beg_inv: Dict[str, int],
    dtc_demand: Dict[str, List[int]],
    year: int,
    prior_ending: Dict[str, int] = None,
) -> Dict[str, Dict[str, List]]:
    """Calculate per-product monthly inventory balance.

    Returns:
        {"Beta": {"begin":[...], "arrive":[...], "ws":[...], "available":[...],
                  "demand":[...], "dtc_sales":[...], "ending":[...]},
         "Alpha": {...}}
    """
    arrivals = calculate_po_arrivals(po_data, lead_time, year)
    shipments = calculate_ws_shipments(wholesale_deals, year)

    result = {}
    for product in ["Beta", "Alpha"]:
        begin_list = []
        arrive_list = []
        ws_list = []
        avail_list = []
        demand_list = []
        dtc_list = []
        end_list = []

        for m in range(1, 13):
            # Beginning inventory
            if m == 1:
                if prior_ending and product in prior_ending:
                    begin = prior_ending[product]
                else:
                    begin = beg_inv.get(product, 0)
            else:
                begin = end_list[-1]

            arrive = arrivals[product].get(m, 0)
            ws = shipments[product].get(m, 0)
            available = begin + arrive - ws
            demand = dtc_demand.get(product, [0]*12)[m - 1]
            dtc_sales = min(demand, max(available, 0))
            ending = available - dtc_sales

            begin_list.append(begin)
            arrive_list.append(arrive)
            ws_list.append(ws)
            avail_list.append(available)
            demand_list.append(demand)
            dtc_list.append(dtc_sales)
            end_list.append(ending)

        result[product] = {
            "begin": begin_list,
            "arrive": arrive_list,
            "ws": ws_list,
            "available": avail_list,
            "demand": demand_list,
            "dtc_sales": dtc_list,
            "ending": end_list,
        }

    return result


def calculate_constrained_dtc_revenue(
    inventory_balance: Dict,
    beta_aov: float = 250,
    alpha_aov: float = 450,
    discount_rate: float = 0.0,
    return_rate: float = 0.0,
) -> Dict[str, Dict[int, float]]:
    """Calculate constrained DTC revenue from inventory-limited sales.
    Returns {"gross": {1:..., 12:...}, "net": {1:..., 12:...}}
    """
    gross = {}
    net = {}
    for m in range(1, 13):
        beta_sales = inventory_balance["Beta"]["dtc_sales"][m - 1]
        alpha_sales = inventory_balance["Alpha"]["dtc_sales"][m - 1]
        g = beta_sales * beta_aov + alpha_sales * alpha_aov
        n = g * (1 - discount_rate) * (1 - return_rate)
        gross[m] = g
        net[m] = n
    return {"gross": gross, "net": net}


def calculate_po_payments(
    po_data: List[Dict], lead_time: int, payment_terms: int, year: int
) -> Dict[int, float]:
    """Calculate monthly PO payments for a given year.
    Payment hits cash at: order_month + lead_time + payment_terms (in absolute months).
    Returns {1:0, 2:0, ..., 12:amount}
    """
    payments = {m: 0.0 for m in range(1, 13)}
    year_offset = (year - 2026) * 12

    for po in po_data:
        amount = po.get('amount', 0)
        if amount <= 0:
            continue
        payment_abs = (po['order_year'] - 2026) * 12 + po['order_month'] + lead_time + payment_terms
        month_in_year = payment_abs - year_offset
        if 1 <= month_in_year <= 12:
            payments[month_in_year] += amount

    return payments


def generate_monthly_pl(
    year: int,
    team_members: List[Dict],
    opex_expenses: List[Dict],
    wholesale_deals: List[Dict],
    dtc_discount_rate: float = 0.0,
    dtc_return_rate: float = 0.0,
    po_data: List[Dict] = None,
    inventory_config: Dict = None,
    prior_ending_inv: Dict[str, int] = None,
) -> pd.DataFrame:
    """
    Generate complete monthly P&L integrating all data sources.

    When po_data and inventory_config are provided, DTC revenue is constrained
    by available inventory and DTC Gross Revenue is included for cash flow split.

    Returns: DataFrame with monthly P&L
    """
    ws_revenue, ws_cogs = calculate_wholesale_revenue_monthly(wholesale_deals, year)
    team_costs = calculate_team_costs_monthly(team_members, year)
    opex_costs = calculate_opex_monthly(opex_expenses, year)

    # Determine if inventory-constrained
    use_inventory = po_data is not None and inventory_config is not None
    inv_balance = None

    if use_inventory:
        lead_time = inventory_config.get('lead_time_months', 4)
        beg_inv = {
            "Beta": inventory_config.get('beg_inv_beta', 0),
            "Alpha": inventory_config.get('beg_inv_alpha', 0),
        }
        dtc_demand = get_dtc_demand_units(year)
        inv_balance = calculate_inventory_balance(
            po_data, wholesale_deals, lead_time, beg_inv, dtc_demand, year,
            prior_ending=prior_ending_inv,
        )
        beta_aov = inventory_config.get('beta_aov', 250)
        alpha_aov = inventory_config.get('alpha_aov', 450)
        constr_rev = calculate_constrained_dtc_revenue(
            inv_balance, beta_aov, alpha_aov, dtc_discount_rate, dtc_return_rate,
        )
        # Build DTC dicts from constrained revenue
        dtc_revenue = constr_rev["net"]
        dtc_gross_revenue = constr_rev["gross"]
        cogs_rate = inventory_config.get('cogs_total_rate', 0.40)
        dtc_cogs = {m: dtc_gross_revenue[m] * cogs_rate for m in range(1, 13)}
    else:
        dtc_revenue, dtc_cogs = calculate_dtc_revenue_monthly(year, dtc_discount_rate, dtc_return_rate)
        dtc_gross_revenue = None

    # Build monthly data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    data = []

    for month_num in range(1, 13):
        dtc_rev = dtc_revenue[month_num]
        ws_rev = ws_revenue[month_num]
        total_rev = dtc_rev + ws_rev

        dtc_cog = dtc_cogs[month_num]
        ws_cog = ws_cogs[month_num]
        total_cogs = dtc_cog + ws_cog

        gross_profit = total_rev - total_cogs
        gross_margin = (gross_profit / total_rev * 100) if total_rev > 0 else 0

        team_cost = team_costs[month_num]
        opex_cost = opex_costs[month_num]
        total_opex = team_cost + opex_cost

        ebitda = gross_profit - total_opex

        row = {
            'Month': months[month_num-1],
            'DTC Revenue': dtc_rev,
            'Wholesale Revenue': ws_rev,
            'Total Revenue': total_rev,
            'DTC COGS': dtc_cog,
            'Wholesale COGS': ws_cog,
            'Total COGS': total_cogs,
            'Gross Profit': gross_profit,
            'Gross Margin %': gross_margin,
            'Team Costs': team_cost,
            'Other OpEx': opex_cost,
            'Total OpEx': total_opex,
            'EBITDA': ebitda,
            'EBITDA Margin %': (ebitda / total_rev * 100) if total_rev > 0 else 0,
        }
        if dtc_gross_revenue is not None:
            row['DTC Gross Revenue'] = dtc_gross_revenue[month_num]
        data.append(row)

    return pd.DataFrame(data)
