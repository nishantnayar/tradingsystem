import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data.data_manager import DataManager
from src.ui.components.data_display import display_market_data

def test_data_display():
    """Test the market data display functionality."""
    # Test symbol
    symbol = "AAPL"
    
    # Get data directly from DataManager
    data_manager = DataManager()
    data = data_manager.get_latest_data(symbol)
    
    print("\nTesting Data Display:")
    print("-" * 50)
    
    # Check if data is being retrieved
    if data is None:
        print("❌ Error: No data retrieved from DataManager")
        return
    elif data.empty:
        print("❌ Error: Empty DataFrame returned from DataManager")
        return
    else:
        print("✅ Data successfully retrieved from DataManager")
        print(f"Data shape: {data.shape}")
        print("\nFirst few rows of data:")
        print(data.head())
    
    # Test display_market_data function
    print("\nTesting display_market_data function:")
    print("-" * 50)
    try:
        display_market_data(symbol)
        print("✅ display_market_data function executed without errors")
    except Exception as e:
        print(f"❌ Error in display_market_data: {str(e)}")

if __name__ == "__main__":
    test_data_display() 