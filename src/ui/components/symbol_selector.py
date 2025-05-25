import streamlit as st
from loguru import logger

from src.data.symbol_manager import SymbolManager


def display_symbol_selector() -> str:
    """Display symbol selector component.
    
    Returns:
        str: Selected symbol or None if no selection
    """
    try:
        # Get active symbols
        symbols = SymbolManager.get_active_symbols()
        
        if not symbols:
            st.warning("No active symbols found")
            return None
            
        # Create symbol selector
        selected_symbol = st.selectbox(
            "Select a Symbol",
            options=symbols,
            index=0 if symbols else None
        )
        
        return selected_symbol
        
    except Exception as e:
        logger.error(f"Error in symbol selector: {e}")
        st.error("Error loading symbols. Please try again later.")
        return None 