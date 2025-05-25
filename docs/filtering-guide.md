# DataBridge Filtering Modifiers - Complete Guide

## Overview

The DataBridge fluent API includes comprehensive filtering capabilities that allow you to selectively include or exclude tables, schemas, and patterns during schema discovery and query generation. This keeps your data operations focused and intentional.

## Filtering Categories

### 1. Table-Level Filtering

#### Include Only Specific Tables
```python
# Include only specific tables
schema = (bridge.discover_schema()
         .from_database()
         .only_tables(['customers', 'orders', 'products'])
         .build())

# Alias for natural reading
schema = (bridge.discover_schema()
         .include_tables(['loan_data', 'lender_customer'])
         .build())

# Single table focus
schema = bridge.discover_schema().only_tables('loan_data').build()
```

#### Exclude Specific Tables
```python
# Exclude unwanted tables
schema = (bridge.discover_schema()
         .from_database()
         .exclude_tables(['temp_data', 'logs', 'audit_trail'])
         .build())

# Alias for natural reading
schema = (bridge.discover_schema()
         .without_tables(['loan_comments', 'test_data'])
         .build())
```

### 2. Schema/Owner Filtering

#### Include Only Specific Schemas
```python
# Include only specific database schemas
schema = (bridge.discover_schema()
         .from_database()
         .only_schemas(['dbo', 'sales'])
         .build())

# Single schema focus
schema = bridge.discover_schema().only_schemas('production').build()
```

#### Exclude Specific Schemas
```python
# Exclude test/temporary schemas
schema = (bridge.discover_schema()
         .from_database()
         .exclude_schemas(['test', 'temp', 'staging'])
         .build())

# Alias for natural reading
schema = (bridge.discover_schema()
         .without_schemas(['backup', 'archive'])
         .build())
```

### 3. Pattern-Based Filtering

#### Include Tables Matching Patterns
```python
# Include tables matching regex patterns
schema = (bridge.discover_schema()
         .from_database()
         .matching_pattern(r'^loan_.*')  # All loan tables
         .build())

# Multiple patterns
schema = (bridge.discover_schema()
         .matching_pattern([r'^user_.*', r'^customer_.*'])
         .build())
```

#### Exclude Tables Matching Patterns
```python
# Exclude tables matching patterns
schema = (bridge.discover_schema()
         .from_database()
         .excluding_pattern([r'^temp_.*', r'.*_backup$'])
         .build())

# Alias for natural reading
schema = (bridge.discover_schema()
         .without_pattern(r'^test_.*')
         .build())
```

### 4. Convenience Methods

#### Focus On (Include)
```python
# Focus on specific targets
schema = bridge.discover_schema().focus_on('customers').build()
schema = bridge.discover_schema().focus_on(['orders', 'products']).build()
schema = bridge.discover_schema().focus_on('dbo', 'schemas').build()
schema = bridge.discover_schema().focus_on(r'^user_.*', 'patterns').build()
```

#### Ignore (Exclude)
```python
# Ignore specific targets
schema = bridge.discover_schema().ignore('temp_data').build()
schema = bridge.discover_schema().ignore(['logs', 'audit']).build()
schema = bridge.discover_schema().ignore('test', 'schemas').build()
schema = bridge.discover_schema().ignore(r'^temp_.*', 'patterns').build()
```

### 5. Combined Filtering

```python
# Combine multiple filtering approaches
schema = (bridge.discover_schema()
         .from_database()
         .only_schemas(['dbo'])
         .exclude_tables(['temp_data', 'logs'])
         .excluding_pattern(r'^test_.*')
         .with_relationships_from_csv('data/relationships.csv')
         .build())

# Business logic filtering
schema = (bridge.discover_schema()
         .from_database()
         .matching_pattern(r'^(customer|order|product|inventory).*')
         .exclude_tables(['customer_temp', 'order_backup'])
         .build())
```

## Query Generation with Filtering

### Table Filtering in Queries

```python
# Include only specific tables in query
query = (bridge.generate_query()
        .select_all()
        .where({'customers': ['customer_id']})
        .only_from_tables(['customers', 'orders'])
        .build())

# Exclude tables from query
query = (bridge.generate_query()
        .select_all()
        .where({'loan_data': ['loan_id']})
        .excluding_tables(['loan_comments', 'temp_data'])
        .build())

# Alias for natural reading
query = (bridge.generate_query()
        .where({'customers': ['id']})
        .without_tables(['logs', 'audit'])
        .build())
```

### Use Pre-Filtered Schema for Queries

