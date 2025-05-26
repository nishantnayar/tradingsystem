from prefect.blocks.system import Secret

Secret(value="postgres").save("db-user", overwrite=True)
Secret(value="nishant").save("db-password", overwrite=True)
Secret(value="localhost").save("db-host", overwrite=True)
Secret(value="trading_system").save("db-name", overwrite=True)
