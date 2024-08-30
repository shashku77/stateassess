
"""Supports authentication page."""

import logging
import streamlit as st
import streamlit_authenticator as stauth
from modules.conf import (get_config_data, save_config_data,
                          CONFIG_FN
                          )


config = get_config_data()

def get_auth():    
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

def get_role(username: str):
    try:
        role = (config['credentials']['usernames'][username]['role'])
        return role
    except Exception as e:
        role = 'user'
        return role
    
def get_login(authenticator):
    
    authenticator.login()

    #hashed_passwords = stauth.Hasher(['sk#qs@123', 'ak#qs@123','dl#qs@123','xq#qs@123','bc#qs@123']).generate()
    
    if st.session_state["authentication_status"]:
        st.write(f'Logged username: **{st.session_state.username}**')

    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

    else:
        st.error('Username/password is incorrect')


def get_reg(authenticator):
    try:
        if authenticator.register_user(pre_authorization=False):
            save_config_data(config)
            st.success('Registration is successful!')
    except Exception as e:
        st.error(e)


def get_logout(authenticator):
    st.markdown(f'''Welcome **{st.session_state["name"]}**''')
    authenticator.logout('Logout', 'main', key='unique_key')


def get_forgot_password(authenticator):
    if not st.session_state["authentication_status"]:
        try:
            (username_of_forgotten_password,
            email_of_forgotten_password,
            new_random_password) = authenticator.forgot_password()
            if username_of_forgotten_password:
                # Here you can access the forgotten password. It can also get the email and random password.
                # This random password can be sent to the user via email using email services.
                # This needs to be implemented. One email service that you can use is courier.
                st.success('Successfully get the user info.')
                # st.write(f'Your new password is {new_random_password}. Keep it and update it.')
            else:
                st.error('Sorry username is not found.')
        except Exception as e:
            st.error(e)
        
