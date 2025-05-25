# DataBridge Examples

This directory contains usage examples for the DataBridge  utility.

## 📁 Example Files

# DataBridge Examples

This directory contains practical usage examples for the DataBridge database schema analysis utility. All examples demonstrate the modern, fluent API without any legacy code.

## 📁 Example Files

### [`comprehensive_demo.py`](comprehensive_demo.py)
**Complete demonstration** of DataBridge capabilities including:
- Schema discovery with advanced filtering
- Query optimization and index analysis  
- Multi-format exports (YAML, XML, JSON)
- Enterprise workflow patterns
- Relationship analysis and DAG visualization

**Use this example** as your starting point for understanding DataBridge's full capabilities.

### [`advanced_filtering.py`](advanced_filtering.py) 
**Focused demonstration** of DataBridge's advanced filtering capabilities:
- Table inclusion/exclusion patterns
- Regex-based filtering
- Pattern matching for business tables
- Query filtering with table constraints

**Use this example** when you need to understand DataBridge's filtering system.

### [`getting_started.py`](getting_started.py)
**Simple getting started** example for new users:
- Basic schema discovery
- Simple filtering operations
- Quick export operations
- Basic relationship mapping

**Use this example** to get started with DataBridge quickly.

## 🚀 Running the Examples

### Prerequisites
1. **Database Connection**: Update the connection string in each example
2. **Dependencies**: Install requirements: `pip install -r ../requirements.txt`
3. **Data Files**: Ensure `../data/relationships.csv` exists for relationship examples

### Basic Usage
```bash
# Run the comprehensive professional example
python professional_usage_example.py

# Run specific filtering demonstrations
python filtering_example.py
python practical_filtering_demo.py
```

### Configuration
Each example includes database connection configuration at the top of the `main()` function:

```python
# Update this connection string for your database
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=pocdb;UID=sa;PWD=Two3RobotDuckTag!'
```

## 📊 Example Outputs

### Schema Discovery
- **YAML Schema**: `output/professional_schema.yaml`
- **XML Schema**: `output/professional_schema.xml`  
- **JSON Schema**: `output/professional_schema.json`

### Visualizations
- **Relationship Diagrams**: `output/relationships.png`
- **Schema Graphs**: `output/schema_relationships_[timestamp].png`

### Documentation
- **Schema Documentation**: `output/schema_documentation_[timestamp].yaml`
- **Performance Analysis**: Console output and log files

## 🎯 Key Features Demonstrated

### Modern Fluent API
```python
schema = (bridge.discover_schema()
         .from_database()
         .matching_pattern(r'^(loan|customer).*')
         .with_relationships_from_database()
         .build())
```

### Query Optimization
```python
result = (bridge.generate_query()
         .select_all()
         .where({'loan_data': ['loan_id']})
         .optimize_with_indexes()
         .build())
```

### Multi-Format Export
```python
bridge.export_schema().to_yaml('output/schema.yaml')
bridge.export_schema().to_xml('output/schema.xml')
bridge.export_schema().to_json('output/schema.json')
```

### Relationship Analysis
```python
dag_info = bridge.relationship_manager.create_dag(schema.tables)
bridge.relationship_manager.visualize_dag(dag_info['dag'], 'output/graph.png')
```

## 📝 Notes

- **No Legacy Code**: All examples use the modern DataBridge API only
- **Professional Quality**: Examples follow best practices for production use
- **Error Handling**: Comprehensive exception handling and logging
- **Documentation**: Each function is well-documented with clear purposes
- **Modularity**: Examples are structured for easy customization and extension

## 🔧 Customization

### Adding Your Database
1. Update the connection string in the example
2. Modify table names to match your schema
3. Adjust filtering patterns for your naming conventions

### Extending Examples
- Add new filtering patterns for your business logic
- Include additional export formats
- Customize visualization layouts
- Add performance monitoring

---

**These examples showcase DataBridge as a professional, enterprise-ready database schema analysis utility.**
