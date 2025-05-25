![DataBridge Logo](img/logo.png)

# DataBridge

A sophisticated Python utility for bridging SQL database schemas with modern data analysis and optimization capabilities. DataBridge provides a fluent API for schema discovery, relationship mapping, query optimization, and multi-format data exports.

## 📚 Documentation

### Getting Started
- 📖 [**Quick Start Guide**](docs/quick-start.md) - Get up and running in minutes
- 🛠️ [**Installation Guide**](docs/installation.md) - Detailed installation and setup
- ⚙️ [**Configuration Guide**](docs/configuration.md) - System configuration
- 🗄️ [**Database Setup**](docs/database-setup.md) - Setup SQL Server with Docker

### User Guides  
- 📘 [**User Guide**](docs/user-guide.md) - Complete user manual with examples
- 🔍 [**API Reference**](docs/api-reference.md) - Comprehensive API documentation
- 🎯 [**Filtering Guide**](docs/filtering-guide.md) - Advanced filtering capabilities

### Advanced Topics
- 🏗️ [**Architecture Guide**](docs/architecture.md) - Technical architecture and design
- 📊 [**Examples Gallery**](examples/) - Working code examples and demonstrations

## 🚀 Key Features

### Core Capabilities
- **Fluent Schema Discovery**: Intuitive API for extracting and analyzing database schemas
- **Advanced Filtering**: Pattern-based table filtering with regex support
- **Relationship Mapping**: Multi-source relationship analysis (database FKs, CSV, XML)
- **Query Optimization**: Intelligent SQL generation with index analysis
- **Multi-Format Export**: YAML, XML, JSON schema serialization
- **Index Analysis**: Performance optimization recommendations
- **DAG Visualization**: Network graph generation for relationship analysis

### Technical Features
- **Modular Architecture**: Layered design for extensibility and testing
- **Connection Management**: Robust database connection handling (pyodbc)
- **XML Processing**: Advanced XML parsing for metadata and relationships
- **Network Analysis**: Graph-based relationship analysis using NetworkX
- **Comprehensive Logging**: Detailed operation tracking and debugging
- **Configuration Management**: YAML-based configuration system

## 📁 Project Structure

```
databridge/
├── img/                      # Project assets and logos
├── src/
│   ├── database/            # Core database operations
│   │   ├── datamodel_service.py    # Main DataBridge orchestration
│   │   ├── schema_extractor.py     # Schema discovery engine
│   │   ├── relationship_manager.py # Relationship mapping
│   │   ├── query_builder.py        # Optimized query generation
│   │   └── schema_serializer.py    # Multi-format export
│   ├── xml/                 # XML processing and parsing
│   ├── utils/               # Utilities (logging, config)
│   ├── tests/               # Comprehensive unit tests
│   └── main.py              # Demonstration entry point
├── data/                    # Example data and configurations
├── requirements.txt         # Python dependencies
└── config.yaml             # Configuration file
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/databridge.git
   cd databridge
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database connection** in `config.yaml`:
   ```yaml
   source_database:
     connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=pocdb;UID=sa;PWD=DataBridge2025!"
   ```

4. **Run the demonstration**:
   ```bash
   python src/main.py
   ```

## 📋 Requirements

- **Python 3.8+**
- **pyodbc**: Database connectivity
- **networkx**: Relationship analysis and graph visualization
- **matplotlib**: Graph plotting and visualization

## 🎯 Quick Start Example

```python
from src.database.datamodel_service import DataBridge
import pyodbc

# Initialize connection
db_conn = pyodbc.connect(connection_string)
bridge = DataBridge(db_conn)

# Discover schema with fluent API
schema = (bridge.discover_schema()
         .from_database()
         .only_tables(['users', 'orders', 'products'])
         .with_relationships_from_csv('data/relationships.csv')
         .build())

# Generate optimized queries
query = (bridge.generate_query()
        .select_all()
        .where({'users': ['user_id']})
        .with_joins()
        .build())

# Export to multiple formats
bridge.export_schema().to_yaml('output/schema.yaml')
bridge.export_schema().to_json('output/schema.json')

print(f"Discovered {len(schema.tables)} tables")
print(f"Generated query: {query['query']}")
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/databridge.git
   cd databridge
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database connection** in `config.yaml`:
   ```yaml
   source_database:
     connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=pocdb;UID=sa;PWD=DataBridge2025!"
   ```

4. **Run the demonstration**:
   ```bash
   python src/main.py
   ```

For detailed installation instructions, see the [Installation Guide](docs/installation.md).

### Advanced Filtering and Analysis

