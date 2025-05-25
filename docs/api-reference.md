# DataBridge API Reference

Complete reference documentation for the DataBridge fluent API.

## Core Classes

### DataBridge

The main orchestration class that provides access to all DataBridge functionality.

```python
from src.database.datamodel_service import DataBridge

bridge = DataBridge(db_conn=None, logger=None)
```

#### Constructor Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `db_conn` | `pyodbc.Connection` | Database connection object | No |
| `logger` | `logging.Logger` | Logger instance for operation tracking | No |

#### Core Methods

##### `discover_schema() -> SchemaDiscovery`

Returns a fluent schema discovery builder for extracting database metadata.

```python
schema = bridge.discover_schema().from_database().build()
```

##### `generate_query() -> QueryBridge`

Returns a fluent query generation builder for creating optimized SQL.

```python
result = bridge.generate_query().select_all().where({...}).build()
```

##### `export_schema(schema=None) -> ExportBridge`

Returns a fluent export builder for multi-format schema serialization.

```python
bridge.export_schema().to_yaml('output.yaml')
```

## Fluent Builders

### SchemaDiscovery

Builder class for fluent schema discovery operations.

#### Source Methods

##### `from_database() -> SchemaDiscovery`

Extract schema from the connected database.

```python
schema = bridge.discover_schema().from_database().build()
```

#### Filtering Methods

##### `only_tables(tables) -> SchemaDiscovery`

Include only specified tables in the schema.

**Parameters:**
- `tables` (str|list): Table name(s) to include

```python
# Single table
schema = bridge.discover_schema().only_tables('users').build()

# Multiple tables
schema = bridge.discover_schema().only_tables(['users', 'orders']).build()
```

**Aliases:** `include_tables()`

##### `exclude_tables(tables) -> SchemaDiscovery`

Exclude specified tables from the schema.

**Parameters:**
- `tables` (str|list): Table name(s) to exclude

```python
schema = bridge.discover_schema().exclude_tables(['temp_data', 'logs']).build()
```

**Aliases:** `without_tables()`

##### `only_schemas(schemas) -> SchemaDiscovery`

Include only specified database schemas.

**Parameters:**
- `schemas` (str|list): Schema name(s) to include

```python
schema = bridge.discover_schema().only_schemas(['dbo', 'sales']).build()
```

##### `exclude_schemas(schemas) -> SchemaDiscovery`

Exclude specified database schemas.

**Parameters:**
- `schemas` (str|list): Schema name(s) to exclude

```python
schema = bridge.discover_schema().exclude_schemas(['test', 'temp']).build()
```

**Aliases:** `without_schemas()`

##### `matching_pattern(patterns) -> SchemaDiscovery`

Include tables matching regex patterns.

**Parameters:**
- `patterns` (str|list): Regex pattern(s) to match

```python
# Single pattern
schema = bridge.discover_schema().matching_pattern(r'^user_.*').build()

# Multiple patterns
schema = bridge.discover_schema().matching_pattern([r'^user_.*', r'^order_.*']).build()
```

##### `excluding_pattern(patterns) -> SchemaDiscovery`

Exclude tables matching regex patterns.

**Parameters:**
- `patterns` (str|list): Regex pattern(s) to exclude

```python
schema = bridge.discover_schema().excluding_pattern([r'^temp_.*', r'.*_backup$']).build()
```

**Aliases:** `without_pattern()`

##### `focus_on(target, type='tables') -> SchemaDiscovery`

Generic include method supporting multiple target types.

**Parameters:**
- `target` (str|list): Target to focus on
- `type` (str): Type of target ('tables', 'schemas', 'patterns')

```python
schema = bridge.discover_schema().focus_on('customers').build()
schema = bridge.discover_schema().focus_on('dbo', 'schemas').build()
schema = bridge.discover_schema().focus_on(r'^core_.*', 'patterns').build()
```

##### `ignore(target, type='tables') -> SchemaDiscovery`

Generic exclude method supporting multiple target types.

**Parameters:**
- `target` (str|list): Target to ignore
- `type` (str): Type of target ('tables', 'schemas', 'patterns')

```python
schema = bridge.discover_schema().ignore(['temp_data', 'logs']).build()
schema = bridge.discover_schema().ignore('test', 'schemas').build()
```

#### Relationship Methods

##### `with_relationships_from_database() -> SchemaDiscovery`

Include foreign key relationships from the database.

```python
schema = (bridge.discover_schema()
         .from_database()
         .with_relationships_from_database()
         .build())
```

##### `with_relationships_from_csv(file_path) -> SchemaDiscovery`

Include relationships from a CSV file.

**Parameters:**
- `file_path` (str): Path to CSV relationships file

**CSV Format:**
```csv
table,parent,relation,parent_column,child_column
orders,users,many-to-one,user_id,user_id
```

