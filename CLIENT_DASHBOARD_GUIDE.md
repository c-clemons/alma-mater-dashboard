# Alma Mater Client Dashboard - Quick Start Guide

## 🚀 For Tonight's Client Presentation

### **What You Have:**
A professional financial dashboard with:
- ✅ 2025 Actual results (from your QBO data)
- ✅ 2026 Projections (Matt Econ Roadmap)
- ✅ Cash flow analysis with funding requirements
- ✅ Wholesale deal tracker
- ✅ Export to PDF capability

---

## 📱 **Option 1: Run Locally (Recommended for Tonight)**

### Step 1: Navigate to the folder
```bash
cd /Users/chandlerclemons/Desktop/"Alma Mater"/alma_mater_model
```

### Step 2: Run the dashboard
```bash
streamlit run app_client.py
```

Or use the helper script:
```bash
./run_client_dashboard.sh
```

### Step 3: Share with client
The app will open at `http://localhost:8501`

**To share:**
1. Take screenshots of key sections
2. Use browser Print → Save as PDF
3. Email PDF to client

---

## 🌐 **Option 2: Deploy to Cloud (5 minutes)**

### Deploy to Streamlit Cloud (Free)

1. **Push to GitHub:**
```bash
cd /Users/chandlerclemons/Desktop/"Alma Mater"/alma_mater_model
git init
git add .
git commit -m "Initial client dashboard"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

2. **Deploy on Streamlit Cloud:**
- Go to https://share.streamlit.io/
- Connect your GitHub account
- Select your repo
- Choose `app_client.py` as the main file
- Click "Deploy"

3. **Share link with client:**
- You'll get a URL like: `https://almamater-dashboard.streamlit.app`
- Client can view it in real-time from anywhere
- You can update it anytime by pushing to GitHub

---

## 📊 **What's in the Dashboard**

### **Page 1: Management Dashboard** 🎯
**Best for client presentation**

Shows:
- Executive summary (2025 vs 2026)
- Revenue trends (actual vs forecast)
- P&L comparison table
- Cash flow projection with funding needs
- Operating expense breakdown
- Key insights and recommendations

**Key Metrics Highlighted:**
- Starting cash: $93,412
- 2026 revenue target: $867K
- Funding need: $100-150K in Q1 2026
- Growth: 760% YoY

### **Page 2: Wholesale Tracker** 🤝
**For adding wholesale deals**

Features:
- Add new deals with full details
- Calculate revenue and margins automatically
- Track pipeline
- Export to CSV

### **Page 3: Export to PDF** 📤
**Generate client-ready reports**

Options:
- Select sections to include
- Choose format (PDF, PPT, Excel)
- Download for sharing

---

## 💡 **Quick Demo Script for Client**

### Opening (30 seconds)
"I've built a comprehensive financial dashboard that tracks our 2025 actuals and projects 2026 based on Matt's roadmap. Let me walk you through the key metrics."

### Page 1: Management Dashboard (3-4 minutes)

**Executive Summary:**
- "In 2025, we did $101K in revenue with significant losses as we were in development mode."
- "For 2026, we're projecting $867K in revenue - that's 760% growth."
- "We'll launch Beta in Q1 and Alpha in Q3."

**Cash Flow:**
- "We're starting 2026 with $93K in cash."
- "Based on Matt's expense roadmap, we'll need $100-150K in Q1 to maintain runway."
- "This chart shows our projected cash balance - you can see we'll need funding around March."

**Expense Breakdown:**
- "Total 2026 operating budget is $542K"
- "Biggest categories are Performance Marketing ($160K) and Marketing Management ($103K)"
- "We're being strategic with spend - ramping as we validate product-market fit."

**Key Insights:**
- "Gross margin improves from 6% to 60% as we move from prototypes to production"
- "Monthly burn averages $30-40K once we're in market"
- "Path to profitability by Q4 2026 if we hit our unit targets"

### Page 2: Wholesale (1 minute)
"I've also built a wholesale tracker so we can easily add new deals and see the revenue impact. Want to add any deals we're working on?"

### Closing (30 seconds)
"This dashboard updates in real-time. I can share the link so you can check progress anytime, or I can generate a PDF for your records."

---

## 🎨 **Customization Tips**

### Update Data:
All data is in `pages/management_dashboard.py`:
- Lines 10-30: 2025 actuals
- Lines 35-60: 2026 projections

### Change Colors/Branding:
Edit `app_client.py` lines 15-30 for CSS styling

### Add Your Logo:
```python
st.sidebar.image("path/to/logo.png", width=200)
```

---

## 🐛 **Troubleshooting**

### "Module not found" error:
```bash
pip install streamlit pandas plotly numpy
```

### Dashboard won't load:
1. Check you're in the right directory
2. Make sure Python 3.8+ is installed
3. Try: `python3 -m streamlit run app_client.py`

### Charts not showing:
```bash
pip install --upgrade plotly
```

---

## 📞 **Quick Support**

**If something breaks:**
1. Restart the app (Ctrl+C, then run again)
2. Clear browser cache
3. Check terminal for error messages

**For tonight, fastest option:**
1. Run locally
2. Use browser Print → Save as PDF
3. Email PDF to client

**For ongoing use:**
Deploy to Streamlit Cloud so client has live access

---

## ✅ **Pre-Meeting Checklist**

- [ ] Dashboard runs without errors
- [ ] All numbers look correct
- [ ] Screenshots/PDF ready as backup
- [ ] Tested on your laptop (not just desktop)
- [ ] Have GitHub repo ready (if deploying)
- [ ] Client contact info handy

---

## 🎯 **Tonight's Goal**

Show the client:
1. **Where we are:** 2025 results
2. **Where we're going:** 2026 projections  
3. **What we need:** $100-150K funding in Q1
4. **How we'll use it:** Detailed expense breakdown
5. **When we'll be profitable:** Q4 2026 path

**You're ready! This dashboard tells a compelling story.** 🚀

---

**Questions?** Everything is documented. Code is clean and commented. You can customize anything.

**Good luck with the client meeting!** 💪
