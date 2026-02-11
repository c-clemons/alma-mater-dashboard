# FINAL DEPLOYMENT - With Cash Flow & Updated Baseline

## 🎯 What's New In This Version

### 1. **Cash Flow & Runway Calculator** ✅ NEW!
- Complete cash runway analysis
- Input current cash ($41,422), AP ($8,414), AR ($0)
- Monthly cash projections through 2026
- Burn rate tracking
- Days of cash remaining
- Waterfall charts showing cash flow
- Alerts when cash runs low
- CSV export

### 2. **Updated Baseline OpEx** ✅ UPDATED!
Added Matt's systems costs from forecast:
- **Shopify:** $2,850/month ($34,200 annually)
- **Klaviyo:** $2,500/month (Jan-Feb), then $250/month ($2,500 after migration)
- **Yotpo:** $100/month ($1,200 annually)
- **UpPromote:** $250/month ($3,000 annually)
- **Performance Marketing:** $10K-$25K/month ($160K annually)
- **Affiliate Costs:** $5K/month ($50K annually)

**New Baseline OpEx Total: ~$387K annually** (was $132K)

### 3. **Corrected Wholesale Projections** ✅ UPDATED!
- Spring 2026: 500 units, $72K revenue, $77,770 cost
- Fall 2026: 1,500 units, $216K revenue, $138,875 cost
- Total: $288K revenue

### 4. **Marty Salary Confirmed** ✅ CONFIRMED!
- Starts January 1, 2026
- $48,000 annually ($4,000/month)
- W9 contractor (no burdens)

---

## 📦 DEPLOYMENT INSTRUCTIONS

### **Step 1: Delete Old Files from GitHub**

1. Go to: https://github.com/c-clemons/alma-mater-dashboard

2. **Delete EVERYTHING:**
   - Click on each file
   - Click trash icon
   - Commit deletion
   - OR: Delete entire repository and create fresh one

### **Step 2: Upload New Files**

1. **Extract** `alma_mater_FINAL_CASH_FLOW.zip`

2. **Upload ALL files:**
   - Drag entire folder to GitHub
   - Or upload file-by-file
   - Commit message: "Complete dashboard with cash flow, updated baseline, systems costs"

3. **Files you're uploading:**
   ```
   ├── app_client.py (UPDATED - new navigation)
   ├── baseline_data.py (UPDATED - Matt's systems costs)
   ├── financial_calcs.py (complete)
   ├── data_persistence.py (complete)
   ├── requirements_client.txt (reportlab added)
   ├── pages/
   │   ├── management_dashboard.py (integrated)
   │   ├── cash_runway.py (NEW!)
   │   ├── monthly_pl_detail.py (complete)
   │   ├── team_tracker.py (baseline indicators)
   │   ├── opex_tracker.py (baseline indicators)
   │   ├── wholesale_tracker.py (baseline indicators)
   │   ├── export_pdf.py (working)
   │   └── assumptions_page.py (existing)
   ├── .streamlit/config.toml
   ├── .gitignore
   └── README.md
   ```

### **Step 3: Streamlit Auto-Deploys**

- Wait 2-3 minutes
- Check: https://almamater-financial.streamlit.app
- App should auto-update

---

## ✅ POST-DEPLOYMENT TESTING

### **Test 1: Baseline Data**
- [ ] Open Team Tracker → See 7 baseline members
- [ ] Open OpEx Tracker → See 16 baseline expenses (~$387K)
- [ ] Open Wholesale Tracker → See 2 baseline deals ($288K)

### **Test 2: Cash Flow Calculator**
- [ ] Go to "Cash Flow & Runway" page
- [ ] Should show:
  - Current Cash: $41,422 (default)
  - Current AP: $8,414 (default)
  - Current AR: $0 (default)
- [ ] See monthly cash projections
- [ ] See waterfall chart
- [ ] See runway projection
- [ ] Can modify inputs and recalculate