```python
# Complex schema discovery with filtering
schema = (bridge.discover_schema()
         .from_database()
         .excluding_pattern([r'^sys.*', r'^temp.*'])
         .with_relationships_from_database()
         .with_relationships_from_csv('data/custom_relationships.csv')
         .build())

# Generate relationship DAG
dag_info = bridge.relationship_manager.create_dag(schema.tables)
bridge.relationship_manager.visualize_dag(dag_info['dag'], 'output/schema_graph.png')
```

### Optimized Query Generation

```python
# Generate optimized queries with index analysis
result = (bridge.generate_query()
         .select_all()
         .where({'users': ['user_id', 'email']})
         .with_joins()
         .optimize_with_indexes()
         .build())

print("Generated SQL:", result['query'])
print("Index Recommendations:", result['index_recommendations'])
```

### Multi-Format Export

```python
# Export schema to multiple formats
bridge.export_schema().to_yaml('output/schema.yaml')
bridge.export_schema().to_xml('output/schema.xml')
bridge.export_schema().to_json('output/schema.json')
```

## 🔧 Advanced Usage

### Custom Relationship Sources

DataBridge supports multiple relationship data sources:

```python
# CSV relationships
bridge.discover_schema().with_relationships_from_csv('data/relationships.csv')

# XML relationships  
bridge.discover_schema().with_relationships_from_xml('data/relationships.xml')

# Database foreign keys
bridge.discover_schema().with_relationships_from_database()

# Combine multiple sources
schema = (bridge.discover_schema()
         .from_database()
         .with_relationships_from_database()
         .with_relationships_from_csv('data/custom_relationships.csv')
         .build())
```

### Index Analysis and Optimization

```python
# Analyze existing indexes
index_analysis = bridge.query_builder.analyze_indexes(['users', 'orders'])

# Generate optimization recommendations
recommendations = bridge.query_builder.suggest_index_optimizations(
    tables=['users', 'orders'],
    query_patterns=['user_id', 'order_date', 'status']
)

print("Index Recommendations:")
for rec in recommendations:
    print(f"  {rec['table']}: {rec['recommendation']}")
```

### DAG Visualization

```python
# Create and visualize relationship DAG
dag_info = bridge.relationship_manager.create_dag(schema.tables)

# Generate network graph
bridge.relationship_manager.visualize_dag(
    dag_info['dag'], 
    'output/relationships.png',
    layout='spring',
    node_size=1000,
    font_size=8
)

print(f"DAG has {dag_info['node_count']} nodes and {dag_info['edge_count']} edges")
```

## 📊 Metadata Formats

### Schema Export Formats

DataBridge supports multiple export formats for maximum compatibility:

#### YAML Schema
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
        nullable: false
    indexes:
      - name: idx_users_email
        type: NONCLUSTERED
        columns: [email]
    relationships:
      - target_table: orders
        relationship_type: one-to-many
        foreign_key: user_id
```

#### XML Schema
```xml
<schema>
  <table name="users">
    <columns>
      <column name="user_id" type="int" nullable="false" primary_key="true"/>
      <column name="email" type="varchar" max_length="255" nullable="false"/>
    </columns>
    <relationships>
      <relationship target="orders" type="one-to-many" key="user_id"/>
    </relationships>
  </table>
</schema>
```

### Relationship Data Sources

#### CSV Format
```csv
table,parent,relation,parent_column,child_column
orders,users,many-to-one,user_id,user_id
order_items,orders,many-to-one,order_id,order_id
order_items,products,many-to-one,product_id,product_id
```

#### XML Format
```xml
<relationships>
  <relationship>
    <child_table>orders</child_table>
    <parent_table>users</parent_table>
    <relationship_type>many-to-one</relationship_type>
    <parent_column>user_id</parent_column>
    <child_column>user_id</child_column>
  </relationship>
</relationships>
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest src/tests/

# Run specific test modules
python -m pytest src/tests/test_schema_extractor.py
python -m pytest src/tests/test_relationship_manager.py

# Run with coverage
python -m pytest src/tests/ --cov=src/
```

## 🎨 Configuration

Customize DataBridge behavior via `config.yaml`:

```yaml
# Database connections
source_database:
  connection_string: "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=pocdb;UID=sa;PWD=DataBridge2025!"

# Logging configuration
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
# Schema discovery settings
schema_discovery:
  include_system_tables: false
  max_table_count: 1000
  relationship_sources:
    - database_foreign_keys
    - csv_files
    
# Export settings
export:
  default_format: yaml
  include_indexes: true
  include_relationships: true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **pyodbc**: Database connectivity foundation
- **NetworkX**: Graph analysis capabilities
- **matplotlib**: Visualization support
- SQL Server community for database best practices

---

**DataBridge** - Bridging the gap between database schemas and modern data analysis.
