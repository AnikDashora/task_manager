import streamlit as st
import random
from streamlit_echarts import st_echarts
from datetime import datetime, timedelta, date  # ✅ recommended
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from models.task_model import UserTasks
from models.user_model import User
from models.task_model import UserTasks
from backend.analytics import KpiServices,GraphServices
from backend.tasks import TaskSerives


def make_graph(total_task_all_day=12, completed_task=None, days=31,
               completed_color="#4caf50", remaining_color="#9fa8da", line_color="orange",
               show_bars=True):
    """
    Generate ECharts options for a task progress graph.

    Args:
        total_task_all_day (int): Max tasks in a day.
        completed_task (list): List of completed tasks per day. If None → random values.
        days (int): Number of days to display.
        completed_color (str): Color for completed bar.
        remaining_color (str): Color for remaining bar.
        line_color (str): Color for percentage line.
        show_bars (bool): If False → only show percentage line.

    Returns:
        dict: ECharts options
    """

    # Generate random data if not provided
    if completed_task is None:
        completed_task = [random.randint(0, total_task_all_day) for _ in range(days)]

    # Validate inputs
    if len(completed_task) != days:
        raise ValueError("completed_task length must match 'days'")
    if total_task_all_day <= 0:
        raise ValueError("total_task_all_day must be positive")

    # Clip values into range [0, total_task_all_day]
    completed_task = [min(max(0, val), total_task_all_day) for val in completed_task]

    # Dates for X-axis → past days
    today = date.today()
    if days > 31:
        x_labels = [(today - timedelta(days=days - i - 1)).strftime("%b %d") for i in range(days)]
    else:
        x_labels = [(today - timedelta(days=days - i - 1)).strftime("%a %d") for i in range(days)]

    # Calculations
    total_task_remaining = [total_task_all_day - c for c in completed_task]
    completed_percentage = [round((c / total_task_all_day) * 100, 2) for c in completed_task]

    # Base chart options
    options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
        "legend": {"data": ["Completed Task", "Remaining Task", "Percentage"]},
        "xAxis": {"type": "category", "data": x_labels},
        "yAxis": [
            {"type": "value", "name": "Tasks", "position": "left"},
            {
                "type": "value", "name": "Percentage", "position": "right",
                "min": 0, "max": 100, "axisLabel": {"formatter": "{value}%"}
            }
        ],
        "series": []
    }

    # Bar series (optional)
    if show_bars:
        options["series"].extend([
            {
                "name": "Completed Task", "type": "bar", "stack": "total",
                "data": completed_task, "itemStyle": {"color": completed_color}
            },
            {
                "name": "Remaining Task", "type": "bar", "stack": "total",
                "data": total_task_remaining, "itemStyle": {"color": remaining_color}
            }
        ])

    # Line chart for %
    options["series"].append(
        {
            "name": "Percentage", "type": "line", "yAxisIndex": 1,
            "data": completed_percentage, "itemStyle": {"color": line_color},
            "smooth": True
        }
    )

    return options

def change_theme():
    if(st.session_state["user"].theme == "Light"):
        st.session_state["user"].theme = "Dark"
    else:
        st.session_state["user"].theme = "Light"

def modal_toggle():
    st.session_state["modal_show"] = not(st.session_state["modal_show"])

root_variables = [# 0 for light theme and 1 for dark theme
    """:root{
            --bg-color: #f8f9fa;
            --text-color: #333;
            --primary-color: #4c9f70;
            --secondary-color: #4e598c;
            --card-bg: #fff;
            --card-title-color: #6b7280;
            --card-value-color: #333;
            --badge-bg-completion: rgba(76, 159, 112, 0.1);
            --badge-color-completion: #4c9f70;
            --badge-bg-progress: rgba(252, 175, 88, 0.1);
            --badge-color-progress: #fcaf58;
            --badge-bg-days: rgba(78, 89, 140, 0.1);
            --badge-color-days: #4e598c;
            --badge-bg-attention: rgba(239, 68, 68, 0.1);
            --badge-color-attention: #ef4444;
            --logo-bg: linear-gradient(135deg, #4e598c, rgba(78, 89, 140, 0.8));
            --logo-dot-bg: #4c9f70;
            --logo-dot-border: #f8f9fa;
            --stat-number-color: #333;
            --stat-label-color: #6b7280;
            --action-btn-bg: #f3f4f6;
            --theme-toggle-color: inherit;
            --card-value-bg: #111827;
            --card-subtitle-color: #6b7280;
            --completion-icon-bg: rgba(76, 159, 112, 0.2);
            --progress-icon-bg: rgba(252, 175, 88, 0.2);
            --days-icon-bg: rgba(78, 89, 140, 0.2);
            --attention-icon-bg: rgba(239, 68, 68, 0.2);
            --completion-icon-stroke: #4c9f70;
            --progress-icon-stroke: #fcaf58;
            --days-icon-stroke: #4e598c;
            --attention-icon-stroke: #ef4444;
            --chart-card-bg: #fff;
            --chart-title-color: #333;
            --chart-indicator-bg: #4c9f70;
            --filter-icon-color: #6b7280;
            --filter-select-bg: #fff;
            --filter-select-border: #d1d5db;
            --filter-select-color: #374151;
            --filter-select-focus-border: #4c9f70;
            --filter-select-focus-shadow: 0 0 0 2px rgba(76, 159, 112, 0.1);
            --filter-badge-bg: #f3f4f6;
            --filter-badge-color: #374151;
            --filter-count-color: #6b7280;
            --reset-btn-bg: transparent;
            --reset-btn-color: #6b7280;
            --reset-btn-hover-bg: #f3f4f6;
            --reset-btn-hover-color: #374151;
            --chart-grid: #f3f4f6;
            --chart-text: #6b7280;
            --chart-total-bar: #a7acc6;
            --chart-completed-bar: #4c9f70;
            --chart-line: #fcaf58;
            --border-color: rgba(167, 172, 198, 0.3);
            --task-item-bg: #fff;
            --task-item-border: rgba(167, 172, 198, 0.2);
            --task-item-hover-bg: rgba(78, 89, 140, 0.02);
            --task-checkbox-border: #d1d5db;
            --task-input-bg: #fff;
            --task-input-border: #d1d5db;
            --task-input-focus-border: #4c9f70;
            --task-input-focus-shadow: 0 0 0 2px rgba(76, 159, 112, 0.1);
            --add-task-btn-bg: #4c9f70;
            --add-task-btn-hover-bg: #3d7c5a;
            --add-date-btn-bg: linear-gradient(135deg, #4e598c, rgba(78, 89, 140, 0.8));
            --progress-bar-bg: rgba(167, 172, 198, 0.2);
            --progress-fill-bg: linear-gradient(to right, #4c9f70, #fcaf58);
            --empty-state-icon-bg: rgba(167, 172, 198, 0.1);
            --modal-overlay-bg: rgba(0, 0, 0, 0.5);
            --modal-bg: #fff;
            --modal-icon-bg: rgba(78, 89, 140, 0.1);
            --header-border-color: #e5e7eb;
        }
    """,
    """:root{
            --bg-color: #1a1a1a;
            --text-color: #fff;
            --primary-color: #10b981;
            --secondary-color: #8b5cf6;
            --card-bg: #1a1a19;
            --card-title-color: #9ca3af;
            --card-value-color: #e5e7eb;
            --badge-bg-completion: rgba(16, 185, 129, 0.1);
            --badge-color-completion: #10b981;
            --badge-bg-progress: rgba(245, 158, 11, 0.1);
            --badge-color-progress: #f59e0b;
            --badge-bg-days: rgba(139, 92, 246, 0.1);
            --badge-color-days: #8b5cf6;
            --badge-bg-attention: rgba(220, 38, 38, 0.1);
            --badge-color-attention: #dc2626;
            --logo-bg: linear-gradient(135deg, #6366f1, #8b5cf6);
            --logo-dot-bg: #10b981;
            --logo-dot-border: #1a1a1a;
            --stat-number-color: #e5e7eb;
            --stat-label-color: #9ca3af;
            --action-btn-bg: transparent;
            --theme-toggle-color: #f59e0b;
            --card-value-bg: #fff;
            --card-subtitle-color: #9ca3af;
            --completion-icon-bg: rgba(16, 185, 129, 0.2);
            --progress-icon-bg: rgba(245, 158, 11, 0.2);
            --days-icon-bg: rgba(139, 92, 246, 0.2);
            --attention-icon-bg: rgba(220, 38, 38, 0.2);
            --completion-icon-stroke: #10b981;
            --progress-icon-stroke: #f59e0b;
            --days-icon-stroke: #8b5cf6;
            --attention-icon-stroke: #dc2626;
            --chart-card-bg: #1f1f1f;
            --chart-title-color: #e5e7eb;
            --chart-indicator-bg: #10b981;
            --filter-icon-color: #9ca3af;
            --filter-select-bg: #374151;
            --filter-select-border: #4b5563;
            --filter-select-color: #e5e7eb;
            --filter-select-focus-border: #10b981;
            --filter-select-focus-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
            --filter-badge-bg: #374151;
            --filter-badge-color: #e5e7eb;
            --filter-count-color: #9ca3af;
            --reset-btn-bg: transparent;
            --reset-btn-color: #9ca3af;
            --reset-btn-hover-bg: #374151;
            --reset-btn-hover-color: #e5e7eb;
            --chart-grid: #374151;
            --chart-text: #e5e7eb;
            --chart-total-bar: #374151;
            --chart-completed-bar: #10b981;
            --chart-line: #f59e0b;
            --border-color: rgba(55, 65, 81, 0.5);
            --task-item-bg: #1f1f1f;
            --task-item-border: rgba(55, 65, 81, 0.3);
            --task-item-hover-bg: rgba(55, 65, 81, 0.3);
            --task-checkbox-border: #4b5563;
            --task-input-bg: #374151;
            --task-input-border: #4b5563;
            --task-input-focus-border: #10b981;
            --task-input-focus-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
            --add-task-btn-bg: #10b981;
            --add-task-btn-hover-bg: #059669;
            --add-date-btn-bg: linear-gradient(135deg, #6366f1, #8b5cf6);
            --progress-bar-bg: rgba(55, 65, 81, 0.3);
            --progress-fill-bg: linear-gradient(to right, #10b981, #f59e0b);
            --empty-state-icon-bg: rgba(55, 65, 81, 0.3);
            --modal-overlay-bg: rgba(0, 0, 0, 0.5);
            --modal-bg: #1f1f1f;
            --modal-icon-bg: rgba(139, 92, 246, 0.1);
            --header-border-color: rgba(55, 65, 81, 0.5);
        }
    """
]

