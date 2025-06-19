import streamlit as st
from utils.hash_utils import hash_password, verify_password_similarity
from utils.email_utils import send_otp
from utils.encryption_utils import encrypt_otp, decrypt_otp
from utils.socket_utils import run_key_server, receive_key, stop_server
import os
import time
import threading

USER_FILE = "user_data.txt"

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'key_server_running' not in st.session_state:
    st.session_state.key_server_running = False

st.set_page_config(page_title="2FA Auth", layout="centered")
st.title("🔐 2FA Authentication System")

def go_to_login():
    st.session_state.page = "login"
    stop_server()  # Clean up any running server

def go_to_register():
    st.session_state.page = "register"
    stop_server()  # Clean up any running server

# ----- Page: Register -----
if st.session_state.page == "register":
    st.subheader("📋 Register New Account")

    full_name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Re-type Password", type="password")

    # Password Rules
    def valid_password(pwd):
        return (len(pwd) >= 8 and
                any(c.isalpha() for c in pwd) and
                any(c.isdigit() for c in pwd) and
                any(c in "@_!#$%^&*()-+=?" for c in pwd))

    if st.button("Register"):
        if not all([full_name, email, password, confirm_password]):
            st.error("Please fill in all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif not valid_password(password):
            st.warning("Password must be ≥8 chars, include a number, a letter, and a special character.")
        else:
            # Check if user exists
            if os.path.exists(USER_FILE):
                with open(USER_FILE, "r") as f:
                    if any(line.startswith(email) for line in f):
                        st.error("User already exists.")
                        st.stop()

            # Generate random key (bytes)
            key = os.urandom(16)
            st.session_state.key = key
            
            # Start key server in background thread
            stop_server()  # Ensure any previous server is stopped
            threading.Thread(
                target=run_key_server,
                args=(key,),
                daemon=True
            ).start()
            st.session_state.key_server_running = True
            
            # Small delay to ensure server is ready
            time.sleep(0.5)
            
            # Send OTP and encrypt
            otp = send_otp(email)
            if otp is None:
                st.error("Failed to send OTP. Please try again.")
                stop_server()
                st.stop()
                
            encrypted_otp = encrypt_otp(otp, key)
            st.session_state.encrypted_otp = encrypted_otp
            st.session_state.new_user = f"{email}|{hash_password(password)}|{full_name}\n"
            st.session_state.page = "verify_register"
            st.rerun()

# ----- Page: OTP Verification (Registration) -----
elif st.session_state.page == "verify_register":
    st.subheader("📨 Verify OTP to Complete Registration")

    otp_input = st.text_input("Enter OTP")

    if st.button("Verify OTP"):
        try:
            key = receive_key()  # This will wait for server
            decrypted_otp = decrypt_otp(st.session_state.encrypted_otp, key)
            
            if otp_input == decrypted_otp:
                with open(USER_FILE, "a") as f:
                    f.write(st.session_state.new_user)
                st.success("Registration successful! You can now log in.")
                time.sleep(2)
                stop_server()
                go_to_login()
                st.rerun()
            else:
                st.error("Incorrect OTP. Try again.")
        except Exception as e:
            st.error(f"Verification failed: {str(e)}")
            stop_server()

    if st.button("Back to Login"):
        stop_server()
        go_to_login()

# ----- Page: Login -----
elif st.session_state.page == "login":
    st.subheader("🔑 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Send OTP"):
        if not os.path.exists(USER_FILE):
            st.error("No users registered yet")
            st.stop()
            
        with open(USER_FILE, "r") as f:
            users = [line.strip().split("|") for line in f]
        user = next((u for u in users if u[0] == email), None)
        
        if not user:
            st.error("User not found.")
        elif verify_password_similarity(password, user[1]):
            # Generate random key (bytes)
            key = os.urandom(16)
            st.session_state.key = key
            
            # Start key server in background thread
            stop_server()  # Ensure any previous server is stopped
            threading.Thread(
                target=run_key_server,
                args=(key,),
                daemon=True
            ).start()
            st.session_state.key_server_running = True
            
            # Small delay to ensure server is ready
            time.sleep(0.5)
            
            # Send OTP and encrypt
            otp = send_otp(email)
            if otp is None:
                st.error("Failed to send OTP. Please try again.")
                stop_server()
                st.stop()
                
            encrypted_otp = encrypt_otp(otp, key)
            st.session_state.encrypted_otp = encrypted_otp
            st.session_state.email = email
            st.session_state.page = "verify_login"
            st.rerun()
        else:
            st.error("Incorrect password.")

    if st.button("Register"):
        stop_server()
        go_to_register()

# ----- Page: OTP Verification (Login) -----
elif st.session_state.page == "verify_login":
    st.subheader("📨 Enter OTP to Login")

    otp_input = st.text_input("OTP from email")

    if st.button("Verify"):
        try:
            key = receive_key()  # This will wait for server
            decrypted_otp = decrypt_otp(st.session_state.encrypted_otp, key)
            
            if otp_input == decrypted_otp:
                st.success("Access Granted ✅")
                time.sleep(1)
                stop_server()
                st.switch_page("pages/home.py")
            else:
                st.error("Invalid OTP ❌")
        except Exception as e:
            st.error(f"Verification failed: {str(e)}")
            stop_server()

    if st.button("Back to Login"):
        stop_server()
        go_to_login()

####################################################################################
# import streamlit as st
# from utils.hash_utils import hash_password, verify_password_similarity
# from utils.email_utils import send_otp
# from utils.encryption_utils import encrypt_otp, decrypt_otp
# from utils.socket_utils import send_key, receive_key
# import os
# import time

# USER_FILE = "user_data.txt"

# st.set_page_config(page_title="2FA Auth", layout="centered")
# st.title("🔐 2FA Authentication System")

# if "page" not in st.session_state:
#     st.session_state.page = "login"

# def go_to_login():
#     st.session_state.page = "login"

# def go_to_register():
#     st.session_state.page = "register"

# # ----- Page: Register -----
# if st.session_state.page == "register":
#     st.subheader("📋 Register New Account")

#     full_name = st.text_input("Full Name")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     confirm_password = st.text_input("Re-type Password", type="password")

#     # Password Rules
#     def valid_password(pwd):
#         return (len(pwd) >= 8 and
#                 any(c.isalpha() for c in pwd) and
#                 any(c.isdigit() for c in pwd) and
#                 any(c in "@_!#$%^&*()-+=?" for c in pwd))

#     if st.button("Register"):

#         if not all([full_name, email, password, confirm_password]):
#             st.error("Please fill in all fields.")
#         elif password != confirm_password:
#             st.error("Passwords do not match.")
#         elif not valid_password(password):
#             st.warning("Password must be ≥8 chars, include a number, a letter, and a special character.")
#         else:
#             # Check if user exists
#             if os.path.exists(USER_FILE):
#                 with open(USER_FILE, "r") as f:
#                     if any(line.startswith(email) for line in f):
#                         st.error("User already exists.")
#                         st.stop()

#             key = os.urandom(16)
#             send_key(key)
#             otp = send_otp(email)
#             encrypted_otp = encrypt_otp(otp, key)
#             st.session_state.encrypted_otp = encrypted_otp
#             st.session_state.key = key
#             st.session_state.new_user = f"{email}|{hash_password(password)}\n"
#             st.session_state.page = "verify_register"
#             st.experimental_rerun()

# # ----- Page: OTP Verification (Registration) -----
# elif st.session_state.page == "verify_register":
#     st.subheader("📨 Verify OTP to Complete Registration")

#     otp_input = st.text_input("Enter OTP")

#     if st.button("Verify OTP"):
#         key = receive_key()
#         decrypted_otp = decrypt_otp(st.session_state.encrypted_otp, key)
#         if otp_input == decrypted_otp:
#             with open(USER_FILE, "a") as f:
#                 f.write(st.session_state.new_user)
#             st.success("Registration successful! You can now log in.")
#             time.sleep(2)
#             go_to_login()
#             st.experimental_rerun()
#         else:
#             st.error("Incorrect OTP. Try again.")

#     st.button("Back to Login", on_click=go_to_login)

# # ----- Page: Login -----
# elif st.session_state.page == "login":
#     st.subheader("🔑 Login")

#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")

#     if st.button("Send OTP"):
#         with open(USER_FILE, "r") as f:
#             users = [line.strip().split("|") for line in f]
#         user = next((u for u in users if u[0] == email), None)
#         if not user:
#             st.error("User not found.")
#         elif verify_password_similarity(password, user[1]):
#             key = os.urandom(16)
#             # send_key(key)
#             otp = send_otp(email)
#             encrypted_otp = encrypt_otp(otp, key)
#             st.session_state.encrypted_otp = encrypted_otp
#             st.session_state.page = "verify_login"
#             st.session_state.email = email
#             st.experimental_rerun()
#         else:
#             st.error("Incorrect password.")

#     st.button("Register", on_click=go_to_register)

# # ----- Page: OTP Verification (Login) -----
# elif st.session_state.page == "verify_login":
#     st.subheader("📨 Enter OTP to Login")

#     otp_input = st.text_input("OTP from email")

#     if st.button("Verify"):
#         key = receive_key()
#         decrypted_otp = decrypt_otp(st.session_state.encrypted_otp, key)
#         if otp_input == decrypted_otp:
#             st.success("Access Granted ✅")
#             time.sleep(1)
#             st.switch_page("home.py")  # navigate to home
#         else:
#             st.error("Invalid OTP ❌")

#     st.button("Back to Login", on_click=go_to_login)

###################################################################################################
# import streamlit as st
# from utils.hash_utils import hash_password, verify_password_similarity
# from utils.email_utils import send_otp
# from utils.encryption_utils import encrypt_otp, decrypt_otp
# from utils.socket_utils import send_key, receive_key
# import os

# USER_FILE = "user_data.txt"

# st.title("🔐 2FA Authentication System")

# menu = ["Register", "Login"]
# choice = st.sidebar.selectbox("Menu", menu)

# if choice == "Register":
#     st.subheader("Create Account")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Register"):
#         hashed_pwd = hash_password(password)
#         with open(USER_FILE, "a") as f:
#             f.write(f"{email}|{hashed_pwd}\n")
#         st.success("Registered successfully!")

# elif choice == "Login":
#     st.subheader("Login")
#     email = st.text_input("Email")
#     password = st.text_input("Password", type="password")
#     if st.button("Send OTP"):
#         # Check email and password
#         with open(USER_FILE, "r") as f:
#             lines = f.readlines()
#             user = [line for line in lines if line.startswith(email)]
#             if not user:
#                 st.error("User not found.")
#             else:
#                 stored_hash = user[0].strip().split("|")[1]
#                 if verify_password_similarity(password, stored_hash):
#                     key = os.urandom(16)
#                     send_key(key)
#                     otp = send_otp(email)
#                     encrypted_otp = encrypt_otp(otp, key)
#                     st.session_state.encrypted_otp = encrypted_otp
#                     st.success("OTP sent to your email.")
#                 else:
#                     st.error("Incorrect password.")

#     if "encrypted_otp" in st.session_state:
#         otp_input = st.text_input("Enter OTP")
#         if st.button("Verify"):
#             key = receive_key()
#             decrypted_otp = decrypt_otp(st.session_state.encrypted_otp, key)
#             if otp_input == decrypted_otp:
#                 st.success("Access Granted ✅")
#             else:
#                 st.error("Invalid OTP ❌")


st.markdown(
    """
    <style>
/* Main app background */
.stApp {
    background-color: #F5F5DC; /* Beige background */
    color: #333333; /* Dark text for contrast */
}

/* Main header (e.g., "2FA Authentication System") */
h1 {
    text-align: center;
    color: #2E8B57; /* Sea green for headers */
    font-size: 3em;
    font-weight: bold;
    margin-bottom: 0.5em;
}

/* Subheaders (e.g., "Login", "Register New Account", "Verify OTP") */
h2 {
    color: #4682B4; /* Steel blue for subheaders */
    font-size: 1.8em;
    font-weight: bold;
    margin-top: 1em;
    margin-bottom: 0.5em;
}

/* Content styling for text, inputs, and general content */
div.stTextInput > div > input,
div.stButton > button,
p, div.stMarkdown {
    font-size: 1.1em;
    line-height: 1.6;
    color: #333333;
}

/* Card styling for form containers */
div.stTextInput, div.stButton {
    background-color: #FFFFFF; /* White card background */
    padding: 1.5em;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    margin-bottom: 1.5em;
}

/* Input fields */
div.stTextInput > div > input {
    border: 1px solid #4682B4; /* Steel blue border */
    border-radius: 5px;
    padding: 0.5em;
}

/* Buttons (e.g., "Register", "Send OTP", "Verify") */
div.stButton > button {
    background-color: #2E8B57; /* Sea green for buttons */
    color: white;
    border: none;
    border-radius: 5px;
    padding: 0.5em 1em;
    font-weight: bold;
    transition: background-color 0.3s;
}
div.stButton > button:hover {
    background-color: #228B22; /* Darker sea green on hover */
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #E6E6FA; /* Lavender sidebar */
}

/* Logout button */
.logout-button {
    background-color: #DC143C; /* Crimson for logout button */
    color: white;
    padding: 0.5em 1em;
    border-radius: 5px;
    text-align: center;
    text-decoration: none;
    display: block;
    margin-top: 1em;
    font-weight: bold;
    transition: background-color 0.3s;
}
.logout-button:hover {
    background-color: #B22222; /* Darker crimson on hover */
}

/* Error, success, and warning messages */
div.stAlert > div {
    border-radius: 5px;
    padding: 1em;
    margin-bottom: 1em;
}
div.stAlert[role="alert"] {
    background-color: #FFF8DC; /* Light beige for alerts */
    color: #333333;
    border: 1px solid #4682B4; /* Steel blue border */
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 2em;
    color: #666666;
    font-size: 0.9em;
}
</style>
""",
    unsafe_allow_html=True
)