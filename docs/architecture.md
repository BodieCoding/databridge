# DataBridge Architecture

## Overview

DataBridge is built with a clean, modular architecture that follows SOLID principles and provides clear separation of concerns. This document outlines the architecture components and their interactions.

## Architecture Components

### 1. Core DTOs (`dtos.py`)
- **Purpose**: Define data structures for schema, tables, columns, relationships, and indexes
- **Key Classes**: `SchemaDTO`, `TableDTO`, `ColumnDTO`, `RelationshipDTO`, `RelationshipColumnDTO`, `IndexDTO`
- **Benefits**: Type-safe data transfer, clear data contracts

### 2. Schema Extractor (`schema_extractor.py`)
- **Purpose**: Extract schema metadata from database connections
- **Responsibilities**: 
  - Fetch table, column, index, and primary key information
  - Convert raw database metadata to DTOs
- **Single Responsibility**: Only handles database schema extraction

### 3. Relationship Manager (`relationship_manager.py`)
- **Purpose**: Manage relationships between tables
- **Responsibilities**:
  - Load relationships from CSV files
  - Extract foreign key relationships from database
  - Build relationship graphs
  - Find top-level tables
- **Multi-source Support**: Database FKs, CSV definitions, future YAML/XML support

### 4. Query Builder (`query_builder.py`)
- **Purpose**: Generate SQL queries from schema information
- **Responsibilities**:
  - Build SELECT statements with JOINs
  - Handle multi-column relationships
  - Generate table aliases (T1, T2, T3...)
  - Build WHERE clauses from filter specifications
- **Features**: Supports both `{'table': ['col1', 'col2']}` and `{'table.col': 'value'}` filter formats

### 5. Schema Serializer (`schema_serializer.py`)
- **Purpose**: Convert schema DTOs to various output formats
- **Supported Formats**: YAML, XML, JSON
- **Responsibilities**:
  - Convert DTOs to format-specific dictionaries
  - Write files with proper encoding and formatting
  - Handle optional fields and metadata

### 6. DataBridge Service (`datamodel_service.py`)
- **Purpose**: Main orchestration service and public API
- **Responsibilities**:
  - Coordinate all components
  - Provide simple, high-level interface
  - Cache schema for performance
  - Validate schemas
  - Generate relationship analysis

## Usage Examples

### Basic Usage

```python
from database.datamodel_service import DataBridge
import pyodbc

# Connect to database
db_conn = pyodbc.connect(connection_string)

# Initialize service
bridge = DataBridge(db_conn)

# Extract full schema with relationships
schema = bridge.extract_full_schema(
    include_db_relationships=True,
    csv_relationships_path='data/relationships.csv'
)

# Generate SELECT query
sql = bridge.generate_select_query(
    filter_spec={'lender_customer': ['customer_id']}
)

# Export schema
bridge.export_schema('yaml', 'output/schema.yaml')
```

### Advanced Usage

```python
# Get relationship analysis
rel_info = bridge.get_relationship_info()
print(f"Top-level tables: {rel_info['top_level_tables']}")

# Validate schema
validation = bridge.validate_schema()
if not validation['is_valid']:
    for issue in validation['issues']:
        print(f"Issue: {issue}")

# Generate query with specific root table
sql = bridge.generate_select_query(
    filter_spec={'orders.customer_id': 'value'},
    root_table='customers'
)
```

### Using Individual Components

```python
# Use components individually for fine-grained control
from database.schema_extractor import SchemaExtractor
from database.relationship_manager import RelationshipManager
from database.query_builder import QueryBuilder

extractor = SchemaExtractor(db_conn, logger)
schema = extractor.extract_schema()

rel_manager = RelationshipManager(logger)
schema = rel_manager.load_from_csv(schema, 'relationships.csv')

query_builder = QueryBuilder(logger)
sql = query_builder.generate_select_with_joins(
    schema, {'table': ['column']}
)
```

## Benefits of This Architecture

### 1. **Single Responsibility Principle**
Each class has one clear purpose and reason to change.

### 2. **Dependency Injection**
Components can be easily tested and mocked.

### 3. **Extensibility**
New relationship sources, output formats, or query types can be added easily.

### 4. **Testability**
Each component can be unit tested independently.

### 5. **Maintainability**
Clear separation makes the code easier to understand and modify.

### 6. **Reusability**
Components can be used independently or in different combinations.

## Best Practices

### Recommended Usage
```python
# Clean, consistent interface
bridge = DataBridge(db_conn)
schema = bridge.extract_full_schema(csv_relationships_path='relationships.csv')
sql = bridge.generate_select_query(filter_spec)
bridge.export_schema('yaml', 'output.yaml')
```

## File Structure

```
src/database/
├── dtos.py                    # Data Transfer Objects
├── schema_extractor.py        # Database schema extraction
├── relationship_manager.py    # Relationship management
├── query_builder.py          # SQL query generation
├── schema_serializer.py      # Format serialization
├── datamodel_service.py      # Main orchestration service
└── __init__.py
```

## Configuration

The new architecture is more flexible with configuration:

```yaml
# config.yaml
source_database:
  connection_string: "DRIVER={...};SERVER=...;DATABASE=...;UID=...;PWD=..."
  schema: "dbo"

relationships:
  csv_path: "data/relationships.csv"
  include_database_fks: true

output:
  formats: ["yaml", "xml", "json"]
  directory: "output"
```

## Error Handling

The new architecture provides better error handling:

- **Graceful Degradation**: Works without database connection for some operations
- **Detailed Error Messages**: Clear indication of what went wrong
- **Validation**: Schema validation with specific issue reporting
- **Logging**: Comprehensive logging at appropriate levels

## Performance Improvements

- **Schema Caching**: Avoid re-extracting schema for multiple operations
- **Lazy Loading**: Components initialized only when needed
- **Efficient Relationship Building**: Optimized graph construction
- **Memory Management**: Better object lifecycle management

## Future Extensibility

The new architecture makes it easy to add:

- **New Relationship Sources**: YAML, XML, or API-based relationships
- **New Output Formats**: GraphQL schemas, OpenAPI specs, etc.
- **New Query Types**: INSERT, UPDATE, DELETE generation
- **New Validation Rules**: Custom schema validation logic
- **New Database Providers**: PostgreSQL, MySQL, Oracle support

## Testing Strategy

Each component can be tested independently:

```python
# Unit testing individual components
def test_schema_extractor():
    mock_conn = Mock()
    extractor = SchemaExtractor(mock_conn, logger)
    # Test extraction logic

def test_query_builder():
    builder = QueryBuilder(logger)
    # Test with mock schema DTO

def test_relationship_manager():
    manager = RelationshipManager(logger)
    # Test CSV loading logic
```

## Conclusion

DataBridge's architecture provides a solid foundation that is:

- **Maintainable**: Clear separation of concerns
- **Testable**: Independent, mockable components  
- **Extensible**: Easy to add new features
- **Reliable**: Better error handling and validation
- **Performant**: Optimized data flow and caching

This architecture follows industry best practices and provides a professional, maintainable codebase.
