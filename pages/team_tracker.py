"""
Team Tracker
Add and manage team members with salary and burdens
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime


def initialize_team():
    """Initialize team members in session state"""
    if 'team_members' not in st.session_state:
        st.session_state.team_members = []


def add_team_member(member):
    """Add a new team member"""
    st.session_state.team_members.append(member)


def calculate_total_cost(salary, assumptions):
    """Calculate total cost including burdens"""
    benefits = salary * assumptions['benefits_pct']
    taxes = salary * assumptions['payroll_taxes_pct']
    processing = salary * assumptions['processing_pct']
    
    total_burden = benefits + taxes + processing
    total_cost = salary + total_burden
    
    return {
        'salary': salary,
        'benefits': benefits,
        'taxes': taxes,
        'processing': processing,
        'total_burden': total_burden,
        'total_cost': total_cost
    }


def show():
    """Display team tracker"""
    
    st.markdown('<div class="main-header">Team Member Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage team members, salaries, and payroll costs</div>', unsafe_allow_html=True)
    
    # Info about baseline
    st.info("📋 **Baseline Team:** 7 members hard-coded (Ryan, Jenny, Michele, Sukhjit, Nathan, Jay, Marty). You can add custom members below.")
    
    initialize_team()
    
    # Load assumptions for burden calculations
    if 'assumptions' not in st.session_state:
        from pages.assumptions_page import initialize_assumptions
        initialize_assumptions()
    
    assumptions = st.session_state.assumptions
    
    # Tabs
    tab1, tab2 = st.tabs(["Add Team Member", "Team Roster"])
    
    # --- ADD TEAM MEMBER ---
    with tab1:
        st.markdown("### Add New Team Member")
        
        with st.form("new_team_member_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic Information")
                
                first_name = st.text_input("First Name", placeholder="John")
                last_name = st.text_input("Last Name", placeholder="Doe")
                title = st.text_input("Job Title", placeholder="e.g., Marketing Manager")
                
                department = st.selectbox(
                    "Department",
                    ["General & Administrative", "Sales & Marketing", "Research & Development", "Operations"]
                )
                
                employment_type = st.selectbox(
                    "Employment Type",
                    ["Full-Time Employee (FTE)", "Contractor (1099)", "Part-Time", "Consultant"]
                )
            
            with col2:
                st.markdown("#### Compensation")
                
                annual_salary = st.number_input(
                    "Annual Salary ($)",
                    min_value=0.0,
                    value=80000.0,
                    step=5000.0,
                    help="Base annual salary or contract amount"
                )
                
                start_date = st.date_input(
                    "Start Date",
                    value=date(2026, 1, 1)
                )
                
                termination_date = st.date_input(
                    "Termination Date (Optional)",
                    value=None,
                    help="Leave blank if currently employed"
                )
                
                st.markdown("#### Location & Status")
                
                location = st.selectbox(
                    "Location",
                    ["USA", "Remote - USA", "International"]
                )
                
                status = st.selectbox(
                    "Status",
                    ["Active", "Projected", "Terminated"]
                )
            
            # Notes
            notes = st.text_area("Notes", placeholder="Additional details...")
            
            # Calculate preview
            st.markdown("---")
            st.markdown("### Cost Preview")
            
            costs = calculate_total_cost(annual_salary, assumptions)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Base Salary", f"${costs['salary']:,.0f}")
            
            with col2:
                st.metric("Total Burden", f"${costs['total_burden']:,.0f}")
                st.caption(f"{(costs['total_burden']/costs['salary']*100):.1f}% of salary")
            
            with col3:
                st.metric("Total Annual Cost", f"${costs['total_cost']:,.0f}")
            
            with col4:
                st.metric("Monthly Cost", f"${costs['total_cost']/12:,.0f}")
            
            # Burden breakdown
            with st.expander("View Burden Breakdown"):
                burden_df = pd.DataFrame([
                    {'Component': 'Benefits', 'Amount': costs['benefits'], 'Rate': f"{assumptions['benefits_pct']*100:.1f}%"},
                    {'Component': 'Payroll Taxes', 'Amount': costs['taxes'], 'Rate': f"{assumptions['payroll_taxes_pct']*100:.1f}%"},
                    {'Component': 'Processing', 'Amount': costs['processing'], 'Rate': f"{assumptions['processing_pct']*100:.1f}%"},
                ])
                burden_df['Amount'] = burden_df['Amount'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(burden_df, use_container_width=True, hide_index=True)
            
            # Submit
            submitted = st.form_submit_button("Save Team Member", type="primary", use_container_width=True)
            
            if submitted:
                if not first_name or not last_name:
                    st.error("First and Last Name are required")
                else:
                    # Create team member object
                    member = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'title': title,
                        'department': department,
                        'employment_type': employment_type,
                        'annual_salary': annual_salary,
                        'start_date': start_date.isoformat(),
                        'termination_date': termination_date.isoformat() if termination_date else None,
                        'location': location,
                        'status': status,
                        'notes': notes,
                        'created_at': datetime.now().isoformat(),
                        **costs
                    }
                    
                    add_team_member(member)
                    st.success(f"Added {first_name} {last_name} to the team!")
                    st.balloons()
    
    # --- TEAM ROSTER ---
    with tab2:
        st.markdown("### Current Team Roster")
        
        if len(st.session_state.team_members) == 0:
            st.info("No team members yet. Add your first team member in the 'Add Team Member' tab!")
        else:
            # Summary metrics
            total_annual_cost = sum(m['total_cost'] for m in st.session_state.team_members)
            total_headcount = len(st.session_state.team_members)
            avg_salary = sum(m['annual_salary'] for m in st.session_state.team_members) / total_headcount
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Headcount", f"{total_headcount}")
            
            with col2:
                st.metric("Total Annual Cost", f"${total_annual_cost:,.0f}")
            
            with col3:
                st.metric("Monthly Payroll", f"${total_annual_cost/12:,.0f}")
            
            with col4:
                st.metric("Avg Salary", f"${avg_salary:,.0f}")
            
            st.divider()
            
            # Team table
            st.markdown("#### Team Members")
            
            team_df = pd.DataFrame(st.session_state.team_members)
            
            # Format for display
            display_df = team_df[[
                'first_name', 'last_name', 'title', 'department',
                'employment_type', 'annual_salary', 'total_cost',
                'start_date', 'status'
            ]].copy()
            
            display_df.columns = [
                'First Name', 'Last Name', 'Title', 'Department',
                'Type', 'Base Salary', 'Total Cost',
                'Start Date', 'Status'
            ]
            
            # Format currency
            display_df['Base Salary'] = display_df['Base Salary'].apply(lambda x: f"${x:,.0f}")
            display_df['Total Cost'] = display_df['Total Cost'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Department breakdown
            st.divider()
            st.markdown("#### Department Breakdown")
            
            dept_summary = team_df.groupby('department').agg({
                'first_name': 'count',
                'total_cost': 'sum'
            }).reset_index()
            dept_summary.columns = ['Department', 'Headcount', 'Total Annual Cost']
            dept_summary['Total Annual Cost'] = dept_summary['Total Annual Cost'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(dept_summary, use_container_width=True, hide_index=True)
            
            # Export
            st.divider()
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if st.button("Export to CSV", use_container_width=True):
                    csv = team_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"team_roster_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("Clear All Team Members", type="secondary", use_container_width=True):
                    if st.session_state.get('confirm_clear_team', False):
                        st.session_state.team_members = []
                        st.session_state.confirm_clear_team = False
                        st.success("All team members cleared!")
                        st.rerun()
                    else:
                        st.session_state.confirm_clear_team = True
                        st.warning("Click again to confirm deletion")