chart_theme_variable = [["#fff","#333","#4c9f70"],["#1f1f1f","#e5e7eb","#10b981"]]

modal_variable = [# 0 for none and 1 for show
    """
    .stVerticalBlock.st-key-modal-overlay {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height:100% !important;
    background: var(--modal-overlay-bg) !important;
    display: none !important;
    align-items: center !important;
    justify-content: center !important;
    z-index: 1000 !important;
    opacity: 1 !important;
    visibility: visible !important;
    transition: all 0.3s ease !important;
    backdrop-filter:blur(4px);
    }
    """,
    """
    .stVerticalBlock.st-key-modal-overlay {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height:100% !important;
    background: var(--modal-overlay-bg) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    z-index: 1000 !important;
    opacity: 1 !important;
    visibility: visible !important;
    transition: all 0.3s ease !important;
    backdrop-filter:blur(4px);
    }
    """
]

remove_header_footer = """
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    /* Hide the orange loading progress bar */
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    .stDeployButton{
        display:none;
    }
    /* Remove top padding to avoid white space */
    .block-container {
        padding-top: 1rem !important;
    }
"""

page_setup = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            gap:0;
        }

         body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-color) !important;
            color: var(--text-color) !important;
            transition: all 0.3s ease;
        }

        .stApp {
            min-height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            background: var(--background) !important;
            padding: var(--page-padding);
            box-sizing: border-box;
        }

            /* Main View Container */
        .stAppViewContainer {
            flex: 1 1 auto !important;
            max-width: var(--max-width);
            margin: 0 auto;
            width: 100%;
            background: transparent !important;
            padding: 0 !important;
            display: flex;
            flex-direction: column;
            gap: 2.5rem;    
        }

            /* Main Block Container */
        .stMainBlockContainer {
            background: transparent !important;
            padding: 0 !important;
            width: 100% !important;
            max-width: var(--max-width) !important;
            margin: 0 auto;
            flex: 1 1 auto !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 2rem;
        }

            /* In the Main container inside MainBlockContainer */
        .stMain .stMainBlockContainer {
            padding: 0 !important;
            margin: 0 auto;   
        }

        .block-container {
            padding-top: 1rem !important;
        }
        .st-emotion-cache-tn0cau{
            gap:0;
        }

        .st-emotion-cache-r44huj{
            margin-bottom:0;
        }
        .st-emotion-cache-r44huj h1{
            padding:0;
        }

"""

header_styles = """
        /* Global body and container styling */

        /* Main Streamlit containers */
        

        /* HEADER SECTION MAPPING */
        
        /* Header container - maps to original .header */
        .st-key-header {
            display:flex !important;
            flex-direction:row !important;
            margin-bottom: 32px !important;
            border-bottom: 1px solid var(--header-border-color) !important;
            position: sticky !important;
            top:0 !important;
            backdrop-filter: blur(8px) !important;
            background: transparent !important;
            z-index: 10000 !important;
        }

        /* Header main - maps to original .header-main */
        .st-key-header-main {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 24px;
            padding: 20px 40px 0;
        }

        @media (min-width: 640px) {
            .st-key-header-main {
                flex-direction: row !important;
                align-items: center !important;
                justify-content: space-between !important;
            }
        }

        /* Logo section container */
        .st-key-logo-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .st-key-logo-section .st-emotion-cache-r44huj{
            display:flex;
            flex-direction:row;
            gap:1rem;
            flex-wrap:wrap;
            align-items:center;
            justify-content:center;
            
        }

        /* Logo styling */
        .logo {
           width: 50px;
            height: 50px;
            background: var(--logo-bg);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .logo-user-icon {
            width: 25px !important;
            height: 30px !important;
            stroke: white !important;
        }

        .logo::after {
            content: '';
            width: 16px;
            height: 16px;
            border-radius: 50%;
            position: absolute;
            top: -4px;
            right: -4px;
            border: 2px solid var(--logo-dot-border);
            background: var(--logo-dot-bg);
        }

        /* Brand info */
        .brand-info {
            flex: 1;
        }

        .brand-info h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 2px;
        }

        .brand-info p {
            font-size: 14px !important;
            color: var(--card-title-color) !important;
            font-weight: 400 !important;
            margin: 0 !important;
        }

        /* Header right section */
        .st-key-header-right {
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            flex-direction: row !important;
            justify-content:end;
        }

        @media (min-width: 640px) {
            .st-key-header-right {
                flex-direction: row !important;
            }
        }

        /* Stats container */
        .st-key-stats-container {
            display: flex !important;
            align-items: center !important;
            gap: 16px !important;
            padding: 8px 16px !important;
            background: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            width:fit-content;
        }

        .st-key-stats-container .st-emotion-cache-r44huj{
            display:flex;
            flex-direction:row;
            gap:1rem;
            flex-wrap:wrap;
            align-items:center;
            justify-content:center;
        }
        .st-key-header-right .st-emotion-cache-18kf3ut{
            width:fit-content;
        }

        .stat-item {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }

        .stat-divider {
            width: 1px !important;
            height: 16px !important;
            background: var(--border-color) !important;
        }

        .stat-number {
            font-size: 14px !important;
            font-weight: 500 !important;
            color: var(--stat-number-color) !important;
        }

        .stat-label {
            font-size: 12px !important;
            color: var(--stat-label-color) !important;
        }

        .svg-icon {
            width: 16px !important;
            height: 16px !important;
        }

        /* Header actions */
        .st-key-header-actions {
            display: flex !important;
            align-items: center !important;
            flex-direction:row !important;
            gap: 12px !important;
        }

        /* Streamlit buttons in header */
        .st-key-theme-toggle .stButton button,
        .st-key-logout-btn .stButton button {
            width: 36px !important;
            height: 36px !important;
            border: none !important;
            border-radius: 8px !important;
            background: var(--action-btn-bg) !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
            padding: 0 !important;
            min-height: 36px !important;
        }

        .st-key-theme-toggle .stButton button {
            background: transparent !important;
            color: var(--theme-toggle-color) !important;
        }

        .st-key-logout-btn .stButton button {
            color: var(--badge-color-attention) !important;
            background: transparent !important;
        }

        .st-key-logout-btn .stButton button:hover {
            background: var(--badge-bg-attention) !important;
        }
        
"""

kpi_styles = """
        .st-key-kpi-section {
            padding: 0 40px 40px 40px !important;
            max-width: 1400px !important;
            margin: 0 auto !important;
        }

        /* KPI container - grid layout */
        .st-key-kpi-container {
            display: grid !important;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
            gap: 24px !important;
        }

        /* Card base styling */
        .card {
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
            border: none !important;
            background: var(--card-bg) !important;
            margin-bottom: 0 !important;
        }

        .card-content {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            width: 100% !important;
        }

        .card-info {
            flex: 1 !important;
        }

        .card-title {
            font-size: 14px !important;
            font-weight: 400 !important;
            margin-bottom: 4px !important;
            color: var(--card-title-color) !important;
            margin-top: 0 !important;
        }

        .card-value-container {
            display: flex !important;
            align-items: baseline !important;
            gap: 8px !important;
            margin-top: 4px !important;
        }

        .card-value {
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: var(--card-value-bg) !important;
        }

        .card-badge {
            font-size: 12px !important;
            font-weight: 500 !important;
            padding: 2px 8px !important;
            border-radius: 6px !important;
            line-height: 1.2 !important;
        }

        .card-icon {
            width: 48px !important;
            height: 48px !important;
            border-radius: 12px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex-shrink: 0 !important;
        }

        .card-svg-icon {
            width: 24px !important;
            height: 24px !important;
        }

        /* Card theme variations */
        .card.completion {
            background: var(--badge-bg-completion) !important;
        }

        .card.progress {
            background: var(--badge-bg-progress) !important;
        }

        .card.days {
            background: var(--badge-bg-days) !important;
        }

        .card.attention {
            background: var(--badge-bg-attention) !important;
        }

        .card.completion .card-badge {
            background: var(--badge-bg-completion) !important;
            color: var(--badge-color-completion) !important;
        }

        .card.progress .card-badge {
            background: var(--badge-bg-progress) !important;
            color: var(--badge-color-progress) !important;
        }

        .card.days .card-badge {
            background: var(--badge-bg-days) !important;
            color: var(--badge-color-days) !important;
        }

        .card.attention .card-badge {
            background: var(--badge-bg-attention) !important;
            color: var(--badge-color-attention) !important;
        }

        /* Icon backgrounds and colors */
        .completion-icon {
            background: var(--completion-icon-bg) !important;
        }

        .progress-icon {
            background: var(--progress-icon-bg) !important;
        }

        .days-icon {
            background: var(--days-icon-bg) !important;
        }

        .attention-icon {
            background: var(--attention-icon-bg) !important;
        }

        .completion-icon svg {
            stroke: var(--completion-icon-stroke) !important;
        }

        .progress-icon svg {
            stroke: var(--progress-icon-stroke) !important;
        }

        .days-icon svg {
            stroke: var(--days-icon-stroke) !important;
        }

        .attention-icon svg {
            stroke: var(--attention-icon-stroke) !important;
        }

        

        /* Stats container icon colors - specific overrides */
        .st-key-stats-container svg[stroke="#4e598c"] {
            stroke: var(--days-icon-stroke) !important;
        }

        .st-key-stats-container svg[stroke="#4c9f70"] {
            stroke: var(--completion-icon-stroke) !important;
        }

        

        /* Typography fixes */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color) !important;
        }

        p {
            color: var(--text-color) !important;
        }

        /* RESPONSIVE ADJUSTMENTS */
        @media (max-width: 640px) {
            .st-key-kpi-section {
                padding: 0 20px 40px 20px !important;
            }
            
            .st-key-kpi-container {
                grid-template-columns: 1fr !important;
                gap: 16px !important;
            }
            
            .st-key-stats-container {
                flex-direction: column !important;
                gap: 8px !important;
                padding: 12px !important;
            }
            
            .stat-divider {
                width: 100% !important;
                height: 1px !important;
            }
        }

        /* Additional utility classes */
        .svg-icon-sm {
            width: 12px !important;
            height: 12px !important;
        }

