"""
Fundraising Events Page
Manage fundraising rounds and track their impact on cash flow
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from baseline_data import get_baseline_fundraising


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

STATUS_OPTIONS = ["Projected", "Committed", "Closed", "TBD"]


def show():
    st.markdown('<div class="main-header">Fundraising Events</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Plan and track fundraising rounds and their cash flow impact</div>', unsafe_allow_html=True)

    # Load fundraising rounds from session state
    if 'fundraising_rounds' not in st.session_state:
        from data_persistence import get_data_store
        store = get_data_store()
        saved = store.load_fundraising()
        if saved:
            st.session_state.fundraising_rounds = saved
        else:
            st.session_state.fundraising_rounds = get_baseline_fundraising()

    rounds = st.session_state.fundraising_rounds

    # --- SAFE Notes Already Raised ---
    st.markdown("## Prior Funding")
    assumptions = st.session_state.get('assumptions', {})
    safe_raised = assumptions.get('safe_notes_raised', 308000.0)
    new_safe = st.number_input(
        "SAFE Notes Already Raised ($)",
        min_value=0.0,
        value=float(safe_raised),
        step=10000.0,
        help="Total amount raised via SAFE notes prior to 2026"
    )
    if new_safe != safe_raised:
        assumptions['safe_notes_raised'] = new_safe
        st.session_state.assumptions = assumptions

    st.divider()

    # --- Fundraising Rounds ---
    st.markdown("## Planned Fundraising Rounds")
    st.info("Add fundraising events below. These will be reflected in your Cash Flow & Runway projections.")

    # Display existing rounds in editable form
    changed = False
    rounds_to_keep = []

    for i, rnd in enumerate(rounds):
        with st.expander(f"**{rnd.get('name', f'Round {i+1}')}** — ${rnd.get('amount', 0):,.0f} | {MONTHS[rnd.get('month', 1)-1]} {rnd.get('year', 2026)} | {rnd.get('status', 'TBD')}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Round Name", value=rnd.get('name', ''), key=f"fr_name_{i}")
                amount = st.number_input("Amount ($)", min_value=0.0, value=float(rnd.get('amount', 0)),
                                         step=10000.0, key=f"fr_amt_{i}")
            with col2:
                month = st.selectbox("Month", options=list(range(1, 13)),
                                     index=rnd.get('month', 1) - 1,
                                     format_func=lambda m: MONTHS[m-1],
                                     key=f"fr_mo_{i}")
                year = st.number_input("Year", min_value=2025, max_value=2030,
                                       value=int(rnd.get('year', 2026)), key=f"fr_yr_{i}")

            col3, col4 = st.columns(2)
            with col3:
                status_idx = STATUS_OPTIONS.index(rnd.get('status', 'TBD')) if rnd.get('status') in STATUS_OPTIONS else 3
                status = st.selectbox("Status", options=STATUS_OPTIONS, index=status_idx, key=f"fr_st_{i}")
            with col4:
                notes = st.text_input("Notes", value=rnd.get('notes', ''), key=f"fr_notes_{i}")

            # Delete button
            col_del, col_space = st.columns([1, 3])
            with col_del:
                delete = st.button("Delete Round", key=f"fr_del_{i}", type="secondary")

            if delete:
                changed = True
                continue  # skip adding to rounds_to_keep

            updated = {
                'name': name,
                'amount': amount,
                'month': month,
                'year': year,
                'status': status,
                'notes': notes,
            }

            if updated != rnd:
                changed = True

            rounds_to_keep.append(updated)

    # Update if changed
    if changed:
        st.session_state.fundraising_rounds = rounds_to_keep
        rounds = rounds_to_keep

    st.divider()

    # --- Add New Round ---
    st.markdown("### Add New Round")
    with st.form("add_round_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Round Name", value="")
            new_amount = st.number_input("Amount ($)", min_value=0.0, value=0.0, step=10000.0)
        with col2:
            new_month = st.selectbox("Month", options=list(range(1, 13)),
                                     format_func=lambda m: MONTHS[m-1])
            new_year = st.number_input("Year", min_value=2025, max_value=2030, value=2026)

        col3, col4 = st.columns(2)
        with col3:
            new_status = st.selectbox("Status", options=STATUS_OPTIONS, index=3)
        with col4:
            new_notes = st.text_input("Notes", value="")

        submitted = st.form_submit_button("Add Round", type="primary")
        if submitted and new_name and new_amount > 0:
            new_round = {
                'name': new_name,
                'amount': new_amount,
                'month': new_month,
                'year': int(new_year),
                'status': new_status,
                'notes': new_notes,
            }
            rounds.append(new_round)
            st.session_state.fundraising_rounds = rounds
            st.success(f"Added **{new_name}** — ${new_amount:,.0f} in {MONTHS[new_month-1]} {int(new_year)}")
            st.rerun()

    st.divider()

    # --- Summary ---
    st.markdown("## Fundraising Summary")

    if rounds:
        summary_data = []
        for rnd in rounds:
            summary_data.append({
                'Round': rnd.get('name', ''),
                'Amount': rnd.get('amount', 0),
                'Timing': f"{MONTHS[rnd.get('month', 1)-1]} {rnd.get('year', 2026)}",
                'Status': rnd.get('status', 'TBD'),
                'Notes': rnd.get('notes', ''),
            })

        summary_df = pd.DataFrame(summary_data)
        total_planned = summary_df['Amount'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Planned Fundraising", f"${total_planned:,.0f}")
        with col2:
            st.metric("SAFE Notes Raised", f"${new_safe:,.0f}")
        with col3:
            st.metric("Total Capital (Raised + Planned)", f"${new_safe + total_planned:,.0f}")

        # Format for display
        display_df = summary_df.copy()
        display_df['Amount'] = display_df['Amount'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Timeline view
        st.markdown("### Timeline")
        for yr in sorted(set(r.get('year', 2026) for r in rounds)):
            yr_rounds = [r for r in rounds if r.get('year') == yr]
            yr_total = sum(r.get('amount', 0) for r in yr_rounds)
            st.markdown(f"**{yr}** — ${yr_total:,.0f} total")
            for r in sorted(yr_rounds, key=lambda x: x.get('month', 0)):
                status_emoji = {"Closed": "✅", "Committed": "🟢", "Projected": "🟡", "TBD": "⚪"}.get(r.get('status'), "⚪")
                st.markdown(f"  - {status_emoji} {MONTHS[r.get('month',1)-1]}: **{r.get('name')}** — ${r.get('amount',0):,.0f} ({r.get('status')})")
    else:
        st.info("No fundraising rounds planned. Add one above.")

    # Save
    if st.button("Save Fundraising Data", type="primary"):
        from data_persistence import get_data_store
        store = get_data_store()
        store.save_fundraising(rounds)
        st.success("Fundraising data saved.")
