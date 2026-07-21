"""
Team Tracker — client view
Shows aggregated headcount and total payroll burn only. Per-person salary
and per-person cost are intentionally hidden.
"""

import streamlit as st
import pandas as pd


def show():
    """Display aggregated team roster (no individual salary/cost figures)."""


    members = st.session_state.get('team_members', [])

    if not members:
        st.info("No team members loaded.")
        return

    # ---- Aggregated metrics ----
    total_headcount = len(members)
    total_annual_cost = sum(
        m.get('total_cost', m.get('annual_salary', 0) * 1.185)
        for m in members
    )
    monthly_payroll = total_annual_cost / 12

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Headcount", f"{total_headcount}")
    with col2:
        st.metric("Total Annual Cost (Burdened)", f"${total_annual_cost:,.0f}")
    with col3:
        st.metric("Monthly Payroll Burn", f"${monthly_payroll:,.0f}")

    st.divider()

    # ---- Roster (no salary / cost columns) ----
    st.markdown("#### Team Members")
    table_rows = []
    for m in members:
        table_rows.append({
            'Name': f"{m.get('first_name', '')} {m.get('last_name', '')}".strip(),
            'Title': m.get('title', ''),
            'Department': m.get('department', ''),
            'Type': m.get('employment_type', ''),
            'Start Date': m.get('start_date', ''),
            'Status': m.get('status', 'Active'),
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    st.divider()

    # ---- Department breakdown (headcount + dept-level total cost) ----
    st.markdown("#### Department Breakdown")
    dept_data = {}
    for m in members:
        dept = m.get('department', 'Other')
        cost = m.get('total_cost', m.get('annual_salary', 0) * 1.185)
        if dept not in dept_data:
            dept_data[dept] = {'count': 0, 'cost': 0}
        dept_data[dept]['count'] += 1
        dept_data[dept]['cost'] += cost

    dept_summary = pd.DataFrame([
        {'Department': dept, 'Headcount': d['count'],
         'Total Annual Cost': f"${d['cost']:,.0f}"}
        for dept, d in dept_data.items()
    ])
    st.dataframe(dept_summary, use_container_width=True, hide_index=True)
