"""
Alma Mater Financial Dashboard - Client Presentation
Streamlined interface for management reporting
"""

import streamlit as st
import sys
from pathlib import Path
from data_persistence import get_data_store

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="Alma Mater Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state with persistent data"""
    
    # Get data store
    store = get_data_store()
    
    # Load data from files if not in session state
    if 'team_members' not in st.session_state:
        st.session_state.team_members = store.load_team_members()
    
    if 'opex_expenses' not in st.session_state:
        st.session_state.opex_expenses = store.load_opex_expenses()
    
    if 'wholesale_deals' not in st.session_state:
        st.session_state.wholesale_deals = store.load_wholesale_deals()
    
    if 'assumptions' not in st.session_state:
        loaded_assumptions = store.load_assumptions()
        if loaded_assumptions:
            st.session_state.assumptions = loaded_assumptions
    
    # Auto-save flag
    if 'auto_save_enabled' not in st.session_state:
        st.session_state.auto_save_enabled = True


def auto_save_data():
    """Auto-save all data to persistent storage"""
    if st.session_state.get('auto_save_enabled', True):
        store = get_data_store()
        
        # Save all data
        if 'team_members' in st.session_state:
            store.save_team_members(st.session_state.team_members)
        
        if 'opex_expenses' in st.session_state:
            store.save_opex_expenses(st.session_state.opex_expenses)
        
        if 'wholesale_deals' in st.session_state:
            store.save_wholesale_deals(st.session_state.wholesale_deals)
        
        if 'assumptions' in st.session_state:
            store.save_assumptions(st.session_state.assumptions)

def main():
    """Main app"""
    
    # Initialize
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Alma Mater Inc.")
        st.markdown("Financial Dashboard")
        st.divider()
        
        # Navigation
        st.markdown("### Navigation")
        page = st.radio(
            "Select Page:",
            [
                "Management Dashboard",
                "Cash Flow & Runway",
                "Monthly P&L Detail",
                "Assumptions",
                "Team Tracker",
                "OpEx Tracker",
                "Wholesale Tracker",
                "Export to PDF"
            ],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Info
        st.markdown("### About")
        st.caption("**Last Updated:** Feb 10, 2026")
        st.caption("**2025 Actuals:** Through Dec 2025")
        st.caption("**2026 Forecast:** Matt Econ Roadmap")
        
        st.divider()
        
        # Quick metrics
        st.markdown("### Quick Stats")
        st.metric("2025 Revenue", "$101K")
        st.metric("2026 Forecast", "$1.15M")
        st.metric("Growth", "1,040% YoY")
        st.metric("Current Cash", "$41K")
        st.metric("Cash Runway", "~2-3 months")
    
    # Main content - route to appropriate page
    if page == "Management Dashboard":
        from pages import management_dashboard
        management_dashboard.show()
    elif page == "Cash Flow & Runway":
        from pages import cash_runway
        cash_runway.show()
    elif page == "Monthly P&L Detail":
        from pages import monthly_pl_detail
        monthly_pl_detail.show()
    elif page == "Assumptions":
        from pages import assumptions_page
        assumptions_page.show()
    elif page == "Team Tracker":
        from pages import team_tracker
        team_tracker.show()
    elif page == "OpEx Tracker":
        from pages import opex_tracker
        opex_tracker.show()
    elif page == "Wholesale Tracker":
        from pages import wholesale_tracker
        wholesale_tracker.show()
    elif page == "Export to PDF":
        from pages import export_pdf
        export_pdf.show()
    
    # Auto-save after page render
    auto_save_data()

if __name__ == "__main__":
    main()
