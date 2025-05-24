# Archived Code

This directory contains documentation for archived code that has been replaced by newer implementations but is kept for reference.

## Contents

### Data Ingestion (`data_ingestion.py`)
- Original implementation of the Alpaca data ingestion system
- Replaced by the new `AlpacaDataSource` class in `src/data/sources/alpaca_source.py`
- Contains useful reference for error handling and retry mechanisms

### Main Application (`main.py`)
- Original main application entry point
- Contains reference implementations for:
  - Flow orchestration
  - Email notifications
  - Real-time data streaming
  - Batch processing
- Replaced by the new modular implementation in `src/scripts/`

## Migration Notes

The archived code has been replaced by more modular and maintainable implementations:

1. Data Ingestion:
   - Moved to `src/data/sources/`
   - Improved error handling
   - Better separation of concerns
   - More efficient data processing

2. Main Application:
   - Split into separate modules
   - Improved workflow management
   - Better configuration handling
   - Enhanced error reporting

## Usage

This code is kept for reference only and should not be used in production. Refer to the current implementation in the `src/` directory for the latest features and improvements. 