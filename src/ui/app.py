"""
Main Streamlit application for the trading system.
"""
import streamlit as st
from pathlib import Path
import sys
from streamlit_option_menu import option_menu

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import page renderers
from src.ui.home import render_home
from src.ui.analysis import render_analysis
from src.ui.settings import render_settings

def main():
    """Main application entry point."""
    # Configure the page - MOVE THIS TO TOP LEVEL AND CALL ONLY ONCE
    st.set_page_config(
        page_title="Trading System",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items=None  # Add this to hide native page menu
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

    # Navigation using option_menu
    with st.sidebar:
        selected = option_menu(
            menu_title="Trading System",
            options=["Home", "Analysis", "Settings"],
            icons=["house", "graph-up", "gear"],
            menu_icon="chart-line",
            default_index=0,
        )

    # Render the selected page
    if selected == "Home":
        render_home()
    elif selected == "Analysis":
        render_analysis()
    elif selected == "Settings":
        render_settings()


if __name__ == "__main__":
    main()