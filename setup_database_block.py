from prefect_sqlalchemy import SqlAlchemyConnector
from prefect.blocks.system import Secret
import yaml
import os
from pathlib import Path

def load_config():
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_database_block():
    """Set up the SQLAlchemy connector block in Prefect."""
    try:
        # Load database configuration
        config = load_config()
        db_config = config['database']

        # Create SQLAlchemy connector block
        connector = SqlAlchemyConnector(
            connection_info={
                "driver": "postgresql",
                "username": db_config['user'],
                "password": db_config['password'],
                "host": db_config['host'],
                "port": db_config['port'],
                "database": db_config['name']
            }
        )
        
        # Save the block
        connector.save("tradingsystemdb", overwrite=True)
        print("Successfully created SQLAlchemy connector block 'tradingsystemdb'")
        
    except Exception as e:
        print(f"Error setting up database block: {e}")
        raise

if __name__ == "__main__":
    setup_database_block() 