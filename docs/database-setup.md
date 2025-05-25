# DataBridge SQL Server Setup Guide

This guide provides instructions for setting up a SQL Server instance for use with DataBridge. Choose the method that works best for your situation.

## Prerequisites

- Docker installed and running
- Python 3.6+ (for the setup script)

## Option 1: Using the Setup Script

The setup script provides a quick way to create a SQL Server container and initialize it with the project's database schema.

### Basic Usage

```bash
python setup_sqlserver.py
```

This will:
1. Pull the SQL Server 2019 Docker image (if not already downloaded)
2. Create and start a container named `databridge-sqlserver`
3. Load the database schema from `data/pocdb.sql`

### Advanced Options

```bash
# Run with custom SA password
python setup_sqlserver.py --sa-password YourStrongPassword123!

# Run on a different port
python setup_sqlserver.py --port 1434

# Run in interactive mode (container stops when script exits)
python setup_sqlserver.py --detached false

# Use TestContainers (useful for automated tests)
python setup_sqlserver.py --test-container
```

## Option 2: Using Docker Compose

If you prefer Docker Compose, we provide a `docker-compose.yml` file.

```bash
# Start the containers
docker compose up -d

# To stop the containers
docker compose down
```

The Docker Compose file:
- Creates a SQL Server container
- Automatically initializes the database with the schema
- Configures appropriate health checks

## Connection Details

Regardless of which method you choose, you can connect to the database using:

- **Server**: localhost,1433
- **Username**: sa
- **Password**: DataBridge2025! (unless you specified a different one)
- **Database**: pocdb

## For Development

For local development, you can use the connection string:

```
DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=pocdb;UID=sa;PWD=DataBridge2025!
```

## For Testing

When using the `--test-container` option, the database will be automatically created and destroyed as part of your test runs, ensuring a clean environment for each test.

Add this to your test code:

```python
from testcontainers.mssql import SqlServerContainer

# Create and start container
sql_container = SqlServerContainer("mcr.microsoft.com/mssql/server:2019-latest")
sql_container.start()

# Get connection URL
connection_url = sql_container.get_connection_url()

# Initialize database
# (code to execute SQL script)

# Use the database in your tests
# ...

# Clean up
sql_container.stop()
```

## Troubleshooting

### SQL Server container won't start

Check if you have another service running on port 1433:
```bash
# On Windows
netstat -ano | findstr :1433

# On Linux/macOS
netstat -tuln | grep 1433
```

### "Login failed" errors

Make sure you're using the correct credentials:
```bash
# Test connection
docker exec -it databridge-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P DataBridge2025!
```
