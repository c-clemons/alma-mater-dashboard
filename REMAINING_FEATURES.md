# Remaining Features TODO

## COMPLETED
- ✅ Removed emojis from all pages
- ✅ Created Assumptions page (fully editable parameters)
- ✅ Created Team Tracker (add team members with burdens)
- ✅ Created OpEx Tracker (add expenses like wholesale tracker)
- ✅ Updated main navigation

## IN PROGRESS / REMAINING

### 1. Monthly P&L Detail Page
Need to create `pages/monthly_pl_detail.py` with:
- Data table showing monthly P&L for 2025 and 2026
- Time series bar chart showing revenue, COGS, OpEx, EBITDA by month
- Toggle between actual and forecast
- Export to CSV functionality

### 2. Fix PDF Export
Current issue: PDF downloads but won't open
Solution needed:
- Use reportlab or matplotlib to generate actual PDF
- Or use browser print-to-PDF as documented workaround
- Add instructions in export_pdf.py

### 3. Add DTC Discounts & Returns
In `pages/management_dashboard.py`:
- Apply 10% discount to all DTC revenue
- Apply 20% returns only to 2027+ forecasts
- Update load_projections() function
- Show adjustment in COGS breakdown

### 4. Integrate Team Costs into Model
In `pages/management_dashboard.py`:
- Pull team_members from session state
- Calculate monthly payroll by department
- Add to operating expenses in P&L
- Show in expense breakdown chart

### 5. Integrate OpEx Expenses into Model
In `pages/management_dashboard.py`:
- Pull opex_expenses from session state
- Add to monthly operating expenses
- Combine with Matt's roadmap expenses
- Show in expense breakdown

### 6. COGS Breakdown Display
In `pages/management_dashboard.py`:
- Add section showing COGS components
- Table with % and $ for each component:
  - Product Costs (25%)
  - Warehousing & Fulfillment (6%)
  - Freight In (6%)
  - Merchant Fees (3%)
- Show calculation example

### 7. Remove Recommended Action Section
In `pages/management_dashboard.py`:
- Remove the "Recommended Action" info box
- Keep only the "Funding Requirements" section

### 8. Update __init__.py
Add new pages to imports:
```python
from . import assumptions_page
from . import team_tracker
from . import opex_tracker
from . import monthly_pl_detail
```

## QUICK FIXES NEEDED

### management_dashboard.py
Line 10: Add apply_dtc_adjustments function (already added)
Line 35-60: Update load_projections to apply adjustments
Line 300+: Add COGS breakdown section
Line 400+: Remove recommended action section

### export_pdf.py
Update to use browser print workaround until real PDF generation added

## TESTING CHECKLIST
- [ ] All pages load without errors
- [ ] Assumptions save/load correctly
- [ ] Team members calculate burdens correctly
- [ ] OpEx expenses sum correctly
- [ ] Wholesale deals work as before
- [ ] Monthly P&L shows correct data
- [ ] Charts render properly
- [ ] PDF export works (even if via print)

## PRIORITY ORDER
1. Monthly P&L Detail page (high priority - client needs this)
2. Integrate team/opex into main dashboard
3. Fix PDF export
4. Add COGS breakdown
5. Apply DTC adjustments

## ESTIMATED TIME
- Monthly P&L page: 30 min
- Integrations: 30 min
- PDF fix: 15 min
- COGS breakdown: 15 min
- Testing: 15 min
**Total: ~2 hours additional work**
