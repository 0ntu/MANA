from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Energy Scheduler", page_icon=":zap:", layout="wide")

APP_DIR = Path(__file__).parent

# Custom CSS for a modern, structured layout
st.markdown(
    """
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f9f9f9;
        color: #333;
        margin: 0;
        padding: 0;
    }
    .header {
        background-color: #4CAF50;
        color: white;
        padding: 2rem 0;
        text-align: center;
    }
    .header h1 {
        font-size: 3rem;
        margin: 0;
    }
    .header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0;
    }
    .features {
        display: flex;
        justify-content: space-around;
        padding: 2rem 1rem;
        background-color: #fff;
    }
    .feature {
        text-align: center;
        max-width: 300px;
    }
    .feature h3 {
        font-size: 1.5rem;
        color: #4CAF50;
    }
    .feature p {
        font-size: 1rem;
        color: #555;
    }
    .cta {
        text-align: center;
        padding: 2rem 1rem;
        background-color: #f1f1f1;
    }
    .cta button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        border-radius: 5px;
        cursor: pointer;
        margin: 0.5rem;
    }
    .cta button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def landing_page():
    # Header Section
    st.markdown(
        """
        <div class="header">
            <h1>Energy Scheduler</h1>
            <p>Plan your day based on your energy levels, not just your time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Features Section
    st.markdown(
        """
        <div class="features">
            <div class="feature">
                <h3>Track Your Energy</h3>
                <p>Monitor your energy levels throughout the day to stay productive.</p>
            </div>
            <div class="feature">
                <h3>Smart Scheduling</h3>
                <p>Get personalized task recommendations based on your energy.</p>
            </div>
            <div class="feature">
                <h3>Stay Balanced</h3>
                <p>Avoid burnout by planning tasks that match your energy levels.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Call-to-Action Section
    st.markdown(
        """
        <div class="cta">
            <button onclick="location.href='#'">Sign In</button>
            <button onclick="location.href='#'">Sign Up</button>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Render the landing page
landing_page()
