# Trading System

A comprehensive algorithmic trading system built with Python, featuring machine learning models, real-time data processing, and an interactive dashboard.

## Features

- Real-time market data processing
- Machine learning-based trading strategies
- Portfolio management and risk control
- Interactive Streamlit dashboard
- PostgreSQL database integration
- Comprehensive backtesting framework

## Project Structure

```
trading_system/
├── src/               # Source code
│   ├── data/         # Data processing modules
│   ├── models/       # ML models and strategies
│   ├── trading/      # Trading logic
│   ├── database/     # Database operations
│   └── utils/        # Utility functions
├── tests/            # Test suite
├── config/           # Configuration files
├── docs/             # Documentation
└── notebooks/        # Jupyter notebooks
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd trading_system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
- Create a database named 'trading_system'
- Update the database credentials in config/config.yaml

5. Create .env file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

6. Run tests:
```bash
pytest
```

## Usage

1. Start the Streamlit dashboard:
```bash
streamlit run src/app.py
```

2. Access the dashboard at http://localhost:8501

## Development

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed
- Use type hints and docstrings

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 