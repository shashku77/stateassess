"""Manages user authentication."""


import streamlit as st
from modules.auth import (get_auth, get_login, get_reg,
                          get_logout, get_forgot_password)

st.image("./images/QSlogo.png", width = 300)
st.title('Authentication')

authenticator = get_auth()

tab1, tab2, tab3, tab4 = st.tabs(['Login', 'Register', 'Logout', 'ForgotPassword'])

with tab1:
    get_login(authenticator)
    

with tab2:
    if not st.session_state["authentication_status"]:
        get_reg(authenticator)

with tab3:
    if st.session_state["authentication_status"]:
        get_logout(authenticator)

with tab4:
    get_forgot_password(authenticator)