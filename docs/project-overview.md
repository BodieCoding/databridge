# DataBridge v1.0 - Project Overview

## What is DataBridge?

DataBridge is a modular Python utility for cloning and analyzing SQL database schemas, generating Data Manipulation Language (DML) queries, and handling XML-based relationships. It provides a clean, fluent API for database schema discovery, relationship analysis, and SQL query generation.

## Key Features

- **Schema Discovery**: Extract complete database schema metadata including tables, columns, indexes, and relationships
- **Fluent API**: Intuitive, chainable interface for building complex operations
- **Multiple Output Formats**: Export schemas to YAML, XML, and JSON
- **Advanced Filtering**: Include/exclude tables, schemas, or use regex patterns
- **Relationship Analysis**: Support for database foreign keys and CSV-defined relationships
- **Query Generation**: Automated SQL SELECT statement generation with proper JOINs
- **Modular Architecture**: Clean separation of concerns with testable components

## Architecture Highlights

DataBridge follows SOLID principles with a modular design:

- **DTOs**: Type-safe data structures for schema components
- **Schema Extractor**: Database metadata extraction
- **Relationship Manager**: Multi-source relationship handling
- **Query Builder**: SQL generation with JOIN optimization
- **Schema Serializer**: Multiple output format support
- **DataBridge Service**: Main orchestration API

## Quick Start

```python
from database.datamodel_service import DataBridge
import pyodbc

# Connect and analyze
bridge = DataBridge(pyodbc.connect(connection_string))
schema = bridge.extract_full_schema()

# Generate queries
sql = bridge.generate_query().select_all().where({'customers': ['customer_id']}).build()

# Export results
bridge.export_schema('yaml', 'output/schema.yaml')
```

## Documentation Structure

- **[Quick Start Guide](quick-start.md)** - Get up and running in minutes
- **[User Guide](user-guide.md)** - Comprehensive usage documentation
- **[API Reference](api-reference.md)** - Complete method documentation
- **[Installation Guide](installation.md)** - Setup and requirements
- **[Configuration Guide](configuration.md)** - Configuration options
- **[Filtering Guide](filtering-guide.md)** - Advanced filtering techniques
- **[Architecture Guide](architecture.md)** - Technical architecture details

## Example Projects

See the `examples/` directory for:

- **[Getting Started](../examples/getting_started.py)** - Basic usage patterns
- **[Advanced Filtering](../examples/advanced_filtering.py)** - Complex filtering scenarios
- **[Comprehensive Demo](../examples/comprehensive_demo.py)** - Full feature demonstration

## Technology Stack

- **Python 3.8+** - Core language
- **pyodbc** - Database connectivity
- **xml.etree.ElementTree** - XML processing
- **networkx** - Relationship graph analysis
- **PyYAML** - YAML serialization

## Use Cases

- **Database Documentation**: Generate comprehensive schema documentation
- **Migration Planning**: Analyze relationships before database migrations
- **Query Optimization**: Understand table relationships for efficient queries
- **Schema Validation**: Verify database structure and relationships
- **API Development**: Generate data access patterns from schema analysis

## Version 1.0 Features

This v1.0 release represents a complete rewrite focused on:

- Clean, professional API design
- Comprehensive documentation
- Modular, testable architecture
- Production-ready code quality
- Extensive filtering capabilities
- Multiple output format support

## Getting Help

- Review the [User Guide](user-guide.md) for detailed usage instructions
- Check the [API Reference](api-reference.md) for method documentation
- See [examples/](../examples/) for working code samples
- Review [Configuration Guide](configuration.md) for setup options

DataBridge v1.0 provides a robust foundation for database schema analysis and query generation with a focus on usability, extensibility, and maintainability.
