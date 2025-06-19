import streamlit as st
import requests
import time
from utils.encryption_utils import decrypt_otp
from utils.socket_utils import receive_key
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

SERVER_URL = "http://localhost:5000"

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'encrypted_otp' not in st.session_state:
    st.session_state.encrypted_otp = None
if 'login_email' not in st.session_state:
    st.session_state.login_email = None
if 'register_email' not in st.session_state:
    st.session_state.register_email = None
if 'session_cookie' not in st.session_state:
    st.session_state.session_cookie = None

# Create a session with retry logic
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=["GET", "POST"])
session.mount('http://', HTTPAdapter(max_retries=retries))

# Fetch AES key (try socket first, then HTTP fallback)
KEY = None
def fetch_key():
    logging.debug("Attempting to fetch AES key via socket")
    try:
        return receive_key()
    except Exception as e:
        logging.warning(f"Socket key retrieval failed: {e}")
        logging.debug("Falling back to HTTP key retrieval")
        try:
            res = session.get(f"{SERVER_URL}/key")
            if res.status_code == 200:
                key_hex = res.json()['key']
                logging.info(f"Received key via HTTP: {key_hex}")
                return bytes.fromhex(key_hex)
            else:
                raise Exception(f"HTTP key retrieval failed: {res.status_code}")
        except Exception as e:
            logging.error(f"HTTP key retrieval failed: {e}")
            raise Exception("Failed to fetch AES key")

try:
    KEY = fetch_key()
except Exception as e:
    st.error(f"Failed to receive AES key: {e}")
    logging.error(f"Key retrieval failed: {e}")
    st.stop()

def check_server_health():
    try:
        res = session.get(f"{SERVER_URL}/health")
        return res.status_code == 200
    except Exception as e:
        logging.error(f"Server health check failed: {e}")
        return False

def check_auth():
    try:
        cookies = {'session': st.session_state.session_cookie} if st.session_state.session_cookie else {}
        res = session.get(f"{SERVER_URL}/check_auth", cookies=cookies)
        if res.status_code == 200:
            data = res.json()
            return data.get('authenticated', False), data.get('email', '')
    except Exception as e:
        logging.error(f"Check auth failed: {e}")
        return False, ''

def logout():
    try:
        cookies = {'session': st.session_state.session_cookie} if st.session_state.session_cookie else {}
        res = session.post(f"{SERVER_URL}/logout", cookies=cookies)
        st.session_state.authenticated = False
        st.session_state.session_cookie = None
        st.success("Logged out successfully")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {e}")
        logging.error(f"Logout failed: {e}")

