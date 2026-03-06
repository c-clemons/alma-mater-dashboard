"""
Wholesale Deal Tracker
Add and manage wholesale deals with detailed tracking
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import json


def initialize_deals():
    """Initialize wholesale deals in session state"""
    if 'wholesale_deals' not in st.session_state:
        st.session_state.wholesale_deals = []


def save_deal(deal):
    """Save a new deal"""
    st.session_state.wholesale_deals.append(deal)


def calculate_deal_metrics(deal):
    """Calculate revenue and margins for a deal"""
    pairs = deal['pairs']
    price = deal['price_per_pair']
    
    revenue = pairs * price
    
    # COGS breakdown
    product_cost = revenue * deal['cogs_product_pct']
    warehousing = revenue * deal['cogs_warehousing_pct']
    freight = revenue * deal['cogs_freight_pct']
    merchant = revenue * deal['cogs_merchant_pct']
    total_cogs = product_cost + warehousing + freight + merchant
    
    gross_profit = revenue - total_cogs
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    
    # Commission
    commission = revenue * deal['commission_pct']
    
    net_profit = gross_profit - commission
    
    return {
        'revenue': revenue,
        'total_cogs': total_cogs,
        'gross_profit': gross_profit,
        'gross_margin_pct': gross_margin,
        'commission': commission,
        'net_profit': net_profit,
    }


def show():
    """Display wholesale deal tracker"""
    
    st.markdown('<div class="main-header">Wholesale Deal Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage wholesale partnerships and revenue pipeline</div>', unsafe_allow_html=True)
    
    # Info about baseline
    st.info("📋 **Baseline Deals:** Spring 2026 (500 units, $72K) and Fall 2026 (1,500 units, $216K). Total: $288K. You can add custom deals below.")
    
    initialize_deals()
    
    # Tabs
    tab1, tab2 = st.tabs(["➕ Add New Deal", "📊 Deal Pipeline"])
    
    # --- ADD NEW DEAL ---
    with tab1:
        st.markdown("### Add New Wholesale Deal")
        
        with st.form("new_deal_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Deal Information")
                
                club_name = st.text_input("Club/Customer Name*", placeholder="e.g., Country Club of Virginia")
                
                product_type = st.selectbox(
                    "Product Type*",
                    ["Beta", "Alpha", "Gamma", "Custom"]
                )
                
                is_inline = st.radio(
                    "Order Type*",
                    ["In-Line Collection", "Custom Order"],
                    horizontal=True
                )
                
                pairs = st.number_input(
                    "Number of Pairs*",
                    min_value=1,
                    value=40,
                    step=10,
                    help="Total pairs in this order"
                )
                
                price_per_pair = st.number_input(
                    "Wholesale Price per Pair ($)*",
                    min_value=0.0,
                    value=144.0,
                    step=5.0,
                    format="%.2f"
                )
            
            with col2:
                st.markdown("#### Dates & Terms")
                
                close_date = st.date_input(
                    "Close Date*",
                    value=date.today(),
                    help="When deal is expected to close"
                )
                
                delivery_date = st.date_input(
                    "Delivery Date*",
                    value=date.today(),
                    help="When product will be delivered"
                )
                
                commission_pct = st.slider(
                    "Sales Commission %*",
                    min_value=0.0,
                    max_value=25.0,
                    value=10.0,
                    step=0.5,
                    format="%.1f%%"
                ) / 100
                
                st.markdown("#### COGS Components (%)")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    cogs_product = st.number_input("Product Costs", value=25.0, step=1.0) / 100
                    cogs_warehouse = st.number_input("Warehousing & Fulfillment", value=6.0, step=0.5) / 100
                
                with col_b:
                    cogs_freight = st.number_input("Freight In", value=6.0, step=0.5) / 100
                    cogs_merchant = st.number_input("Merchant Fees", value=3.0, step=0.5) / 100
            
            # Notes
            notes = st.text_area("Notes", placeholder="Additional details about this deal...")
            
            # Calculate preview
            st.markdown("---")
            st.markdown("### 💰 Deal Preview")
            
            preview_deal = {
                'pairs': pairs,
                'price_per_pair': price_per_pair,
                'cogs_product_pct': cogs_product,
                'cogs_warehousing_pct': cogs_warehouse,
                'cogs_freight_pct': cogs_freight,
                'cogs_merchant_pct': cogs_merchant,
                'commission_pct': commission_pct,
            }
            
            metrics = calculate_deal_metrics(preview_deal)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Revenue", f"${metrics['revenue']:,.0f}")
            
            with col2:
                st.metric("Gross Profit", f"${metrics['gross_profit']:,.0f}")
            
            with col3:
                st.metric("Gross Margin", f"{metrics['gross_margin_pct']:.1f}%")
            
            with col4:
                st.metric("Net After Commission", f"${metrics['net_profit']:,.0f}")
            
            # Submit
            submitted = st.form_submit_button("💾 Save Deal", type="primary", use_container_width=True)
            
            if submitted:
                if not club_name:
                    st.error("⚠️ Club/Customer Name is required")
                else:
                    # Create deal object
                    deal = {
                        'club_name': club_name,
                        'product_type': product_type,
                        'is_inline': is_inline == "In-Line Collection",
                        'pairs': pairs,
                        'price_per_pair': price_per_pair,
                        'close_date': close_date.isoformat(),
                        'delivery_date': delivery_date.isoformat(),
                        'commission_pct': commission_pct,
                        'cogs_product_pct': cogs_product,
                        'cogs_warehousing_pct': cogs_warehouse,
                        'cogs_freight_pct': cogs_freight,
                        'cogs_merchant_pct': cogs_merchant,
                        'notes': notes,
                        'created_at': datetime.now().isoformat(),
                        **metrics
                    }
                    
                    save_deal(deal)
                    st.success(f"✅ Deal with {club_name} saved successfully!")
                    st.balloons()
    
    # --- DEAL PIPELINE ---
    with tab2:
        st.markdown("### Wholesale Pipeline")
        
        if len(st.session_state.wholesale_deals) == 0:
            st.info("📋 No deals yet. Add your first deal in the 'Add New Deal' tab!")
        else:
            # Summary metrics
            total_revenue = sum(d['revenue'] for d in st.session_state.wholesale_deals)
            total_pairs = sum(d['pairs'] for d in st.session_state.wholesale_deals)
            avg_price = sum(d['price_per_pair'] * d['pairs'] for d in st.session_state.wholesale_deals) / total_pairs if total_pairs > 0 else 0
            total_gross_profit = sum(d['gross_profit'] for d in st.session_state.wholesale_deals)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Pipeline Revenue", f"${total_revenue:,.0f}")
            
            with col2:
                st.metric("Total Pairs", f"{total_pairs:,.0f}")
            
            with col3:
                st.metric("Avg Price/Pair", f"${avg_price:.2f}")
            
            with col4:
                st.metric("Total Gross Profit", f"${total_gross_profit:,.0f}")
            
            st.divider()
            
            # Deals table
            st.markdown("#### 📊 All Deals")
            
            deals_df = pd.DataFrame(st.session_state.wholesale_deals)
            
            # Format for display
            display_df = deals_df[[
                'club_name', 'product_type', 'pairs', 'price_per_pair',
                'revenue', 'gross_profit', 'gross_margin_pct', 
                'close_date', 'delivery_date'
            ]].copy()
            
            display_df.columns = [
                'Club', 'Product', 'Pairs', 'Price/Pair',
                'Revenue', 'Gross Profit', 'GM %',
                'Close Date', 'Delivery Date'
            ]
            
            # Format currency
            display_df['Price/Pair'] = display_df['Price/Pair'].apply(lambda x: f"${x:.2f}")
            display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"${x:,.0f}")
            display_df['Gross Profit'] = display_df['Gross Profit'].apply(lambda x: f"${x:,.0f}")
            display_df['GM %'] = display_df['GM %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Export deals
            st.divider()
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if st.button("📥 Export to CSV", use_container_width=True):
                    csv = deals_df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv,
                        file_name=f"wholesale_deals_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🗑️ Clear All Deals", type="secondary", use_container_width=True):
                    if st.session_state.get('confirm_clear', False):
                        st.session_state.wholesale_deals = []
                        st.session_state.confirm_clear = False
                        st.success("✅ All deals cleared!")
                        st.rerun()
                    else:
                        st.session_state.confirm_clear = True
                        st.warning("⚠️ Click again to confirm deletion")
