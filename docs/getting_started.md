# Getting Started

This guide will help you set up and run the Trading System.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- Redis (for real-time data)
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

## Configuration

### Database Configuration

The system uses PostgreSQL for data storage. Configure the following in your `.env` file:

```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_db
```

### Alpaca API Configuration

Configure your Alpaca API credentials in the `.env` file:

```
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
```

### Redis Configuration

For real-time data processing, configure Redis:

```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## First Run

1. Start the Streamlit UI:
```bash
streamlit run src/ui/app.py
```

2. Run data collection workflows:
```bash
python src/scripts/deploy_flows.py
```

3. Access the dashboard at `http://localhost:8501`

## Next Steps

- Read the [User Guide](user_guide.md) for detailed usage instructions
- Check the [Architecture](architecture.md) documentation for system design
- Review the [API Reference](api_reference.md) for development 