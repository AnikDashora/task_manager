import streamlit as st
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from backend.auth import VerifyUser,ValidateUser,UserServies
from models.user_model import User
from models.task_model import UserTasks
from backend.database import SqlConnection
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
        :root{
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

signup_style = """

.st-key-main {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            min-height: 100vh;
            max-width:100%;
        }
.stVerticalBlock.st-key-signup-container {
            background: var(--card-bg) !important;
            border-radius: 16px !important;
            padding: 1.75rem !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
            width: 100% !important;
            max-width: 380px !important;
            margin: 0 auto !important;
        }

        /* Remove default Streamlit spacing */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        .st-emotion-cache-tn0cau,
        .st-emotion-cache-1n6tfoc {
            gap: 0 !important;
        }

        .st-emotion-cache-r44huj {
            margin-bottom: 0 !important;
        }

        /* ===== WELCOME SECTION MAPPING ===== */
        
        /* Original: .welcome-section */
        .welcome-section {
            text-align: center !important;
            margin-bottom: 1.5rem !important;
        }

        /* Original: .welcome-title */
        .welcome-title {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: var(--text-color) !important;
            margin-bottom: 0.5rem !important;
            padding: 0 !important;
        }

        /* Hide Streamlit's heading anchor */
        .welcome-title span[data-testid="stHeaderActionElements"] {
            display: none !important;
        }

        /* Original: .welcome-subtitle */
        .welcome-subtitle {
            color: var(--card-title-color) !important;
            font-size: 0.9rem !important;
            margin: 0 !important;
        }

        /* ===== FORM SECTION MAPPING ===== */

        /* Original: form container */
        .stVerticalBlock.st-key-signupForm {
            display: flex !important;
            flex-direction: column !important;
            gap: 0 !important;
        }

        /* Original: .form-group */
        .stVerticalBlock.st-key-form-group-1,
        .stVerticalBlock.st-key-form-group-2,
        .stVerticalBlock.st-key-form-group-3 {
            margin-bottom: 1rem !important;
        }

        /* Original: .form-label */
        .stTextInput label[data-testid="stWidgetLabel"] {
            display: block !important;
            margin-bottom: 0.5rem !important;
            font-weight: 500 !important;
            color: var(--text-color) !important;
        }

        .stTextInput label[data-testid="stWidgetLabel"] p {
            margin: 0 !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            color: var(--text-color) !important;
        }

        /* Original: .input-wrapper -> .form-input */
        .stTextInput div[data-baseweb="input"] {
            position: relative !important;
            width: 100% !important;
        }

        .stTextInput div[data-baseweb="base-input"] {
            border-radius: 10px !important;
            border: 1px solid var(--task-input-border) !important;
            background: var(--task-input-bg) !important;
            transition: all 0.2s ease !important;
            overflow: hidden !important;
        }

        .stTextInput input {
            width: 100% !important;
            padding: 0.75rem 1rem !important;
            border: none !important;
            border-radius: 10px !important;
            font-size: 1rem !important;
            background: transparent !important;
            color: var(--text-color) !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        }

        .stTextInput input:focus {
            outline: none !important;
            box-shadow: var(--task-input-focus-shadow) !important;
        }

        .stTextInput div[data-baseweb="base-input"]:focus-within {
            border-color: var(--task-input-focus-border) !important;
            box-shadow: var(--task-input-focus-shadow) !important;
        }

        .stTextInput input::placeholder {
            color: var(--card-title-color) !important;
        }

        /* Password input adjustments */
        .stTextInput input[type="password"] {
            padding-right: 3rem !important;
        }

        /* Password toggle button */
        .stTextInput button[aria-label*="password"] {
            position: absolute !important;
            right: 1rem !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            background: none !important;
            border: none !important;
            color: var(--card-title-color) !important;
            cursor: pointer !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 20px !important;
            height: 20px !important;
        }

        .stTextInput button[aria-label*="password"] svg {
            width: 20px !important;
            height: 20px !important;
        }

        /* ===== BUTTON MAPPING ===== */

        /* Original: .create-account-btn */
        .stElementContainer.st-key-create-account-btn .stButton button {
            width: 100% !important;
            padding: 0.75rem !important;
            background: var(--secondary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: background 0.3s cubic-bezier(0.4,0,0.2,1), 
                        opacity 0.3s cubic-bezier(0.4,0,0.2,1), 
                        box-shadow 0.3s cubic-bezier(0.4,0,0.2,1) !important;
            margin-bottom: 1rem !important;
            opacity: 0.75 !important;
            box-shadow: 0 2px 8px rgba(78, 89, 140, 0.08) !important;
            min-height: auto !important;
        }

        .stElementContainer.st-key-create-account-btn .stButton button:hover {
            background: linear-gradient(135deg, #4e598c, #6b7fd1) !important;
            opacity: 1 !important;
            box-shadow: 0 4px 16px rgba(78, 89, 140, 0.15) !important;
        }

        .stElementContainer.st-key-create-account-btn .stButton button:active {
            transform: translateY(1px) !important;
        }

        .stElementContainer.st-key-create-account-btn .stButton button div p {
            margin: 0 !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
        }

        /* ===== FOOTER SECTION MAPPING ===== */

        /* Original: .signup-footer */
        .stVerticalBlock.st-key-signup-footer {
            text-align: center !important;
            margin-top: 0 !important;
        }

        /* Original: .signin-link */
        .stVerticalBlock.st-key-signup-footer .stMarkdown p {
            color: var(--card-title-color) !important;
            margin: 0 !important;
            display: inline !important;
            font-size:0.95rem;
        }

        /* Sign in button styling */
        .stElementContainer.st-key-Sign-in-btn .stButton button {
            background: transparent !important;
            border: none !important;
            color: var(--primary-color) !important;
            text-decoration: none !important;
            font-weight: 500 !important;
            cursor: pointer !important;
            padding: 0.25rem 0.5rem !important;
            border-radius: 4px !important;
            transition: all 0.2s ease !important;
            margin-left: 0.25rem !important;
            min-height: auto !important;
        }

        .stElementContainer.st-key-Sign-in-btn .stButton button:hover {
            background: var(--filter-badge-bg) !important;
            text-decoration: underline !important;
        }

        .stElementContainer.st-key-Sign-in-btn .stButton button div p {
            margin: 0 !important;
            color: var(--primary-color) !important;
            font-weight: 500 !important;
        }

        /* ===== RESPONSIVE DESIGN ===== */
        @media (max-width: 768px) {
            .stApp {
                padding: 1rem !important;
            }

            .stVerticalBlock.st-key-signup-container {
                padding: 1.5rem !important;
            }
        }

        /* ===== ADDITIONAL STREAMLIT CLEANUP ===== */
        
        /* Remove unnecessary margins and paddings */
        .st-emotion-cache-1vo6xi6,
        .st-emotion-cache-zh2fnc {
            margin: 0 !important;
        }

        /* Ensure proper stacking */
        .stElementContainer {
            position: relative !important;
        }

        /* Clean up button containers */
        .stButton {
            width: 100% !important;
        }

        .stElementContainer.st-key-create-account-btn {
            width: 100% !important;
            margin-bottom: 1rem !important;
        }

        .stElementContainer.st-key-Sign-in-btn {
            width: fit-content !important;
            display: inline-block !important;
        }

        /* Layout adjustments for footer */
        .stVerticalBlock.st-key-signup-footer {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            justify-content: center !important;
            flex-wrap: wrap !important;
            gap: 0 !important;
        }

        .stVerticalBlock.st-key-signup-footer .stElementContainer {
            margin: 0 !important;
            width:50%;
            display:flex;
            align-items:center;
            justify-content:center;
        }
"""

styles = f"""
<style>
{remove_header_footer}
{page_setup}
{signup_style}
</style>
"""
def signup_page():
    st.markdown(styles,unsafe_allow_html=True)
    with st.container(key = "main"):
        with st.container(key = "signup-container"):
            st.markdown(
                """
                <div class="welcome-section">
                    <h1 class="welcome-title">Welcome to TaskFlow</h1>
                    <p class="welcome-subtitle">Track your tasks, achieve your goals</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.container(key = "signupForm"):
                with st.container(key = "form-group-1"):
                    name = st.text_input(
                        label="Name",
                        placeholder="Enter your full name",
                        key = "form-input-1"
                    )
                    name_flag = ValidateUser.validate_name(name)
                
                with st.container(key = "form-group-2"):
                    email = st.text_input(
                        label="Email",
                        placeholder="Enter your full name",
                        key = "form-input-2"
                    )
                    email_flag = ValidateUser.validate_email(email)

                with st.container(key = "form-group-3"):
                    password = st.text_input(
                        label="Password",
                        placeholder="Enter your full name",
                        key = "form-input-3",
                        type="password"
                    )
                    password_flag = ValidateUser.validate_password(password)

                signup_btn = st.button(
                    label="Create Account",
                    type="secondary",
                    key = "create-account-btn"
                )
                if(signup_btn):
                    if((name_flag and email_flag and password_flag) and (name and email and password)):
                        if(not(VerifyUser.if_user_exists(email))):
                            st.session_state["user"].set_user_data(#saving user state
                                user_id=UserServies.generate_user_id(),
                                name=name,
                                email=email,
                                password=UserServies.encrypt_password(email,password)
                            )
                            UserServies.user_serialization(st.session_state["user"])
                            st.session_state["user"].set_user_exist()
                            st.session_state["user_task"].set_show_user_tasks(st.session_state["user"].user_id)
                            st.session_state["navigation"].to_dashboard_page()
                            st.rerun()
                        else:
                            st.error("User Already Exist")
                    else:
                        st.error("Invalid Entries")

                with st.container(key = "signup-footer"):
                    st.markdown(
                        """
                        <p class="signin-link">
                        Already have an account? 
                        </p>
                        """,
                        unsafe_allow_html=True
                    )
                    st.button(
                        label="Sign in here",
                        type="tertiary",
                        key = "Sign-in-btn",
                        on_click=st.session_state["navigation"].to_login_page
                    )


                    