#!/usr/bin/env python
"""
DataBridge SQL Server Docker Setup Script

This script automates setting up a SQL Server Docker container and initializing it with
the project's database schema. It supports both regular Docker for development use and
TestContainers for automated testing.

Usage:
    python setup_sqlserver.py [--test-container] [--sa-password PASSWORD]

Options:
    --test-container    Use TestContainers instead of regular Docker (useful for tests)
    --sa-password       Set a custom SA password (default: DataBridge2025!)
    --detached          Run container in detached mode (default for regular Docker)
    --port PORT         Specify custom port (default: 1433)
    --help              Show this help message

Requirements:
    - Docker must be installed and running
    - For test containers: pip install testcontainers
"""
import os
import sys
import time
import argparse
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("databridge_docker_setup")

# Default settings
DEFAULT_PASSWORD = "DataBridge2025!"
DEFAULT_PORT = 1433
CONTAINER_NAME = "databridge-sqlserver"
SQL_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pocdb.sql")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Set up SQL Server in Docker for DataBridge")
    parser.add_argument("--test-container", action="store_true", 
                        help="Use TestContainers instead of regular Docker")
    parser.add_argument("--sa-password", default=DEFAULT_PASSWORD,
                        help=f"SA password for SQL Server (default: {DEFAULT_PASSWORD})")
    parser.add_argument("--detached", action="store_true",
                        help="Run container in detached mode")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"Port to expose SQL Server on (default: {DEFAULT_PORT})")
    return parser.parse_args()

def check_docker_installed():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(
            ["docker", "info"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode != 0:
            logger.error("Docker is not running or not accessible.")
            logger.error(result.stderr)
            return False
        return True
    except FileNotFoundError:
        logger.error("Docker is not installed or not in PATH.")
        return False

def setup_with_docker(args):
    """Set up SQL Server using regular Docker."""
    # Check if container already exists
    container_check = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    
    if CONTAINER_NAME in container_check.stdout:
        logger.info(f"Container {CONTAINER_NAME} already exists. Removing it...")
        subprocess.run(["docker", "rm", "-f", CONTAINER_NAME], check=True)
    
    # Create and start the container
    logger.info(f"Creating SQL Server container with name: {CONTAINER_NAME}")
    cmd = [
        "docker", "run",
        "--name", CONTAINER_NAME,
        "-e", f"ACCEPT_EULA=Y",
        "-e", f"SA_PASSWORD={args.sa_password}",
        "-p", f"{args.port}:1433",
    ]
    
    if args.detached:
        cmd.append("-d")
    
    cmd.append("mcr.microsoft.com/mssql/server:2019-latest")
    
    subprocess.run(cmd, check=True)
    logger.info("SQL Server container started")
    
    # Wait for SQL Server to be ready
    if args.detached:
        logger.info("Waiting for SQL Server to start...")
        time.sleep(20)  # Simple wait for SQL Server to initialize
    
    # Copy and execute SQL script
    logger.info(f"Copying SQL script to container...")
    subprocess.run([
        "docker", "cp", 
        SQL_SCRIPT_PATH, 
        f"{CONTAINER_NAME}:/pocdb.sql"
    ], check=True)
    
    logger.info("Executing SQL script...")
    subprocess.run([
        "docker", "exec", 
        "-it", CONTAINER_NAME,
        "/opt/mssql-tools/bin/sqlcmd", 
        "-S", "localhost",
        "-U", "sa",
        "-P", args.sa_password,
        "-i", "/pocdb.sql"
    ], check=True)
    
    logger.info(f"""
SQL Server container is ready!
Connection details:
  - Server: localhost,{args.port}
  - Username: sa
  - Password: {args.sa_password}
  - Database: pocdb
""")

def setup_with_testcontainers(args):
    """Set up SQL Server using TestContainers."""
    try:
        from testcontainers.mssql import SqlServerContainer
    except ImportError:
        logger.error("TestContainers not installed. Run: pip install testcontainers")
        sys.exit(1)
    
    logger.info("Starting SQL Server using TestContainers...")
    
    # Create SQL Server container
    container = SqlServerContainer(
        "mcr.microsoft.com/mssql/server:2019-latest",
        password=args.sa_password
    )
    
    # Start the container
    container.start()
    
    # Get connection details
    connection_url = container.get_connection_url()
    logger.info(f"Container started with connection URL: {connection_url}")
    
    # Execute SQL script using sqlcmd inside the container
    container_id = container.get_container_id()
    
    logger.info(f"Copying SQL script to container...")
    subprocess.run([
        "docker", "cp", 
        SQL_SCRIPT_PATH, 
        f"{container_id}:/pocdb.sql"
    ], check=True)
    
    logger.info("Executing SQL script...")
    subprocess.run([
        "docker", "exec", 
        "-it", container_id,
        "/opt/mssql-tools/bin/sqlcmd", 
        "-S", "localhost",
        "-U", "sa",
        "-P", args.sa_password,
        "-i", "/pocdb.sql"
    ], check=True)
    
    logger.info(f"""
TestContainer SQL Server is ready!
Connection details:
  - Connection URL: {connection_url}
  - Database: pocdb
  - Container ID: {container_id}

Note: This container will be automatically removed when the script exits.
To keep it running, press Ctrl+C now and the container will remain active.
""")
    
    try:
        # Keep the script running to maintain the container
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nKeyboard interrupt received. Container will remain running.")
        logger.info(f"To stop it manually, use: docker stop {container_id}")
        logger.info(f"To remove it, use: docker rm {container_id}")
        sys.exit(0)
    finally:
        # Cleanup on script exit
        container.stop()

def main():
    """Main function."""
    args = parse_arguments()
    
    # Validate SQL script exists
    if not os.path.exists(SQL_SCRIPT_PATH):
        logger.error(f"SQL script not found at: {SQL_SCRIPT_PATH}")
        sys.exit(1)
    
    # Check Docker installation
    if not check_docker_installed():
        sys.exit(1)
    
    # Set default detached mode for regular Docker
    if not args.test_container and not args.detached:
        args.detached = True
    
    try:
        if args.test_container:
            setup_with_testcontainers(args)
        else:
            setup_with_docker(args)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
