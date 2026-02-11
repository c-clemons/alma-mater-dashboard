"""
Alma Mater Financial Dashboard - Client Presentation
Streamlined interface for management reporting
"""

import streamlit as st
import sys
from pathlib import Path

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
    """Initialize session state variables"""
    
    if 'wholesale_deals' not in st.session_state:
        st.session_state.wholesale_deals = []

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
        st.metric("2026 Forecast", "$867K")
        st.metric("Growth", "760% YoY")
        st.metric("Starting Cash", "$93K")
    
    # Main content - route to appropriate page
    if page == "Management Dashboard":
        from pages import management_dashboard
        management_dashboard.show()
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

if __name__ == "__main__":
    main()
