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
    Calculate monthly team costs including Rippling burdens starting May 2026
    
    Returns: Dict of {month: total_cost}
    """
    monthly_costs = {month: 0.0 for month in range(1, 13)}
    rippling = get_rippling_burdens()
    
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
            
            # Add burdens
            if member.get('employment_type') == 'Contractor (1099)':
                # No burdens for contractors
                pass
            else:
                # W2 employees get burdens
                if month >= rippling['start_month']:
                    # Rippling PEO starts in May
                    cost += rippling['rippling']  # $137/month
                    cost += rippling['healthcare']  # $697.91/month
                    cost += rippling['futa']  # $3.50/month
                    cost += monthly_salary * rippling['medicare']  # 1.45%
                    cost += monthly_salary * rippling['soc_secur']  # 6.2%
                    cost += monthly_salary * rippling['ca_ett']  # 0.1% (CA only)
                else:
                    # Pre-Rippling (simplified burdens)
                    cost += monthly_salary * 0.10  # Benefits 10%
                    cost += monthly_salary * 0.08  # Payroll taxes 8%
                    cost += monthly_salary * 0.005  # Processing 0.5%
            
            monthly_costs[month] += cost
    
    return monthly_costs


def calculate_opex_monthly(opex_expenses: List[Dict], year: int = 2026) -> Dict[int, float]:
    """
    Calculate monthly OpEx costs
    
    Returns: Dict of {month: total_cost}
    """
    monthly_costs = {month: 0.0 for month in range(1, 13)}
    
    for expense in opex_expenses:
        frequency = expense.get('frequency', 'Monthly')
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
            # Allocate in months 3, 6, 9, 12
            for month in [3, 6, 9, 12]:
                month_date = date(year, month, 1)
                if month_date >= start_date:
                    if not end_date or month_date <= end_date:
                        monthly_costs[month] += amount * 3
        
        elif frequency == 'Annual':
            # Allocate full amount in December or spread evenly
            annual_amount = expense.get('annual_cost', amount * 12)
            for month in range(1, 13):
                month_date = date(year, month, 1)
                if month_date >= start_date:
                    if not end_date or month_date <= end_date:
                        monthly_costs[month] += annual_amount / 12
        
        elif frequency == 'One-Time':
            # Allocate in start month
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


def generate_monthly_pl(
    year: int,
    team_members: List[Dict],
    opex_expenses: List[Dict],
    wholesale_deals: List[Dict],
    dtc_discount_rate: float = 0.0,
    dtc_return_rate: float = 0.0
) -> pd.DataFrame:
    """
    Generate complete monthly P&L integrating all data sources
    
    Returns: DataFrame with monthly P&L
    """
    # Calculate all components
    dtc_revenue, dtc_cogs = calculate_dtc_revenue_monthly(year, dtc_discount_rate, dtc_return_rate)
    ws_revenue, ws_cogs = calculate_wholesale_revenue_monthly(wholesale_deals, year)
    team_costs = calculate_team_costs_monthly(team_members, year)
    opex_costs = calculate_opex_monthly(opex_expenses, year)
    
    # Build monthly data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    data = []
    
    for month_num in range(1, 13):
        # Revenue
        dtc_rev = dtc_revenue[month_num]
        ws_rev = ws_revenue[month_num]
        total_rev = dtc_rev + ws_rev
        
        # COGS
        dtc_cog = dtc_cogs[month_num]
        ws_cog = ws_cogs[month_num]
        total_cogs = dtc_cog + ws_cog
        
        # Gross profit
        gross_profit = total_rev - total_cogs
        gross_margin = (gross_profit / total_rev * 100) if total_rev > 0 else 0
        
        # Operating expenses
        team_cost = team_costs[month_num]
        opex_cost = opex_costs[month_num]
        total_opex = team_cost + opex_cost
        
        # EBITDA
        ebitda = gross_profit - total_opex
        
        data.append({
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
            'EBITDA Margin %': (ebitda / total_rev * 100) if total_rev > 0 else 0
        })
    
    return pd.DataFrame(data)
