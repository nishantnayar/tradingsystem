"""
Main Streamlit application for the trading system.
"""
import streamlit as st
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.ui.pages.home import render_home
from src.ui.pages.analysis import render_analysis
from src.ui.pages.settings import render_settings


def main():
    """Main application entry point."""
    # Configure the page
    st.set_page_config(
        page_title="Trading System",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 4rem;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 4px 4px 0px 0px;
            gap: 1rem;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Home", "Analysis", "Settings"],
        label_visibility="collapsed"
    )
    
    # Render the selected page
    if page == "Home":
        render_home()
    elif page == "Analysis":
        render_analysis()
    elif page == "Settings":
        render_settings()


if __name__ == "__main__":
    main() 