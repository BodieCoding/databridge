# Configuration Guide

Comprehensive guide to configuring DataBridge for your environment and use cases.

## Configuration Overview

DataBridge uses a layered configuration approach:

1. **Default Configuration**: Built-in sensible defaults
2. **Configuration File**: `config.yaml` for persistent settings
3. **Environment Variables**: For sensitive data and deployment
4. **Runtime Parameters**: Programmatic configuration

## Configuration File

### Basic Configuration

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
  
# Schema Discovery Settings
schema_discovery:
  include_system_tables: false
  max_table_count: 1000
  
# Export Settings
export:
  default_format: yaml
  output_directory: "output"
```

### Complete Configuration Reference

```yaml
# =================================
# DATABASE CONFIGURATION
# =================================
source_database:
  # Connection string for the source database
  connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=mydb;UID=myuser;PWD=mypassword"
  
  # Default schema to analyze
  schema: "dbo"
  
  # Connection timeout in seconds
  timeout: 30
  
  # Connection pool settings
  pool_size: 5
  pool_timeout: 60
  
  # Retry settings
  max_retries: 3
  retry_delay: 5

# =================================
# LOGGING CONFIGURATION
# =================================
logging:
  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  level: INFO
  
  # Log message format
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # Log file settings
  file:
    enabled: true
    path: "logs/databridge.log"
    max_size: 10485760  # 10 MB
    backup_count: 5
    rotation: true
  
  # Console logging
  console:
    enabled: true
    level: INFO

# =================================
# SCHEMA DISCOVERY SETTINGS
# =================================
schema_discovery:
  # Include system/built-in tables
  include_system_tables: false
  
  # Maximum number of tables to process
  max_table_count: 1000
  
  # Default relationship sources to include
  default_relationship_sources:
    - database_foreign_keys
    - csv_files
  
  # Schema extraction options
  extraction:
    include_indexes: true
    include_constraints: true
    include_triggers: false
    include_views: false
    include_procedures: false
  
  # Filtering defaults
  filtering:
    exclude_patterns:
      - "^sys.*"
      - "^temp.*"
      - ".*_backup$"
    exclude_schemas:
      - "information_schema"
      - "sys"

# =================================
# RELATIONSHIP CONFIGURATION
# =================================
relationships:
  # CSV relationship files
  csv_files:
    default_path: "data/relationships.csv"
    encoding: "utf-8"
    delimiter: ","
  
  # XML relationship files
  xml_files:
    default_path: "data/relationships.xml"
    encoding: "utf-8"
  
  # Database foreign key extraction
  database_foreign_keys:
    enabled: true
    cross_schema: false

# =================================
# QUERY GENERATION SETTINGS
# =================================
query_generation:
  # Default query options
  defaults:
    include_joins: true
    optimize_with_indexes: true
    table_alias_prefix: "T"
  
  # Query optimization
  optimization:
    enabled: true
    analyze_indexes: true
    suggest_improvements: true
    max_join_tables: 10
  
  # SQL formatting
  formatting:
    style: "readable"  # readable, compact, minimal
    indent_size: 2
    keyword_case: "upper"  # upper, lower, title

# =================================
# EXPORT CONFIGURATION
# =================================
export:
  # Default export format
  default_format: yaml
  
  # Output directory
  output_directory: "output"
  
  # File naming
  file_naming:
    include_timestamp: true
    timestamp_format: "%Y%m%d_%H%M%S"
    prefix: "schema"
  
  # Export options
  options:
    include_metadata: true
    include_statistics: true
    pretty_print: true
  
  # Format-specific settings
  yaml:
    default_flow_style: false
    indent: 2
    width: 120
  
  xml:
    encoding: "utf-8"
    indent: "  "
    root_element: "schema"
  
  json:
    indent: 2
    sort_keys: true
    ensure_ascii: false

# =================================
# VISUALIZATION SETTINGS
# =================================
visualization:
  # Graph layout settings
  layout:
    default_algorithm: "spring"
    node_size: 1000
    font_size: 8
    figure_size: [12, 8]
  
  # Color scheme
  colors:
    node_color: "lightblue"
    edge_color: "gray"
    text_color: "black"
  
  # Output settings
  output:
    format: "png"
    dpi: 300
    transparent: false

# =================================
# PERFORMANCE SETTINGS
# =================================
performance:
  # Caching
  cache:
    enabled: true
    ttl: 3600  # 1 hour
    max_size: 100
  
  # Parallel processing
  parallel:
    enabled: true
    max_workers: 4
  
  # Memory management
  memory:
    max_table_size: 1000000  # rows
    chunk_size: 10000

# =================================
# SECURITY SETTINGS
# =================================
security:
  # Credential handling
  credentials:
    encrypt_in_memory: true
    clear_after_use: true
  
  # Data filtering
  data_filtering:
    exclude_sensitive_columns: true
    sensitive_patterns:
      - ".*password.*"
      - ".*ssn.*"
      - ".*credit.*"