```python
# Create filtered schema first
filtered_schema = (bridge.discover_schema()
                  .from_database()
                  .only_tables(['customers', 'orders', 'products'])
                  .build())

# Use filtered schema in query generation
query = (bridge.generate_query()
        .select_all()
        .where({'customers': ['customer_id']})
        .using_schema(filtered_schema)
        .limit_to_filtered_schema()
        .build())
```

## Practical Examples with Real Data

Based on the pocdb database tables:
- `lender_customer`
- `loan_borrower_creditscore_data`
- `loan_borrower_data`
- `loan_comments`
- `loan_data`

### Example 1: Focus on Core Loan Tables
```python
# Get only the main loan tables (exclude comments and credit scores)
core_schema = (bridge.discover_schema()
              .from_database()
              .only_tables(['loan_data', 'loan_borrower_data', 'lender_customer'])
              .build())
```

### Example 2: Exclude Auxiliary Data
```python
# Get all tables except comments and credit score data
main_schema = (bridge.discover_schema()
              .from_database()
              .exclude_tables(['loan_comments', 'loan_borrower_creditscore_data'])
              .build())
```

### Example 3: Pattern-Based Loan Focus
```python
# Get only loan-related tables using pattern matching
loan_schema = (bridge.discover_schema()
              .from_database()
              .matching_pattern(r'^loan_.*')
              .build())
```

### Example 4: Combined Business Logic
```python
# Loan tables but exclude comments, with relationships
business_schema = (bridge.discover_schema()
                  .from_database()
                  .matching_pattern(r'^loan_.*')
                  .exclude_tables(['loan_comments'])
                  .with_relationships_from_csv('data/relationships.csv')
                  .build())
```

## Method Reference

### SchemaDiscovery Builder Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `only_tables(tables)` | Include only specified tables | `.only_tables(['customers', 'orders'])` |
| `include_tables(tables)` | Alias for `only_tables` | `.include_tables('loan_data')` |
| `exclude_tables(tables)` | Exclude specified tables | `.exclude_tables(['temp_data', 'logs'])` |
| `without_tables(tables)` | Alias for `exclude_tables` | `.without_tables('audit_trail')` |
| `only_schemas(schemas)` | Include only specified schemas | `.only_schemas(['dbo', 'sales'])` |
| `exclude_schemas(schemas)` | Exclude specified schemas | `.exclude_schemas(['test', 'staging'])` |
| `without_schemas(schemas)` | Alias for `exclude_schemas` | `.without_schemas('temp')` |
| `matching_pattern(patterns)` | Include tables matching regex | `.matching_pattern(r'^user_.*')` |
| `excluding_pattern(patterns)` | Exclude tables matching regex | `.excluding_pattern([r'^temp_.*', r'.*_backup$'])` |
| `without_pattern(patterns)` | Alias for `excluding_pattern` | `.without_pattern(r'^test_.*')` |
| `focus_on(target, type)` | Generic include method | `.focus_on('customers')` |
| `ignore(target, type)` | Generic exclude method | `.ignore(['logs', 'audit'])` |

### QueryBridge Builder Methods

| Method | Purpose | Example |
|--------|---------|---------|
| `only_from_tables(tables)` | Include only specified tables in query | `.only_from_tables(['customers', 'orders'])` |
| `excluding_tables(tables)` | Exclude specified tables from query | `.excluding_tables(['temp_data', 'logs'])` |
| `without_tables(tables)` | Alias for `excluding_tables` | `.without_tables('audit_trail')` |
| `limit_to_filtered_schema()` | Use only tables from filtered schema | `.limit_to_filtered_schema()` |

## Benefits

1. **Performance**: Reduce processing time by working with only relevant tables
2. **Focus**: Keep operations targeted to specific business domains
3. **Security**: Exclude sensitive or temporary data from operations
4. **Maintainability**: Clear, readable filtering logic in your code
5. **Flexibility**: Combine multiple filtering approaches as needed

## Best Practices

1. **Use descriptive filtering**: Choose the most readable method for your use case
2. **Combine filters logically**: Start broad (schemas) then narrow down (tables, patterns)
3. **Cache filtered schemas**: Store frequently used filtered schemas for reuse
4. **Document business logic**: Use comments to explain complex filtering combinations
5. **Test filtering results**: Verify that your filters return expected tables

## Backward Compatibility

All filtering modifiers are additive to the existing API. The original `extract_full_schema()` and other methods continue to work unchanged, ensuring 100% backward compatibility.
