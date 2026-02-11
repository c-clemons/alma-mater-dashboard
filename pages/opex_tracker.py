"""
OpEx Expense Tracker
Add and manage operating expenses
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date


def initialize_expenses():
    """Initialize expenses in session state"""
    if 'opex_expenses' not in st.session_state:
        st.session_state.opex_expenses = []


def add_expense(expense):
    """Add a new expense"""
    st.session_state.opex_expenses.append(expense)


def show():
    """Display OpEx tracker"""
    
    st.markdown('<div class="main-header">Operating Expense Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage recurring and one-time operating expenses</div>', unsafe_allow_html=True)
    
    initialize_expenses()
    
    # Tabs
    tab1, tab2 = st.tabs(["Add Expense", "Expense List"])
    
    # --- ADD EXPENSE ---
    with tab1:
        st.markdown("### Add New Operating Expense")
        
        with st.form("new_expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Expense Details")
                
                expense_name = st.text_input(
                    "Expense Name",
                    placeholder="e.g., Shopify Subscription, Office Rent"
                )
                
                category = st.selectbox(
                    "Category",
                    [
                        "Systems & Software",
                        "Marketing & Advertising",
                        "Professional Services",
                        "Rent & Facilities",
                        "Travel & Entertainment",
                        "Office Supplies",
                        "Insurance",
                        "Other"
                    ]
                )
                
                vendor = st.text_input(
                    "Vendor/Payee",
                    placeholder="e.g., Shopify, WeWork"
                )
                
                frequency = st.selectbox(
                    "Frequency",
                    ["Monthly", "Quarterly", "Annual", "One-Time"]
                )
            
            with col2:
                st.markdown("#### Cost Information")
                
                monthly_amount = st.number_input(
                    "Monthly Amount ($)",
                    min_value=0.0,
                    value=0.0,
                    step=10.0,
                    help="For recurring expenses, enter monthly cost"
                )
                
                start_date = st.date_input(
                    "Start Date",
                    value=date(2026, 1, 1)
                )
                
                end_date = st.date_input(
                    "End Date (Optional)",
                    value=None,
                    help="Leave blank for ongoing expenses"
                )
                
                growth_rate = st.number_input(
                    "Annual Growth Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    help="Expected annual increase"
                ) / 100
            
            # Notes
            notes = st.text_area("Notes", placeholder="Additional details...")
            
            # Calculate preview
            st.markdown("---")
            st.markdown("### Cost Preview")
            
            # Annual calculation
            if frequency == "Monthly":
                annual_cost = monthly_amount * 12
            elif frequency == "Quarterly":
                annual_cost = monthly_amount * 4
            elif frequency == "Annual":
                annual_cost = monthly_amount
            else:  # One-Time
                annual_cost = monthly_amount
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Monthly Cost", f"${monthly_amount:,.0f}")
            
            with col2:
                st.metric("Annual Cost (Year 1)", f"${annual_cost:,.0f}")
            
            with col3:
                if growth_rate > 0:
                    year_2_cost = annual_cost * (1 + growth_rate)
                    st.metric("Annual Cost (Year 2)", f"${year_2_cost:,.0f}")
                else:
                    st.metric("Growth Rate", "0%")
            
            # Submit
            submitted = st.form_submit_button("Save Expense", type="primary", use_container_width=True)
            
            if submitted:
                if not expense_name:
                    st.error("Expense Name is required")
                else:
                    # Create expense object
                    expense = {
                        'expense_name': expense_name,
                        'category': category,
                        'vendor': vendor,
                        'frequency': frequency,
                        'monthly_amount': monthly_amount,
                        'annual_cost': annual_cost,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat() if end_date else None,
                        'growth_rate': growth_rate,
                        'notes': notes,
                        'created_at': datetime.now().isoformat(),
                    }
                    
                    add_expense(expense)
                    st.success(f"Added expense: {expense_name}")
                    st.balloons()
    
    # --- EXPENSE LIST ---
    with tab2:
        st.markdown("### Operating Expense List")
        
        if len(st.session_state.opex_expenses) == 0:
            st.info("No expenses yet. Add your first expense in the 'Add Expense' tab!")
        else:
            # Summary metrics
            total_monthly = sum(e['monthly_amount'] for e in st.session_state.opex_expenses)
            total_annual = sum(e['annual_cost'] for e in st.session_state.opex_expenses)
            expense_count = len(st.session_state.opex_expenses)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Expenses", f"{expense_count}")
            
            with col2:
                st.metric("Monthly Total", f"${total_monthly:,.0f}")
            
            with col3:
                st.metric("Annual Total", f"${total_annual:,.0f}")
            
            with col4:
                # Calculate by category
                categories = set(e['category'] for e in st.session_state.opex_expenses)
                st.metric("Categories", f"{len(categories)}")
            
            st.divider()
            
            # Expense table
            st.markdown("#### All Expenses")
            
            expenses_df = pd.DataFrame(st.session_state.opex_expenses)
            
            # Format for display
            display_df = expenses_df[[
                'expense_name', 'category', 'vendor', 'frequency',
                'monthly_amount', 'annual_cost', 'start_date'
            ]].copy()
            
            display_df.columns = [
                'Expense', 'Category', 'Vendor', 'Frequency',
                'Monthly', 'Annual', 'Start Date'
            ]
            
            # Format currency
            display_df['Monthly'] = display_df['Monthly'].apply(lambda x: f"${x:,.0f}")
            display_df['Annual'] = display_df['Annual'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Category breakdown
            st.divider()
            st.markdown("#### Breakdown by Category")
            
            cat_summary = expenses_df.groupby('category').agg({
                'expense_name': 'count',
                'monthly_amount': 'sum',
                'annual_cost': 'sum'
            }).reset_index()
            cat_summary.columns = ['Category', 'Count', 'Monthly Total', 'Annual Total']
            cat_summary['Monthly Total'] = cat_summary['Monthly Total'].apply(lambda x: f"${x:,.0f}")
            cat_summary['Annual Total'] = cat_summary['Annual Total'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(cat_summary, use_container_width=True, hide_index=True)
            
            # Export
            st.divider()
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if st.button("Export to CSV", use_container_width=True):
                    csv = expenses_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"opex_expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("Clear All Expenses", type="secondary", use_container_width=True):
                    if st.session_state.get('confirm_clear_expenses', False):
                        st.session_state.opex_expenses = []
                        st.session_state.confirm_clear_expenses = False
                        st.success("All expenses cleared!")
                        st.rerun()
                    else:
                        st.session_state.confirm_clear_expenses = True
                        st.warning("Click again to confirm deletion")
