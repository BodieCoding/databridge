# DataBridge User Guide

A comprehensive guide to using DataBridge for database schema analysis, relationship mapping, and query optimization.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Fluent API](#fluent-api)
3. [Schema Discovery](#schema-discovery)
4. [Relationship Management](#relationship-management)
5. [Query Generation](#query-generation)
6. [Data Export](#data-export)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)

## Core Concepts

### The DataBridge Philosophy

DataBridge acts as a "bridge" between your database schema and data analysis needs. It provides:

- **Schema Discovery**: Extract and analyze database metadata
- **Relationship Mapping**: Connect tables through various relationship sources
- **Query Optimization**: Generate efficient SQL with intelligent analysis
- **Multi-Format Export**: Convert schemas to YAML, XML, JSON formats

### Key Components

```python
from src.database.datamodel_service import DataBridge

# Main orchestration class
bridge = DataBridge(db_connection, logger)

# Core operations
schema = bridge.discover_schema()    # Schema discovery builder
query = bridge.generate_query()     # Query generation builder
export = bridge.export_schema()     # Export operations
```

## Fluent API

DataBridge provides a fluent, chainable API that reads like natural language:

### Method Chaining Pattern

```python
# Schema discovery with chaining
schema = (bridge.discover_schema()
         .from_database()
         .only_tables(['users', 'orders'])
         .with_relationships_from_csv('data/relationships.csv')
         .build())

# Query generation with chaining
result = (bridge.generate_query()
         .select_all()
         .where({'users': ['user_id']})
         .with_joins()
         .build())
```

### Builder Pattern Benefits

- **Readable**: Code reads like documentation
- **Flexible**: Mix and match operations as needed
- **Discoverable**: IDE autocompletion guides usage
- **Maintainable**: Clear separation of concerns

## Schema Discovery

### Basic Schema Extraction

```python
# Extract all tables
full_schema = (bridge.discover_schema()
              .from_database()
              .build())

# Extract with relationships
enhanced_schema = (bridge.discover_schema()
                  .from_database()
                  .with_relationships_from_database()
                  .build())
```

### Table Filtering

#### Include Specific Tables
```python
# Focus on core business tables
core_schema = (bridge.discover_schema()
              .from_database()
              .only_tables(['customers', 'orders', 'products'])
              .build())

# Single table analysis
user_schema = bridge.discover_schema().only_tables('users').build()
```

#### Exclude Unwanted Tables
```python
# Remove temporary and log tables
clean_schema = (bridge.discover_schema()
               .from_database()
               .exclude_tables(['temp_data', 'logs', 'audit_trail'])
               .build())
```

#### Pattern-Based Filtering
```python
# Include tables matching patterns
loan_schema = (bridge.discover_schema()
              .from_database()
              .matching_pattern(r'^loan_.*')
              .build())

# Exclude system tables
user_schema = (bridge.discover_schema()
              .from_database()
              .excluding_pattern([r'^sys.*', r'^temp.*'])
              .build())

# Complex pattern combinations
business_schema = (bridge.discover_schema()
                  .from_database()
                  .matching_pattern([r'^customer.*', r'^order.*', r'^product.*'])
                  .excluding_pattern(r'.*_backup$')
                  .build())
```

### Schema-Level Filtering

```python
# Focus on specific database schemas
production_schema = (bridge.discover_schema()
                    .from_database()
                    .only_schemas(['dbo', 'sales'])
                    .build())

# Exclude test schemas
clean_schema = (bridge.discover_schema()
               .from_database()
               .exclude_schemas(['test', 'staging', 'temp'])
               .build())
```

### Combined Filtering

```python
# Enterprise filtering example
enterprise_schema = (bridge.discover_schema()
                    .from_database()
                    .only_schemas(['production'])
                    .matching_pattern(r'^(customer|order|product|inventory).*')
                    .exclude_tables(['customer_temp', 'order_backup'])
                    .with_relationships_from_database()
                    .with_relationships_from_csv('data/custom_relationships.csv')
                    .build())
```

## Relationship Management

### Relationship Sources

DataBridge supports multiple relationship data sources:

#### Database Foreign Keys
```python
schema = (bridge.discover_schema()
         .from_database()
         .with_relationships_from_database()
         .build())
```

#### CSV Relationships
```python
# CSV format: table,parent,relation,parent_column,child_column
schema = (bridge.discover_schema()
         .from_database()
         .with_relationships_from_csv('data/relationships.csv')
         .build())
```

#### XML Relationships
```python
schema = (bridge.discover_schema()
         .from_database()
         .with_relationships_from_xml('data/relationships.xml')
         .build())
```

#### Multiple Sources
```python
# Combine multiple relationship sources
comprehensive_schema = (bridge.discover_schema()
                       .from_database()
                       .with_relationships_from_database()
                       .with_relationships_from_csv('data/business_rules.csv')
                       .with_relationships_from_xml('data/custom_mappings.xml')
                       .build())
```

### Relationship Analysis

```python
# Create relationship DAG
dag_info = bridge.relationship_manager.create_dag(schema.tables)

print(f"Relationship graph has {dag_info['node_count']} tables")
print(f"Connected by {dag_info['edge_count']} relationships")

# Find top-level (parent) tables
top_tables = bridge.relationship_manager.find_top_level_tables(schema.tables)
print(f"Top-level tables: {top_tables}")
```

### Relationship Visualization

```python
# Generate relationship diagram
bridge.relationship_manager.visualize_dag(
    dag_info['dag'],
    'output/relationships.png',
    layout='spring',          # Layout algorithm
    node_size=1000,          # Node size
    font_size=8,             # Label font size
    edge_labels=True         # Show relationship labels
)
```

## Query Generation

### Basic Query Generation

```python
# Simple SELECT with WHERE clause
result = (bridge.generate_query()
         .select_all()
         .where({'users': ['user_id']})
         .build())

print("SQL:", result['query'])
print("Parameters:", result['parameters'])
```

### Advanced Query Features

#### Multi-Column Filtering
```python
# Filter on multiple columns
result = (bridge.generate_query()
         .select_all()
         .where({'users': ['user_id', 'email', 'status']})
         .with_joins()
         .build())
```

#### Table.Column Format
```python
# Specific column filtering
result = (bridge.generate_query()
         .select_all()
         .where({'users.user_id': 'specific_value'})
         .build())
```

#### Query Optimization
```python
# Generate optimized query with index analysis
result = (bridge.generate_query()
         .select_all()
         .where({'orders': ['customer_id', 'order_date']})
         .optimize_with_indexes()
         .build())

print("Query:", result['query'])
print("Index recommendations:", result['index_recommendations'])
```

### Query Filtering

```python
# Limit query to specific tables
filtered_query = (bridge.generate_query()
                 .select_all()
                 .where({'customers': ['customer_id']})
                 .only_from_tables(['customers', 'orders'])
                 .build())

# Exclude tables from query
clean_query = (bridge.generate_query()
              .select_all()
              .where({'users': ['user_id']})
              .excluding_tables(['temp_data', 'logs'])
              .build())
```

## Data Export

### Multiple Format Support

```python
# Export to all supported formats
bridge.export_schema().to_yaml('output/schema.yaml')
bridge.export_schema().to_xml('output/schema.xml')
bridge.export_schema().to_json('output/schema.json')
```

### Export with Custom Schema

```python
# Export filtered schema
filtered_schema = (bridge.discover_schema()
                  .from_database()
                  .only_tables(['customers', 'orders'])
                  .build())

# Export the filtered result
bridge.export_schema(filtered_schema).to_yaml('output/customer_orders.yaml')
```

### Export Configuration

```python
# Export with metadata
bridge.export_schema_with_metadata().to_yaml('output/documented_schema.yaml')

# Export specific format with options
bridge.export_schema().to_xml('output/schema.xml', include_indexes=True)
```

## Advanced Features

### Index Analysis

```python
# Analyze existing indexes
index_analysis = bridge.query_builder.analyze_indexes(['users', 'orders'])

# Generate optimization recommendations
recommendations = bridge.query_builder.suggest_index_optimizations(
    tables=['users', 'orders', 'products'],
    query_patterns=['user_id', 'order_date', 'product_category']
)

for rec in recommendations:
    print(f"Table: {rec['table']}")
    print(f"Recommendation: {rec['recommendation']}")
    print(f"Expected Improvement: {rec['performance_impact']}")
```

### Schema Validation

```python
# Validate schema integrity
validation = bridge.validate_schema()

if not validation['is_valid']:
    print("Schema validation issues found:")
    for issue in validation['issues']:
        print(f"  - {issue['type']}: {issue['description']}")
        print(f"    Table: {issue['table']}")
        print(f"    Suggestion: {issue['suggestion']}")
```

### Performance Monitoring

```python
# Monitor discovery performance
import time

start_time = time.time()
schema = (bridge.discover_schema()
         .from_database()
         .with_relationships_from_database()
         .build())
end_time = time.time()

print(f"Schema discovery took {end_time - start_time:.2f} seconds")
print(f"Analyzed {len(schema.tables)} tables")
print(f"Found {len(schema.relationships)} relationships")
```

## Best Practices

### Schema Discovery

1. **Start Broad, Filter Down**
   ```python
   # Get full picture first
   full_schema = bridge.discover_schema().from_database().build()
   
   # Then apply targeted filtering
   focused_schema = (bridge.discover_schema()
                    .from_database()
                    .matching_pattern(r'^core_.*')
                    .build())
   ```

2. **Cache Expensive Operations**
   ```python
   # Cache schema for reuse
   cached_schema = bridge.discover_schema().from_database().build()
   
   # Reuse for multiple operations
   query1 = bridge.generate_query().using_schema(cached_schema).build()
   query2 = bridge.generate_query().using_schema(cached_schema).build()
   ```

3. **Combine Relationship Sources**
   ```python
   # Use multiple sources for comprehensive mapping
   schema = (bridge.discover_schema()
            .from_database()
            .with_relationships_from_database()     # Foreign keys
            .with_relationships_from_csv('business.csv')  # Business rules
            .build())
   ```

### Query Generation

1. **Use Specific Filtering**
   ```python
   # Prefer specific table filtering
   result = (bridge.generate_query()
            .select_all()
            .where({'orders': ['customer_id']})
            .only_from_tables(['customers', 'orders', 'order_items'])
            .build())
   ```

2. **Enable Optimization**
   ```python
   # Always use optimization for production queries
   result = (bridge.generate_query()
            .select_all()
            .where({'users': ['user_id']})
            .optimize_with_indexes()
            .build())
   ```

### Export and Documentation

1. **Document Your Schemas**
   ```python
   # Include metadata in exports
   bridge.export_schema_with_metadata().to_yaml('documented_schema.yaml')
   ```

2. **Use Consistent Naming**
   ```python
   # Consistent output naming
   timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
   bridge.export_schema().to_yaml(f'output/schema_{timestamp}.yaml')
   ```

### Error Handling

```python
import logging

try:
    schema = (bridge.discover_schema()
             .from_database()
             .with_relationships_from_csv('data/relationships.csv')
             .build())
except FileNotFoundError:
    logging.warning("Relationships CSV not found, using database relationships only")
    schema = (bridge.discover_schema()
             .from_database()
             .with_relationships_from_database()
             .build())
except Exception as e:
    logging.error(f"Schema discovery failed: {e}")
    raise
```

---

This user guide covers the comprehensive capabilities of DataBridge. For more specific topics, see:

- [API Reference](api-reference.md) - Complete method documentation
- [Filtering Guide](filtering-guide.md) - Advanced filtering techniques
- [Examples](examples.md) - Working code examples
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