def login_tab():
    st.subheader("User Login")
    email = st.text_input("Email", key="login_email_input")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login", key="login_button"):
        if not check_server_health():
            st.error("Server is not responding. Please try again later.")
            logging.error("Login aborted: Server health check failed")
            return
        
        try:
            res = session.post(
                f"{SERVER_URL}/login",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if res.status_code == 200:
                data = res.json()
                if data['status'] == "success":
                    st.session_state.session_cookie = data.get('session_id')
                    st.session_state.encrypted_otp = data['otp']
                    st.session_state.login_email = email
                    st.success("OTP sent to your email")
                    logging.info(f"Login OTP sent for {email}")
                    st.rerun()
                else:
                    st.error(data['message'])
                    logging.warning(f"Login failed: {data['message']}")
            else:
                st.error(f"Login error: {res.status_code}")
                logging.error(f"Login error: {res.status_code}")
        except Exception as e:
            st.error(f"Login failed: {e}")
            logging.error(f"Login failed: {e}")
    
    if st.session_state.encrypted_otp and st.session_state.login_email:
        try:
            decrypted_otp = decrypt_otp(st.session_state.encrypted_otp, KEY)
            st.info(f"encrypted OTP: {st.session_state.encrypted_otp}")
            st.info(f"Decrypted OTP (for testing): {decrypted_otp}")
            logging.debug(f"Decrypted OTP: {decrypted_otp}")
        except Exception as e:
            st.error(f"OTP decryption failed: {e}")
            logging.error(f"OTP decryption failed: {e}")
        
        otp = st.text_input("Enter OTP", key="login_otp_input")
        if st.button("Verify OTP", key="verify_login_otp"):
            try:
                cookies = {'session': st.session_state.session_cookie} if st.session_state.session_cookie else {}
                res = session.post(
                    f"{SERVER_URL}/verify_login",
                    json={"otp": otp},
                    cookies=cookies
                )
                
                if res.status_code == 200:
                    data = res.json()
                    if data['status'] == "success":
                        st.session_state.authenticated = True
                        st.success("Login successful! Redirecting...")
                        logging.info(f"Login verified for {st.session_state.login_email}")
                        time.sleep(1)
                        st.switch_page("pages/home.py")
                    else:
                        st.error(data['message'])
                        logging.warning(f"OTP verification failed: {data['message']}")
                else:
                    st.error(f"Verification failed: {res.status_code}")
                    logging.error(f"Verification failed: {res.status_code}")
            except Exception as e:
                st.error(f"Verification error: {e}")
                logging.error(f"Verification error: {e}")

def register_tab():
    st.subheader("New User Registration")
    email = st.text_input("Email", key="reg_email_input")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
    
    if st.button("Register", key="reg_button"):
        if password != confirm:
            st.error("Passwords don't match")
            logging.warning("Registration failed: Passwords don't match")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters")
            logging.warning("Registration failed: Password too short")
        else:
            if not check_server_health():
                st.error("Server is not responding. Please try again later.")
                logging.error("Registration aborted: Server health check failed")
                return
            
            try:
                res = session.post(
                    f"{SERVER_URL}/register",
                    json={"email": email, "password": password},
                    headers={"Content-Type": "application/json"}
                )
                
                if res.status_code == 200:
                    data = res.json()
                    if data['status'] == "success":
                        st.session_state.session_cookie = data.get('session_id')
                        st.session_state.encrypted_otp = data['otp']
                        st.session_state.register_email = email
                        st.success("Registration complete! Check email for OTP")
                        logging.info(f"Registration OTP sent for {email}")
                        st.rerun()
                    else:
                        st.error(data['message'])
                        logging.warning(f"Registration failed: {data['message']}")
                else:
                    st.error(f"Registration error: {res.status_code}")
                    logging.error(f"Registration error: {res.status_code}")
            except Exception as e:
                st.error(f"Registration failed: {e}")
                logging.error(f"Registration failed: {e}")
    
    if st.session_state.encrypted_otp and st.session_state.register_email:
        try:
            decrypted_otp = decrypt_otp(st.session_state.encrypted_otp, KEY)
            st.info(f"Decrypted OTP (for testing): {decrypted_otp}")
            logging.debug(f"Decrypted OTP: {decrypted_otp}")
        except Exception as e:
            st.error(f"OTP decryption failed: {e}")
            logging.error(f"OTP decryption failed: {e}")
        
        otp = st.text_input("Enter OTP", key="reg_otp_input")
        if st.button("Verify Registration", key="verify_reg_otp"):
            try:
                cookies = {'session': st.session_state.session_cookie} if st.session_state.session_cookie else {}
                res = session.post(
                    f"{SERVER_URL}/verify_registration",
                    json={"otp": otp},
                    cookies=cookies
                )
                
                if res.status_code == 200:
                    data = res.json()
                    if data['status'] == "success":
                        st.success("Account verified! Please login")
                        logging.info(f"Registration verified for {st.session_state.register_email}")
                        st.session_state.encrypted_otp = None
                        st.session_state.register_email = None
                        st.rerun()
                    else:
                        st.error(data['message'])
                        logging.warning(f"Registration OTP verification failed: {data['message']}")
                else:
                    st.error(f"Verification failed: {res.status_code}")
                    logging.error(f"Verification failed: {res.status_code}")
            except Exception as e:
                st.error(f"Verification failed: {e}")
                logging.error(f"Verification failed: {e}")

if __name__ == "__main__":
    st.title("Authentication Portal")
    
    if st.session_state.authenticated:
        st.switch_page("pages/home.py")
    else:
        tab = st.sidebar.radio("Menu", ["Login", "Register"], key="auth_tab")
        
        if tab == "Login":
            login_tab()
        elif tab == "Register":
            register_tab()