```python
schema = (bridge.discover_schema()
         .from_database()
         .with_relationships_from_csv('data/relationships.csv')
         .build())
```

##### `with_relationships_from_xml(file_path) -> SchemaDiscovery`

Include relationships from an XML file.

**Parameters:**
- `file_path` (str): Path to XML relationships file

```python
schema = (bridge.discover_schema()
         .from_database()
         .with_relationships_from_xml('data/relationships.xml')
         .build())
```

#### Build Method

##### `build() -> SchemaDTO`

Execute the schema discovery and return the result.

**Returns:** `SchemaDTO` object containing discovered schema

```python
schema = bridge.discover_schema().from_database().build()
```

### QueryBridge

Builder class for fluent query generation operations.

#### Selection Methods

##### `select_all() -> QueryBridge`

Generate SELECT * queries for all relevant tables.

```python
result = bridge.generate_query().select_all().build()
```

#### Filtering Methods

##### `where(filter_spec) -> QueryBridge`

Add WHERE clause filtering to the query.

**Parameters:**
- `filter_spec` (dict): Filter specification

**Filter Formats:**

1. **Table-Column List Format:**
   ```python
   result = bridge.generate_query().where({'users': ['user_id', 'email']}).build()
   ```

2. **Table.Column Value Format:**
   ```python
   result = bridge.generate_query().where({'users.user_id': 'specific_value'}).build()
   ```

##### `only_from_tables(tables) -> QueryBridge`

Limit query to specific tables.

**Parameters:**
- `tables` (str|list): Table name(s) to include

```python
result = (bridge.generate_query()
         .select_all()
         .only_from_tables(['customers', 'orders'])
         .build())
```

##### `excluding_tables(tables) -> QueryBridge`

Exclude specific tables from query.

**Parameters:**
- `tables` (str|list): Table name(s) to exclude

```python
result = (bridge.generate_query()
         .select_all()
         .excluding_tables(['temp_data', 'logs'])
         .build())
```

**Aliases:** `without_tables()`

#### Join Methods

##### `with_joins() -> QueryBridge`

Include JOIN clauses based on relationships.

```python
result = (bridge.generate_query()
         .select_all()
         .where({'users': ['user_id']})
         .with_joins()
         .build())
```

#### Optimization Methods

##### `optimize_with_indexes() -> QueryBridge`

Enable query optimization with index analysis.

```python
result = (bridge.generate_query()
         .select_all()
         .where({'orders': ['customer_id', 'order_date']})
         .optimize_with_indexes()
         .build())
```

#### Schema Methods

##### `using_schema(schema) -> QueryBridge`

Use a specific schema for query generation.

**Parameters:**
- `schema` (SchemaDTO): Pre-discovered schema to use

```python
custom_schema = bridge.discover_schema().only_tables(['users']).build()
result = (bridge.generate_query()
         .select_all()
         .using_schema(custom_schema)
         .build())
```

##### `limit_to_filtered_schema() -> QueryBridge`

Limit query to tables present in the filtered schema.

```python
result = (bridge.generate_query()
         .select_all()
         .limit_to_filtered_schema()
         .build())
```

#### Build Method

##### `build() -> dict`

Execute the query generation and return the result.

**Returns:** Dictionary containing:
- `query` (str): Generated SQL query
- `parameters` (list): Query parameters
- `tables_used` (list): Tables included in query
- `index_recommendations` (list): Index optimization suggestions (if enabled)

```python
result = bridge.generate_query().select_all().where({...}).build()
print(result['query'])
```

### ExportBridge

Builder class for fluent schema export operations.

#### Export Methods

##### `to_yaml(file_path) -> ExportBridge`

Export schema to YAML format.

**Parameters:**
- `file_path` (str): Output file path

```python
bridge.export_schema().to_yaml('output/schema.yaml')
```

##### `to_xml(file_path, **options) -> ExportBridge`

Export schema to XML format.

**Parameters:**
- `file_path` (str): Output file path
- `**options`: Export options (include_indexes, etc.)

```python
bridge.export_schema().to_xml('output/schema.xml', include_indexes=True)
```

##### `to_json(file_path) -> ExportBridge`

Export schema to JSON format.

**Parameters:**
- `file_path` (str): Output file path

```python
bridge.export_schema().to_json('output/schema.json')
```

## Data Transfer Objects (DTOs)

### SchemaDTO

Container for complete schema information.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `database_name` | str | Name of the source database |
| `tables` | dict | Dictionary of table name -> TableDTO |
| `relationships` | list | List of RelationshipDTO objects |
| `extraction_timestamp` | datetime | When the schema was extracted |

```python
schema = bridge.discover_schema().from_database().build()
print(f"Database: {schema.database_name}")
print(f"Tables: {len(schema.tables)}")
print(f"Relationships: {len(schema.relationships)}")
```

