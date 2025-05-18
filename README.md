# Trading System

A robust trading system built with Python, featuring real-time market data collection, analysis, and automated trading capabilities.

## Features

- Real-time market data collection from Alpaca API
- Automated data storage in PostgreSQL database
- Prefect workflow orchestration for reliable data collection
- Configurable trading strategies
- Comprehensive logging and monitoring

## Project Structure

```
tradingsystem/
├── config/
│   ├── .env                 # Environment variables
│   └── config.yaml         # Configuration file
├── src/
│   ├── data/
│   │   ├── data_manager.py    # Data collection and management
│   │   ├── sources/           # Data source implementations
│   │   └── symbol_manager.py  # Symbol management
│   ├── database/
│   │   ├── db_manager.py      # Database connection management
│   │   └── models.py          # Database models
│   ├── utils/
│   │   ├── config.py          # Configuration utilities
│   │   └── logger.py          # Logging utilities
│   └── scripts/
│       └── run_data_collection.py  # Script to run data collection
├── deploy_flows.py          # Prefect flow deployment script
└── requirements.txt         # Project dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the following variables:
     ```
     DB_USER=your_db_user
     DB_PASSWORD=your_db_password
     ALPACA_API_KEY=your_alpaca_api_key
     ALPACA_SECRET_KEY=your_alpaca_secret_key
     ```

4. Initialize the database:
```bash
python src/scripts/init_db.py
```

## Running the System

### Data Collection

1. Start the Prefect server:
```bash
prefect server start
```

2. Deploy the data collection flow:
```bash
python deploy_flows.py
```

3. Start a Prefect worker:
```bash
prefect worker start -p default
```

The system will now:
- Collect market data every hour
- Store data in the PostgreSQL database
- Log all activities for monitoring

### Monitoring

- Access the Prefect UI at http://localhost:4200 to monitor flow runs
- Check the logs in the `logs` directory
- Query the database for collected data

## Development

### Adding New Symbols

Use the SymbolManager to add new symbols:
```python
from src.data.symbol_manager import SymbolManager

# Add a new symbol
SymbolManager.add_symbol("AAPL", "Apple Inc.")
```

### Running Tests

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 