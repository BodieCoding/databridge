# Quick Start Guide

Get started with DataBridge in minutes. This guide will have you analyzing database schemas and generating optimized queries quickly.

## Prerequisites

- Python 3.7+
- SQL Server database access
- ODBC drivers installed

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/databridge.git
cd databridge

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Database Connection

Create or update `config.yaml`:

```yaml
source_database:
  connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=mydb;UID=user;PWD=pass"
  schema: "dbo"

logging:
  level: INFO
```

## First Steps

### 1. Basic Schema Discovery

```python
from src.database.datamodel_service import DataBridge
import pyodbc

# Initialize connection
conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=mydb;UID=user;PWD=pass"
db_conn = pyodbc.connect(conn_str)

# Create DataBridge instance
bridge = DataBridge(db_conn)

# Discover schema
schema = (bridge.discover_schema()
         .from_database()
         .build())

print(f"Discovered {len(schema.tables)} tables")
```

### 2. Advanced Schema Discovery with Filtering

```python
# Focus on specific tables
schema = (bridge.discover_schema()
         .from_database()
         .only_tables(['users', 'orders', 'products'])
         .with_relationships_from_database()
         .build())

# Pattern-based filtering
schema = (bridge.discover_schema()
         .from_database()
         .matching_pattern(r'^customer.*')
         .excluding_pattern(r'.*_temp$')
         .build())
```

### 3. Generate Optimized Queries

```python
# Basic query generation
result = (bridge.generate_query()
         .select_all()
         .where({'users': ['user_id']})
         .with_joins()
         .build())

print("Generated SQL:", result['query'])
```

### 4. Export Schema to Multiple Formats

```python
# Create output directory
import os
os.makedirs('output', exist_ok=True)

# Export to multiple formats
bridge.export_schema().to_yaml('output/schema.yaml')
bridge.export_schema().to_xml('output/schema.xml')
bridge.export_schema().to_json('output/schema.json')
```

## Common Patterns

### Business Domain Focus

```python
# Analyze only loan-related tables
loan_schema = (bridge.discover_schema()
              .from_database()
              .matching_pattern(r'^loan_.*')
              .with_relationships_from_csv('data/loan_relationships.csv')
              .build())
```

### Performance Analysis

```python
# Generate query with optimization
result = (bridge.generate_query()
         .select_all()
         .where({'orders': ['customer_id', 'order_date']})
         .optimize_with_indexes()
         .build())

print("Optimization suggestions:", result['index_recommendations'])
```

### Relationship Visualization

```python
# Create relationship DAG
dag_info = bridge.relationship_manager.create_dag(schema.tables)

# Generate visualization
bridge.relationship_manager.visualize_dag(
    dag_info['dag'], 
    'output/relationships.png'
)
```

## Example Outputs

### Schema YAML
```yaml
tables:
  users:
    columns:
      user_id:
        type: int
        nullable: false
        primary_key: true
      email:
        type: varchar
        max_length: 255
    relationships:
      - target_table: orders
        relationship_type: one-to-many
```

### Generated SQL
```sql
SELECT 
    T1.user_id,
    T1.email,
    T2.order_id,
    T2.order_date
FROM users T1
LEFT JOIN orders T2 ON T1.user_id = T2.user_id
WHERE T1.user_id = ?
```

## Next Steps

1. **Explore Examples**: Check out the [examples directory](../examples/) for real-world scenarios
2. **Read User Guide**: Dive deeper with the [comprehensive user guide](user-guide.md)
3. **Learn Filtering**: Master advanced filtering with the [filtering guide](filtering-guide.md)
4. **API Reference**: Explore all features in the [API reference](api-reference.md)

## Need Help?

- **Documentation**: Browse the [full documentation](README.md)
- **Examples**: Check [working examples](examples.md)
- **Issues**: Report problems on [GitHub Issues](https://github.com/your-org/databridge/issues)
- **Troubleshooting**: See [common solutions](troubleshooting.md)

---

**You're ready to start!** DataBridge makes database schema analysis powerful yet simple.