### TableDTO

Container for table metadata.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `table_name` | str | Name of the table |
| `columns` | dict | Dictionary of column name -> ColumnDTO |
| `indexes` | list | List of IndexDTO objects |
| `primary_keys` | list | List of primary key column names |

```python
for table_name, table in schema.tables.items():
    print(f"Table: {table.table_name}")
    print(f"Columns: {len(table.columns)}")
    print(f"Primary Keys: {table.primary_keys}")
```

### ColumnDTO

Container for column metadata.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `column_name` | str | Name of the column |
| `data_type` | str | SQL data type |
| `max_length` | int | Maximum length (for string types) |
| `precision` | int | Numeric precision |
| `scale` | int | Numeric scale |
| `is_nullable` | bool | Whether column allows NULL |
| `is_primary_key` | bool | Whether column is part of primary key |

### RelationshipDTO

Container for table relationship information.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `child_table` | str | Child table name |
| `parent_table` | str | Parent table name |
| `relationship_type` | str | Type of relationship |
| `columns` | list | List of RelationshipColumnDTO objects |

### IndexDTO

Container for index information.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `index_name` | str | Name of the index |
| `table_name` | str | Table the index belongs to |
| `index_type` | str | Type of index (CLUSTERED, NONCLUSTERED, etc.) |
| `columns` | list | List of indexed column names |
| `is_unique` | bool | Whether index enforces uniqueness |

## Utility Methods

### Direct Access Methods

For quick operations without fluent builders:

#### `bridge_schema(**options) -> SchemaDTO`

One-liner schema discovery.

**Parameters:**
- `include_db_relationships` (bool): Include database relationships
- `csv_relationships_path` (str): Path to CSV relationships file
- `xml_relationships_path` (str): Path to XML relationships file
- `table_filter` (list): Tables to include
- `schema_filter` (list): Schemas to include

```python
schema = bridge.bridge_schema(
    include_db_relationships=True,
    csv_relationships_path='data/relationships.csv'
)
```

#### `bridge_query(filter_spec, **options) -> dict`

One-liner query generation.

**Parameters:**
- `filter_spec` (dict): Query filter specification
- `optimize` (bool): Enable optimization
- `include_joins` (bool): Include JOIN clauses

```python
result = bridge.bridge_query(
    {'users': ['user_id']},
    optimize=True,
    include_joins=True
)
```

#### `bridge_to_format(format_type, output_path, schema=None) -> None`

One-liner schema export.

**Parameters:**
- `format_type` (str): Export format ('yaml', 'xml', 'json')
- `output_path` (str): Output file path
- `schema` (SchemaDTO): Schema to export (optional)

```python
bridge.bridge_to_format('yaml', 'output/schema.yaml')
```

## Error Handling

### Common Exceptions

#### `ConnectionError`
Raised when database connection fails.

```python
try:
    schema = bridge.discover_schema().from_database().build()
except ConnectionError as e:
    print(f"Database connection failed: {e}")
```

#### `FileNotFoundError`
Raised when relationship files are not found.

```python
try:
    schema = (bridge.discover_schema()
             .with_relationships_from_csv('missing.csv')
             .build())
except FileNotFoundError:
    print("Relationships file not found, using database relationships only")
```

#### `ValidationError`
Raised when schema validation fails.

```python
try:
    validation = bridge.validate_schema()
    if not validation['is_valid']:
        for issue in validation['issues']:
            print(f"Validation issue: {issue}")
except ValidationError as e:
    print(f"Schema validation error: {e}")
```

## Performance Considerations

### Best Practices

1. **Cache Expensive Operations**
   ```python
   # Cache schema for multiple operations
   cached_schema = bridge.discover_schema().from_database().build()
   
   # Reuse cached schema
   query1 = bridge.generate_query().using_schema(cached_schema).build()
   query2 = bridge.generate_query().using_schema(cached_schema).build()
   ```

2. **Use Targeted Filtering**
   ```python
   # More efficient than processing all tables
   focused_schema = (bridge.discover_schema()
                    .from_database()
                    .only_tables(['core_tables'])
                    .build())
   ```

3. **Enable Query Optimization**
   ```python
   # Always use optimization for production
   result = (bridge.generate_query()
            .select_all()
            .optimize_with_indexes()
            .build())
   ```

## Version Compatibility

### Current Version: 1.0

- **Breaking Changes**: None (first stable release)
- **New Features**: Complete fluent API implementation
- **Deprecated**: None

### Migration from Legacy

If upgrading from pre-1.0 versions, see the [Migration Guide](migration.md) for detailed upgrade instructions.

---

This API reference covers all public methods and classes in DataBridge v1.0. For usage examples, see the [User Guide](user-guide.md) and [Example Gallery](examples.md).