# =================================
# DEVELOPMENT SETTINGS
# =================================
development:
  # Debug options
  debug:
    enabled: false
    verbose_sql: false
    save_intermediate_results: false
  
  # Testing
  testing:
    use_mock_data: false
    mock_data_path: "tests/mock_data"
```

## Environment Variables

### Database Credentials

For secure credential management:

```bash
# Windows
set DB_SERVER=myserver.database.windows.net
set DB_DATABASE=mydatabase
set DB_USERNAME=myuser
set DB_PASSWORD=mypassword
set DB_DRIVER=ODBC Driver 17 for SQL Server

# macOS/Linux
export DB_SERVER=myserver.database.windows.net
export DB_DATABASE=mydatabase
export DB_USERNAME=myuser
export DB_PASSWORD=mypassword
export DB_DRIVER="ODBC Driver 17 for SQL Server"
```

### Configuration Override

```bash
# Override configuration file path
export DATABRIDGE_CONFIG_PATH="/path/to/custom/config.yaml"

# Override log level
export DATABRIDGE_LOG_LEVEL=DEBUG

# Override output directory
export DATABRIDGE_OUTPUT_DIR="/custom/output/path"
```

### Environment-Based Connection String

Update `config.yaml` to use environment variables:

```yaml
source_database:
  connection_string: "DRIVER={${DB_DRIVER}};SERVER=${DB_SERVER};DATABASE=${DB_DATABASE};UID=${DB_USERNAME};PWD=${DB_PASSWORD}"
```

## Environment-Specific Configurations

### Development Environment

`config-dev.yaml`:
```yaml
source_database:
  connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=dev_db;UID=dev_user;PWD=dev_pass"
  timeout: 10

logging:
  level: DEBUG
  console:
    enabled: true
    level: DEBUG

development:
  debug:
    enabled: true
    verbose_sql: true
    save_intermediate_results: true

performance:
  cache:
    enabled: false
```

### Testing Environment

`config-test.yaml`:
```yaml
source_database:
  connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=test-server;DATABASE=test_db;UID=test_user;PWD=test_pass"

schema_discovery:
  max_table_count: 100

development:
  testing:
    use_mock_data: true
    mock_data_path: "tests/mock_data"

export:
  output_directory: "test_output"
```

### Production Environment

`config-prod.yaml`:
```yaml
source_database:
  connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=${PROD_SERVER};DATABASE=${PROD_DATABASE};UID=${PROD_USERNAME};PWD=${PROD_PASSWORD}"
  timeout: 60
  pool_size: 10

logging:
  level: INFO
  file:
    enabled: true
    path: "/var/log/databridge/databridge.log"
  console:
    enabled: false

performance:
  cache:
    enabled: true
    ttl: 7200  # 2 hours
  parallel:
    enabled: true
    max_workers: 8

security:
  credentials:
    encrypt_in_memory: true
    clear_after_use: true
```

## Runtime Configuration

### Programmatic Configuration

```python
from src.database.datamodel_service import DataBridge
import logging

# Configure logging programmatically
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize with custom settings
bridge = DataBridge(
    db_conn=None,  # Will use config file connection
    logger=logging.getLogger('databridge'),
    config_path='config-prod.yaml'
)

# Override specific settings
bridge.configure({
    'schema_discovery': {
        'max_table_count': 500
    },
    'export': {
        'default_format': 'json'
    }
})
```

### Dynamic Configuration

```python
# Load configuration from different sources
def load_config():
    config = {}
    
    # 1. Load base configuration
    if os.path.exists('config.yaml'):
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    
    # 2. Override with environment-specific config
    env = os.getenv('ENVIRONMENT', 'dev')
    env_config_path = f'config-{env}.yaml'
    if os.path.exists(env_config_path):
        with open(env_config_path, 'r') as f:
            env_config = yaml.safe_load(f)
            config.update(env_config)
    
    # 3. Override with environment variables
    if os.getenv('DB_SERVER'):
        config.setdefault('source_database', {})
        config['source_database']['server'] = os.getenv('DB_SERVER')
    
    return config

# Use dynamic configuration
config = load_config()
bridge = DataBridge(config=config)
```

## Configuration Validation

### Validation Script

Create `validate_config.py`:

```python
#!/usr/bin/env python
"""Validate DataBridge configuration."""

import yaml
import os
import sys
from typing import Dict, Any

def validate_database_config(config: Dict[str, Any]) -> bool:
    """Validate database configuration."""
    db_config = config.get('source_database', {})
    
    required_fields = ['connection_string']
    for field in required_fields:
        if field not in db_config:
            print(f"✗ Missing required database field: {field}")
            return False
    
    # Validate connection string format
    conn_str = db_config['connection_string']
    if 'DRIVER=' not in conn_str or 'SERVER=' not in conn_str:
        print("✗ Invalid connection string format")
        return False
    
    print("✓ Database configuration valid")
    return True

def validate_logging_config(config: Dict[str, Any]) -> bool:
    """Validate logging configuration."""
    log_config = config.get('logging', {})
    
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    level = log_config.get('level', 'INFO')
    
    if level not in valid_levels:
        print(f"✗ Invalid log level: {level}")
        return False
    
    print("✓ Logging configuration valid")
    return True

