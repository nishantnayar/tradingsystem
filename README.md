# Trading System

A comprehensive trading system with real-time market data collection and analysis capabilities.

## Features

- Real-time market data collection from Alpaca API
- Historical data storage in PostgreSQL
- Technical analysis tools and indicators
- Modern UI with Streamlit and custom navigation
- Automated data collection workflows with Prefect
- Comprehensive test suite

## Project Structure

```
tradingsystem/
├── config/                 # Configuration files
│   ├── config.yaml        # Main configuration
│   └── prefect.yaml       # Prefect workflow configuration
├── docs/                  # Documentation
├── notebooks/            # Jupyter notebooks for analysis
├── src/                  # Source code
│   ├── data/            # Data management
│   │   ├── sources/     # Data source implementations
│   │   └── models/      # Data models
│   ├── database/        # Database management
│   │   ├── migrations/  # Database migrations
│   │   └── sql/        # SQL scripts
│   ├── models/          # ML models
│   ├── scripts/         # Utility scripts
│   ├── trading/         # Trading strategies
│   ├── ui/             # User interface
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/      # Page modules
│   │   └── state/      # UI state management
│   └── utils/          # Utility functions
├── tests/               # Test suite
│   ├── test_data/      # Data tests
│   ├── test_models/    # Model tests
│   └── test_trading/   # Trading tests
├── .gitignore          # Git ignore file
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Alpaca API credentials

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tradingsystem.git
cd tradingsystem
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
cp config/.env.example config/.env
# Edit config/.env with your credentials
```

5. Initialize the database:
```bash
python src/scripts/init_db.py
```

## Usage

1. Start the Streamlit UI:
```bash
streamlit run src/ui/app.py
```

The UI provides three main sections:
- **Home**: Dashboard with market overview and real-time data
- **Analysis**: Technical analysis tools and charting capabilities
- **Settings**: System configuration and preferences

2. Run data collection workflows:
```bash
python src/scripts/deploy_flows.py
```

## Development

1. Run tests:
```bash
pytest
```

2. Check code style:
```bash
black src tests
flake8 src tests
mypy src
```

3. Sort imports:
```bash
isort src tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Alpaca API for market data
- Streamlit for the UI framework
- SQLAlchemy for database management
- Prefect for workflow orchestration
- streamlit-option-menu for enhanced navigation 