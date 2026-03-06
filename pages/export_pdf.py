"""
PDF Export
Generate professional PDF report of financial data
"""

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from financial_calcs import generate_monthly_pl


def generate_pdf_report():
    """Generate PDF report using ReportLab"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        
        # Get data
        team_members = st.session_state.get('team_members', [])
        opex_expenses = st.session_state.get('opex_expenses', [])
        wholesale_deals = st.session_state.get('wholesale_deals', [])
        
        # Generate monthly P&L
        df = generate_monthly_pl(
            year=2026,
            team_members=team_members,
            opex_expenses=opex_expenses,
            wholesale_deals=wholesale_deals,
            dtc_discount_rate=0.0,
            dtc_return_rate=0.0
        )
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30
        )
        
        story.append(Paragraph("Alma Mater Financial Report", title_style))
        story.append(Paragraph(f"2026 Projections - Generated {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        
        annual_revenue = df['Total Revenue'].sum()
        annual_cogs = df['Total COGS'].sum()
        annual_gross_profit = df['Gross Profit'].sum()
        annual_opex = df['Total OpEx'].sum()
        annual_ebitda = df['EBITDA'].sum()
        
        summary_data = [
            ['Metric', 'Amount'],
            ['Total Revenue', f"${annual_revenue:,.0f}"],
            ['Total COGS', f"${annual_cogs:,.0f}"],
            ['Gross Profit', f"${annual_gross_profit:,.0f}"],
            ['Total OpEx', f"${annual_opex:,.0f}"],
            ['EBITDA', f"${annual_ebitda:,.0f}"],
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Monthly P&L
        story.append(Paragraph("Monthly Profit & Loss", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Prepare monthly data
        monthly_data = [['Month', 'Revenue', 'COGS', 'Gross Profit', 'OpEx', 'EBITDA']]
        
        for _, row in df.iterrows():
            monthly_data.append([
                row['Month'],
                f"${row['Total Revenue']:,.0f}",
                f"${row['Total COGS']:,.0f}",
                f"${row['Gross Profit']:,.0f}",
                f"${row['Total OpEx']:,.0f}",
                f"${row['EBITDA']:,.0f}"
            ])
        
        monthly_table = Table(monthly_data)
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(monthly_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return None


def show():
    """Display PDF export page"""
    
    st.markdown('<div class="main-header">Export to PDF</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Generate professional financial report</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Report Contents
    
    The PDF report includes:
    - Executive summary with key financial metrics
    - Monthly profit & loss statement
    - Revenue, COGS, and OpEx breakdowns
    - EBITDA analysis
    
    All data is pulled from your integrated dashboard.
    """)
    
    st.divider()
    
    # Generate PDF button
    if st.button("📄 Generate PDF Report", type="primary"):
        with st.spinner("Generating PDF report..."):
            pdf_buffer = generate_pdf_report()
            
            if pdf_buffer:
                st.success("✅ PDF generated successfully!")
                
                # Download button
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_buffer,
                    file_name=f"alma_mater_financial_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    
    st.divider()
    
    st.info("💡 **Tip:** For browser-based PDF export, use your browser's Print function (Ctrl/Cmd+P) and select 'Save as PDF'.")
