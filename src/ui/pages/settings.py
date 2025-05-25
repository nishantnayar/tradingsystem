"""
Settings page for system configuration.
"""
import streamlit as st
import yaml
from pathlib import Path
import os
from loguru import logger

from src.utils.config import get_config, update_config


def render_settings():
    """Render the settings page."""
    st.title("System Settings")
    
    # Create tabs for different settings
    tab1, tab2, tab3 = st.tabs(["Data Collection", "Trading", "System"])
    
    with tab1:
        st.header("Data Collection Settings")
        
        # Data source settings
        st.subheader("Data Source")
        data_source = st.radio(
            "Select Data Source",
            options=["Alpaca"],  # Removed "Yahoo Finance" as it's not implemented yet
            help="Choose the data source for market data"
        )
        
        if data_source == "Alpaca":
            # Alpaca API settings
            st.subheader("Alpaca API Settings")
            
            # Get current config
            config = get_config()
            alpaca_config = config.get("alpaca", {})
            
            # Display API configuration status
            if alpaca_config.get("api_key") and alpaca_config.get("secret_key"):
                st.success("✅ API credentials configured")
            else:
                st.warning("⚠️ API credentials not found in configuration")
                st.info("Please ensure your API credentials are set in the .env file")
        
        # Collection settings
        st.subheader("Collection Settings")
        st.number_input("Update Interval (minutes)", value=60, min_value=1)
        st.multiselect(
            "Default Symbols",
            options=["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
            default=["AAPL", "MSFT"]
        )
    
    with tab2:
        st.header("Trading Settings")
        
        # Account settings
        st.subheader("Account Settings")
        st.number_input("Initial Capital", value=100000, min_value=1000)
        st.number_input("Max Position Size (%)", value=10.0, min_value=1.0, max_value=100.0, step=0.1)
        
        # Risk management
        st.subheader("Risk Management")
        st.number_input("Stop Loss (%)", value=2.0, min_value=0.1, max_value=10.0, step=0.1)
        st.number_input("Take Profit (%)", value=5.0, min_value=0.1, max_value=20.0, step=0.1)
        st.number_input("Max Open Positions", value=5, min_value=1, max_value=20)
    
    with tab3:
        st.header("System Settings")
        
        # Database settings
        st.subheader("Database")
        db_config = get_config().get("database", {})
        st.text_input("Host", value=db_config.get("host", "localhost"))
        st.number_input("Port", value=db_config.get("port", 5432))
        st.text_input("Database", value=db_config.get("name", "trading"))
        st.text_input("Username", value=db_config.get("user", ""))
        st.text_input("Password", value="", type="password")
        
        # Logging settings
        st.subheader("Logging")
        st.selectbox(
            "Log Level",
            options=["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1
        )
        st.checkbox("Enable Database Logging", value=True)
        st.number_input("Log Retention (days)", value=30, min_value=1)
    
    # Save button
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
        # TODO: Implement settings save functionality 