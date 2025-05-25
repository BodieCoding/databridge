# Tests Directory

This directory contains comprehensive test suites for the DataBridge project.

## Test Files

### Unit Tests
- `test_dtos.py` - Tests for data transfer objects and validation
- `test_config_loader.py` - Tests for configuration loading and validation
- `test_logger.py` - Tests for logger setup and functionality
- `test_query_builder.py` - Tests for SQL query generation and JOIN logic
- `test_relationship_manager.py` - Tests for relationship loading and analysis
- `test_schema_serializer.py` - Tests for schema serialization to YAML/XML/JSON
- `test_fluent_api.py` - Tests for fluent API functionality and naming conventions

### Integration Tests
- `test_integration.py` - End-to-end workflow and component integration tests

## Running Tests

To run all tests:
```bash
python -m pytest tests/ -v
```

To run specific test categories:
```bash
# Run only unit tests
python -m pytest tests/test_*.py -k "not integration" -v

# Run only integration tests
python -m pytest tests/test_integration.py -v

# Run tests for specific component
python -m pytest tests/test_query_builder.py -v
```

To run tests with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=html -v
```

## Test Structure

- All test files follow the `test_*.py` naming convention
- Tests use the unittest framework with pytest as the test runner
- Mock objects are used to avoid database dependencies in unit tests
- Tests focus on API surface validation, behavior verification, and error handling
- Integration tests verify end-to-end workflows and component interactions

## Test Coverage

The test suite provides comprehensive coverage of:

- **Data Transfer Objects**: Validation and structure integrity
- **Configuration Management**: Config loading, validation, and error handling
- **Logging**: Logger setup, configuration, and output verification
- **Query Building**: SQL generation, JOIN logic, and filter handling
- **Relationship Management**: CSV loading, graph building, and analysis
- **Schema Serialization**: Export to YAML, XML, and JSON formats
- **Fluent API**: Method chaining, naming conventions, and interface consistency
- **Integration Workflows**: End-to-end functionality and error scenarios
