"""
Assumptions Page
Configure all model parameters and inputs
"""

import streamlit as st
import json


def initialize_assumptions():
    """Initialize model assumptions in session state"""
    
    if 'assumptions' not in st.session_state:
        st.session_state.assumptions = {
            # Revenue assumptions
            'beta_aov': 250,
            'alpha_aov': 450,
            'gamma_aov': 188,
            'dtc_discount_pct': 0.10,
            'dtc_returns_pct': 0.20,
            'apply_returns_year': 2027,
            
            # COGS assumptions
            'cogs_product_pct': 0.25,
            'cogs_warehousing_pct': 0.06,
            'cogs_freight_pct': 0.06,
            'cogs_merchant_pct': 0.03,
            
            # Team burdens
            'benefits_pct': 0.10,
            'payroll_taxes_pct': 0.08,
            'processing_pct': 0.005,
            
            # CAC and Marketing
            'cac_improvement_rate': 0.15,
            'cac_floor': 30,
            
            # Starting values
            'starting_cash_2026': 93412,
        }


def save_assumptions():
    """Save assumptions to file"""
    with open('model_assumptions.json', 'w') as f:
        json.dump(st.session_state.assumptions, f, indent=2)
    st.success("Assumptions saved successfully!")


def load_assumptions():
    """Load assumptions from file"""
    try:
        with open('model_assumptions.json', 'r') as f:
            st.session_state.assumptions = json.load(f)
        st.success("Assumptions loaded successfully!")
    except FileNotFoundError:
        st.warning("No saved assumptions found. Using defaults.")


