import streamlit as st
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from session_state.session_manager import NavigationState
from models.user_model import User
from models.task_model import UserTasks
from frontend.signup import signup_page
from frontend.login import signin_page
from frontend.dashboard import dashboard_page

if("navigation" not in st.session_state):
    st.session_state["navigation"] = NavigationState()
if("user" not in st.session_state):
    st.session_state["user"] = User()
if "user_task" not in st.session_state or not isinstance(st.session_state["user_task"], UserTasks):
    st.session_state["user_task"] = UserTasks()
if("modal_show" not in st.session_state):
    st.session_state["modal_show"] = False

if(st.session_state["navigation"].page == 1):
    signup_page()
elif(st.session_state["navigation"].page == 2):
    signin_page()
elif(st.session_state["navigation"].page == 3):
    dashboard_page()
