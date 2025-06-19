# AES-OTP-Auth

**AES-OTP-Auth** is a secure authentication portal for Sir Syed University of Engineering and Technology (SSUET), built with a Flask backend and Streamlit frontend. It provides user registration and login with OTP-based two-factor authentication, AES-128 encryption for OTPs, and a socket-based key exchange mechanism. The system includes a protected dashboard displaying SSUET information, accessible only to authenticated users.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- **Secure Authentication**:
  - User registration and login with email and password.
  - Two-factor authentication using OTP sent via email.
  - OTPs encrypted with AES-128 (EAX mode) for confidentiality and authenticity.
- **Key Exchange**:
  - Socket-based key server (`localhost:65432`) for secure AES key delivery.
  - HTTP fallback endpoint (`/key`) for key retrieval if socket fails.
- **Streamlit Frontend**:
  - User-friendly login/registration interface.
  - Protected dashboard (`home.py`) with SSUET details, including Overview, Programs Offered, Research Focus, Campus Facilities, and Contact Information.
  - Responsive UI with custom CSS (beige theme, card layouts, sidebar navigation).
- **Flask Backend**:
  - RESTful API endpoints for registration, login, OTP verification, and logout.
  - Filesystem-based session management with a 30-minute timeout.
  - Health check (`/health`) and graceful shutdown (`/shutdown`) endpoints.
- **Robust Error Handling**:
  - Retry logic for HTTP requests to handle transient connection issues (`ConnectionResetError`).
  - Disabled Flask reloader to prevent `ValueError: signal only works in main thread`.
- **Logging**:
  - Detailed logs for debugging key exchange, authentication, and server operations.

## Project Structure
```
SSUET-SecureAuth/
├── client.py                # Streamlit frontend for login/registration
├── server.py                # Flask backend with API and key server
├── pages/
│   └── home.py              # Protected SSUET dashboard
├── utils/
│   ├── encryption_utils.py  # AES encryption/decryption for OTPs
│   ├── hash_utils.py        # Password hashing and verification
│   ├── email_utils.py       # OTP email sending
│   └── socket_utils.py      # Socket-based key exchange
├── user_data.txt            # Stores user email and hashed password
├── flask_session/           # Flask session storage
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Prerequisites
- **Python**: 3.13 or higher
- **Operating System**: Windows (tested), Linux, or macOS
- **Dependencies** (listed in `requirements.txt`):
  ```
  flask==2.3.3
  flask-session==0.5.0
  streamlit==1.38.0
  requests==2.31.0
  pycryptodome==3.20.0
  ```
- **Email Service**: Configured SMTP server for sending OTP emails (update `utils/email_utils.py` with your credentials).
- **Ports**: Ensure ports `5000` (Flask) and `65432` (key server) are free.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/SSUET-SecureAuth.git
   cd SSUET-SecureAuth
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Email Settings**:
   - Edit `utils/email_utils.py` to add your SMTP server details (e.g., Gmail):
     ```python
     SMTP_SERVER = "smtp.gmail.com"
     SMTP_PORT = 587
     SMTP_USER = "your-email@gmail.com"
     SMTP_PASSWORD = "your-app-password"
     ```

5. **Open Firewall Ports** (Windows):
   ```bash
   netsh advfirewall firewall add rule name="Allow Port 5000" dir=in action=allow protocol=TCP localport=5000
   netsh advfirewall firewall add rule name="Allow Port 65432" dir=in action=allow protocol=TCP localport=65432
   ```

## Usage
1. **Run the Flask Server**:
   ```bash
   python server.py
   ```
   - Starts the Flask API on `http://localhost:5000` and key server on `localhost:65432`.
   - Logs:
     ```
     2025-06-19 07:40:00,123 - INFO - [SERVER] Initialized with AES Key: <key_hex>
     2025-06-19 07:40:00,126 - INFO - Key server listening on localhost:65432
     ```

2. **Run the Streamlit Client**:
   ```bash
   streamlit run client.py
   ```
   - Opens the portal at `http://localhost:8501`.
   - Logs:
     ```
     2025-06-19 07:40:01,124 - INFO - Received key: <key_hex>
     ```

3. **Register or Login**:
   - **Register**: Enter email and password, receive an OTP via email, and verify to create an account.
   - **Login**: Enter credentials, receive an OTP, and verify to access the SSUET dashboard (`home.py`).
   - **Dashboard**: View SSUET information (Overview, Programs, etc.) and log out via the sidebar.

4. **Shutdown**:
   - Stop the server gracefully:
     ```bash
     curl -X POST http://localhost:5000/shutdown
     ```
   - Or use `Ctrl+C` in the server terminal.

## Security Considerations
- **Current Protections**:
  - OTPs are encrypted with AES-128 (EAX mode) for confidentiality and authenticity.
  - Key exchange uses a local socket server (`localhost:65432`) to limit external access.
  - Short-lived OTPs reduce the attack window.
- **Vulnerabilities**:
  - **HTTP Usage**: OTPs and keys are sent over HTTP, vulnerable to man-in-the-middle (MITM) attacks.
  - **Unauthenticated Key Server**: Any local process can access `localhost:65432` or `/key`.
  - **Static Key**: The AES key doesn’t rotate, increasing risk if compromised.
- **Recommendations**:
  - Enable HTTPS with SSL/TLS (e.g., use `ssl_context='adhoc'` in `server.py` or a reverse proxy like Nginx).
  - Remove the HTTP `/key` fallback and authenticate socket clients with a token.
  - Implement key rotation and store keys securely (e.g., environment variables).
  - Restrict server access to `localhost` and use a firewall to block external connections.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request with a detailed description.

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) and ensure tests pass before submitting.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
- **Project Maintainer**: [Your Name] (your-email@example.com)
- **SSUET Contact**: registrar@ssuet.edu.pk | +92 21 34988000 | [www.ssuet.edu.pk](https://www.ssuet.edu.pk)
- **Issues**: File bugs or feature requests on the [GitHub Issues page](https://github.com/<your-username>/SSUET-SecureAuth/issues).

---

### Notes
- **Customization**: Replace `<your-username>` with your GitHub username. Add your contact details in the "Contact" section if desired.
- **Security Section**: Highlights vulnerabilities (e.g., HTTP usage) discussed in your question about OTP decryption risks.
- **Dependencies**: Assumes `pycryptodome` for AES encryption, based on typical implementations. If you use a different library, update `requirements.txt`.
- **Testing**: The README aligns with the fixed code (`client.py`, `server.py`, `home.py`) addressing `ConnectionResetError`, `ValueError`, and logout functionality.

To use this:
1. Save as `README.md` in your project root (`C:\Users\khali\OneDrive\Desktop\CNS Project`).
2. Create `requirements.txt`:
   ```plaintext
   flask==2.3.3
   flask-session==0.5.0
   streamlit==1.38.0
   requests==2.31.0
   pycryptodome==3.20.0
   ```
3. Push to GitHub:
   ```bash
   git add README.md requirements.txt
   git commit -m "Add README and requirements"
   git push origin main
   ```

If you need adjustments (e.g., specific contributors, additional features, or a different license), let me know!