def show():
    """Display assumptions page"""
    
    st.markdown('<div class="main-header">Model Assumptions</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure revenue, costs, and operational parameters</div>', unsafe_allow_html=True)
    
    initialize_assumptions()
    
    # Tabs for different categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Revenue & Pricing",
        "COGS Components", 
        "Team & Payroll",
        "Marketing & CAC",
        "Other Assumptions"
    ])
    
    # --- REVENUE TAB ---
    with tab1:
        st.markdown("### Product Pricing")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.assumptions['beta_aov'] = st.number_input(
                "Beta AOV ($)",
                min_value=0.0,
                value=float(st.session_state.assumptions['beta_aov']),
                step=10.0,
                help="Average order value for Beta product"
            )
        
        with col2:
            st.session_state.assumptions['alpha_aov'] = st.number_input(
                "Alpha AOV ($)",
                min_value=0.0,
                value=float(st.session_state.assumptions['alpha_aov']),
                step=10.0,
                help="Average order value for Alpha product"
            )
        
        with col3:
            st.session_state.assumptions['gamma_aov'] = st.number_input(
                "Gamma AOV ($)",
                min_value=0.0,
                value=float(st.session_state.assumptions['gamma_aov']),
                step=10.0,
                help="Average order value for Gamma product (future)"
            )
        
        st.divider()
        
        st.markdown("### DTC Adjustments")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.assumptions['dtc_discount_pct'] = st.slider(
                "Discount Rate (%)",
                min_value=0.0,
                max_value=50.0,
                value=float(st.session_state.assumptions['dtc_discount_pct'] * 100),
                step=1.0,
                help="Average discount on DTC sales"
            ) / 100
        
        with col2:
            st.session_state.assumptions['dtc_returns_pct'] = st.slider(
                "Return Rate (%)",
                min_value=0.0,
                max_value=50.0,
                value=float(st.session_state.assumptions['dtc_returns_pct'] * 100),
                step=1.0,
                help="Expected return rate for DTC"
            ) / 100
        
        with col3:
            st.session_state.assumptions['apply_returns_year'] = st.number_input(
                "Apply Returns From Year",
                min_value=2026,
                max_value=2030,
                value=int(st.session_state.assumptions['apply_returns_year']),
                help="Year to start applying return rate"
            )
        
        st.info(
            f"**Net DTC Revenue:** "
            f"Gross × {(1-st.session_state.assumptions['dtc_discount_pct'])*100:.0f}% (after discount) "
            f"× {(1-st.session_state.assumptions['dtc_returns_pct'])*100:.0f}% (after returns, {st.session_state.assumptions['apply_returns_year']}+)"
        )
    
    # --- COGS TAB ---
    with tab2:
        st.markdown("### COGS Component Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.assumptions['cogs_product_pct'] = st.slider(
                "Product Costs (% of Revenue)",
                min_value=0.0,
                max_value=100.0,
                value=float(st.session_state.assumptions['cogs_product_pct'] * 100),
                step=1.0
            ) / 100
            
            st.session_state.assumptions['cogs_warehousing_pct'] = st.slider(
                "Warehousing & Fulfillment (% of Revenue)",
                min_value=0.0,
                max_value=20.0,
                value=float(st.session_state.assumptions['cogs_warehousing_pct'] * 100),
                step=0.5
            ) / 100
        
        with col2:
            st.session_state.assumptions['cogs_freight_pct'] = st.slider(
                "Freight In (% of Revenue)",
                min_value=0.0,
                max_value=20.0,
                value=float(st.session_state.assumptions['cogs_freight_pct'] * 100),
                step=0.5
            ) / 100
            
            st.session_state.assumptions['cogs_merchant_pct'] = st.slider(
                "Merchant Fees (% of Revenue)",
                min_value=0.0,
                max_value=10.0,
                value=float(st.session_state.assumptions['cogs_merchant_pct'] * 100),
                step=0.5
            ) / 100
        
        # Calculate total
        total_cogs_pct = (
            st.session_state.assumptions['cogs_product_pct'] +
            st.session_state.assumptions['cogs_warehousing_pct'] +
            st.session_state.assumptions['cogs_freight_pct'] +
            st.session_state.assumptions['cogs_merchant_pct']
        )
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total COGS Rate", f"{total_cogs_pct*100:.1f}%")
        
        with col2:
            st.metric("Implied Gross Margin", f"{(1-total_cogs_pct)*100:.1f}%")
        
        with col3:
            # Example calculation
            example_revenue = 10000
            example_cogs = example_revenue * total_cogs_pct
            st.metric("On $10K Revenue", f"${example_cogs:,.0f} COGS")
    
    # --- TEAM TAB ---
    with tab3:
        st.markdown("### Payroll Burden Rates")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.assumptions['benefits_pct'] = st.slider(
                "Benefits (% of Salary)",
                min_value=0.0,
                max_value=30.0,
                value=float(st.session_state.assumptions['benefits_pct'] * 100),
                step=1.0
            ) / 100
        
        with col2:
            st.session_state.assumptions['payroll_taxes_pct'] = st.slider(
                "Payroll Taxes (% of Salary)",
                min_value=0.0,
                max_value=20.0,
                value=float(st.session_state.assumptions['payroll_taxes_pct'] * 100),
                step=0.5
            ) / 100
        
        with col3:
            st.session_state.assumptions['processing_pct'] = st.slider(
                "Processing Fees (% of Salary)",
                min_value=0.0,
                max_value=2.0,
                value=float(st.session_state.assumptions['processing_pct'] * 100),
                step=0.1
            ) / 100
        
        # Calculate total burden
        total_burden = (
            st.session_state.assumptions['benefits_pct'] +
            st.session_state.assumptions['payroll_taxes_pct'] +
            st.session_state.assumptions['processing_pct']
        )
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Payroll Burden", f"{total_burden*100:.1f}%")
            st.caption("Added on top of base salary")
        
        with col2:
            # Example
            example_salary = 100000
            example_burden = example_salary * total_burden
            example_total = example_salary + example_burden
            st.metric("Example: $100K Salary", f"${example_total:,.0f} total cost")
            st.caption(f"Salary + ${example_burden:,.0f} burden")
    
    # --- MARKETING TAB ---
    with tab4:
        st.markdown("### CAC Projection Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.assumptions['cac_improvement_rate'] = st.slider(
                "Annual CAC Improvement Rate",
                min_value=0.0,
                max_value=50.0,
                value=float(st.session_state.assumptions['cac_improvement_rate'] * 100),
                step=1.0,
                help="Expected annual reduction in CAC as marketing matures"
            ) / 100
        
        with col2:
            st.session_state.assumptions['cac_floor'] = st.number_input(
                "CAC Floor ($)",
                min_value=0.0,
                value=float(st.session_state.assumptions['cac_floor']),
                step=5.0,
                help="Minimum realistic CAC"
            )
        
        st.info(
            f"CAC will improve {st.session_state.assumptions['cac_improvement_rate']*100:.0f}% annually "
            f"until reaching floor of ${st.session_state.assumptions['cac_floor']:.0f}"
        )
    
    # --- OTHER TAB ---
    with tab5:
        st.markdown("### Starting Values")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.assumptions['starting_cash_2026'] = st.number_input(
                "Starting Cash (2026)",
                min_value=0.0,
                value=float(st.session_state.assumptions['starting_cash_2026']),
                step=1000.0,
                format="%.2f"
            )
        
        with col2:
            st.metric(
                "Current Value",
                f"${st.session_state.assumptions['starting_cash_2026']:,.0f}",
                help="From 12/31/2025 balance sheet"
            )
    
    # --- ACTION BUTTONS ---
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Save Assumptions", type="primary", use_container_width=True):
            save_assumptions()
    
    with col2:
        if st.button("Load Saved", use_container_width=True):
            load_assumptions()
    
    with col3:
        if st.button("Reset to Defaults", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                initialize_assumptions()
                st.session_state.confirm_reset = False
                st.success("Reset to defaults!")
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("Click again to confirm")
    
    with col4:
        if st.button("View Current", use_container_width=True):
            st.json(st.session_state.assumptions)
