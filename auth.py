import sqlite3
import hashlib
import streamlit as st
from typing import Optional, Tuple

def init_db():
    conn = sqlite3.connect('uz_chat.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str) -> bool:
    conn = init_db()
    c = conn.cursor()
    try:
        hashed_password = hash_password(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                 (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    conn = init_db()
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result is not None and result[0] == hashed_password

def login_user() -> Optional[str]:
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    
    if st.session_state.username is None:
        # Center the authentication container

        
        with st.container():
            # Show either login or signup form based on state
            if not st.session_state.show_signup:
                with st.form("login_form"):
                    st.markdown("### Login")
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    submit = st.form_submit_button("Login", use_container_width=True)
                    
                    if submit:
                        if verify_user(username, password):
                            st.session_state.username = username
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                
                # Show signup toggle button
                st.markdown("---")
                if st.button("Don't have an account? Sign up", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()
            else:
                with st.form("signup_form"):
                    st.markdown("### Sign Up")
                    new_username = st.text_input("Choose Username", placeholder="Choose a username")
                    new_password = st.text_input("Choose Password", type="password", placeholder="Choose a password")
                    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                    submit = st.form_submit_button("Sign Up", use_container_width=True)
                    
                    if submit:
                        if new_password != confirm_password:
                            st.error("Passwords do not match")
                        elif register_user(new_username, new_password):
                            st.success("Registration successful! Please login.")
                            st.session_state.show_signup = False
                            st.rerun()
                        else:
                            st.error("Username already exists")
                
                # Show login toggle button
                st.markdown("---")
                if st.button("Already have an account? Login", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    return st.session_state.username 