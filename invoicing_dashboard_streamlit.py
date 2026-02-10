"""
Invoicing Manager KPI Dashboard - Streamlit Application with Excel Upload
Upload your monthly invoicing data Excel file to view the dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Invoicing KPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    .main-header {
        background: #F5F7FA;
        color: #2F5496;
        padding: 0.75rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: left;
        border-left: 4px solid #2F5496;
    }
    
    .kpi-category {
        background: white;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .kpi-category h3 {
        color: #2F5496;
        border-bottom: 2px solid #2F5496;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }

    .kpi-table {
        width: 100%;
        border-collapse: collapse;
    }

    .kpi-table th {
        background: #D9E1F2;
        padding: 10px;
        text-align: left;
        font-weight: bold;
    }

    .kpi-table td {
        padding: 10px;
        border-bottom: 1px solid #E0E0E0;
    }

    .kpi-table tr:hover {
        background: #F8F9FA;
    }

    .success { color: #00B050; font-size: 20px; }
    .warning { color: #FFC000; font-size: 20px; }
    .error { color: #C00000; font-size: 20px; }

    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
    }
    
    .category-header {
        color: #2F5496;
        border-bottom: 3px solid #2F5496;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA VALIDATION AND LOADING
# =============================================================================

def validate_excel_data(df):
    """Validate that Excel has all required columns"""
    required_columns = [
        'Month', 'Total_Invoices', 'OnTime_Invoices', 'Avg_Billing_Timeliness',
        'Avg_Invoice_Cycle_Time', 'Planned_Milestones', 'Invoiced_Milestones',
        'Corrected_Invoices', 'Reissued_Invoices', 'Disputed_Invoices',
        'Avg_Dispute_Resolution_Days', 'Recognized_Revenue', 'Invoiced_Amount',
        'CO_Approved', 'CO_Invoiced', 'Advance_Received', 'Advance_Used',
        'WIP', 'Avg_Daily_Billed_Revenue', 'Old_WIP', 'Monthly_Revenue',
        'Submitted_Packages', 'Returned_Packages', 'Avg_PM_Approval_Days',
        'Total_Cost_Reports', 'Late_Cost_Reports'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, missing_columns
    return True, []

def load_data_from_excel(uploaded_file):
    """Load and process data from uploaded Excel file"""
    try:
        # Read the Excel file
        df = pd.read_excel(uploaded_file, sheet_name=0)
        
        # Validate the data
        is_valid, missing_cols = validate_excel_data(df)
        
        if not is_valid:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            st.info("Please upload a file with all required columns.")
            return None
        
        # Convert Month column to datetime
        df['Month'] = pd.to_datetime(df['Month'])
        
        # Sort by month
        df = df.sort_values('Month').reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.info("Please make sure your file is a valid Excel file with the correct format.")
        return None

# =============================================================================
# KPI CALCULATION FUNCTIONS
# =============================================================================

def calculate_kpis(data, month_idx):
    """Calculate all KPIs for a given month"""
    row = data.iloc[month_idx]
    
    kpis = {
        # Timeliness
        'billing_timeliness_days': row['Avg_Billing_Timeliness'],
        'pct_invoices_on_time': (row['OnTime_Invoices'] / row['Total_Invoices'] * 100),
        'invoice_cycle_time': row['Avg_Invoice_Cycle_Time'],
        'missed_milestones': row['Planned_Milestones'] - row['Invoiced_Milestones'],
        
        # Quality
        'invoice_error_rate': (row['Corrected_Invoices'] / row['Total_Invoices'] * 100),
        'invoice_reissue_rate': (row['Reissued_Invoices'] / row['Total_Invoices'] * 100),
        'disputed_invoice_pct': (row['Disputed_Invoices'] / row['Total_Invoices'] * 100),
        'dispute_resolution_days': row['Avg_Dispute_Resolution_Days'],
        
        # Coverage
        'billing_coverage_pct': (row['Invoiced_Amount'] / row['Recognized_Revenue'] * 100),
        'unbilled_revenue_pct': ((row['Recognized_Revenue'] - row['Invoiced_Amount']) / row['Recognized_Revenue'] * 100),
        'co_billing_rate': (row['CO_Invoiced'] / row['CO_Approved'] * 100),
        'advance_drawdown_rate': (row['Advance_Used'] / row['Advance_Received'] * 100),
        
        # WIP Control
        'wip_aging_days': row['WIP'] / row['Avg_Daily_Billed_Revenue'],
        'stale_wip_pct': (row['Old_WIP'] / row['WIP'] * 100),
        'wip_to_revenue_ratio': row['WIP'] / row['Monthly_Revenue'],
        
        # Collaboration
        'pm_approval_days': row['Avg_PM_Approval_Days'],
        'incomplete_packages_pct': (row['Returned_Packages'] / row['Submitted_Packages'] * 100),
        'late_cost_inputs_pct': (row['Late_Cost_Reports'] / row['Total_Cost_Reports'] * 100),
    }
    
    return kpis

def get_status(value, target, comparison='<='):
    """Determine KPI status (Green/Amber/Red)"""
    if comparison == '<=':
        if value <= target:
            return '🟢', 'success'
        elif value <= target * 1.1:
            return '🟠', 'warning'
        else:
            return '🔴', 'error'
    else:  # '>='
        if value >= target:
            return '🟢', 'success'
        elif value >= target * 0.9:
            return '🟠', 'warning'
        else:
            return '🔴', 'error'

# =============================================================================
# KPI DEFINITIONS
# =============================================================================

kpi_definitions = {
    'timeliness': [
        {'name': 'Billing Timeliness (Days)', 'key': 'billing_timeliness_days', 'target': 5, 'comparison': '<=', 'priority': True},
        {'name': '% Invoices Issued on Time', 'key': 'pct_invoices_on_time', 'target': 95, 'comparison': '>='},
        {'name': 'Invoice Cycle Time (Days)', 'key': 'invoice_cycle_time', 'target': 7, 'comparison': '<='},
        {'name': 'Missed Billing Milestones', 'key': 'missed_milestones', 'target': 0, 'comparison': '<='},
    ],
    'quality': [
        {'name': 'Invoice Error Rate %', 'key': 'invoice_error_rate', 'target': 2, 'comparison': '<='},
        {'name': 'Invoice Reissue Rate %', 'key': 'invoice_reissue_rate', 'target': 3, 'comparison': '<='},
        {'name': 'Disputed Invoice %', 'key': 'disputed_invoice_pct', 'target': 5, 'comparison': '<=', 'priority': True},
        {'name': 'Dispute Resolution Days', 'key': 'dispute_resolution_days', 'target': 10, 'comparison': '<='},
    ],
    'coverage': [
        {'name': 'Billing Coverage %', 'key': 'billing_coverage_pct', 'target': 98, 'comparison': '>=', 'priority': True},
        {'name': 'Unbilled Revenue %', 'key': 'unbilled_revenue_pct', 'target': 5, 'comparison': '<=', 'priority': True},
        {'name': 'Change Order Billing Rate %', 'key': 'co_billing_rate', 'target': 95, 'comparison': '>='},
        {'name': 'Advance Drawdown Rate %', 'key': 'advance_drawdown_rate', 'target': 100, 'comparison': '<='},
    ],
    'wip': [
        {'name': 'WIP Aging (Days)', 'key': 'wip_aging_days', 'target': 30, 'comparison': '<=', 'priority': True},
        {'name': 'Stale WIP % (>60 days)', 'key': 'stale_wip_pct', 'target': 10, 'comparison': '<='},
        {'name': 'WIP to Revenue Ratio', 'key': 'wip_to_revenue_ratio', 'target': 1.0, 'comparison': '<='},
    ],
    'collaboration': [
        {'name': 'PM Approval Time (Days)', 'key': 'pm_approval_days', 'target': 3, 'comparison': '<='},
        {'name': 'Incomplete Billing Packages %', 'key': 'incomplete_packages_pct', 'target': 5, 'comparison': '<='},
        {'name': 'Late Cost Inputs %', 'key': 'late_cost_inputs_pct', 'target': 5, 'comparison': '<='},
    ]
}

# =============================================================================
# CHART GENERATION FUNCTIONS
# =============================================================================

def create_trend_chart(data, metric_key, title, target=None):
    """Create a trend line chart for a KPI over time"""
    
    # Calculate metric for all months
    values = []
    for idx in range(len(data)):
        kpis = calculate_kpis(data, idx)
        values.append(kpis[metric_key])
    
    fig = go.Figure()
    
    # Add actual values line
    fig.add_trace(go.Scatter(
        x=data['Month'],
        y=values,
        mode='lines+markers',
        name='Actual',
        line=dict(color='#2F5496', width=3),
        marker=dict(size=8)
    ))
    
    # Add target line if provided
    if target:
        fig.add_trace(go.Scatter(
            x=data['Month'],
            y=[target] * len(data),
            mode='lines',
            name='Target',
            line=dict(color='#C00000', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Month',
        yaxis_title='Value',
        hovermode='x unified',
        template='plotly_white',
        height=300,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def create_gm_summary_chart(kpis):
    """Create a horizontal bar chart for GM focus KPIs"""
    
    gm_kpis = []
    for category_kpis in kpi_definitions.values():
        for kpi_def in category_kpis:
            if kpi_def.get('priority'):
                value = kpis[kpi_def['key']]
                target = kpi_def['target']
                status_icon, status_color = get_status(value, target, kpi_def['comparison'])
                
                gm_kpis.append({
                    'name': kpi_def['name'],
                    'value': value,
                    'target': target,
                    'status': status_icon
                })
                break
    
    fig = go.Figure()
    
    colors = ['#00B050' if '🟢' in kpi['status'] else '#FFC000' if '🟠' in kpi['status'] else '#C00000' for kpi in gm_kpis]
    
    fig.add_trace(go.Bar(
        y=[kpi['name'] for kpi in gm_kpis],
        x=[kpi['value'] for kpi in gm_kpis],
        orientation='h',
        marker=dict(color=colors),
        text=[f"{kpi['value']:.1f} (Target: {kpi['target']})" for kpi in gm_kpis],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='GM Monthly Focus - Top 5 KPIs',
        xaxis_title='Value',
        template='plotly_white',
        height=400,
        margin=dict(l=200, r=50, t=50, b=50)
    )
    
    return fig

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h3 style='margin: 0;'>📊 Invoicing Manager KPI Dashboard</h3>
        <p style='margin: 5px 0 0 0; font-size: 13px; color: #666;'>Real-time tracking of invoicing performance metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - File Upload
    st.sidebar.header("📁 Data Upload")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload Monthly Data Excel File",
        type=['xlsx', 'xls'],
        help="Upload your monthly invoicing data file"
    )
    
    # Instructions
    st.sidebar.markdown("---")
    with st.sidebar.expander("📋 Required Excel Columns"):
        st.markdown("""
        **Timeliness:**
        - Month, Total_Invoices, OnTime_Invoices
        - Avg_Billing_Timeliness, Avg_Invoice_Cycle_Time
        - Planned_Milestones, Invoiced_Milestones
        
        **Quality:**
        - Corrected_Invoices, Reissued_Invoices
        - Disputed_Invoices, Avg_Dispute_Resolution_Days
        
        **Coverage:**
        - Recognized_Revenue, Invoiced_Amount
        - CO_Approved, CO_Invoiced
        - Advance_Received, Advance_Used
        
        **WIP:**
        - WIP, Avg_Daily_Billed_Revenue
        - Old_WIP, Monthly_Revenue
        
        **Collaboration:**
        - Submitted_Packages, Returned_Packages
        - Avg_PM_Approval_Days, Total_Cost_Reports
        - Late_Cost_Reports
        """)
    
    # =============================================================================
    # PROCESS UPLOADED FILE OR SHOW INSTRUCTIONS
    # =============================================================================
    
    if uploaded_file is not None:
        # Load data from uploaded file
        monthly_data = load_data_from_excel(uploaded_file)
        
        if monthly_data is None:
            return  # Error already displayed
        
        # Success message
        st.success(f"✅ File uploaded successfully! Found {len(monthly_data)} months of data")
        
        # Show file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📅 Months Loaded", len(monthly_data))
        with col2:
            st.metric("📆 From", monthly_data['Month'].min().strftime('%b %Y'))
        with col3:
            st.metric("📆 To", monthly_data['Month'].max().strftime('%b %Y'))
        
        st.markdown("---")
        
        # Month selector
        month_options = [m.strftime('%B %Y') for m in monthly_data['Month']]
        selected_month = st.sidebar.selectbox(
            "Select Month",
            month_options,
            index=len(month_options) - 1
        )
        
        month_idx = month_options.index(selected_month)
        
        # View mode selector
        view_mode = st.sidebar.radio(
            "View Mode",
            ["GM Summary", "Detailed KPIs", "Trend Analysis"],
            index=0
        )
        
        st.sidebar.markdown("---")
        st.sidebar.info(f"📅 Viewing data for: **{selected_month}**")
        
        # Calculate current KPIs
        current_kpis = calculate_kpis(monthly_data, month_idx)
        
        # =============================================================================
        # GM SUMMARY VIEW
        # =============================================================================
        
        if view_mode == "GM Summary":
            st.header("🎯 GM Monthly Focus - Top 5 KPIs")
            
            # Display chart
            gm_chart = create_gm_summary_chart(current_kpis)
            st.plotly_chart(gm_chart, use_container_width=True)
            
            # Summary metrics
            st.markdown("### Key Performance Indicators")
            
            cols = st.columns(5)
            
            priority_kpis = []
            for category_kpis in kpi_definitions.values():
                for kpi_def in category_kpis:
                    if kpi_def.get('priority'):
                        priority_kpis.append(kpi_def)
            
            for idx, kpi_def in enumerate(priority_kpis):
                value = current_kpis[kpi_def['key']]
                target = kpi_def['target']
                status_icon, _ = get_status(value, target, kpi_def['comparison'])
                
                with cols[idx % 5]:
                    if '%' in kpi_def['name']:
                        st.metric(
                            kpi_def['name'],
                            f"{value:.1f}%",
                            f"Target: {target}%"
                        )
                    elif 'Ratio' in kpi_def['name']:
                        st.metric(
                            kpi_def['name'],
                            f"{value:.2f}",
                            f"Target: {target:.1f}"
                        )
                    else:
                        st.metric(
                            kpi_def['name'],
                            f"{value:.1f}",
                            f"Target: {target}"
                        )
                    st.markdown(f"<div style='text-align: center; font-size: 24px;'>{status_icon}</div>", unsafe_allow_html=True)
        
        # =============================================================================
        # DETAILED KPIs VIEW
        # =============================================================================
        
        elif view_mode == "Detailed KPIs":
            st.header("📈 Detailed KPI Breakdown")
            
            # Create tabs for each category
            tabs = st.tabs(["⏱️ Timeliness", "✅ Quality", "💰 Coverage", "📦 WIP Control", "🤝 Collaboration"])
            
            categories = ['timeliness', 'quality', 'coverage', 'wip', 'collaboration']
            
            for tab, category in zip(tabs, categories):
                with tab:
                    kpi_list = kpi_definitions[category]
                    
                    for kpi_def in kpi_list:
                        value = current_kpis[kpi_def['key']]
                        target = kpi_def['target']
                        status_icon, status_class = get_status(value, target, kpi_def['comparison'])
                        
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{kpi_def['name']}**")
                        
                        with col2:
                            if '%' in kpi_def['name']:
                                st.markdown(f"Target: {target}%")
                            elif 'Ratio' in kpi_def['name']:
                                st.markdown(f"Target: {target:.1f}")
                            else:
                                st.markdown(f"Target: {target}")
                        
                        with col3:
                            if '%' in kpi_def['name']:
                                st.markdown(f"**{value:.1f}%**")
                            elif 'Ratio' in kpi_def['name']:
                                st.markdown(f"**{value:.2f}**")
                            else:
                                st.markdown(f"**{value:.1f}**")
                        
                        with col4:
                            st.markdown(f"<div class='{status_class}'>{status_icon}</div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
        
        # =============================================================================
        # TREND ANALYSIS VIEW
        # =============================================================================
        
        else:  # Trend Analysis
            st.header("📊 Trend Analysis")
            
            # Metric selector
            all_metrics = []
            for category_name, kpi_list in kpi_definitions.items():
                for kpi_def in kpi_list:
                    all_metrics.append({
                        'display': f"{kpi_def['name']} ({category_name.title()})",
                        'key': kpi_def['key'],
                        'name': kpi_def['name'],
                        'target': kpi_def['target']
                    })
            
            selected_metric = st.selectbox(
                "Select KPI to analyze",
                [m['display'] for m in all_metrics],
                index=0
            )
            
            metric_info = [m for m in all_metrics if m['display'] == selected_metric][0]
            
            # Display trend chart
            trend_chart = create_trend_chart(
                monthly_data,
                metric_info['key'],
                metric_info['name'],
                metric_info['target']
            )
            st.plotly_chart(trend_chart, use_container_width=True)
            
            # Statistics
            st.markdown("### Statistics")
            
            values = []
            for idx in range(len(monthly_data)):
                kpis = calculate_kpis(monthly_data, idx)
                values.append(kpis[metric_info['key']])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current", f"{values[-1]:.2f}")
            with col2:
                st.metric("Average", f"{sum(values)/len(values):.2f}")
            with col3:
                st.metric("Best", f"{min(values) if metric_info.get('comparison') == '<=' else max(values):.2f}")
            with col4:
                st.metric("Worst", f"{max(values) if metric_info.get('comparison') == '<=' else min(values):.2f}")

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>Invoicing Manager KPI Dashboard | Built with Streamlit</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # No file uploaded - show instructions
        st.info("👆 Please upload an Excel file using the sidebar to get started")
        
        st.markdown("### 📋 How to Use This Dashboard")
        st.markdown("""
        1. **Prepare your monthly data** in Excel with all required columns (see sidebar for list)
        2. **Upload the file** using the file uploader in the sidebar
        3. **View your dashboard** - it will update automatically!
        4. **Select different months** to see historical performance
        5. **Explore different views** - GM Summary, Detailed KPIs, or Trend Analysis
        """)
        
        st.markdown("### ✨ Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - 📊 **Interactive Charts** - Hover for details, zoom, pan
            - 📅 **Month Selection** - View any historical period
            - 🎯 **GM Focus** - Top 5 critical metrics at a glance
            """)
        
        with col2:
            st.markdown("""
            - 📈 **Trend Analysis** - Track performance over time
            - 🔄 **Auto-Update** - Upload new data anytime
            - 💡 **Three View Modes** - Summary, Detailed, Trends
            """)
        
        st.markdown("### 📥 Need Test Data?")
        st.markdown("""
        Download the test Excel files to see the dashboard in action:
        - **October 2024** - Sample data for testing
        - **November 2024** - Sample data for testing  
        - **December 2024** - Sample data for testing
        
        Each file contains one month of invoicing data with all required columns.
        """)

if __name__ == '__main__':
    main()
