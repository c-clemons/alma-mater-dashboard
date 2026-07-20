"""
Alma Mater Financial Dashboard - Client Presentation
Streamlined interface for management reporting
v2.0 - QBO Import & Variance Analysis
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

# Empirica brand system + Alma customization
from empirica_core.portal import chrome  # noqa: E402

ALMA_LOGO = Path(__file__).parent / "assets" / "logo.svg"
ALMA_ACCENT = "#b08d57"   # Alma's warm gold
chrome.inject_brand_css(ALMA_ACCENT)

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
    
    # Load QBO actuals (always refresh from file to pick up new fields after deploys)
    qbo_data = store.load_qbo_actuals()
    if qbo_data:
        st.session_state.qbo_actuals = qbo_data

    # Load fundraising rounds
    if 'fundraising_rounds' not in st.session_state:
        fundraising = store.load_fundraising()
        if fundraising:
            st.session_state.fundraising_rounds = fundraising
        else:
            from baseline_data import get_baseline_fundraising
            st.session_state.fundraising_rounds = get_baseline_fundraising()

    # Load PO data and inventory config
    if 'po_data' not in st.session_state:
        po_data = store.load_po_data()
        if po_data:
            st.session_state.po_data = po_data
        else:
            from baseline_data import get_baseline_po_data
            st.session_state.po_data = get_baseline_po_data()

    if 'inventory_config' not in st.session_state:
        from baseline_data import get_baseline_inventory_config
        loaded_assumptions = st.session_state.get('assumptions', {})
        config = get_baseline_inventory_config()
        # Override with any saved assumption values
        for key in config:
            if key in loaded_assumptions:
                config[key] = loaded_assumptions[key]
        st.session_state.inventory_config = config

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

        if 'fundraising_rounds' in st.session_state:
            store.save_fundraising(st.session_state.fundraising_rounds)

        if 'po_data' in st.session_state:
            store.save_po_data(st.session_state.po_data)

def check_password() -> bool:
    """Gate the app: single sign-on via an identity proxy when present, else the
    shared password from st.secrets.

    Behind Cloudflare Access / Google IAP the proxy has already authenticated the
    user and forwards their verified email, so we trust it and skip the password
    prompt (single email login). With no proxy (local dev / direct access) the
    existing shared-password gate applies.
    """
    from empirica_core.portal.auth import proxy_identity
    if proxy_identity():
        return True

    if st.session_state.get('authenticated'):
        return True

    st.markdown('<div class="main-header">Alma Mater Financial Dashboard</div>',
                unsafe_allow_html=True)
    st.markdown("Enter password to continue.")

    pw = st.text_input("Password", type="password", key="pw_input")
    if pw:
        expected = st.secrets.get("dashboard_password")
        if expected and pw == expected:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


# --- Access control (roles) -------------------------------------------------
import os  # noqa: E402
from empirica_core.portal import roles as _roles  # noqa: E402
from empirica_core.portal.admin import render_user_admin  # noqa: E402

# Seeded admin(s) — always admin regardless of the stored file, so someone can
# reach User Management to grant everyone else. Add Nathan via the Admin page.
BOOTSTRAP_ADMINS = ["chandler@empirica-analytics.com"]

# Minimum role required to SEE each page (order = nav order).
# admin > management > employee > investor.  Team Tracker = payroll → management+.
PAGE_MIN = {
    "Management Dashboard": "investor",
    "Shopify Analytics":    "employee",
    "Cash Flow & Runway":   "investor",
    "Monthly P&L Detail":   "management",
    "Fundraising":          "management",
    "QBO Import":           "management",
    "Assumptions":          "management",
    "Team Tracker":         "management",
    "OpEx Tracker":         "employee",
    "Wholesale Tracker":    "employee",
    "Inventory Tracker":    "employee",
    "Export to PDF":        "management",
}
ALL_PAGES = list(PAGE_MIN.keys())
ADMIN_PAGE = "⚙ User Management"

_ROLE_STORE = _roles.RoleStore(
    "alma",
    bucket="empirica-portals-state" if os.environ.get("K_SERVICE") else None,
    bootstrap_admins=BOOTSTRAP_ADMINS,
    local_path=Path(__file__).parent / "data" / "roles_local.json",
)


def main():
    """Main app"""

    # Auth gate (Cloudflare Access / password)
    if not check_password():
        return

    # Role gate: Access admits anyone with a verified email; roles decide what
    # they can see. No role yet → landing page (fail-closed).
    email = _roles.resolve_identity()
    role = _ROLE_STORE.role_for(email)
    if role is None:
        _roles.render_landing(email, "Alma Mater Financial Dashboard", _ROLE_STORE)
        return

    # Write gate: only admin/management persist changes (shared, durable state).
    can_write = role in ("admin", "management")
    st.session_state["_empirica_can_write"] = can_write

    # Initialize
    init_session_state()

    # Pages this role may see (+ Admin page for admins).
    allowed = [p for p in ALL_PAGES if _roles.can_view(role, PAGE_MIN[p])]
    if role == "admin":
        allowed = allowed + [ADMIN_PAGE]

    # Sidebar
    with st.sidebar:
        chrome.render_brand(st.sidebar, client_logo=ALMA_LOGO,
                            client_name="Alma Mater", accent_color=ALMA_ACCENT)
        st.caption("Financial Dashboard")
        st.caption(f"{email} · **{role}**")
        if not can_write:
            st.caption("👁 Read-only — ask an admin to make changes")
        st.divider()

        # Navigation
        st.markdown("### Navigation")
        page = st.radio(
            "Select Page:",
            allowed,
            label_visibility="collapsed"
        )

        st.divider()
        
        # Info
        st.markdown("### About")
        qbo = st.session_state.get('qbo_actuals')
        if qbo:
            from qbo_parser import MONTHS
            lm = qbo.get('last_month', 0)
            ly = qbo.get('last_year', 0)
            cash = qbo.get('latest_cash', 0)
            st.caption(f"**QBO Actuals:** Through {MONTHS[lm-1]} {ly}")
            st.caption(f"**Cash (QBO):** ${cash:,.0f}")
        else:
            st.caption("**QBO Actuals:** Not loaded")
        st.caption("**2026 Forecast:** Matt Econ Roadmap")

        st.divider()

        # Quick metrics
        st.markdown("### Quick Stats")
        st.metric("2025 Revenue", "$101K")
        st.metric("2026 Forecast", "$1.15M")
        st.metric("Growth", "1,040% YoY")
        if qbo:
            st.metric("Current Cash", f"${qbo.get('latest_cash', 0):,.0f}")
        else:
            st.metric("Current Cash", "$41K")
        st.metric("Cash Runway", "~2-3 months")

        st.divider()
        chrome.render_footer(st.sidebar)

    # Admin page (admins only — it's only in `allowed` for them)
    if page == ADMIN_PAGE:
        render_user_admin(_ROLE_STORE, current_admin_email=email)
        return

    # Main content - route to appropriate page
    if page == "Management Dashboard":
        from pages import management_dashboard
        management_dashboard.show()
    elif page == "Shopify Analytics":
        from pages import shopify_analytics
        shopify_analytics.show()
    elif page == "Cash Flow & Runway":
        from pages import cash_runway
        cash_runway.show()
    elif page == "Monthly P&L Detail":
        from pages import monthly_pl_detail
        monthly_pl_detail.show()
    elif page == "Fundraising":
        from pages import fundraising
        fundraising.show()
    elif page == "QBO Import":
        from pages import qbo_import
        qbo_import.show()
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
    elif page == "Inventory Tracker":
        from pages import inventory_tracker
        inventory_tracker.show()
    elif page == "Export to PDF":
        from pages import export_pdf
        export_pdf.show()
    
    # Auto-save after page render
    auto_save_data()

if __name__ == "__main__":
    main()
