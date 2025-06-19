import streamlit as st
import requests
import time
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Set page configuration
st.set_page_config(
    page_title="Sir Syed University of Engineering and Technology",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS for beige background and styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F5F5DC; /* Beige background */
        color: #333333; /* Dark text for contrast */
    }
    .header {
        text-align: center;
        color: #2E8B57; /* Sea green for headers */
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subheader {
        color: #4682B4; /* Steel blue for subheaders */
        font-size: 1.8em;
        font-weight: bold;
        margin-top: 1em;
    }
    .content {
        font-size: 1.1em;
        line-height: 1.6;
        margin-bottom: 1em;
    }
    .card {
        background-color: #FFFFFF; /* White card background */
        padding: 1.5em;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5em;
    }
    .sidebar .sidebar-content {
        background-color: #E6E6FA; /* Lavender sidebar */
    }
    .logout-button {
        background-color: #DC143C; /* Crimson for logout button */
        color: white;
        padding: 0.5em 1em;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        display: block;
        margin-top: 1em;
    }
    .logout-button:hover {
        background-color: #B22222; /* Darker crimson on hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)

SERVER_URL = "http://localhost:5000"

# Create a session with retry logic
http_session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504], allowed_methods=["GET", "POST"])
http_session.mount('http://', HTTPAdapter(max_retries=retries))

def check_auth():
    try:
        cookies = {'session': st.session_state.session_cookie} if st.session_state.get('session_cookie') else {}
        res = http_session.get(f"{SERVER_URL}/check_auth", cookies=cookies)
        if res.status_code == 200:
            data = res.json()
            return data.get('authenticated', False), data.get('email', '')
        logging.error(f"Check auth failed: {res.status_code} {res.text}")
        return False, ''
    except Exception as e:
        logging.error(f"Check auth failed: {e}")
        return False, ''

def logout():
    try:
        cookies = {'session': st.session_state.session_cookie} if st.session_state.get('session_cookie') else {}
        res = http_session.post(f"{SERVER_URL}/logout", cookies=cookies)
        if res.status_code == 200 and res.json().get('status') == 'success':
            logging.info("Logout successful: Flask session cleared")
        else:
            logging.warning(f"Logout endpoint failed: {res.status_code} {res.text}")
        
        # Clear Streamlit session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        logging.debug("Streamlit session state cleared")
        
        st.success("Logged out successfully")
        time.sleep(1)
        st.switch_page("client.py")
    except Exception as e:
        st.error(f"Logout failed: {e}")
        logging.error(f"Logout failed: {e}")
        time.sleep(1)
        st.switch_page("client.py")

# Check authentication
auth, email = check_auth()
if not auth:
    st.warning("Please login first")
    time.sleep(1)
    st.switch_page("client.py")

# Main header
st.markdown('<div class="header">Sir Syed University of Engineering and Technology (SSUET)</div>', unsafe_allow_html=True)

# Sidebar with navigation and logout button
with st.sidebar:
    st.image("https://cdn-education.tribune.com.pk/institutes-logo/Dt75XTqYrK6p7oHLtMxXcQr5pMgMt0CtrOpRbWjr.jpeg", use_container_width=True)
    st.markdown('<div class="subheader">Navigation</div>', unsafe_allow_html=True)
    page = st.selectbox("Go to", ["Overview", "Programs Offered", "Research Focus", "Campus Facilities", "Contact Information"])
    
    # Logout button with custom styling
    if st.button("Logout", key="logout_button", help="Sign out of your account"):
        logout()