"""

chart_styles = """
.stVerticalBlock.st-key-chart-section {
    display: flex !important;
    flex-direction: column !important;
    padding: 0 40px 40px 40px !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
    width: 100% !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

.stVerticalBlock.st-key-chart-section .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: column !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* ===== CHART CARD ===== */
/* Maps to original .chart-card */
.stVerticalBlock.st-key-chart-card {
    display: flex !important;
    flex-direction: column !important;
    background: var(--chart-card-bg) !important;
    border-radius: 16px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s ease !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

.stVerticalBlock.st-key-chart-card .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: column !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* ===== CHART HEADER ===== */
/* Maps to original .chart-header */
.stVerticalBlock.st-key-chart-header {
    display: flex !important;
    flex-direction: column !important;
    padding: 24px 24px 0 24px !important;
    border-bottom: none !important;
    background: transparent !important;
    width: 100% !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex-shrink: 0 !important;
}

.stVerticalBlock.st-key-chart-header .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: column !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* ===== CHART HEADER TOP ===== */
/* Maps to original .chart-header-top */
.stVerticalBlock.st-key-chart-header-top {
    display: flex !important;
    flex-direction: column !important;
    gap: 16px !important;
    margin-bottom: 16px !important;
    background: transparent !important;
    padding: 0 !important;
    width: 100% !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex-shrink: 0 !important;
}

@media (min-width: 640px) {
    .stVerticalBlock.st-key-chart-header-top {
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 16px !important;
    }
}

.stVerticalBlock.st-key-chart-header-top .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: column !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

@media (min-width: 640px) {
    .stVerticalBlock.st-key-chart-header-top .st-emotion-cache-18kf3ut {
        flex-direction: row !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
}

/* ===== CHART TITLE ===== */
/* Maps to original .chart-title */
.chart-title {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    color: var(--chart-title-color) !important;
    gap: 8px !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.4 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex-shrink: 0 !important;
}

.chart-indicator {
    display: block !important;
    width: 8px !important;
    height: 8px !important;
    background: var(--chart-indicator-bg) !important;
    border-radius: 50% !important;
    flex-shrink: 0 !important;
}

/* Hide Streamlit's default header action elements */
.st-emotion-cache-gi0tri {
    display: none !important;
}

/* ===== FILTER CONTROLS ===== */
/* Maps to original .filter-controls */
.stVerticalBlock.st-key-filter-controls {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
    flex-wrap: wrap !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    width: auto !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex-shrink: 0 !important;
}

.stVerticalBlock.st-key-filter-controls .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* ===== FILTER GROUP ===== */
/* Maps to original .filter-group */
.stVerticalBlock.st-key-filter-group {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    width: auto !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex-shrink: 0 !important;
}

.stVerticalBlock.st-key-filter-group .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* ===== FILTER ICON ===== */
/* Maps to original .filter-icon */
.filter-icon {
    display: block !important;
    width: 16px !important;
    height: 16px !important;
    color: var(--filter-icon-color) !important;
    flex-shrink: 0 !important;
}

.stVerticalBlock.st-key-filter-group .stMarkdown {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content:end !important;
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

.stVerticalBlock.st-key-filter-group .st-emotion-cache-r44huj {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* ===== FILTER SELECT ===== */
/* Maps to original .filter-select */
.stElementContainer.st-key-filter-select {
    display: flex !important;
    flex-direction: column !important;
    margin: 0 !important;
    padding: 0 !important;
    width: auto !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex-shrink: 0 !important;
}

.stElementContainer.st-key-filter-select .stSelectbox {
    display: flex !important;
    flex-direction: column !important;
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* Hide the label */
.stElementContainer.st-key-filter-select .st-emotion-cache-12x9678 {
    display: none !important;
}

/* Style the select container */
.stElementContainer.st-key-filter-select [data-baseweb="select"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    height: 32px !important;
    min-height: 32px !important;
    max-height: 32px !important;
    margin: 0 !important;
    overflow: visible !important;
}

.stElementContainer.st-key-filter-select [data-baseweb="select"] > div {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    height: 32px !important;
    min-height: 32px !important;
    max-height: 32px !important;
    padding: 4px 8px !important;
    border: 1px solid var(--filter-select-border) !important;
    border-radius: 6px !important;
    background: var(--filter-select-bg) !important;
    transition: all 0.2s ease !important;
    width: fit-content !important;
    overflow: hidden !important;
}

.stElementContainer.st-key-filter-select [data-baseweb="select"] > div:focus-within {
    border-color: var(--filter-select-focus-border) !important;
    box-shadow: var(--filter-select-focus-shadow) !important;
}

/* Style the selected value text */
.stElementContainer.st-key-filter-select .st-bm {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    color: var(--filter-select-color) !important;
    font-size: 14px !important;
    line-height: 1.2 !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    flex: 1 !important;
}

/* Style the dropdown arrow */
.stElementContainer.st-key-filter-select .st-co {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: center !important;
    color: var(--filter-icon-color) !important;
    width: 12px !important;
    height: 12px !important;
    flex-shrink: 0 !important;
}

/* Style the input field */
.stElementContainer.st-key-filter-select input {
    display: flex !important;
    flex-direction: row !important;
    color: var(--filter-select-color) !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    font-size: 14px !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: hidden !important;
}

/* ===== RESET BUTTON ===== */
/* Maps to original .reset-btn */
.stElementContainer.st-key-reset-btn {
    display: flex !important;
    flex-direction: column !important;
    margin: 0 !important;
    padding: 0 !important;
    width: fit-content !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex-shrink: 0 !important;
}

.stElementContainer.st-key-reset-btn .stButton {
    display: flex !important;
    flex-direction: column !important;
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

.stElementContainer.st-key-reset-btn button {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: center !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
    max-width: 32px !important;
    max-height: 32px !important;
    border: none !important;
    background: var(--reset-btn-bg) !important;
    border-radius: 6px !important;
    cursor: pointer !important;
    color: var(--reset-btn-color) !important;
    transition: all 0.2s ease !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}

.stElementContainer.st-key-reset-btn button:hover {
    background: var(--reset-btn-hover-bg) !important;
    color: var(--reset-btn-hover-color) !important;
}

.stElementContainer.st-key-reset-btn button span {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 12px !important;
    line-height: 1 !important;
    width: 100% !important;
    height: 100% !important;
}

/* ===== CHART CONTENT ===== */
/* Maps to original .chart-content */

.stVerticalBlock.st-key-chart-content {
    display: flex !important;
    flex-direction: column !important;
    padding: 24px !important;
    background: transparent !important;
    width: 100% !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex: 1 !important;
}

.stVerticalBlock.st-key-chart-content .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: column !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    flex: 1 !important;
}

/* ===== CHART CONTAINER ===== */
/* Maps to original .chart-container */
.stVerticalBlock.st-key-chart-container {
    display: flex !important;
    flex-direction: column !important;
    height: 320px !important;
    min-height: 320px !important;
    max-height: 320px !important;
    position: relative !important;
    overflow: hidden !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    flex-shrink: 0 !important;
}

.stVerticalBlock.st-key-chart-container .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    overflow: hidden !important;
}

/* ===== CHART IFRAME ===== */
/* Maps to original #taskChart */
.stElementContainer.st-key-taskChart {
    display: flex !important;
    flex-direction: column !important;
    width: 100% !important;
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    flex: 1 !important;
}

.stElementContainer.st-key-taskChart iframe {
    display: block !important;
    width: 100% !important;
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    overflow: hidden !important;
}

.stElementContainer.st-key-taskChart .st-emotion-cache-8atqhb {
    display: flex !important;
    flex-direction: column !important;
    width: 100% !important;
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

/* ===== GLOBAL STREAMLIT OVERRIDES ===== */
/* Remove default Streamlit spacing and styling */
.stVerticalBlock.st-key-chart-section .stElementContainer,
.stVerticalBlock.st-key-chart-card .stElementContainer,
.stVerticalBlock.st-key-chart-header .stElementContainer,
.stVerticalBlock.st-key-chart-header-top .stElementContainer,
.stVerticalBlock.st-key-filter-controls .stElementContainer,
.stVerticalBlock.st-key-filter-group .stElementContainer,
.stVerticalBlock.st-key-chart-content .stElementContainer,
.stVerticalBlock.st-key-chart-container .stElementContainer {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-bottom: 0 !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
    overflow: visible !important;
}

/* Special handling for chart container element */
.stVerticalBlock.st-key-chart-container .stElementContainer.st-key-taskChart {
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    overflow: hidden !important;
}

/* Remove default gaps between elements */
.stVerticalBlock.st-key-chart-section .st-emotion-cache-18kf3ut,
.stVerticalBlock.st-key-chart-card .st-emotion-cache-18kf3ut,
.stVerticalBlock.st-key-chart-header .st-emotion-cache-18kf3ut,
.stVerticalBlock.st-key-chart-content .st-emotion-cache-18kf3ut {
    gap: 0 !important;
}

/* Apply theme transitions */
.stVerticalBlock.st-key-chart-section,
.stVerticalBlock.st-key-chart-card,
.chart-title,
.filter-icon,
.stElementContainer.st-key-filter-select [data-baseweb="select"] > div,
.stElementContainer.st-key-reset-btn button {
    transition: all 0.3s ease !important;
}

/* ===== RESPONSIVE DESIGN ===== */
@media (max-width: 639px) {
    .stVerticalBlock.st-key-chart-section {
        padding: 0 20px 20px 20px !important;
    }
    
    .stVerticalBlock.st-key-chart-header {
        padding: 16px 16px 0 16px !important;
    }
    
    .stVerticalBlock.st-key-chart-content {
        padding: 16px !important;
    }
    
    .stVerticalBlock.st-key-chart-header-top {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 12px !important;
    }
    
    .stVerticalBlock.st-key-chart-header-top .st-emotion-cache-18kf3ut {
        flex-direction: column !important;
        align-items: flex-start !important;
    }
    
    .stVerticalBlock.st-key-filter-controls {
        width: 100% !important;
        justify-content: flex-start !important;
        flex-direction: row !important;
    }
    
    .stVerticalBlock.st-key-filter-controls .st-emotion-cache-18kf3ut {
        flex-direction: row !important;
        justify-content: flex-start !important;
    }
    
    .chart-title {
        flex-direction: row !important;
    }
    
    .stVerticalBlock.st-key-filter-group {
        flex-direction: row !important;
    }
    
    .stVerticalBlock.st-key-filter-group .st-emotion-cache-18kf3ut {
        flex-direction: row !important;
    }
}
"""

empty_date_styles = """
        .stVerticalBlock.st-key-main-content {
            padding: 40px !important;
            max-width: 1400px !important;
            margin: 0 auto !important;
            width: 100% !important;
            background: transparent !important;
        }

        .stVerticalBlock.st-key-main-content .st-emotion-cache-18kf3ut {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ===== SECTION HEADER ===== */
        /* Maps to original .section-header */
        .stVerticalBlock.st-key-section-header {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            margin-bottom: 24px !important;
            gap: 16px !important;
            background: transparent !important;
            padding: 0 !important;
            width: 100% !important;
        }

        .stVerticalBlock.st-key-section-header .st-emotion-cache-18kf3ut {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            width: 100% !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            gap: 16px !important;
        }

        

        /* Section Title */
        .section-title {
            font-size: 18px !important;
            font-weight: 600 !important;
            color: var(--chart-title-color) !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Hide default Streamlit heading action elements */
        .st-emotion-cache-gi0tri {
            display: none !important;
        }

        /* ===== ADD DATE BUTTONS ===== */
        /* Maps to original .add-date-btn */
        .stElementContainer.st-key-add-date-btn-1,
        .stElementContainer.st-key-add-date-btn-2 {
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            background: transparent !important;
        }

        .stElementContainer.st-key-add-date-btn-1 .stButton,
        .stElementContainer.st-key-add-date-btn-2 .stButton {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
        }

        .stElementContainer.st-key-add-date-btn-1 .stButton{
            display: flex !important;
            justify-content: end !important;
            align-items: center !important;
        }

        .stElementContainer.st-key-add-date-btn-1 button,
        .stElementContainer.st-key-add-date-btn-2 button {
            background: var(--add-date-btn-bg) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            transition: all 0.2s ease !important;
            min-height: auto !important;
            height: auto !important;
            width:fit-content;
        }

        .stElementContainer.st-key-add-date-btn-1 button:hover,
        .stElementContainer.st-key-add-date-btn-2 button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
        }

        .stElementContainer.st-key-add-date-btn-1 button .st-emotion-cache-cli92z,
        .stElementContainer.st-key-add-date-btn-2 button .st-emotion-cache-cli92z {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .stElementContainer.st-key-add-date-btn-1 button span[data-testid="stIconMaterial"],
        .stElementContainer.st-key-add-date-btn-2 button span[data-testid="stIconMaterial"] {
            font-size: 16px !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .stElementContainer.st-key-add-date-btn-1 button .st-emotion-cache-17c7e5f,
        .stElementContainer.st-key-add-date-btn-2 button .st-emotion-cache-17c7e5f {
            margin: 0 !important;
            padding: 0 !important;
        }

        .stElementContainer.st-key-add-date-btn-1 button .st-emotion-cache-17c7e5f p,
        .stElementContainer.st-key-add-date-btn-2 button .st-emotion-cache-17c7e5f p {
            margin: 0 !important;
            padding: 0 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            color: inherit !important;
        }

        /* ===== TASKS CONTAINER ===== */
        /* Maps to original #tasksContainer */
        .stVerticalBlock.st-key-tasksContainer {
            width: 100% !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .stVerticalBlock.st-key-tasksContainer .st-emotion-cache-18kf3ut {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            height:initial;
        }

        /* ===== EMPTY STATE ===== */
        /* Maps to original .empty-state */
        .stVerticalBlock.st-key-empty-state {
            display:flex !important;
            align-items:center !important;
            text-align: center !important;
            padding: 48px 20px !important;
            background: transparent !important;
            width: 100% !important;
            margin: 0 !important;
        }

        .stVerticalBlock.st-key-empty-state .st-emotion-cache-18kf3ut {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            text-align: center !important;
        }

        /* Empty State Icon */
        .empty-state-icon {
            width: 96px !important;
            height: 96px !important;
            background: var(--empty-state-icon-bg) !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 auto 24px !important;
        }

        .empty-state-icon svg {
            width: 48px !important;
            height: 48px !important;
            stroke: var(--filter-icon-color) !important;
        }

        /* Empty State Text */
        .stVerticalBlock.st-key-empty-state h3 {
            font-size: 18px !important;
            font-weight: 600 !important;
            color: var(--text-color) !important;
            margin: 0 0 8px 0 !important;
            padding: 0 !important;
        }

        .stVerticalBlock.st-key-empty-state p {
            color: var(--card-title-color) !important;
            margin: 0 0 24px 0 !important;
            padding: 0 !important;
            max-width: 400px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            font-size: 14px !important;
        }

        /* Center the second add button in empty state */
        .stVerticalBlock.st-key-empty-state .stElementContainer.st-key-add-date-btn-2 {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 25% !important;
        }

        /* ===== RESPONSIVE DESIGN ===== */
        @media (max-width: 640px) {
            .block-container {
                padding: 1rem 20px !important;
            }

            .stVerticalBlock.st-key-main-content {
                padding: 20px !important;
            }

            .stVerticalBlock.st-key-section-header .st-emotion-cache-18kf3ut {
                flex-direction: column !important;
                align-items: flex-start !important;
                gap: 12px !important;
            }

            .stVerticalBlock.st-key-empty-state {
                padding: 32px 16px !important;
            }

            .empty-state-icon {
                width: 80px !important;
                height: 80px !important;
                margin-bottom: 20px !important;
            }

            .empty-state-icon svg {
                width: 40px !important;
                height: 40px !important;
            }
        }

        /* ===== UTILITY CLASSES ===== */
        .svg-icon {
            width: 16px !important;
            height: 16px !important;
        }

        .svg-icon-sm {
            width: 12px !important;
            height: 12px !important;
        }

        .card-svg-icon {
            width: 24px !important;
            height: 24px !important;
        }

        /* ===== TYPOGRAPHY OVERRIDES ===== */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color) !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        p {
            color: var(--text-color) !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        
"""

fill_date_styles = """ 
      
        .stVerticalBlock.st-key-tasks-grid  {
            display: grid !important;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)) !important;
            gap: 16px !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ===== DATE CARDS ===== */
        .stVerticalBlock[class *= "st-key-date-card"] {
            background: var(--card-bg) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            border: 1px solid var(--border-color) !important;
            transition: all 0.3s ease !important;
            margin: 0 !important;
            min-height:450px;
        }

        .stVerticalBlock[class *= "st-key-date-card"]:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }

        .stVerticalBlock[class *= "st-key-date-card"] .st-emotion-cache-18kf3ut {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ===== DATE CARD HEADERS ===== */
        .stVerticalBlock[class *= "st-key-task-card-header-"] {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: flex-start !important;
            background: transparent !important;
            padding: 0 !important;
        }

        .stVerticalBlock[class *= "st-key-task-card-header-"] .st-emotion-cache-18kf3ut {
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: flex-start !important;
            width: 100% !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Date info styling */
        .date-info {
            flex: 1;
            min-width: 0;
        }

        .date-title {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            margin-bottom: 8px !important;
        }

        .date-title h3 {
            font-size: 16px !important;
            font-weight: 600 !important;
            color: var(--chart-title-color) !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .date-badge {
            display: inline-block !important;
            padding: 2px 8px !important;
            border-radius: 6px !important;
            font-size: 12px !important;
            font-weight: 500 !important;
        }

        .badge-no-tasks {
            background: rgba(167, 172, 198, 0.1) !important;
            color: #47331c !important;
        }

        .badge-medium {
            background: var(--badge-bg-days) !important;
            color: var(--badge-color-days) !important;
        }

        .badge-complete {
            background: var(--badge-bg-completion) !important;
            color: var(--badge-color-completion) !important;
        }

        .badge-high {
            background: var(--badge-bg-progress) !important;
            color: var(--badge-color-progress) !important;
        }

        .badge-low {
            background: rgba(167, 172, 198, 0.1) !important;
            color: #47331c !important;
        }

        /* ===== REMOVE DATE BUTTONS ===== */
        .stElementContainer[class *= "st-key-remove-date-btn-"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .stElementContainer[class *= "st-key-remove-date-btn-"] button {
            width: 28px !important;
            height: 28px !important;
            border: none !important;
            background: transparent !important;
            cursor: pointer !important;
            border-radius: 6px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: var(--filter-icon-color) !important;
            transition: all 0.2s ease !important;
            padding: 0 !important;
            min-height: auto !important;
        }

        .stElementContainer[class *= "st-key-remove-date-btn-"] button:hover {
            background: var(--badge-bg-attention) !important;
            color: var(--badge-color-attention) !important;
        }

        /* ===== PROGRESS BAR ===== */
        .progress-bar {
            width: 100% !important;
            height: 6px !important;
            background: var(--progress-bar-bg) !important;
            border-radius: 3px !important;
            overflow: hidden !important;
            position: relative !important;
        }
        .progress-fill{
            height: 100% !important;
            background: var(--progress-fill-bg) !important;
            border-radius: 3px !important;
            transition: width 0.3s ease !important;
        }

        /* ===== ADD TASK FORMS ===== */
        .stVerticalBlock[class *= "st-key-add-task-form-"] {
            display: flex !important;
            align-items:center !important;
            flex-direction: row !important;
            gap: 8px !important;
            background: transparent !important;
            padding: 0 !important;
        }

        .stVerticalBlock[class *= "st-key-add-task-form-"] .st-emotion-cache-18kf3ut{
            display: flex !important;
            flex-direction: row !important;
            align-items: flex-end !important;
            gap: 8px !important;
            width: 100% !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ===== TASK INPUTS ===== */
        .stElementContainer[class *= "st-key-task-input-"] {
            flex: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .stElementContainer[class *= "st-key-task-input-"] .stTextInput {
            margin: 0 !important;
        }
        
        .stElementContainer[class *= "st-key-task-input-"] label {
            display: none !important;
        }

        div[data-testid="stTextInputRootElement"]{
            border-radius: 10px !important;
            border:none !important;
            border-color:transparent !important;
            width:100% !important;
            height:100% !important;
        }

        .stElementContainer[class *= "st-key-task-input-"] input {
            padding: 8px 12px !important;
            border: 2px solid var(--task-input-border) !important;
            border-radius: 10px !important;
            font-size: 14px !important;
            background: var(--task-input-bg) !important;
            color: var(--text-color) !important;
            width: 100% !important;
        }

        .stElementContainer[class *= "st-key-task-input-"] input::placeholder{
            color:var(--text-color) !important;
            opacity:50% !important;
        }


        .stElementContainer[class *= "st-key-task-input-"] input:focus {
            outline: none !important;
            border-color: var(--task-input-focus-border) !important;
            box-shadow: var(--task-input-focus-shadow) !important;
        }

        /* ===== ADD TASK BUTTONS ===== */
        .stElementContainer[class *= "st-key-add-task-btn-"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .stElementContainer[class *= "st-key-add-task-btn-"] button {
            padding: 8px 12px !important;
            background: var(--add-task-btn-bg) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
            min-height: auto !important;
            height: auto !important;
            width: fit-content !important;
        }

        .stElementContainer[class *= "st-key-add-task-btn-"] button:hover {
            background: var(--add-task-btn-hover-bg) !important;
        }

        /* ===== TASK LISTS ===== */
        .stVerticalBlock[class *= "st-key-task-list-"] {
            max-height: 250px !important;
            overflow-y: auto !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            gap:0.25rem;
        }

        .stVerticalBlock[class *= "st-key-task-list-"] .st-emotion-cache-18kf3ut {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ===== TASK ITEMS ===== */
        .stVerticalBlock[class *= "st-key-task-item-"],
        .stVerticalBlock[class *= "st-key-task-completed-item-"] {
            display: flex !important;
            flex-direction: row !important;
            align-items: flex-start !important;
            justify-content:space-between !important;
            gap: 8px !important;
            padding: 12px !important;
            border: 1px solid var(--task-item-border) !important;
            border-radius: 8px !important;
            background: var(--task-item-bg) !important;
            transition: all 0.2s ease !important;
        }

        .stVerticalBlock[class *= "st-key-task-item-"]:hover,
        .stVerticalBlock[class *= "st-key-task-completed-item-"]:hover {
            background: var(--task-item-hover-bg) !important;
        }

        .stVerticalBlock[class *= "st-key-task-completed-item-"] {
            background: var(--badge-bg-completion) !important;
            border-color: var(--badge-color-completion) !important;
        }

        .stVerticalBlock[class *= "st-key-task-item-"] .st-emotion-cache-18kf3ut,
        .stVerticalBlock[class *= "st-key-task-completed-item-"] .st-emotion-cache-18kf3ut {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 12px !important;
            width: 100% !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* ===== TASK CHECKBOXES ===== */
        .stElementContainer[class *= "st-key-task-checkbox-"],
        .stElementContainer[class *= "st-key-task-checkbox-"] {
            margin: 0 !important;
            padding: 0 !important;
            flex-shrink: 0 !important;
            width:85%;
        }

        .stElementContainer[class *= "st-key-task-checkbox-"] .stCheckbox,
        .stElementContainer[class *= "st-key-task-checkbox-"] .stCheckbox {
            margin: 0 !important;
            padding: 0 !important;
            width:100%;
        }

        .stElementContainer[class *= "st-key-task-checkbox-"] label,
        .stElementContainer[class *= "st-key-task-checkbox-"] label {
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            margin: 0 !important;
            padding: 0 !important;
            cursor: pointer !important;
            width:100%;
        }

        .stElementContainer[class *= "st-key-task-checkbox-"] span{
            margin:0 !important;
        }

        

        /* Custom checkbox styling */
        .stElementContainer[class *= "st-key-task-checkbox-"] input[type="checkbox"]{
                position: absolute !important;
                opacity: 0 !important;
                width: 20px !important;
                height: 20px !important;
                margin: 0 !important;
                cursor: pointer !important;
        }

        .stElementContainer[class *= "st-key-task-checkbox-"] input[type="checkbox"]:checked{
            background: var(--primary-color) !important;
            border-color: var(--primary-color) !important;
            
        }

        .stElementContainer[class *= "st-key-task-checkbox-"] input[type="checkbox"]:checked::after {
            content: '✓' !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            color: white !important;
            font-size: 12px !important;
            font-weight: bold !important;
        }

        /* Task text styling */
        .stElementContainer[class *= "st-key-task-checkbox-"] .st-emotion-cache-17c7e5f p {
            font-size: 14px !important;
            line-height: 1.4 !important;
            color: var(--text-color) !important;
            word-wrap: break-word !important;
            margin: 0 !important;
            padding: 0 !important;
            flex: 1 !important;
        }

        /* Completed task text styling */
        .stVerticalBlock[class *= "st-key-task-completed-item-"] .st-emotion-cache-17c7e5f p {
            text-decoration: line-through !important;
            color: var(--primary-color) !important;
        }

        /* Hide default checkbox styling elements */
        .stElementContainer[class *= "st-key-task-checkbox-"] .st-c6{
            display: none !important;
        }

        .stElementContainer[class *= "st-key-task-checkbox-"] .st-emotion-cache-y4bq5x {
            visibility: visible !important;
            flex: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* ===== REMOVE TASK BUTTONS ===== */
        .stElementContainer[class *= "st-key-remove-task-btn-"] {
            margin: 0 !important;
            padding: 0 !important;
            flex-shrink: 0 !important;
        }

        .stElementContainer[class *= "st-key-remove-task-btn-"] button {
            width: 24px !important;
            height: 24px !important;
            border: none !important;
            background: transparent !important;
            cursor: pointer !important;
            border-radius: 4px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: var(--filter-icon-color) !important;
            transition: all 0.2s ease !important;
            flex-shrink: 0 !important;
            padding: 0 !important;
            min-height: auto !important;
        }

        .stElementContainer[class *= "st-key-remove-task-btn-"] button:hover {
            background: var(--badge-bg-attention) !important;
            color: var(--badge-color-attention) !important;
        }

        /* ===== NO TASKS STATE ===== */
        .no-tasks {
            text-align: center !important;
            padding: 24px !important;
            color: var(--card-title-color) !important;
        }

        .no-tasks-icon {
            margin: 0 auto 8px !important;
            opacity: 0.5 !important;
        }

        .no-tasks p {
            margin: 8px 0 0 0 !important;
            padding: 0 !important;
            font-size: 14px !important;
            color: var(--card-title-color) !important;
        }

        /* ===== EMPTY STATE ===== */
        .stVerticalBlock.st-key-empty-state {
            display: flex !important;
            align-items: center !important;
            text-align: center !important;
            padding: 48px 20px !important;
            background: transparent !important;
            width: 100% !important;
            margin: 0 !important;
        }

        .stVerticalBlock.st-key-empty-state .st-emotion-cache-18kf3ut {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            text-align: center !important;
            width: 100% !important;
        }

        .empty-state-icon {
            width: 96px !important;
            height: 96px !important;
            background: var(--empty-state-icon-bg) !important;
            border-radius: 50% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 auto 24px !important;
        }

        .empty-state-icon svg {
            width: 48px !important;
            height: 48px !important;
            stroke: var(--filter-icon-color) !important;
        }

        .stVerticalBlock.st-key-empty-state h3 {
            font-size: 18px !important;
            font-weight: 600 !important;
            color: var(--text-color) !important;
            margin: 0 0 8px 0 !important;
            padding: 0 !important;
        }

        .stVerticalBlock.st-key-empty-state p {
            color: var(--card-title-color) !important;
            margin: 0 0 24px 0 !important;
            padding: 0 !important;
            max-width: 400px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            font-size: 14px !important;
        }

        

        /* ===== UTILITY CLASSES ===== */
        .svg-icon {
            width: 16px !important;
            height: 16px !important;
        }

        .svg-icon-sm {
            width: 12px !important;
            height: 12px !important;
        }

        .card-svg-icon {
            width: 24px !important;
            height: 24px !important;
        }

        /* ===== RESPONSIVE DESIGN ===== */
        @media (max-width: 640px) {
            .stMainBlockContainer {
                padding: 20px !important;
            }

            .stVerticalBlock.st-key-section-header .st-emotion-cache-18kf3ut {
                flex-direction: column !important;
                align-items: flex-start !important;
                gap: 12px !important;
            }

            .stVerticalBlock.st-key-empty-state {
                padding: 32px 16px !important;
            }

            .empty-state-icon {
                width: 80px !important;
                height: 80px !important;
                margin-bottom: 20px !important;
            }

            .empty-state-icon svg {
                width: 40px !important;
                height: 40px !important;
            }

            .stVerticalBlock.st-key-tasks-grid .st-emotion-cache-18kf3ut {
                grid-template-columns: 1fr !important;
            }
        }

        /* ===== TYPOGRAPHY OVERRIDES ===== */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color) !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        p {
            color: var(--text-color) !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        /* ===== ICON STYLING ===== */
        .stElementContainer[class *= "st-key-add-task-btn-"] [data-testid="stIconMaterial"],
        .stElementContainer[class *= "st-key-remove-date-btn-"] [data-testid="stIconMaterial"],
        .stElementContainer[class *= "st-key-remove-task-btn-"] [data-testid="stIconMaterial"],
        .stElementContainer[class *= "st-key-remove-task-btn-"] [data-testid="stIconMaterial"] {
            font-size: 16px !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
            display:flex;
            align-items:center;
            justify-content:center;
            width:100%;
            height:100%;
        }

        /* ===== STREAMLIT ELEMENT OVERRIDES ===== */
        .stElementContainer {
            margin: 0 !important;
        }

        .stButton {
            margin: 0 !important;
        }

        .stTextInput {
            margin: 0 !important;
        }

        .stCheckbox {
            margin: 0 !important;
        }

        .stMarkdown {
            margin: 0 !important;
        }

        /* ===== ADDITIONAL FIXES ===== */
        .st-emotion-cache-18kf3ut {
            gap: 0 !important;
        }

        

        

        /* Fix for icon containers */
        .stElementContainer[class *= "st-key-add-task-btn-"] .st-emotion-cache-1kfcwut,
        .stElementContainer[class *= "st-key-remove-date-btn-"] .st-emotion-cache-1kfcwut,
        .stElementContainer[class *= "st-key-remove-task-btn-"] .st-emotion-cache-1kfcwut,
        .stElementContainer[class *= "st-key-remove-task-btn-"] .st-emotion-cache-1kfcwut {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0 !important;
            width:100%;
            height:100%;
        }
"""

modal_style = """

.stVerticalBlock.st-key-modal-overlay .st-emotion-cache-18kf3ut {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: 100% !important;
}

/* ===== MODAL CONTAINER MAPPING ===== */
/* Maps to original .modal */
.stVerticalBlock.st-key-modal {
    background: var(--modal-bg) !important;
    border-radius: 16px !important;
    max-width: 500px !important;
    width: 90% !important;
    max-height: max-content !important;
    overflow-y: auto !important;
    transform: scale(1) !important;
    transition: transform 0.3s ease !important;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25) !important;
}

.stVerticalBlock.st-key-modal .st-emotion-cache-18kf3ut {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ===== MODAL HEADER MAPPING ===== */
/* Maps to original .modal-header */
.modal-header {
    padding: 24px 24px 0 !important;
    border-bottom: none !important;
}

.modal-header-content {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    margin-bottom: 16px !important;
}

.modal-icon {
    width: 40px !important;
    height: 40px !important;
    background: var(--modal-icon-bg) !important;
    border-radius: 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.modal-icon svg {
    width: 16px !important;
    height: 16px !important;
}

.modal-title {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: var(--text-color) !important;
    margin: 0 0 4px !important;
}
h3#add-new-date{
    padding:0;

}
.modal-description {
    font-size: 14px !important;
    color: var(--card-title-color) !important;
    margin: 0 !important;
}

/* Hide Streamlit heading action elements */
.st-emotion-cache-gi0tri {
    display: none !important;
}

/* ===== MODAL CONTENT MAPPING ===== */
/* Maps to original .modal-content */
.stVerticalBlock.st-key-modal-content {
    padding: 24px !important;
    background: transparent !important;
}

.stVerticalBlock.st-key-modal-content .st-emotion-cache-18kf3ut {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    gap: 24px !important;
}

/* ===== FORM SECTIONS MAPPING ===== */
/* Maps to original .form-section */
.stVerticalBlock.st-key-form-section {
    margin-bottom: 24px !important;
    background: transparent !important;
    padding: 0 !important;
}

.stVerticalBlock.st-key-form-section:last-child {
    margin-bottom: 0 !important;
}

.stVerticalBlock.st-key-form-section .st-emotion-cache-18kf3ut {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    gap: 12px !important;
}

/* ===== DATE INPUT CONTAINER MAPPING ===== */
/* Maps to original .date-input-container */
.stVerticalBlock.st-key-date-input-container {
    position: relative !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}

.stVerticalBlock.st-key-date-input-container .st-emotion-cache-18kf3ut {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    position: relative !important;
}

/* Date input icon styling */
.date-input-icon {
    position: absolute !important;
    left: 12px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    color: var(--filter-icon-color) !important;
    pointer-events: none !important;
    z-index: 10 !important;
    width: 16px !important;
    height: 16px !important;
}

/* ===== DATE INPUT FIELD MAPPING ===== */
/* Maps to original .date-input */
.stElementContainer.st-key-date-input {
    margin: 0 !important;
    padding: 0 !important;
}

.stElementContainer.st-key-date-input .stDateInput {
    margin: 0 !important;
}

.stElementContainer.st-key-date-input label {
    display: none !important;
}

/* Streamlit date input wrapper */
.stElementContainer.st-key-date-input .st-ae {
    width: 100% !important;
    position: relative !important;
}

.stElementContainer.st-key-date-input .st-af {
    width: 100% !important;
    border-radius: 8px !important;
    border: 1px solid var(--task-input-border) !important;
    background: var(--task-input-bg) !important;
}

/* Date input field styling */
.stElementContainer.st-key-date-input input {
    width: 100% !important;
    padding: 12px 16px 12px 44px !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    background: transparent !important;
    color: var(--text-color) !important;
}

.stElementContainer.st-key-date-input input:focus {
    outline: none !important;
    box-shadow: var(--task-input-focus-shadow) !important;
}

.stElementContainer.st-key-date-input input::placeholder {
    color: var(--card-title-color) !important;
    opacity: 0.7 !important;
}

/* ===== DATE PREVIEW MAPPING ===== */
/* Maps to original .date-preview */
.date-preview {
    background: var(--modal-icon-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 16px !important;
    margin-top: 16px !important;
}

.date-preview-content {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-size: 14px !important;
}

.date-preview-label {
    font-weight: 500 !important;
    color: var(--text-color) !important;
}

.date-preview-value {
    color: var(--text-color) !important;
}

.date-preview svg {
    width: 16px !important;
    height: 16px !important;
}

/* ===== MODAL ACTIONS MAPPING ===== */
/* Maps to original .modal-actions */
.stVerticalBlock.st-key-modal-actions {
    display: flex !important;
    justify-content: flex-end !important;
    flex-direction:row;
    gap: 12px !important;
    padding-top: 16px !important;
    border-top: 1px solid var(--border-color) !important;
    background: transparent !important;
    margin: 0 !important;
}

.stVerticalBlock.st-key-modal-actions .st-emotion-cache-18kf3ut {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-end !important;
    align-items: center !important;
    gap: 12px !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}

/* ===== MODAL BUTTONS MAPPING ===== */
/* Maps to original .btn-cancel */
.stElementContainer.st-key-btn-cancel {
    margin: 0 !important;
    padding: 0 !important;
}

.stElementContainer.st-key-btn-cancel button {
    padding: 8px 16px !important;
    border: 1px solid var(--task-input-border) !important;
    border-radius: 8px !important;
    background: var(--task-input-bg) !important;
    color: var(--text-color) !important;
    cursor: pointer !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
    min-height: auto !important;
    height: auto !important;
}

.stElementContainer.st-key-btn-cancel button:hover {
    background: var(--task-item-hover-bg) !important;
}

/* Maps to original .btn-submit */
.stElementContainer.st-key-btn-submit {
    margin: 0 !important;
    padding: 0 !important;
}

.stElementContainer.st-key-btn-submit button {
    padding: 10px 16px !important;
    background: var(--primary-color) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    font-size: 14px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    transition: all 0.2s ease !important;
    min-height: auto !important;
    height: auto !important;
}

.stElementContainer.st-key-btn-submit button:hover {
    background: var(--add-task-btn-hover-bg) !important;
}

.stElementContainer.st-key-btn-submit button:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}

/* ===== ICON STYLING FOR MODAL BUTTONS ===== */
.stElementContainer.st-key-btn-submit [data-testid="stIconMaterial"] {
    font-size: 16px !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
}

.stElementContainer.st-key-btn-submit .st-emotion-cache-cli92z {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
}

.stElementContainer.st-key-btn-submit .st-emotion-cache-17c7e5f {
    margin: 0 !important;
    padding: 0 !important;
}

.stElementContainer.st-key-btn-submit .st-emotion-cache-17c7e5f p {
    margin: 0 !important;
    padding: 0 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: inherit !important;
}

/* ===== UTILITY CLASSES ===== */
.svg-icon {
    width: 16px !important;
    height: 16px !important;
}

.svg-icon-sm {
    width: 12px !important;
    height: 12px !important;
}

.card-svg-icon {
    width: 24px !important;
    height: 24px !important;
}

/* ===== RESPONSIVE DESIGN ===== */
@media (max-width: 640px) {
    .stAppViewContainer {
        padding: 0 20px !important;
    }

    .stVerticalBlock.st-key-modal {
        width: 95% !important;
        max-height: 95vh !important;
    }

    .modal-header {
        padding: 20px 20px 0 !important;
    }

    .stVerticalBlock.st-key-modal-content {
        padding: 20px !important;
    }

    .stVerticalBlock.st-key-modal-actions .st-emotion-cache-18kf3ut {
        flex-direction: column !important;
        gap: 8px !important;
    }

    .stElementContainer.st-key-btn-cancel button,
    .stElementContainer.st-key-btn-submit button {
        width: 100% !important;
        justify-content: center !important;
    }
}

/* ===== TYPOGRAPHY OVERRIDES ===== */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-color) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

p {
    color: var(--text-color) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* ===== STREAMLIT COMPONENT OVERRIDES ===== */
.stElementContainer {
    margin: 0 !important;
}

.stButton {
    margin: 0 !important;
}

.stDateInput {
    margin: 0 !important;
}

.stMarkdown {
    margin: 0 !important;
}

/* Fix for nested layout gaps */
.st-emotion-cache-18kf3ut {
    gap: 0 !important;
}

/* ===== ADDITIONAL STREAMLIT OVERRIDES ===== */
/* Fix button containers */
.stElementContainer.st-key-btn-cancel .st-emotion-cache-8atqhb,
.stElementContainer.st-key-btn-submit .st-emotion-cache-8atqhb {
    margin: 0 !important;
    padding: 0 !important;
}

/* Fix icon containers in buttons */
.stElementContainer.st-key-btn-submit .st-emotion-cache-1kfcwut {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Ensure proper button styling inheritance */
.stElementContainer.st-key-btn-cancel .stButton button,
.stElementContainer.st-key-btn-submit .stButton button {
    font-family: inherit !important;
    font-weight: 500 !important;
}

/* Fix date input focus states */
.stElementContainer.st-key-date-input .st-af:focus-within {
    border-color: var(--task-input-focus-border) !important;
    box-shadow: var(--task-input-focus-shadow) !important;
}

/* Ensure modal appears above all Streamlit elements */
.stVerticalBlock.st-key-modal-overlay {
    z-index: 9999 !important;
}
"""




def dashboard_page():
    if(st.session_state["user"].theme == "Light"):
        root_theme = root_variables[0] #light theme
        chart_theme = chart_theme_variable[0]
    else:
        root_theme = root_variables[1] #dark theme
        chart_theme = chart_theme_variable[1]
    root_style = f"""
    {root_theme}
    """

    if(st.session_state["modal_show"] == False):
        model_display = modal_variable[0]
    else:
        model_display = modal_variable[1]
    

    styles = f"""
    <style>
    {root_style}
    {remove_header_footer}
    {page_setup}
    {header_styles}
    {kpi_styles}
    {chart_styles}
    {empty_date_styles}
    {fill_date_styles}
    {model_display}
    {modal_style}
    </style>
    """
    
    st.markdown(styles,unsafe_allow_html=True)

    user_score = KpiServices.analysis_user_stats(st.session_state["user_task"].plan_status)

    with st.container(key = "header"):
        with st.container(key = "header-main"):
            with st.container(key = "logo-section"):
                st.markdown(
                    f"""
                    <div class="logo">
                        <svg class="logo-user-icon" viewBox="0 0 24 24" fill="none" stroke-width="2">
                            <path d="M20,21V19a4,4,0,0,0-4-4H8a4,4,0,0,0-4,4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                    </div>
                    <div class="brand-info">
                        <h1>{st.session_state["user"].name}</h1>
                        <p>{st.session_state["user"].email}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with st.container(key = "header-right"):
                with st.container(key = "stats-container"):
                    st.markdown(
                        f"""
                        <div class="stat-item">
                            <svg class="svg-icon" viewBox="0 0 24 24" fill="none" stroke="#4e598c" stroke-width="2">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="16" y1="2" x2="16" y2="6"></line>
                                <line x1="8" y1="2" x2="8" y2="6"></line>
                                <line x1="3" y1="10" x2="21" y2="10"></line>
                            </svg>
                            <span class="stat-number" id="totalDatesCount">{user_score["total_dates"]}</span>
                            <span class="stat-label">dates</span>
                        </div>
                        <div class="stat-divider"></div>
                        <div class="stat-item">
                            <svg class="svg-icon" viewBox="0 0 24 24" fill="none" stroke="#4c9f70" stroke-width="2">
                                <line x1="18" y1="20" x2="18" y2="10"></line>
                                <line x1="12" y1="20" x2="12" y2="4"></line>
                                <line x1="6" y1="20" x2="6" y2="14"></line>
                            </svg>
                            <span class="stat-number" id="totalTasksCount">{user_score["sum_completed_tasks"]}/{user_score["sum_total_tasks"]}</span>
                            <span class="stat-label">done</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with st.container(key = "header-actions"):
                    toggle_icon = ":material/dark_mode:" if (st.session_state["user"].theme == 'Light') else ":material/light_mode:"
                    st.button(
                        label="",
                        type="tertiary",
                        icon = toggle_icon,
                        key = "theme-toggle",
                        on_click=change_theme
                    )
                    st.button(
                        label="",
                        type="tertiary",
                        icon = ":material/logout:",
                        key = "logout-btn"
                    )

    with st.container(key = "kpi-section"):
        with st.container(key = "kpi-container"):
            st.markdown(#card completion
                f"""
                <div class="card completion">
                    <div class="card-content">
                        <div class="card-info">
                            <p class="card-title">Average Completion</p>
                            <div class="card-value-container">
                                <span class="card-value" id="avgCompletionRate">{user_score["avg_completion_percentage"]}%</span>
                            </div>
                        </div>
                        <div class="card-icon completion-icon">
                            <svg class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"></circle>
                                <circle cx="12" cy="12" r="4"></circle>
                                <line x1="12" y1="2" x2="12" y2="6"></line>
                                <line x1="12" y1="18" x2="12" y2="22"></line>
                                <line x1="2" y1="12" x2="6" y2="12"></line>
                                <line x1="18" y1="12" x2="22" y2="12"></line>
                            </svg>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(#card progress
                f"""
                <div class="card progress">
                    <div class="card-content">
                        <div class="card-info">
                            <p class="card-title">Total Progress</p>
                            <div class="card-value-container">
                                <span class="card-value" id="totalProgress">{user_score["sum_completed_tasks"]}/{user_score["sum_total_tasks"]}</span>
                                <span class="card-badge" id="totalProgressPercentage">{user_score["avg_completion_percentage"]}%</span>
                            </div>
                        </div>
                        <div class="card-icon progress-icon">
                            <svg class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                                <polyline points="17 6 23 6 23 12"></polyline>
                            </svg>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(#card days
                f"""
                <div class="card days">
                    <div class="card-content">
                        <div class="card-info">
                            <p class="card-title">Active Days</p>
                            <div class="card-value-container">
                                <span class="card-value" id="activeDays">{user_score["active_days"]}</span>
                                <span class="card-badge">Tracked</span>
                            </div>
                        </div>
                        <div class="card-icon days-icon">
                            <svg class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke-width="2">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="16" y1="2" x2="16" y2="6"></line>
                                <line x1="8" y1="2" x2="8" y2="6"></line>
                                <line x1="3" y1="10" x2="21" y2="10"></line>
                                <line x1="8" y1="14" x2="16" y2="14"></line>
                                <line x1="8" y1="18" x2="16" y2="18"></line>
                            </svg>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(#card attention
                f"""
                <div class="card attention">
                    <div class="card-content">
                        <div class="card-info">
                            <p class="card-title">Needs Attention</p>
                            <div class="card-value-container">
                                <span class="card-value" id="incompleteCount">{user_score["incomplete_tasks_list"]}</span>
                                <span class="card-badge" id="attentionBadge">All Good</span>
                            </div>
                        </div>
                        <div class="card-icon attention-icon">
                            <svg class="card-svg-icon" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="12" y1="8" x2="12" y2="12"></line>
                                <line x1="12" y1="16" x2="12.01" y2="16"></line>
                            </svg>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with st.container(key = "chart-section"):
        with st.container(key = "chart-card"):
            with st.container(key = "chart-header"):
                with st.container(key = "chart-header-top"):
                    st.markdown(
                        """
                        <h3 class="chart-title">
                            <div class="chart-indicator"></div>
                            Task Completion Analytics
                        </h3>
                        """,
                        unsafe_allow_html=True
                    )

                    with st.container(key = "filter-controls"):
                        with st.container(key = "filter-group"):
                            st.markdown(
                                """
                                <svg class="filter-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
                                </svg>
                                """,
                                unsafe_allow_html=True
                            )
                            filter_option = ["All Time","Current Month","Last Month","Month","Year"]
                            filters = st.selectbox(
                                label="Filter Time",
                                options=filter_option,
                                index = 1,
                                label_visibility="collapsed",
                                key="filter-select",
                                accept_new_options=False
                            )
                            st.button(
                                label="",
                                key = "reset-btn",
                                icon = ":material/close:",
                                type="tertiary"
                            )
            with st.container(key = "chart-content"):
                with st.container(key = "chart-container"):

                    option = GraphServices.graph_analysis(st.session_state["user_task"].plan_status,filters,chart_theme[0],chart_theme[1],chart_theme[2])    
                    st_echarts(
                        options = option,
                        key = "taskChart"
                    )

    with st.container(key = "main-content"):
        with st.container(key = "section-header"):
            st.markdown(
                """<h2 class="section-title">Daily Task Management</h2>""",
                unsafe_allow_html=True
            )
            st.button(
                label="Add Date",
                type="secondary",
                key = "add-date-btn-1",
                icon = ":material/add:",
                on_click=modal_toggle
            )

        with st.container(key = "tasksContainer"):
            user_task = st.session_state["user_task"].show_user_task
            if(user_task is None):
                with st.container(key = "empty-state"):
                    st.markdown(
                        """
                        <div class="empty-state-icon">
                            <svg class="svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 48px; height: 48px;">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="16" y1="2" x2="16" y2="6"></line>
                                <line x1="8" y1="2" x2="8" y2="6"></line>
                                <line x1="3" y1="10" x2="21" y2="10"></line>
                            </svg>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        """
                        <h3>No dates added yet</h3>
                        <p>Start by adding your first date to begin tracking your daily tasks and progress.</p>
                        """,
                        unsafe_allow_html=True
                    )

                    st.button(
                        label="Add Your First Date",
                        type="secondary",
                        key = "add-date-btn-2",
                        icon = ":material/add:",
                        on_click=modal_toggle
                    )
            else:
                with st.container(key = "tasks-grid"):
                    task_count = 0
                    user_all_dates = list(user_task.keys())
                    for date_count in range(len(user_all_dates)):#itter over the list of task dict keys {date:{tasks:status},} (give dates)
                        with st.container(key = f"date-card-{date_count+1}"):
                            with st.container(key = f"task-card-header-{date_count+1}"):
                                st.markdown(
                                    f"""
                                    <div class="date-info">
                                        <div class="date-title">
                                            <svg class="svg-icon" viewBox="0 0 24 24" fill="none" stroke="#4e598c" stroke-width="2">
                                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                                <line x1="16" y1="2" x2="16" y2="6"></line>
                                                <line x1="8" y1="2" x2="8" y2="6"></line>
                                                <line x1="3" y1="10" x2="21" y2="10"></line>
                                            </svg>
                                            <h3>{TaskSerives.get_date_detail(user_all_dates[date_count])}</h3>
                                        </div>
                                        <span class="date-badge {TaskSerives.get_badge_status(user_task[user_all_dates[date_count]])}">
                                            {TaskSerives.get_task_status(user_task[user_all_dates[date_count]])}
                                        </span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                st.button(
                                    label = "",
                                    icon=":material/delete:",
                                    type = "tertiary",
                                    key = f"remove-date-btn-{date_count+1}"
                                )

                            if(TaskSerives.get_task_exist(user_task[user_all_dates[date_count]])):
                                st.markdown(
                                    f"""
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: {TaskSerives.get_progress_percent(user_task[user_all_dates[date_count]])}%;"></div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            with st.container(key = f"add-task-form-{date_count+1}"):
                                new_task = st.text_input(
                                    label="New Text Input",
                                    label_visibility="collapsed",
                                    placeholder="Add task...",
                                    key = f"task-input-{date_count+1}"
                                )

                                st.button(
                                    label = "",
                                    icon=":material/add:",
                                    type = "tertiary",
                                    key = f"add-task-btn-{date_count+1}"
                                )
                            
                            with st.container(key = f"task-list-{date_count+1}"):
                                if(not(TaskSerives.get_task_exist(user_task[user_all_dates[date_count]]))):
                                    st.markdown(
                                        """
                                        <div class="no-tasks">
                                            <svg class="no-tasks-icon svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                                stroke-width="2" style="width: 24px; height: 24px;">
                                                <circle cx="12" cy="12" r="10"></circle>
                                                <circle cx="12" cy="12" r="4"></circle>
                                                <line x1="12" y1="2" x2="12" y2="6"></line>
                                                <line x1="12" y1="18" x2="12" y2="22"></line>
                                                <line x1="2" y1="12" x2="6" y2="12"></line>
                                                <line x1="18" y1="12" x2="22" y2="12"></line>
                                            </svg>
                                            <p>No tasks yet</p>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                else:
                                    current_date_task = user_task[user_all_dates[date_count]]
                                    for current_task,current_task_status in current_date_task.items():
                                        if(current_task_status == "Incomplete"):
                                            with st.container(key = f"task-item-{task_count+1}"):
                                                check = st.checkbox(
                                                    label=current_task,
                                                    key = f"task-checkbox-{task_count+1}"
                                                )
                                                st.button(
                                                    label = "",
                                                    icon=":material/delete:",
                                                    type = "tertiary",
                                                    key = f"remove-task-btn-{task_count+1}"
                                                )
                                        elif(current_task_status == "Completed"):
                                            with st.container(key = f"task-completed-item-{task_count+1}"):
                                                check = st.checkbox(
                                                    label=current_task,
                                                    key = f"task-checkbox-{task_count+1}",
                                                    value=True
                                                )
                                                st.button(
                                                    label = "",
                                                    icon=":material/delete:",
                                                    type = "tertiary",
                                                    key = f"remove-task-btn-{task_count+1}"
                                                )
                                        task_count += 1                

    with st.container(key = "modal-overlay"):
        with st.container(key = "modal"):
            st.markdown(
                """
                <div class="modal-header">
                    <div class="modal-header-content">
                        <div class="modal-icon">
                            <svg class="svg-icon" viewBox="0 0 24 24" fill="none" stroke="#4e598c" stroke-width="2">
                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="16" y1="2" x2="16" y2="6"></line>
                                <line x1="8" y1="2" x2="8" y2="6"></line>
                                <line x1="3" y1="10" x2="21" y2="10"></line>
                            </svg>
                        </div>
                        <div class = "modal-section">
                            <h3 class="modal-title">Add New Date</h3>
                            <p class="modal-description">Select a date to start tracking your tasks</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            with st.container(key = "modal-content"):
                with st.container(key = "addDateForm"):
                    with st.container(key = "date-input-container"):
                        with st.container(key = "form-section"):
                            manual_date = st.date_input(
                                key = "date-input",
                                label="manual-date",
                                label_visibility="collapsed"
                            )

                    st.markdown(
                        f"""
                        <div class="date-preview" id="datePreview" style="display: block;">
                            <div class="date-preview-content">
                                <svg class="svg-icon" viewBox="0 0 24 24" fill="none" stroke="#4e598c" stroke-width="2">
                                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                    <line x1="16" y1="2" x2="16" y2="6"></line>
                                    <line x1="8" y1="2" x2="8" y2="6"></line>
                                    <line x1="3" y1="10" x2="21" y2="10"></line>
                                </svg>
                                <span class="date-preview-label">Selected date:</span>
                                <span class="date-preview-value" id="selectedDatePreview">{TaskSerives.get_date_detail(str(manual_date))}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    with st.container(key = "modal-actions"):
                        st.button(
                            label="Cancel",
                            key = "btn-cancel",
                            type="secondary",
                            on_click=modal_toggle
                        )

                        st.button(
                            label="Add Date",
                            key = "btn-submit",
                            icon=":material/add:",
                            type="secondary"
                        )

