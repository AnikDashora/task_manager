import streamlit as st

PAGES = ("looto/auth/signup_page",#1
         "looto/auth/login_page"#2
         "looto/screens/dashboard_page",#3
        )

class NavigationState:
    def __init__(self):
        self.page =  1

    def to_signup_page(self):
        self.page = 1
        
    def to_login_page(self):
        self.page = 2
    
    def to_dashboard_page(self):
        self.page = 3