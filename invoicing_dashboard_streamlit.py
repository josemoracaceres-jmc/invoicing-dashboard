"""
Invoicing Manager KPI Dashboard - Streamlit Application
A comprehensive dashboard for tracking invoicing KPIs in a refit shipyard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

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
        background: linear-gradient(135deg, #2F5496 0%, #4472C4 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .kpi-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid #2F5496;
        padding: 1rem;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    .status-green {
        color: #00B050;
        font-size: 24px;
    }
    
    .status-amber {
        color: #FFC000;
        font-size: 24px;
    }
    
    .status-red {
        color: #C00000;
        font-size: 24px;
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
# DATA INITIALIZATION
# =============================================================================

@st.cache_data
def initialize_data():
    """Initialize sample monthly data for the dashboard"""
    months = pd.date_range(start='2024-01-01', periods=12, freq='MS')
    
    data = {
        'Month': months,
        # Timeliness metrics
        'Total_Invoices': [45, 52, 48, 51, 49, 53, 50, 47, 52, 54, 51, 49],
        'OnTime_Invoices': [42, 49, 45, 48, 47, 51, 48, 45, 50, 52, 49, 47],
        'Avg_Billing_Timeliness': [4.2, 5.8, 4.5, 5.2, 4.0, 4.8, 3.9, 4.1, 4.3, 4.0, 4.2, 3.8],
        'Avg_Invoice_Cycle_Time': [6.5, 7.2, 6.8, 7.0, 6.3, 6.9, 6.1, 6.4, 6.6, 6.2, 6.5, 6.0],
        'Planned_Milestones': [50, 55, 52, 54, 51, 56, 53, 50, 55, 57, 54, 52],
        'Invoiced_Milestones': [50, 54, 52, 54, 51, 56, 53, 50, 55, 57, 54, 52],
        
        # Quality metrics
        'Corrected_Invoices': [1, 2, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
        'Reissued_Invoices': [1, 2, 1, 2, 1, 1, 0, 1, 1, 1, 1, 0],
        'Disputed_Invoices': [2, 3, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2],
        'Avg_Dispute_Resolution_Days': [9.5, 11.2, 9.8, 10.1, 8.5, 9.3, 8.8, 8.2, 9.0, 8.7, 8.9, 8.5],
        
        # Coverage metrics
        'Recognized_Revenue': [2500000, 2700000, 2600000, 2650000, 2550000, 2750000, 2680000, 2620000, 2700000, 2800000, 2720000, 2650000],
        'Invoiced_Amount': [2475000, 2673000, 2574000, 2623500, 2524500, 2722500, 2653600, 2593800, 2673000, 2772000, 2693600, 2623500],
        'CO_Approved': [150000, 180000, 160000, 170000, 155000, 185000, 175000, 165000, 180000, 190000, 182000, 170000],
        'CO_Invoiced': [145000, 171000, 155200, 163500, 150250, 179750, 170125, 159825, 174600, 184550, 176540, 164500],
        'Advance_Received': [500000, 500000, 500000, 500000, 500000, 500000, 500000, 500000, 500000, 500000, 500000, 500000],
        'Advance_Used': [450000, 465000, 472000, 485000, 492000, 498000, 500000, 500000, 500000, 500000, 500000, 500000],
        
        # WIP metrics
        'WIP': [2100000, 2250000, 2180000, 2200000, 2150000, 2280000, 2220000, 2170000, 2240000, 2300000, 2260000, 2190000],
        'Avg_Daily_Billed_Revenue': [83333, 90000, 86667, 88333, 85000, 91667, 89333, 87333, 90000, 93333, 90667, 88333],
        'Old_WIP': [168000, 202500, 174400, 176000, 172000, 205200, 177600, 173600, 201600, 207000, 203400, 175200],
        'Monthly_Revenue': [2500000, 2700000, 2600000, 2650000, 2550000, 2750000, 2680000, 2620000, 2700000, 2800000, 2720000, 2650000],
        
        # Collaboration metrics
        'Submitted_Packages': [48, 54, 50, 52, 50, 55, 52, 49, 54, 56, 53, 51],
        'Returned_Packages': [2, 3, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2],
        'Avg_PM_Approval_Days': [2.8, 3.2, 2.9, 3.0, 2.5, 2.9, 2.7, 2.6, 2.8, 2.7, 2.6, 2.5],
        'Total_Cost_Reports': [50, 55, 52, 54, 51, 56, 53, 50, 55, 57, 54, 52],
        'Late_Cost_Reports': [2, 3, 2, 3, 2, 2, 2, 1, 2, 2, 1, 2],
    }
    
    return pd.DataFrame(data)

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
            return '🟢', 'green'
        elif value <= target * 1.1:
            return '🟠', 'amber'
        else:
            return '🔴', 'red'
    else:  # '>='
        if value >= target:
            return '🟢', 'green'
        elif value >= target * 0.9:
            return '🟠', 'amber'
        else:
            return '🔴', 'red'

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
# CHART FUNCTIONS
# =============================================================================

def create_trend_chart(data, metric_key, title, target=None):
    """Create a trend line chart for a KPI over time"""
    values = []
    for idx in range(len(data)):
        kpis = calculate_kpis(data, idx)
        values.append(kpis[metric_key])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['Month'],
        y=values,
        mode='lines+markers',
        name='Actual',
        line=dict(color='#2F5496', width=3),
        marker=dict(size=8),
        hovertemplate='%{x|%b %Y}<br>Value: %{y:.1f}<extra></extra>'
    ))
    
    if target:
        fig.add_trace(go.Scatter(
            x=data['Month'],
            y=[target] * len(data),
            mode='lines',
            name='Target',
            line=dict(color='#C00000', width=2, dash='dash'),
            hovertemplate='Target: %{y}<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Month',
        yaxis_title='Value',
        hovermode='x unified',
        template='plotly_white',
        height=350,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def create_gm_summary_chart(kpis):
    """Create horizontal bar chart for GM focus KPIs"""
    gm_kpis = []
    
    for category_kpis in kpi_definitions.values():
        for kpi_def in category_kpis:
            if kpi_def.get('priority'):
                value = kpis[kpi_def['key']]
                target = kpi_def['target']
                status_icon, status_class = get_status(value, target, kpi_def['comparison'])
                
                gm_kpis.append({
                    'name': kpi_def['name'],
                    'value': value,
                    'target': target,
                    'status': status_class
                })
    
    colors = ['#00B050' if kpi['status'] == 'green' else '#FFC000' if kpi['status'] == 'amber' else '#C00000' for kpi in gm_kpis]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=[kpi['name'] for kpi in gm_kpis],
        x=[kpi['value'] for kpi in gm_kpis],
        orientation='h',
        marker=dict(color=colors),
        text=[f"{kpi['value']:.1f}" for kpi in gm_kpis],
        textposition='auto',
        hovertemplate='%{y}<br>Actual: %{x:.1f}<br>Target: %{customdata}<extra></extra>',
        customdata=[kpi['target'] for kpi in gm_kpis]
    ))
    
    fig.update_layout(
        title='GM Monthly Focus - Top 5 KPIs',
        xaxis_title='Value',
        template='plotly_white',
        height=400,
        margin=dict(l=250, r=50, t=50, b=50)
    )
    
    return fig

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Invoicing Manager KPI Dashboard</h1>
        <p>Real-time tracking of invoicing performance metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    monthly_data = initialize_data()
    
    # Sidebar
    st.sidebar.header("📅 Dashboard Controls")
    
    # Month selector
    month_options = [m.strftime('%B %Y') for m in monthly_data['Month']]
    selected_month = st.sidebar.selectbox(
        "Select Month",
        month_options,
        index=len(month_options) - 1
    )
    
    month_idx = month_options.index(selected_month)
    current_kpis = calculate_kpis(monthly_data, month_idx)
    
    # View mode
    view_mode = st.sidebar.radio(
        "View Mode",
        ["GM Summary", "Detailed KPIs", "Trend Analysis"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📅 Viewing data for: **{selected_month}**")
    
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
                        st.markdown(f"<div class='status-{status_class}'>{status_icon}</div>", unsafe_allow_html=True)
                    
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

if __name__ == '__main__':
    main()
