"""
QBO Import Page
Upload QuickBooks Online exports to update actuals in the model
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from io import BytesIO

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from qbo_parser import (
    parse_qbo_file, build_actuals_dataframe, actuals_to_pl_format,
    serialize_qbo_data, MONTHS
)


def show():
    st.markdown('<div class="main-header">QBO Actuals Import</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload QuickBooks P&L and Balance Sheet to update actuals</div>', unsafe_allow_html=True)

    # Current status
    qbo_data = st.session_state.get('qbo_actuals')
    if qbo_data:
        last_mo = qbo_data.get('last_month', 0)
        last_yr = qbo_data.get('last_year', 0)
        cash = qbo_data.get('latest_cash', 0)
        st.success(
            f"Actuals loaded through **{MONTHS[last_mo - 1]} {last_yr}** | "
            f"Cash Balance: **${cash:,.2f}**"
        )
    else:
        st.warning("No QBO actuals loaded. Upload a file below to get started.")

    st.divider()

    # File upload
    st.markdown("## Upload QBO Export")
    st.markdown(
        "Export your **Profit and Loss** and **Balance Sheet** from QuickBooks Online "
        "as a single Excel file (.xlsx). The file should have two tabs: "
        "'Profit and Loss' and 'Balance Sheet' with monthly columns."
    )

    uploaded_file = st.file_uploader(
        "Choose QBO Excel file",
        type=["xlsx"],
        help="Export from QBO: Reports > Profit and Loss > Customize > Monthly columns > Export to Excel"
    )

    if uploaded_file is not None:
        try:
            file_bytes = BytesIO(uploaded_file.getvalue())
            parsed = parse_qbo_file(file_bytes)

            st.success(f"File parsed successfully.")

            # Show summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Months Found", len(parsed['months_found']))
            with col2:
                last_mo = parsed['last_month']
                last_yr = parsed['last_year']
                st.metric("Latest Month", f"{MONTHS[last_mo - 1]} {last_yr}")
            with col3:
                st.metric("Cash Balance", f"${parsed['latest_cash']:,.2f}")

            st.divider()

            # Preview 2025 actuals
            st.markdown("### 2025 P&L Preview")
            actuals_25 = build_actuals_dataframe(parsed['pl_data'], 2025)
            rows_25 = actuals_to_pl_format(actuals_25)
            df_25 = pd.DataFrame(rows_25)

            # Transpose: months as columns, metrics as rows
            key_cols = ['DTC Revenue', 'Wholesale Revenue', 'Total Revenue',
                        'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']
            transposed_25 = df_25.set_index('Month')[key_cols].T
            transposed_25_fmt = transposed_25.applymap(lambda x: f"${x:,.0f}" if x != 0 else "-")

            st.dataframe(transposed_25_fmt, use_container_width=True)

            totals_25 = df_25[['Total Revenue', 'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']].sum()
            st.markdown(
                f"**FY 2025 Totals:** Revenue: ${totals_25['Total Revenue']:,.0f} | "
                f"COGS: ${totals_25['Total COGS']:,.0f} | "
                f"GP: ${totals_25['Gross Profit']:,.0f} | "
                f"OpEx: ${totals_25['Total OpEx']:,.0f} | "
                f"EBITDA: ${totals_25['EBITDA']:,.0f}"
            )

            # Preview 2026 actuals if available
            has_2026 = any(
                parsed['pl_data'].get('Total Revenue', {}).get((2026, m), 0)
                for m in range(1, 13)
            )
            if has_2026:
                st.divider()
                st.markdown("### 2026 YTD Actuals Preview")
                max_26_month = max(
                    (mo for yr, mo in parsed['months_found'] if yr == 2026),
                    default=0
                )
                actuals_26 = build_actuals_dataframe(parsed['pl_data'], 2026, max_26_month)
                rows_26 = actuals_to_pl_format(actuals_26)
                df_26 = pd.DataFrame(rows_26)

                transposed_26 = df_26.set_index('Month')[key_cols].T
                transposed_26_fmt = transposed_26.applymap(lambda x: f"${x:,.0f}" if x != 0 else "-")

                st.dataframe(transposed_26_fmt, use_container_width=True)

                totals_26 = df_26[['Total Revenue', 'Total COGS', 'Gross Profit', 'Total OpEx', 'EBITDA']].sum()
                st.markdown(
                    f"**2026 YTD Totals ({MONTHS[max_26_month - 1]}):** "
                    f"Revenue: ${totals_26['Total Revenue']:,.0f} | "
                    f"COGS: ${totals_26['Total COGS']:,.0f} | "
                    f"GP: ${totals_26['Gross Profit']:,.0f} | "
                    f"OpEx: ${totals_26['Total OpEx']:,.0f} | "
                    f"EBITDA: ${totals_26['EBITDA']:,.0f}"
                )

            # Cash balances
            if parsed['cash_data']:
                st.divider()
                st.markdown("### Cash Balances (from Balance Sheet)")
                cash_rows = []
                for (yr, mo) in sorted(parsed['cash_data'].keys()):
                    cash_rows.append({
                        'Period': f"{MONTHS[mo - 1]} {yr}",
                        'Cash Balance': parsed['cash_data'][(yr, mo)]
                    })
                cash_df = pd.DataFrame(cash_rows)
                cash_df['Cash Balance'] = cash_df['Cash Balance'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(cash_df, use_container_width=True, hide_index=True)

            st.divider()

            # Save button
            if st.button("Save QBO Actuals to Model", type="primary"):
                serialized = serialize_qbo_data(parsed)
                st.session_state['qbo_actuals'] = serialized

                # Update cash balance in session
                if parsed['latest_cash']:
                    assumptions = st.session_state.get('assumptions', {})
                    assumptions['starting_cash_2026'] = parsed['latest_cash']
                    st.session_state['assumptions'] = assumptions

                # Save to persistence
                from data_persistence import get_data_store
                store = get_data_store()
                store.save_qbo_actuals(serialized)

                st.success(
                    f"QBO actuals saved through {MONTHS[last_mo - 1]} {last_yr}. "
                    f"Cash balance updated to ${parsed['latest_cash']:,.2f}. "
                    f"Variance Analysis tab now has live data."
                )
                st.rerun()

        except Exception as e:
            st.error(f"Error parsing file: {str(e)}")
            st.markdown("**Expected format:** QBO export with 'Profit and Loss' and 'Balance Sheet' tabs, monthly columns starting at row 5.")

    st.divider()

    # Instructions
    with st.expander("How to export from QuickBooks Online"):
        st.markdown("""
**Steps to export your QBO file:**

1. Log into QuickBooks Online
2. Go to **Reports** > **Profit and Loss**
3. Set the date range (e.g., Feb 2025 - Jan 2026)
4. Click **Customize** > Display: **Months**
5. Click **Run Report**
6. Click **Export to Excel** (top right)
7. Repeat for **Balance Sheet** (same date range, monthly)
8. Combine both into one Excel file with two tabs
9. Upload the file above

**Monthly Update Process:**
- Each month after books are closed, export a new file
- Upload here to refresh actuals
- The Variance Analysis tab will automatically update
""")
