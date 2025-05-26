from prefect.blocks.system import Secret

Secret(value="postgres").save("db-user", overwrite=True)
Secret(value="nishant").save("db-password", overwrite=True)
Secret(value="localhost").save("db-host", overwrite=True)
Secret(value="trading_system").save("db-name", overwrite=True)

# Add Alpaca API credentials
Secret(value="PKHNBUL9IZIAH53NWNPS").save("alpaca-api-key", overwrite=True)
Secret(value="aeXOKKJbgkOnEydQ5EXdrKsqyYJV3b8SDHXJfcfI").save("alpaca-secret-key", overwrite=True)

db_user = Secret.load("alpaca-api-key").get()
print(f"alpaca-api-key: {db_user}")
