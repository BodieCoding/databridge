# Installation Guide

Complete installation instructions for DataBridge on various platforms and environments.

## System Requirements

### Minimum Requirements
- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 512 MB RAM minimum, 2 GB recommended
- **Storage**: 100 MB free space

### Database Requirements
- **SQL Server**: 2012 or higher (primary support)
- **ODBC Drivers**: Microsoft ODBC Driver 17 for SQL Server
- **Network Access**: Connection to target database server

### Python Dependencies
- `pyodbc` >= 4.0.30
- `networkx` >= 2.6
- `matplotlib` >= 3.3.0
- `pyyaml` >= 5.4.0

## Installation Methods

### Method 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/databridge.git
cd databridge

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Download ZIP

1. Download the latest release from GitHub
2. Extract to your desired directory
3. Follow the virtual environment steps above

### Method 3: Development Installation

For development and contribution:

```bash
# Clone with development branches
git clone -b develop https://github.com/your-org/databridge.git
cd databridge

# Create development environment
python -m venv .venv-dev
.venv-dev\Scripts\activate  # Windows
# source .venv-dev/bin/activate  # macOS/Linux

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt
```

## Database Driver Installation

### Windows

#### SQL Server ODBC Driver

1. **Download Microsoft ODBC Driver 17 for SQL Server**:
   - Visit [Microsoft Downloads](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
   - Download the appropriate version (x64/x86)

2. **Install the Driver**:
   ```cmd
   # Run as Administrator
   msodbcsql.msi /quiet /passive
   ```

3. **Verify Installation**:
   ```cmd
   # Check available drivers
   odbcad32.exe
   ```

#### Alternative: SQL Server Native Client

```cmd
# For older SQL Server versions
# Download SQL Server Native Client from Microsoft
sqlncli.msi /quiet
```

### macOS

#### Using Homebrew

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install unixODBC and Microsoft ODBC Driver
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools
```

#### Manual Installation

```bash
# Download and install manually
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg

# Add Microsoft repository
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list

# Install driver
sudo apt-get update
sudo apt-get install msodbcsql17
```

### Linux (Ubuntu/Debian)

```bash
# Add Microsoft repository
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list

# Update package list
sudo apt-get update

# Install ODBC driver
sudo ACCEPT_EULA=Y apt-get install msodbcsql17

# Install unixODBC development headers
sudo apt-get install unixodbc-dev
```

### Linux (CentOS/RHEL)

```bash
# Add Microsoft repository
sudo curl -o /etc/yum.repos.d/msprod.repo https://packages.microsoft.com/config/rhel/8/prod.repo

# Install ODBC driver
sudo ACCEPT_EULA=Y yum install msodbcsql17

# Install unixODBC development headers
sudo yum install unixODBC-devel
```

## Configuration

### Database Connection

Create `config.yaml` in the project root:

```yaml
# Database Configuration
source_database:
  connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=mydb;UID=myuser;PWD=mypassword"
  schema: "dbo"
  timeout: 30

# Logging Configuration
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/databridge.log"

# Schema Discovery Settings
schema_discovery:
  include_system_tables: false
  max_table_count: 1000
  default_relationship_sources:
    - database_foreign_keys
    
# Export Settings
export:
  default_format: yaml
  output_directory: "output"
  include_metadata: true
  timestamp_files: true
```

### Environment Variables

For secure credential management:

```bash
# Windows
set DB_SERVER=localhost
set DB_DATABASE=mydb
set DB_USERNAME=myuser
set DB_PASSWORD=mypassword

# macOS/Linux
export DB_SERVER=localhost
export DB_DATABASE=mydb
export DB_USERNAME=myuser
export DB_PASSWORD=mypassword
```

Update `config.yaml` to use environment variables:

```yaml
source_database:
  connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=${DB_SERVER};DATABASE=${DB_DATABASE};UID=${DB_USERNAME};PWD=${DB_PASSWORD}"
```

### Directory Structure

Ensure the following directories exist:

```bash
# Create required directories
mkdir -p data output logs

# Set permissions (macOS/Linux)
chmod 755 data output logs
```

## Verification

### Test Installation

Create `test_installation.py`:

```python
#!/usr/bin/env python
"""Test DataBridge installation."""

import sys
import os

def test_imports():
    """Test all required imports."""
    try:
        import pyodbc
        print("✓ pyodbc imported successfully")
    except ImportError as e:
        print(f"✗ pyodbc import failed: {e}")
        return False
        
    try:
        import networkx
        print("✓ networkx imported successfully")
    except ImportError as e:
        print(f"✗ networkx import failed: {e}")
        return False
        
    try:
        import matplotlib
        print("✓ matplotlib imported successfully")
    except ImportError as e:
        print(f"✗ matplotlib import failed: {e}")
        return False
        
    try:
        import yaml
        print("✓ pyyaml imported successfully")
    except ImportError as e:
        print(f"✗ pyyaml import failed: {e}")
        return False
        
    return True

def test_databridge():
    """Test DataBridge import."""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from database.datamodel_service import DataBridge
        print("✓ DataBridge imported successfully")
        
        # Test basic instantiation
        bridge = DataBridge()
        print("✓ DataBridge instance created successfully")
        return True
    except ImportError as e:
        print(f"✗ DataBridge import failed: {e}")
        return False

def test_odbc_drivers():
    """Test ODBC driver availability."""
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        print(f"✓ Available ODBC drivers: {len(drivers)}")
        
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_server_drivers:
            print(f"✓ SQL Server drivers found: {sql_server_drivers}")
            return True
        else:
            print("✗ No SQL Server ODBC drivers found")
            return False
    except Exception as e:
        print(f"✗ ODBC driver test failed: {e}")
        return False

def main():
    """Run all installation tests."""
    print("DataBridge Installation Test")
    print("=" * 40)
    
    tests = [
        ("Python Imports", test_imports),
        ("DataBridge Import", test_databridge),
        ("ODBC Drivers", test_odbc_drivers),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n{name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ Installation verification successful!")
        return 0
    else:
        print("✗ Installation verification failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Run the test:

```bash
python test_installation.py
```

### Test Database Connection

Create `test_connection.py`:

```python
#!/usr/bin/env python
"""Test database connection."""

import sys
import os
import pyodbc

def test_connection():
    """Test database connection."""
    # Update with your database details
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=mydb;"
        "UID=myuser;"
        "PWD=mypassword;"
    )
    
    try:
        # Test connection
        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✓ Connected to SQL Server: {version[:50]}...")
        
        # Test schema access
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES")
        table_count = cursor.fetchone()[0]
        print(f"✓ Found {table_count} tables in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Database Connection Test")
    print("=" * 30)
    success = test_connection()
    sys.exit(0 if success else 1)
```

## Troubleshooting

### Common Issues

#### "No module named 'pyodbc'"

**Solution:**
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Reinstall pyodbc
pip uninstall pyodbc
pip install pyodbc
```

#### "Data source name not found"

**Solution:**
- Verify ODBC driver installation
- Check driver name in connection string
- Use `odbcad32.exe` (Windows) to verify drivers

#### "Login failed for user"

**Solution:**
- Verify username and password
- Check SQL Server authentication mode
- Ensure user has database access permissions

#### "Connection timeout expired"

**Solution:**
- Check network connectivity
- Verify server name and port
- Increase timeout in connection string:
  ```python
  conn_str += "Connection Timeout=60;"
  ```

#### Import errors on Linux

**Solution:**
```bash
# Install development headers
sudo apt-get install python3-dev
sudo apt-get install unixodbc-dev

# Reinstall pyodbc
pip uninstall pyodbc
pip install --no-cache-dir pyodbc
```

### Platform-Specific Issues

#### Windows: "Microsoft Visual C++ 14.0 is required"

**Solution:**
1. Install Microsoft C++ Build Tools
2. Or install Visual Studio Community
3. Or use pre-compiled wheels:
   ```bash
   pip install --only-binary=all pyodbc
   ```

#### macOS: "Library not loaded: libiodbc"

**Solution:**
```bash
# Install via Homebrew
brew install unixodbc

# Or use conda
conda install unixodbc
```

#### Linux: "Symbol lookup error"

**Solution:**
```bash
# Update library links
sudo ldconfig

# Install missing libraries
sudo apt-get install libc6-dev
```

## Performance Optimization

### Virtual Environment

Use virtual environments to avoid dependency conflicts:

```bash
# Create optimized environment
python -m venv .venv --system-site-packages
.venv\Scripts\activate

# Install only required packages
pip install --no-deps -r requirements.txt
```

### Database Connection Pooling

For high-performance scenarios:

```python
# connection_pool.py
import pyodbc
from threading import Lock

class ConnectionPool:
    def __init__(self, connection_string, pool_size=5):
        self.connection_string = connection_string
        self.pool = []
        self.lock = Lock()
        
        # Pre-create connections
        for _ in range(pool_size):
            conn = pyodbc.connect(connection_string)
            self.pool.append(conn)
    
    def get_connection(self):
        with self.lock:
            if self.pool:
                return self.pool.pop()
            else:
                return pyodbc.connect(self.connection_string)
    
    def return_connection(self, conn):
        with self.lock:
            self.pool.append(conn)
```

## Next Steps

After successful installation:

1. **Quick Start**: Follow the [Quick Start Guide](quick-start.md)
2. **Configuration**: Review [Configuration Guide](configuration.md)
3. **Examples**: Explore the [examples directory](../examples/)
4. **Documentation**: Read the [User Guide](user-guide.md)

## Support

For installation issues:

- **Documentation**: Check [Troubleshooting Guide](troubleshooting.md)
- **GitHub Issues**: [Report installation problems](https://github.com/your-org/databridge/issues)
- **Community**: Join discussions in GitHub Discussions

---

**Installation complete!** You're ready to start using DataBridge for database schema analysis.
