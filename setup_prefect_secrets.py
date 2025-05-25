from prefect.blocks.system import Secret
import os
from pathlib import Path
import yaml


def setup_prefect_secrets():
    """Set up Prefect secrets for database credentials."""
    # Load database configuration from config file
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        db_config = config['database']

    # Create Prefect secrets
    secrets = {
        "db-user": str(db_config['user']),
        "db-password": str(db_config['password']),
        "db-host": str(db_config['host']),
        "db-port": str(db_config['port']),  # Ensure port is stored as string
        "db-name": str(db_config['name'])
    }

    # Save secrets to Prefect
    for name, value in secrets.items():
        try:
            secret = Secret.load(name)
            print(f"Secret {name} already exists")
        except ValueError:
            secret = Secret(value=value)
            secret.save(name)
            print(f"Created secret {name}")


if __name__ == "__main__":
    setup_prefect_secrets()