### **Test 3: Integrated Dashboard**
- [ ] Management Dashboard shows updated totals
- [ ] Revenue ~$1.15M (DTC + Wholesale)
- [ ] OpEx ~$387K + Team ~$260K = ~$647K total
- [ ] COGS breakdown displays
- [ ] Charts render correctly

### **Test 4: PDF Export**
- [ ] Click "Generate PDF Report"
- [ ] Download works
- [ ] PDF has summary + monthly table

### **Test 5: Data Persistence**
- [ ] Add custom team member
- [ ] Close browser
- [ ] Reopen
- [ ] Custom member still there
- [ ] Baseline still there

---

## 💰 NEW FINANCIAL SUMMARY (2026)

### **Revenue:**
- DTC: ~$867K (Matt's projections)
- Wholesale: $288K (baseline deals)
- **Total: ~$1.15M**

### **COGS:**
- 40% of revenue = ~$460K

### **Operating Expenses:**

**Team Costs (~$260K):**
- Ryan: $48K (FT, with burdens)
- Jenny: $36K (FT, with burdens)
- Michele: $12K (PT, with burdens)
- Sukhjit: $54K (FT, with burdens)
- Nathan: $30K (starts May, with burdens)
- Jay: $30K (starts May, with burdens)
- Marty: $48K (W9, no burdens)
- **Plus Rippling burdens starting May**

**Other OpEx (~$387K):**
- Original baseline: $132K
- Shopify: $34K
- Klaviyo: $30K → $3K (after migration)
- Yotpo: $1K
- UpPromote: $3K
- Performance Marketing: $160K
- Affiliate Costs: $50K

**Total OpEx: ~$647K**

### **EBITDA:**
- Revenue: $1.15M
- COGS: $460K
- OpEx: $647K
- **EBITDA: ~$43K** (3.7% margin)

### **Cash Flow:**
- Starting Cash: $41K
- Net Cash: $15K (after AP)
- **Runway: ~2-3 months without funding**
- **Funding Need: ~$500K to reach cash positive**

---

## 🚨 KEY INSIGHTS FOR CLIENT

### **Cash Runway Critical**
- Current net cash: $15K
- Monthly burn: ~$30-40K early months
- Will need funding by March/April 2026
- Recommend raising $500K-$750K

### **Systems Costs Significant**
- $307K in new systems/marketing spend
- Biggest line items:
  - Performance Marketing: $160K
  - Affiliate: $50K
  - Shopify: $34K
  - Klaviyo migration: $30K → $3K

### **Profitability Path**
- Need ~200 DTC units/month to break even
- Currently ramping 50 → 200 over year
- Breakeven projected around month 6-8
- Wholesale helps but lumpy (Spring/Fall)

---

## 📊 CASH FLOW CALCULATOR FEATURES

### **Inputs:**
- Current cash balance
- Current AP (accounts payable)
- Current AR (accounts receivable)

### **Calculations:**
- Monthly cash in (revenue)
- Monthly cash out (COGS + OpEx)
- Net cash flow each month
- Cumulative ending cash
- Monthly burn rate
- Days of cash remaining

### **Visualizations:**
- Cash flow waterfall (monthly)
- Projected cash balance (line chart)
- Monthly burn rate (bar chart)
- Key insights (alerts, recommendations)

### **Outputs:**
- Monthly detail table
- CSV export
- Cash-out month prediction
- Funding need calculation

---

## 📋 UPDATED BASELINE COUNTS

**Team:** 7 members
**OpEx:** 16 line items (~$387K)
**Wholesale:** 2 deals ($288K)

**Users can add:**
- More team members
- More OpEx items
- More wholesale deals

Dashboard recalculates everything automatically!

---

## 🎉 READY TO DEPLOY!

1. Delete old files from GitHub
2. Upload new files from ZIP
3. Wait 2-3 minutes
4. Test cash flow calculator
5. Show client the runway analysis!

**The dashboard now has everything the client needs to track cash and make funding decisions!** 🚀
