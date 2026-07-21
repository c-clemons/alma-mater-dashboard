"""
Shopify Analytics - Deep dive into sales, orders, products, discounts, and inventory.
Auto-pulls from Shopify Admin API.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from shopify_client import get_shopify_data, is_configured, fetch_orders_ytd, fetch_products

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def show():

    if not is_configured():
        st.error("Shopify not configured. Add `.env` file with SHOPIFY_STORE and SHOPIFY_ACCESS_TOKEN.")
        return

    # Refresh button
    col_r1, col_r2 = st.columns([4, 1])
    with col_r2:
        if st.button("Refresh Data"):
            for key in list(st.session_state.keys()):
                if key.startswith('shopify_data_'):
                    del st.session_state[key]

    with st.spinner("Fetching Shopify data..."):
        data = get_shopify_data(2026)

    if not data:
        st.error("Failed to fetch Shopify data.")
        return

    so = data['orders']
    inv = data['inventory']
    fetched = data.get('_fetched_at', 'Unknown')

    st.caption(f"Data fetched at {fetched[:19]} | {so['total_orders']} orders YTD")

    # ================================================================
    # TOP-LEVEL KPIS
    # ================================================================
    st.markdown("## YTD Summary")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Orders", f"{so['total_orders']:,}")
    with c2:
        st.metric("Units Sold", f"{so['total_units']:,}")
    with c3:
        st.metric("Adjusted Gross", f"${so['total_net']:,.0f}",
                  help="Gross Sales − Discounts (pre-tax, pre-shipping, pre-returns). Matches Matt's BI tool hero metric \"Adjusted Gross (calc'd)\".")
    with c4:
        st.metric("Discounts", f"${so['total_discounts']:,.0f}",
                  delta=f"{so['discount_rate']:.0f}%", delta_color="inverse")
    with c5:
        st.metric("AOV", f"${so['aov']:,.2f}")

    st.divider()

    # ================================================================
    # CHANNEL BREAKDOWN
    # ================================================================
    st.markdown("## Channel Breakdown")

    channel = so['channel']
    ch_data = []
    for ch_name in ['DTC', 'Wholesale', 'Gifting']:
        ch = channel.get(ch_name, {})
        ch_data.append({
            'Channel': ch_name,
            'Orders': ch.get('orders', 0),
            'Units': ch.get('units', 0),
            'Adjusted Gross': ch.get('net', 0),
        })
    ch_df = pd.DataFrame(ch_data)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(data=[go.Pie(
            labels=ch_df['Channel'], values=ch_df['Adjusted Gross'],
            hole=0.4, marker=dict(colors=['#2E86AB', '#A23B72', '#95D5B2'])
        )])
        fig.update_layout(title='Adjusted Gross by Channel', height=300)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure(data=[go.Pie(
            labels=ch_df['Channel'], values=ch_df['Units'],
            hole=0.4, marker=dict(colors=['#2E86AB', '#A23B72', '#95D5B2'])
        )])
        fig.update_layout(title='Units Sold by Channel', height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Channel table
    ch_display = ch_df.copy()
    ch_display['Adjusted Gross'] = ch_display['Adjusted Gross'].apply(lambda x: f"${x:,.0f}")
    st.dataframe(ch_display, use_container_width=True, hide_index=True)

    st.divider()

    # ================================================================
    # MONTHLY TREND
    # ================================================================
    st.markdown("## Monthly Trend")

    monthly = so['monthly']
    months_with_data = [m for m in monthly if m['orders'] > 0]

    if months_with_data:
        m_df = pd.DataFrame(months_with_data)

        # Adjusted Gross chart with column-top totals
        totals = m_df['dtc_net'] + m_df['ws_net']
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Bar(
            name='DTC Adj Gross', x=m_df['month_name'], y=m_df['dtc_net'],
            marker_color='#2E86AB'
        ))
        fig_rev.add_trace(go.Bar(
            name='Wholesale Adj Gross', x=m_df['month_name'], y=m_df['ws_net'],
            marker_color='#A23B72'
        ))
        # Column-top totals
        fig_rev.add_trace(go.Scatter(
            x=m_df['month_name'], y=totals,
            mode='text',
            text=[f"${v:,.0f}" for v in totals],
            textposition='top center',
            textfont=dict(size=12, color='#111'),
            showlegend=False,
            hoverinfo='skip',
        ))
        fig_rev.update_layout(
            title='Monthly Adjusted Gross by Channel', barmode='stack',
            height=370, yaxis_tickformat='$,.0f',
            yaxis=dict(range=[0, float(totals.max()) * 1.15]) if len(totals) else None,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_rev, use_container_width=True)

        # Orders & units chart
        fig_ou = make_subplots(specs=[[{"secondary_y": True}]])
        fig_ou.add_trace(go.Bar(
            name='Orders', x=m_df['month_name'], y=m_df['orders'],
            marker_color='#457B9D'
        ), secondary_y=False)
        fig_ou.add_trace(go.Scatter(
            name='Units', x=m_df['month_name'], y=m_df['units'],
            mode='lines+markers', line=dict(color='#E63946', width=2),
            marker=dict(size=8),
        ), secondary_y=True)
        fig_ou.update_layout(
            title='Monthly Orders & Units', height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig_ou.update_yaxes(title_text="Orders", secondary_y=False)
        fig_ou.update_yaxes(title_text="Units Sold", secondary_y=True)
        st.plotly_chart(fig_ou, use_container_width=True)

        # AOV trend
        fig_aov = go.Figure()
        fig_aov.add_trace(go.Scatter(
            x=m_df['month_name'], y=m_df['aov'],
            mode='lines+markers+text',
            text=[f"${v:,.0f}" for v in m_df['aov']],
            textposition='top center',
            line=dict(color='#2D6A4F', width=2),
            marker=dict(size=8),
        ))
        fig_aov.update_layout(title='Monthly AOV', height=300, yaxis_tickformat='$,.0f')
        st.plotly_chart(fig_aov, use_container_width=True)

        # Monthly detail table — Orders by channel
        st.markdown("### Monthly Detail — Orders")
        orders_df = m_df[['month_name', 'orders', 'units', 'gross', 'discounts',
                          'discount_rate', 'net', 'aov', 'dtc_orders', 'ws_orders',
                          'gift_orders']].copy()
        orders_df.columns = ['Month', 'Orders', 'Units', 'Gross', 'Discounts',
                             'Disc %', 'Adjusted Gross', 'AOV', 'DTC', 'Wholesale', 'Gifting']
        # Display copy with formatting
        display_df = orders_df.copy()
        for col in ['Gross', 'Discounts', 'Adjusted Gross', 'AOV']:
            display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}")
        display_df['Disc %'] = display_df['Disc %'].apply(lambda x: f"{x:.0f}%")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Monthly detail table — Units by channel (NEW)
        st.markdown("### Monthly Detail — Units by Channel")
        st.caption("Units = total pairs/items inside orders (line_item quantities summed). Wholesale orders typically have many units per order.")
        units_df = m_df[['month_name', 'orders', 'units', 'dtc_units', 'ws_units', 'gift_units']].copy()
        units_df.columns = ['Month', 'Orders', 'Total Units', 'DTC Units', 'Wholesale Units', 'Gifting Units']
        # Compute units/order ratio
        units_df['Units/Order'] = (units_df['Total Units'] / units_df['Orders']).round(2)
        units_df.loc[units_df['Orders'] == 0, 'Units/Order'] = 0
        st.dataframe(units_df, use_container_width=True, hide_index=True)

        # ============================================================
        # Excel-friendly export (raw numbers, monthly DTC/WS/Gifting breakdown)
        # Drops directly into Assumptions/QBO Actuals tabs of the Excel model
        # ============================================================
        st.markdown("### Export to Excel Model")
        st.caption(
            "Download monthly unit breakdown (DTC / Wholesale / Gifting) for "
            "pasting into the Excel model's QBO Actuals tab (R84-R86)."
        )
        # Build clean export rows (raw integers)
        export_rows = []
        for m_dict in monthly:
            export_rows.append({
                'month_num': m_dict['month'],
                'month_name': m_dict['month_name'],
                'dtc_orders': m_dict['dtc_orders'],
                'wholesale_orders': m_dict['ws_orders'],
                'gifting_orders': m_dict['gift_orders'],
                'total_orders': m_dict['orders'],
                'dtc_units': m_dict['dtc_units'],
                'ws_units': m_dict['ws_units'],
                'gift_units': m_dict['gift_units'],
                'total_units': m_dict['units'],
                'gross_revenue': m_dict['gross'],
                'discounts': m_dict['discounts'],
                'net_revenue': m_dict['net'],
                'aov': m_dict['aov'],
            })
        export_df = pd.DataFrame(export_rows)

        col1, col2 = st.columns(2)
        with col1:
            csv = export_df.to_csv(index=False)
            st.download_button(
                "📥 Download Monthly Breakdown CSV",
                csv,
                "shopify_monthly_actuals.csv",
                "text/csv",
                use_container_width=True,
            )
        with col2:
            # Excel-paste-ready format aligned to QBO Actuals R82-R93 structure:
            # R82 = section header
            # R83 = month headers
            # R84-R87 = Orders block (DTC, WS, Gifting, Total formula)
            # R89 = UNITS subsection header
            # R90-R93 = Units block (DTC, WS, Gifting, Total formula)
            paste_lines = [
                "2026 ACTUALS — ORDERS & UNITS (Shopify)",  # → R82
                "Line Item\t" + "\t".join(m_dict['month_name'] for m_dict in monthly),  # → R83
                "DTC Orders\t" + "\t".join(str(m_dict['dtc_orders']) for m_dict in monthly),  # → R84
                "Wholesale Orders\t" + "\t".join(str(m_dict['ws_orders']) for m_dict in monthly),  # → R85
                "Gifting Orders\t" + "\t".join(str(m_dict['gift_orders']) for m_dict in monthly),  # → R86
                "Total Orders\t" + "\t".join(str(m_dict['orders']) for m_dict in monthly),  # → R87 (or use formula)
                "",  # → R88 spacer
                "UNITS",  # → R89
                "DTC Units\t" + "\t".join(str(m_dict['dtc_units']) for m_dict in monthly),  # → R90
                "Wholesale Units\t" + "\t".join(str(m_dict['ws_units']) for m_dict in monthly),  # → R91
                "Gifting Units\t" + "\t".join(str(m_dict['gift_units']) for m_dict in monthly),  # → R92
                "Total Units\t" + "\t".join(str(m_dict['units']) for m_dict in monthly),  # → R93
            ]
            paste_blob = "\n".join(paste_lines)
            st.download_button(
                "📋 Download Excel-Paste TSV (QBO Actuals R82-R93)",
                paste_blob,
                "shopify_excel_paste.tsv",
                "text/tab-separated-values",
                use_container_width=True,
            )

    st.divider()

    # ================================================================
    # DISCOUNT ANALYSIS
    # ================================================================
    st.markdown("## Discount Analysis")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Discounts YTD", f"${so['total_discounts']:,.0f}")
        st.metric("Discount Rate", f"{so['discount_rate']:.1f}%")

    with c2:
        # Discount by code
        if so['top_discounts']:
            disc_df = pd.DataFrame([
                {'Code': code, 'Uses': d['count'], 'Total': d['total']}
                for code, d in so['top_discounts']
            ])
            disc_df['Total'] = disc_df['Total'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(disc_df, use_container_width=True, hide_index=True)

    # Monthly discount trend
    if months_with_data:
        fig_disc = go.Figure()
        m_df2 = pd.DataFrame(months_with_data)
        fig_disc.add_trace(go.Bar(
            name='Discounts', x=m_df2['month_name'], y=m_df2['discounts'],
            marker_color='#E63946'
        ))
        fig_disc.add_trace(go.Scatter(
            name='Discount Rate', x=m_df2['month_name'], y=m_df2['discount_rate'],
            mode='lines+markers', yaxis='y2',
            line=dict(color='#1D3557', width=2), marker=dict(size=8),
        ))
        fig_disc.update_layout(
            title='Monthly Discounts & Rate', height=350,
            yaxis=dict(title='Discount ($)', tickformat='$,.0f'),
            yaxis2=dict(title='Discount Rate (%)', overlaying='y', side='right',
                        tickformat='.0f', ticksuffix='%'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_disc, use_container_width=True)

    st.divider()

    # ================================================================
    # TOP PRODUCTS
    # ================================================================
    st.markdown("## Top Products (by Units Sold)")

    if so['top_products']:
        prod_df = pd.DataFrame([
            {
                'Product': title[:45],
                'Units': d['units'],
                'Gross Revenue': d['gross_revenue'],
                'Net Revenue': d['net_revenue'],
            }
            for title, d in so['top_products'][:20]
        ])

        fig_prod = go.Figure()
        fig_prod.add_trace(go.Bar(
            x=prod_df['Units'], y=prod_df['Product'],
            orientation='h', marker_color='#2E86AB',
            text=prod_df['Units'], textposition='auto',
        ))
        fig_prod.update_layout(
            title='Top 20 Products by Units', height=600,
            yaxis=dict(autorange='reversed'),
            xaxis_title='Units Sold',
        )
        st.plotly_chart(fig_prod, use_container_width=True)

        # Product table
        prod_display = prod_df.copy()
        prod_display['Gross Revenue'] = prod_display['Gross Revenue'].apply(lambda x: f"${x:,.0f}")
        prod_display['Net Revenue'] = prod_display['Net Revenue'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(prod_display, use_container_width=True, hide_index=True)

    st.divider()

    # ================================================================
    # DAILY TREND (current month)
    # ================================================================
    st.markdown("## Daily Trend")

    if so['daily']:
        daily_df = pd.DataFrame([
            {'Date': date, 'Orders': d['orders'], 'Net Revenue': d['net']}
            for date, d in so['daily'].items()
        ])

        # Filter to most recent 60 days
        if len(daily_df) > 60:
            daily_df = daily_df.tail(60)

        fig_daily = make_subplots(specs=[[{"secondary_y": True}]])
        fig_daily.add_trace(go.Bar(
            name='Revenue', x=daily_df['Date'], y=daily_df['Net Revenue'],
            marker_color='#95D5B2',
        ), secondary_y=False)
        fig_daily.add_trace(go.Scatter(
            name='Orders', x=daily_df['Date'], y=daily_df['Orders'],
            mode='lines', line=dict(color='#1B4332', width=1.5),
        ), secondary_y=True)
        fig_daily.update_layout(
            title='Daily Revenue & Orders', height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig_daily.update_yaxes(title_text="Revenue ($)", tickformat="$,.0f", secondary_y=False)
        fig_daily.update_yaxes(title_text="Orders", secondary_y=True)
        st.plotly_chart(fig_daily, use_container_width=True)

    st.divider()

    # ================================================================
    # INVENTORY
    # ================================================================
    st.markdown("## Inventory")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Units", f"{inv['total_units']:,}")
    with c2:
        st.metric("In Stock SKUs", f"{inv['in_stock']}")
    with c3:
        st.metric("Out of Stock", f"{inv['out_of_stock']}",
                  delta_color="inverse" if inv['out_of_stock'] > 0 else "normal")
    with c4:
        st.metric("Negative Inventory", f"{inv['negative']}",
                  delta_color="inverse" if inv['negative'] > 0 else "normal")

    # Top inventory items
    if inv['items']:
        inv_df = pd.DataFrame(inv['items'][:30])
        inv_df = inv_df[['title', 'inventory', 'variants']]
        inv_df.columns = ['Product', 'Units on Hand', 'Variants']

        fig_inv = go.Figure()
        top_inv = inv_df.head(15)
        colors = ['#2D6A4F' if v > 0 else '#E63946' for v in top_inv['Units on Hand']]
        fig_inv.add_trace(go.Bar(
            x=top_inv['Units on Hand'],
            y=top_inv['Product'].apply(lambda x: x[:40]),
            orientation='h', marker_color=colors,
            text=top_inv['Units on Hand'], textposition='auto',
        ))
        fig_inv.update_layout(
            title='Top 15 Products by Inventory', height=500,
            yaxis=dict(autorange='reversed'),
            xaxis_title='Units on Hand',
        )
        st.plotly_chart(fig_inv, use_container_width=True)

        # Full inventory table
        st.markdown("### Full Inventory Table")
        st.dataframe(
            pd.DataFrame(inv['items'])[['title', 'inventory', 'variants', 'status']],
            use_container_width=True, hide_index=True,
            column_config={
                'title': 'Product',
                'inventory': st.column_config.NumberColumn('Units', format="%d"),
                'variants': 'Variants',
                'status': 'Status',
            },
        )

    # ================================================================
    # DATA NOTES
    # ================================================================
    st.divider()
    with st.expander("Data Notes"):
        st.write("**Source:** Shopify Admin API (live)")
        st.write(f"**Orders fetched:** {so['total_orders']} orders YTD 2026")
        st.write(f"**Products fetched:** {inv['total_products']} products")
        st.write("**Classification:** Orders tagged 'wholesale' = Wholesale. "
                 "$0 subtotal with discount = Gifting. All others = DTC.")
        st.write("**Refresh:** Data cached for 15 minutes. Click 'Refresh Data' to force update.")
