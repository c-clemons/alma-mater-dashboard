"""
Inventory Tracker Page
Manage purchase orders, view inventory balances, and see revenue impact
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from financial_calcs import (
    get_dtc_demand_units,
    calculate_inventory_balance,
    calculate_constrained_dtc_revenue,
    calculate_po_payments,
    calculate_dtc_revenue_monthly,
)
from baseline_data import get_baseline_po_data, get_baseline_inventory_config
from data_persistence import get_data_store

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def _get_inventory_config():
    """Get inventory config from session state or baseline."""
    config = st.session_state.get('inventory_config')
    if not config:
        config = get_baseline_inventory_config()
    return config


def _get_po_data():
    """Get PO data from session state or baseline."""
    po_data = st.session_state.get('po_data')
    if po_data is None:
        po_data = get_baseline_po_data()
    return po_data


def show():
    """Display inventory tracker page."""
    st.markdown('<div class="main-header">Inventory & PO Tracker</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Manage purchase orders, track inventory, and see constrained revenue impact</div>',
        unsafe_allow_html=True,
    )

    po_data = _get_po_data()
    config = _get_inventory_config()
    wholesale_deals = st.session_state.get('wholesale_deals', [])

    tab1, tab2, tab3 = st.tabs([
        "PO Management",
        "Inventory Balance",
        "Revenue Impact",
    ])

    # ---------------------------------------------------------------
    # TAB 1 — PO Management
    # ---------------------------------------------------------------
    with tab1:
        st.markdown("### Purchase Orders")
        st.info(
            "Manage your purchase orders below. Changes automatically update "
            "inventory balance and constrained DTC revenue."
        )

        # Summary metrics
        total_pos = len(po_data)
        beta_pairs = sum(p['pairs'] for p in po_data if p.get('product') == 'Beta')
        alpha_pairs = sum(p['pairs'] for p in po_data if p.get('product') == 'Alpha')
        total_amount = sum(p.get('amount', 0) for p in po_data)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total POs", total_pos)
        col2.metric("Beta Pairs", f"{beta_pairs:,}")
        col3.metric("Alpha Pairs", f"{alpha_pairs:,}")
        col4.metric("Total PO Value", f"${total_amount:,.0f}")

        st.divider()

        # Inventory config inputs
        st.markdown("### Inventory Settings")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            config['lead_time_months'] = st.number_input(
                "Lead Time (months)", min_value=1, max_value=12,
                value=int(config.get('lead_time_months', 4)),
                help="Months from PO order to inventory arrival",
            )
        with c2:
            config['payment_terms_months'] = st.number_input(
                "Payment Terms (months)", min_value=0, max_value=12,
                value=int(config.get('payment_terms_months', 5)),
                help="Months after arrival before cash payment is due",
            )
        with c3:
            config['beg_inv_beta'] = st.number_input(
                "Beginning Inv - Beta", min_value=0,
                value=int(config.get('beg_inv_beta', 2500)),
                step=100,
            )
        with c4:
            config['beg_inv_alpha'] = st.number_input(
                "Beginning Inv - Alpha", min_value=0,
                value=int(config.get('beg_inv_alpha', 500)),
                step=100,
            )
        st.session_state.inventory_config = config

        st.divider()

        # PO list with expandable cards
        st.markdown("### PO Details")

        pos_to_delete = []
        for i, po in enumerate(po_data):
            with st.expander(
                f"{po.get('name', f'PO {i+1}')} — {po.get('product', 'Beta')} | "
                f"{po.get('pairs', 0):,} pairs | ${po.get('amount', 0):,.0f}",
                expanded=False,
            ):
                c1, c2 = st.columns(2)
                with c1:
                    po['name'] = st.text_input("PO Name", value=po.get('name', ''), key=f"po_name_{i}")
                    po['product'] = st.selectbox(
                        "Product", ['Beta', 'Alpha'],
                        index=0 if po.get('product', 'Beta') == 'Beta' else 1,
                        key=f"po_prod_{i}",
                    )
                    po['pairs'] = st.number_input(
                        "Pairs", min_value=0, value=int(po.get('pairs', 0)),
                        step=100, key=f"po_pairs_{i}",
                    )
                with c2:
                    po['amount'] = st.number_input(
                        "Amount ($)", min_value=0.0,
                        value=float(po.get('amount', 0)),
                        step=1000.0, key=f"po_amt_{i}",
                    )
                    po['order_month'] = st.selectbox(
                        "Order Month", list(range(1, 13)),
                        index=po.get('order_month', 1) - 1,
                        format_func=lambda m: MONTHS[m - 1],
                        key=f"po_mo_{i}",
                    )
                    po['order_year'] = st.selectbox(
                        "Order Year", [2026, 2027],
                        index=0 if po.get('order_year', 2026) == 2026 else 1,
                        key=f"po_yr_{i}",
                    )

                # Calculated fields
                lead = config.get('lead_time_months', 4)
                pay = config.get('payment_terms_months', 5)
                arr_abs = (po['order_year'] - 2026) * 12 + po['order_month'] + lead
                pay_abs = arr_abs + pay
                arr_mo = MONTHS[(arr_abs - 1) % 12]
                arr_yr = 2026 + (arr_abs - 1) // 12
                pay_mo = MONTHS[(pay_abs - 1) % 12]
                pay_yr = 2026 + (pay_abs - 1) // 12

                st.caption(
                    f"Arrives: **{arr_mo} {arr_yr}** | "
                    f"Payment Due: **{pay_mo} {pay_yr}** | "
                    f"Cost/Pair: **${po.get('amount', 0) / max(po.get('pairs', 1), 1):,.2f}**"
                )

                if st.button("Delete PO", key=f"del_po_{i}", type="secondary"):
                    pos_to_delete.append(i)

        # Process deletions
        if pos_to_delete:
            for idx in sorted(pos_to_delete, reverse=True):
                po_data.pop(idx)
            st.session_state.po_data = po_data
            st.rerun()

        # Add new PO
        st.divider()
        if st.button("Add New PO", type="primary"):
            po_data.append({
                'name': f'New PO {len(po_data) + 1}',
                'product': 'Beta',
                'pairs': 1000,
                'amount': 45000,
                'order_month': 1,
                'order_year': 2026,
            })
            st.session_state.po_data = po_data
            st.rerun()

        # Reset to baseline
        if st.button("Reset to Baseline POs"):
            st.session_state.po_data = get_baseline_po_data()
            st.session_state.inventory_config = get_baseline_inventory_config()
            st.rerun()

        # Save state
        st.session_state.po_data = po_data

    # ---------------------------------------------------------------
    # TAB 2 — Inventory Balance
    # ---------------------------------------------------------------
    with tab2:
        st.markdown("### Monthly Inventory Balance")

        lead_time = config.get('lead_time_months', 4)
        beg_inv = {
            "Beta": config.get('beg_inv_beta', 2500),
            "Alpha": config.get('beg_inv_alpha', 500),
        }

        for year in [2026, 2027]:
            st.markdown(f"#### {year}")

            dtc_demand = get_dtc_demand_units(year)

            if year == 2027:
                # Use 2026 ending inventory as prior
                inv_2026 = calculate_inventory_balance(
                    po_data, wholesale_deals, lead_time, beg_inv,
                    get_dtc_demand_units(2026), 2026,
                )
                prior_ending = {
                    p: inv_2026[p]["ending"][-1] for p in ["Beta", "Alpha"]
                }
            else:
                prior_ending = None

            inv_balance = calculate_inventory_balance(
                po_data, wholesale_deals, lead_time, beg_inv,
                dtc_demand, year, prior_ending=prior_ending,
            )

            for product in ["Beta", "Alpha"]:
                st.markdown(f"**{product}**")
                bal = inv_balance[product]

                df = pd.DataFrame({
                    'Row': ['Beginning', 'PO Arrivals', 'WS Shipments',
                            'Available for DTC', 'DTC Demand', 'DTC Sales (Constrained)',
                            'Ending Inventory'],
                    **{MONTHS[m]: [
                        bal['begin'][m], bal['arrive'][m], bal['ws'][m],
                        bal['available'][m], bal['demand'][m], bal['dtc_sales'][m],
                        bal['ending'][m],
                    ] for m in range(12)}
                })
                df = df.set_index('Row')

                # Highlight constrained months
                def _highlight_constrained(val, demand_row, col):
                    """Return style for cells where demand > sales (constrained)."""
                    return ''

                st.dataframe(
                    df.style.format("{:,.0f}"),
                    use_container_width=True,
                )

                # Check for constrained months
                constrained = [
                    MONTHS[m] for m in range(12)
                    if bal['demand'][m] > bal['dtc_sales'][m]
                ]
                if constrained:
                    st.warning(f"Supply-constrained months: **{', '.join(constrained)}**")

                st.divider()

        # Ending inventory chart
        st.markdown("### Ending Inventory Over Time")

        # Build 24-month series
        inv_2026 = calculate_inventory_balance(
            po_data, wholesale_deals, lead_time, beg_inv,
            get_dtc_demand_units(2026), 2026,
        )
        prior_end = {p: inv_2026[p]["ending"][-1] for p in ["Beta", "Alpha"]}
        inv_2027 = calculate_inventory_balance(
            po_data, wholesale_deals, lead_time, beg_inv,
            get_dtc_demand_units(2027), 2027, prior_ending=prior_end,
        )

        months_labels = [f"{MONTHS[m]} 26" for m in range(12)] + [f"{MONTHS[m]} 27" for m in range(12)]
        beta_ending = inv_2026["Beta"]["ending"] + inv_2027["Beta"]["ending"]
        alpha_ending = inv_2026["Alpha"]["ending"] + inv_2027["Alpha"]["ending"]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months_labels, y=beta_ending,
            name='Beta', mode='lines+markers',
            line=dict(color='#1f77b4', width=2),
        ))
        fig.add_trace(go.Scatter(
            x=months_labels, y=alpha_ending,
            name='Alpha', mode='lines+markers',
            line=dict(color='#ff7f0e', width=2),
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        fig.update_layout(
            title="Ending Inventory by Product (2026-2027)",
            yaxis_title="Units",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------------
    # TAB 3 — Revenue Impact
    # ---------------------------------------------------------------
    with tab3:
        st.markdown("### Revenue Impact: Unconstrained vs Constrained")
        st.info(
            "Compare what DTC revenue would be with unlimited inventory "
            "vs what's achievable given your PO schedule and inventory levels."
        )

        lead_time = config.get('lead_time_months', 4)
        beg_inv = {
            "Beta": config.get('beg_inv_beta', 2500),
            "Alpha": config.get('beg_inv_alpha', 500),
        }

        for year in [2026, 2027]:
            st.markdown(f"#### {year}")

            dtc_demand = get_dtc_demand_units(year)

            if year == 2027:
                inv_2026 = calculate_inventory_balance(
                    po_data, wholesale_deals, lead_time, beg_inv,
                    get_dtc_demand_units(2026), 2026,
                )
                prior_ending = {p: inv_2026[p]["ending"][-1] for p in ["Beta", "Alpha"]}
            else:
                prior_ending = None

            inv_balance = calculate_inventory_balance(
                po_data, wholesale_deals, lead_time, beg_inv,
                dtc_demand, year, prior_ending=prior_ending,
            )

            # Constrained revenue
            constr = calculate_constrained_dtc_revenue(inv_balance)

            # Unconstrained revenue (demand * AOV)
            unconstr_rev, _ = calculate_dtc_revenue_monthly(year, 0.0, 0.0)

            # Build comparison table
            rows = []
            total_unconstr = 0
            total_constr = 0
            for m in range(1, 13):
                u = unconstr_rev[m]
                c = constr['net'][m]
                delta = c - u
                total_unconstr += u
                total_constr += c
                rows.append({
                    'Month': MONTHS[m - 1],
                    'Unconstrained': u,
                    'Constrained': c,
                    'Delta': delta,
                })

            rows.append({
                'Month': 'TOTAL',
                'Unconstrained': total_unconstr,
                'Constrained': total_constr,
                'Delta': total_constr - total_unconstr,
            })

            df = pd.DataFrame(rows)

            # Format
            display_df = df.copy()
            for col in ['Unconstrained', 'Constrained', 'Delta']:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Chart
            fig = go.Figure()
            chart_df = df[df['Month'] != 'TOTAL']
            fig.add_trace(go.Bar(
                x=chart_df['Month'], y=chart_df['Unconstrained'],
                name='Unconstrained', marker_color='#aec7e8',
            ))
            fig.add_trace(go.Bar(
                x=chart_df['Month'], y=chart_df['Constrained'],
                name='Constrained', marker_color='#1f77b4',
            ))
            fig.update_layout(
                title=f"DTC Revenue: Unconstrained vs Constrained ({year})",
                barmode='group', height=350,
                yaxis_title="Revenue ($)",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Lost revenue callout
            lost = total_unconstr - total_constr
            if lost > 0:
                st.error(f"Lost Revenue Due to Inventory Constraints: **${lost:,.0f}** in {year}")
            else:
                st.success(f"No inventory constraints limiting DTC revenue in {year}.")

            st.divider()

        # PO Payment Schedule
        st.markdown("### PO Payment Schedule")
        lead_time = config.get('lead_time_months', 4)
        pay_terms = config.get('payment_terms_months', 5)

        payment_rows = []
        for year in [2026, 2027]:
            payments = calculate_po_payments(po_data, lead_time, pay_terms, year)
            for m in range(1, 13):
                if payments[m] > 0:
                    payment_rows.append({
                        'Month': f"{MONTHS[m - 1]} {year}",
                        'Payment': payments[m],
                    })

        if payment_rows:
            pay_df = pd.DataFrame(payment_rows)
            pay_df['Payment'] = pay_df['Payment'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(pay_df, use_container_width=True, hide_index=True)
        else:
            st.info("No PO payments scheduled in 2026-2027.")
