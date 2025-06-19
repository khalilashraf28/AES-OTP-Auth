from flask import Flask, request, jsonify, session
from flask_session import Session
import os
import secrets
import time
from datetime import timedelta
from utils.hash_utils import hash_password, verify_password_similarity
from utils.email_utils import send_otp
from utils.encryption_utils import encrypt_otp, decrypt_otp
from utils.socket_utils import run_key_server, stop_key_server
import threading
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
Session(app)

USER_FILE = "user_data.txt"
key = os.urandom(16)
logging.info(f"[SERVER] Initialized with AES Key: {key.hex()}")

# Start key server in a separate thread
logging.info("Starting key server thread")
key_server_thread = threading.Thread(target=run_key_server, args=(key,), daemon=True)
key_server_thread.start()
logging.debug("Key server thread started")

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    logging.debug("Health check requested")
    return jsonify({"status": "ok"}), 200

# HTTP fallback for key retrieval
@app.route("/key", methods=["GET"])
def get_key():
    logging.debug("Serving key via HTTP")
    return jsonify({"key": key.hex()})

# Shutdown endpoint for graceful cleanup
@app.route("/shutdown", methods=["POST"])
def shutdown():
    try:
        logging.info("Shutdown requested")
        stop_key_server()
        func = request.environ.get('werkzeug.server.shutdown')
        if func:
            func()
        logging.info("Server shutting down")
        return jsonify({"status": "success", "message": "Server shutting down"})
    except Exception as e:
        logging.error(f"Shutdown error: {e}")
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route("/register", methods=["POST"])
def register():
    try:
        logging.debug("Register endpoint called")
        data = request.get_json()
        if not data:
            logging.warning("No data provided in register request")
            return jsonify({"status": "fail", "message": "No data provided"}), 400
            
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            logging.warning("Email or password missing")
            return jsonify({"status": "fail", "message": "Email and password required"}), 400

        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as f:
                if any(line.startswith(email) for line in f):
                    logging.warning(f"User {email} already exists")
                    return jsonify({"status": "fail", "message": "User already exists"}), 400

        hashed = hash_password(password)
        
        with open(USER_FILE, "a") as f:
            f.write(f"{email}|{hashed}\n")
            logging.debug(f"User {email} registered")

        otp = send_otp(email)
        if not otp:
            logging.error("Failed to send OTP")
            return jsonify({"status": "fail", "message": "Failed to send OTP"}), 500
        encrypted_otp = encrypt_otp(otp, key)
        logging.debug(f"OTP encrypted: {encrypted_otp}")
        
        session['reg_email'] = email
        session['reg_otp'] = otp
        session['reg_attempt'] = True
        
        return jsonify({
            "status": "success", 
            "otp": encrypted_otp,
            "session_id": session.sid
        })
    except Exception as e:
        logging.error(f"Registration error: {e}")
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route("/verify_registration", methods=["POST"])
def verify_registration():
    try:
        logging.debug("Verify registration endpoint called")
        if not session.get('reg_attempt'):
            logging.warning("No registration attempt found")
            return jsonify({"status": "fail", "message": "No registration attempt found"}), 401
        
        data = request.get_json()
        if not data:
            logging.warning("No data provided in verify registration")
            return jsonify({"status": "fail", "message": "No data provided"}), 400
            
        user_otp = data.get('otp', '').strip()
        
        if user_otp == session.get('reg_otp'):
            session.pop('reg_otp', None)
            session.pop('reg_attempt', None)
            session['authenticated'] = True
            logging.info("Registration verified successfully")
            return jsonify({"status": "success", "message": "Registration verified"})
        logging.warning("Invalid OTP provided")
        return jsonify({"status": "fail", "message": "Invalid OTP"}), 401
    except Exception as e:
        logging.error(f"Verify registration error: {e}")
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        logging.debug("Login endpoint called")
        data = request.get_json()
        if not data:
            logging.warning("No data provided in login request")
            return jsonify({"status": "fail", "message": "No data provided"}), 400
            
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        logging.debug(f"Login attempt for {email}")

        if not email or not password:
            logging.warning("Email or password missing")
            return jsonify({"status": "fail", "message": "Email and password required"}), 400

        if not os.path.exists(USER_FILE):
            logging.error("User data file missing")
            return jsonify({"status": "fail", "message": "User data file missing"}), 404

        with open(USER_FILE, "r") as f:
            lines = f.readlines()
            user = [line for line in lines if line.startswith(email)]
            if not user:
                logging.warning(f"User {email} not found")
                return jsonify({"status": "fail", "message": "User not found"}), 404

            stored_hash = user[0].strip().split("|")[1]
            if not verify_password_similarity(password, stored_hash):
                logging.warning(f"Incorrect password for {email}")
                return jsonify({"status": "fail", "message": "Incorrect password"}), 401

        otp = send_otp(email)
        if not otp:
            logging.error("Failed to send OTP")
            return jsonify({"status": "fail", "message": "Failed to send OTP"}), 500
        encrypted_otp = encrypt_otp(otp, key)
        logging.debug(f"OTP encrypted: {encrypted_otp}")
        
        session['login_email'] = email
        session['login_otp'] = otp
        session['login_attempt'] = True
        
        logging.info(f"Login OTP sent for {email}")
        return jsonify({
            "status": "success", 
            "otp": encrypted_otp,
            "session_id": session.sid
        })
    except Exception as e:
        logging.error(f"Login error: {e}")
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route("/verify_login", methods=["POST"])
def verify_login():
    try:
        logging.debug("Verify login endpoint called")
        if not session.get('login_attempt'):
            logging.warning("No login attempt found")
            return jsonify({"status": "fail", "message": "No login attempt found"}), 401
        
        data = request.get_json()
        if not data:
            logging.warning("No data provided in verify login")
            return jsonify({"status": "fail", "message": "No data provided"}), 400
            
        user_otp = data.get('otp', '').strip()
        
        if user_otp == session.get('login_otp'):
            session.pop('login_otp', None)
            session.pop('login_attempt', None)
            session['authenticated'] = True
            session['email'] = session.get('login_email')
            logging.info("Login verified successfully")
            return jsonify({"status": "success", "message": "Login verified"})
        logging.warning("Invalid OTP provided")
        return jsonify({"status": "fail", "message": "Invalid OTP"}), 401
    except Exception as e:
        logging.error(f"Verify login error: {e}")
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route("/check_auth", methods=["GET"])
def check_auth():
    try:
        logging.debug("Check auth endpoint called")
        if session.get('authenticated'):
            return jsonify({
                "status": "success", 
                "authenticated": True,
                "email": session.get('email')
            })
        return jsonify({"status": "fail", "authenticated": False})
    except Exception as e:
        logging.error(f"Check auth error: {e}")
        return jsonify({"status": "fail", "message": str(e)}), 500

@app.route("/logout", methods=["POST"])
def logout():
    try:
        logging.debug("Logout endpoint called")
        session.clear()
        logging.info("User logged out")
        return jsonify({"status": "success", "message": "Logged out"})
    except Exception as e:
        logging.error(f"Logout error: {e}")
        return jsonify({"status": "fail", "message": str(e)}), 500

if __name__ == '__main__':
    try:
        # Wait for key server thread to start
        time.sleep(2)  # Ensure key server is up
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)  # Disable reloader
    except KeyboardInterrupt:
        logging.info("Server interrupted by user")
        stop_key_server()
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server startup error: {e}")
        stop_key_server()
        sys.exit(1)