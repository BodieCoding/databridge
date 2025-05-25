#!/bin/bash
# DataBridge SQL Server Setup Helper
# This script runs the setup_sqlserver.py script with default settings

echo "DataBridge SQL Server Setup"
echo "==========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed or not in PATH"
    echo "Please install Python 3.6 or higher"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed or not in PATH"
    echo "Please install Docker and make sure it's running"
    exit 1
fi

echo "Starting SQL Server setup..."
python3 setup_sqlserver.py "$@"

if [ $? -ne 0 ]; then
    echo "Setup failed"
    exit 1
fi

echo "Setup completed successfully!"
echo "You can now connect to the database using:"
echo "  Server: localhost,1433"
echo "  Username: sa"
echo "  Password: DataBridge2025! (unless you specified a different one)"
echo "  Database: pocdb"