def validate_export_config(config: Dict[str, Any]) -> bool:
    """Validate export configuration."""
    export_config = config.get('export', {})
    
    valid_formats = ['yaml', 'xml', 'json']
    default_format = export_config.get('default_format', 'yaml')
    
    if default_format not in valid_formats:
        print(f"✗ Invalid export format: {default_format}")
        return False
    
    # Check output directory
    output_dir = export_config.get('output_directory', 'output')
    if not os.path.exists(output_dir):
        print(f"! Output directory does not exist: {output_dir}")
        print("  Will be created automatically")
    
    print("✓ Export configuration valid")
    return True

def validate_config_file(config_path: str) -> bool:
    """Validate entire configuration file."""
    if not os.path.exists(config_path):
        print(f"✗ Configuration file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"✗ Invalid YAML format: {e}")
        return False
    
    validators = [
        validate_database_config,
        validate_logging_config,
        validate_export_config,
    ]
    
    all_valid = True
    for validator in validators:
        if not validator(config):
            all_valid = False
    
    return all_valid

def main():
    """Main validation function."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.yaml'
    
    print(f"Validating configuration: {config_path}")
    print("=" * 50)
    
    if validate_config_file(config_path):
        print("\n✓ Configuration validation successful!")
        return 0
    else:
        print("\n✗ Configuration validation failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Run validation:
```bash
python validate_config.py config.yaml
```

## Common Configuration Patterns

### Multi-Database Setup

```yaml
# Multiple database configurations
databases:
  production:
    connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=prod-server;DATABASE=prod_db;UID=${PROD_USER};PWD=${PROD_PASS}"
    schema: "dbo"
  
  staging:
    connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=stage-server;DATABASE=stage_db;UID=${STAGE_USER};PWD=${STAGE_PASS}"
    schema: "dbo"
  
  development:
    connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=dev_db;UID=dev_user;PWD=dev_pass"
    schema: "dbo"

# Select active database
active_database: production
```

### Business Domain Configuration

```yaml
# Business-specific filtering
business_domains:
  customer_domain:
    tables:
      - "customer.*"
      - "contact.*"
      - "address.*"
    relationships:
      - "data/customer_relationships.csv"
  
  order_domain:
    tables:
      - "order.*"
      - "product.*"
      - "inventory.*"
    relationships:
      - "data/order_relationships.csv"

# Active domain
active_domain: customer_domain
```

### Team-Based Configuration

```yaml
# Team-specific settings
teams:
  data_team:
    schema_discovery:
      include_system_tables: true
      max_table_count: 2000
    export:
      formats: ["yaml", "json", "xml"]
  
  dev_team:
    schema_discovery:
      max_table_count: 100
    export:
      formats: ["json"]
  
  analysts:
    visualization:
      enabled: true
      layout:
        node_size: 1500
    export:
      include_statistics: true

# Active team profile
active_team: data_team
```

## Configuration Best Practices

### Security

1. **Never commit passwords**:
   ```yaml
   # Use environment variables
   source_database:
     connection_string: "...;PWD=${DB_PASSWORD}"
   ```

2. **Use encrypted configuration**:
   ```bash
   # Encrypt sensitive config files
   gpg --symmetric --cipher-algo AES256 config-prod.yaml
   ```

3. **Separate sensitive data**:
   ```yaml
   # config.yaml (safe to commit)
   source_database:
     server: "prod-server"
     database: "prod_db"
   
   # secrets.yaml (never commit)
   credentials:
     username: "prod_user"
     password: "prod_password"
   ```

### Maintainability

1. **Use inheritance**:
   ```yaml
   # base-config.yaml
   logging: &default_logging
     level: INFO
     format: "%(asctime)s - %(levelname)s - %(message)s"
   
   # config-dev.yaml
   logging:
     <<: *default_logging
     level: DEBUG
   ```

2. **Document configuration**:
   ```yaml
   # Database connection settings
   source_database:
     # Primary production database
     connection_string: "..."
     # Connection timeout in seconds
     timeout: 30
   ```

3. **Validate on startup**:
   ```python
   def validate_config_on_startup():
       config = load_config()
       if not validate_config(config):
           raise ConfigurationError("Invalid configuration")
   ```

## Troubleshooting Configuration

### Common Issues

#### "Configuration file not found"
```bash
# Check file exists
ls -la config.yaml

# Use absolute path
export DATABRIDGE_CONFIG_PATH="/absolute/path/to/config.yaml"
```

#### "Invalid YAML syntax"
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

#### "Environment variable not found"
```bash
# Check environment variables are set
echo $DB_PASSWORD

# Use default values in config
connection_string: "...;PWD=${DB_PASSWORD:-default_password}"
```

#### "Permission denied on log file"
```bash
# Check log directory permissions
ls -la logs/

# Create with correct permissions
mkdir -p logs
chmod 755 logs
```

---

This configuration guide covers all aspects of configuring DataBridge for your environment. For specific deployment scenarios, see the [Installation Guide](installation.md) and [Performance Guide](performance.md).
