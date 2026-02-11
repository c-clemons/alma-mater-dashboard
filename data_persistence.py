"""
Data Persistence Module
Handles saving and loading of dashboard data with baseline data support
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from baseline_data import (
    get_baseline_team, 
    get_baseline_opex, 
    get_baseline_wholesale
)


class DataStore:
    """Manages persistent storage for dashboard data"""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize data store with directory path"""
        self.data_dir = data_dir
        self.ensure_data_dir()
        
        # File paths (only for CUSTOM data, not baseline)
        self.team_file = os.path.join(data_dir, "custom_team_members.json")
        self.opex_file = os.path.join(data_dir, "custom_opex_expenses.json")
        self.wholesale_file = os.path.join(data_dir, "custom_wholesale_deals.json")
        self.assumptions_file = os.path.join(data_dir, "model_assumptions.json")
    
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    # Team Members (Baseline + Custom)
    def save_team_members(self, all_team_members: List[Dict[str, Any]]):
        """Save ONLY custom team members (not baseline)"""
        baseline = get_baseline_team()
        baseline_ids = set()
        
        # Create IDs for baseline members
        for member in baseline:
            baseline_id = f"{member['first_name']}_{member['last_name']}_{member.get('start_date', '')}"
            baseline_ids.add(baseline_id)
        
        # Filter out baseline members - only save custom additions
        custom_members = []
        for member in all_team_members:
            member_id = f"{member['first_name']}_{member['last_name']}_{member.get('start_date', '')}"
            if member_id not in baseline_ids:
                custom_members.append(member)
        
        with open(self.team_file, 'w') as f:
            json.dump({
                'custom_team_members': custom_members,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def load_team_members(self) -> List[Dict[str, Any]]:
        """Load baseline + custom team members"""
        # Start with baseline
        all_members = get_baseline_team()
        
        # Add custom members
        if os.path.exists(self.team_file):
            with open(self.team_file, 'r') as f:
                data = json.load(f)
                custom_members = data.get('custom_team_members', [])
                all_members.extend(custom_members)
        
        return all_members
    
    # OpEx Expenses (Baseline + Custom)
    def save_opex_expenses(self, all_expenses: List[Dict[str, Any]]):
        """Save ONLY custom expenses (not baseline)"""
        baseline = get_baseline_opex()
        baseline_ids = set()
        
        # Create IDs for baseline expenses
        for expense in baseline:
            baseline_id = f"{expense['expense_name']}_{expense.get('start_date', '')}"
            baseline_ids.add(baseline_id)
        
        # Filter out baseline expenses - only save custom additions
        custom_expenses = []
        for expense in all_expenses:
            expense_id = f"{expense['expense_name']}_{expense.get('start_date', '')}"
            if expense_id not in baseline_ids:
                custom_expenses.append(expense)
        
        with open(self.opex_file, 'w') as f:
            json.dump({
                'custom_expenses': custom_expenses,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def load_opex_expenses(self) -> List[Dict[str, Any]]:
        """Load baseline + custom OpEx expenses"""
        # Start with baseline
        all_expenses = get_baseline_opex()
        
        # Add custom expenses
        if os.path.exists(self.opex_file):
            with open(self.opex_file, 'r') as f:
                data = json.load(f)
                custom_expenses = data.get('custom_expenses', [])
                all_expenses.extend(custom_expenses)
        
        return all_expenses
    
    # Wholesale Deals (Baseline + Custom)
    def save_wholesale_deals(self, all_deals: List[Dict[str, Any]]):
        """Save ONLY custom deals (not baseline)"""
        baseline = get_baseline_wholesale()
        baseline_ids = set()
        
        # Create IDs for baseline deals
        for deal in baseline:
            baseline_id = f"{deal['customer_name']}_{deal.get('close_date', '')}"
            baseline_ids.add(baseline_id)
        
        # Filter out baseline deals - only save custom additions
        custom_deals = []
        for deal in all_deals:
            deal_id = f"{deal['customer_name']}_{deal.get('close_date', '')}"
            if deal_id not in baseline_ids:
                custom_deals.append(deal)
        
        with open(self.wholesale_file, 'w') as f:
            json.dump({
                'custom_deals': custom_deals,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def load_wholesale_deals(self) -> List[Dict[str, Any]]:
        """Load baseline + custom wholesale deals"""
        # Start with baseline
        all_deals = get_baseline_wholesale()
        
        # Add custom deals
        if os.path.exists(self.wholesale_file):
            with open(self.wholesale_file, 'r') as f:
                data = json.load(f)
                custom_deals = data.get('custom_deals', [])
                all_deals.extend(custom_deals)
        
        return all_deals
    
    # Assumptions
    def save_assumptions(self, assumptions: Dict[str, Any]):
        """Save model assumptions to file"""
        with open(self.assumptions_file, 'w') as f:
            json.dump({
                'assumptions': assumptions,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def load_assumptions(self) -> Dict[str, Any]:
        """Load model assumptions from file"""
        if os.path.exists(self.assumptions_file):
            with open(self.assumptions_file, 'r') as f:
                data = json.load(f)
                return data.get('assumptions', {})
        return {}
    
    # Utility
    def clear_all_data(self):
        """Clear all stored data (use with caution!)"""
        for file_path in [self.team_file, self.opex_file, self.wholesale_file, self.assumptions_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def get_last_updated(self, data_type: str) -> str:
        """Get last updated timestamp for a data type"""
        file_map = {
            'team': self.team_file,
            'opex': self.opex_file,
            'wholesale': self.wholesale_file,
            'assumptions': self.assumptions_file
        }
        
        file_path = file_map.get(data_type)
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('last_updated', 'Unknown')
        return 'Never'


# Global instance
_store = None

def get_data_store() -> DataStore:
    """Get or create global data store instance"""
    global _store
    if _store is None:
        _store = DataStore()
    return _store