# Overview Section
if page == "Overview":
    st.markdown('<div class="subheader">Overview</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="card">
            <div class="content">
            Founded in 1994 in Karachi, Pakistan, Sir Syed University of Engineering and Technology (SSUET) is a private research university named after the renowned 19th-century Muslim reformer, Sir Syed Ahmad Khan. Sponsored by the Aligarh Muslim University Old Boys’ Association (AMUOBA), SSUET is committed to advancing education in science, technology, and engineering. Ranked 12th in Pakistan’s engineering category by the Higher Education Commission (HEC) as of 2013, SSUET has produced over 22,000 graduates in the last 27 years, contributing significantly to national and international markets. The university emphasizes quality education, research, and social impact, aligning with global Sustainable Development Goals (SDGs).
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Programs Offered Section
elif page == "Programs Offered":
    st.markdown('<div class="subheader">Programs Offered</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="card">
            <div class="content">
            SSUET offers a diverse range of undergraduate, postgraduate, and doctoral programs across multiple disciplines, including:
            <ul>
                <li><b>Engineering:</b> Civil, Electrical, Mechanical, Biomedical, and more.</li>
                <li><b>Technology:</b> Computer Science, Software Engineering, Artificial Intelligence, Cyber Security.</li>
                <li><b>Business:</b> MBA, Business Administration, Accounting and Finance.</li>
                <li><b>Sciences:</b> Physical Sciences, Mathematics, English.</li>
                <li><b>Architecture:</b> Undergraduate and postgraduate programs in Architecture.</li>
            </ul>
            The MBA program focuses on developing intellectual ability, executive personality, and managerial skills, blending global best practices with local entrepreneurial needs. Programs meet accreditation standards set by bodies like the Pakistan Engineering Council (PEC) and National Computing Education Accreditation Council (NCEAC).
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Research Focus Section
elif page == "Research Focus":
    st.markdown('<div class="subheader">Research Focus</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="card">
            <div class="content">
            SSUET places a strong emphasis on research through its Office of Research Innovation & Commercialization (ORIC). Key research areas include:
            <ul>
                <li>Engineering and Technology Innovations</li>
                <li>Artificial Intelligence and Cyber Security</li>
                <li>Sustainable Development and Environmental Solutions</li>
                <li>Business and Management Studies</li>
            </ul>
            The university actively participates in THE Impact Rankings to achieve SDGs and fosters industry-academia linkages to address socio-economic challenges. Ongoing research projects and collaborations aim to create an entrepreneurial mindset among students and faculty.
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Campus Facilities Section
elif page == "Campus Facilities":
    st.markdown('<div class="subheader">Campus Facilities</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="card">
            <div class="content">
            Located in the heart of Karachi, SSUET’s purpose-built campus offers state-of-the-art facilities, including:
            <ul>
                <li><b>Academic Infrastructure:</b> Air-conditioned classrooms, modern labs meeting international standards.</li>
                <li><b>Sports Facilities:</b> Basketball court, volleyball ground, cricket pitch, and plans for hockey and football grounds.</li>
                <li><b>Student Societies:</b> IEEE SSUET Student Branch, Literary Art & Cultural Forum (SSULACF), and music clubs.</li>
                <li><b>Career Support:</b> Career Planning & Placement Bureau for internships and job placements.</li>
                <li><b>Other Amenities:</b> Health and fitness rooms, symposiums, seminars, and continuing education programs.</li>
            </ul>
            The Sir Syed Ahmed Khan Youth Centre promotes moral values, ethics, and communication skills among students.
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Contact Information Section
elif page == "Contact Information":
    st.markdown('<div class="subheader">Contact Information</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="card">
            <div class="content">
            <ul>
                <li><b>Location:</b> Main University Road, Near NIPA Roundabout, Karachi, Sindh, 75300, Pakistan</li>
                <li><b>Phone:</b> +92 21 34988000</li>
                <li><b>Email:</b> registrar@ssuet.edu.pk</li>
                <li><b>Website:</b> <a href="https://www.ssuet.edu.pk" target="_blank">www.ssuet.edu.pk</a></li>
                <li><b>Social Media:</b> Follow SSUET on LinkedIn, Facebook, and Twitter for updates.</li>
            </ul>
            For admissions, visit the <a href="https://www.ssuet.edu.pk/admissions/undergraduate-admissions/" target="_blank">Undergraduate Admissions</a> page.
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Footer
st.markdown(
    """
    <div style="text-align: center; margin-top: 2em; color: #666666;">
    © 2025 Sir Syed University of Engineering and Technology | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)