"""
Example demonstrating the enhanced DataBridge fluent API with inclusion/exclusion modifiers.
This shows how to use targeted schema discovery and query generation.
"""
import pyodbc
import logging
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.datamodel_service import DataBridge


def setup_databridge_logger():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('advanced_filtering.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('advanced_filtering')


def demonstrate_table_filtering(bridge, logger):
    """Demonstrate table inclusion and exclusion filtering."""
    logger.info("=== TABLE FILTERING EXAMPLES ===")
    
    try:
        # Example 1: Include only specific tables
        logger.info("--- Example 1: Include Only Specific Tables ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .only_tables(['customers', 'orders', 'products'])
                 .build())
        logger.info(f"Single table focus: {len(schema.tables)} tables discovered")
        for table_name in schema.tables.keys():
            print(f"  ✓ {table_name}")
        
        # Example 2: Include single table
        logger.info("--- Example 2: Focus on Single Table ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .focus_on('customers')
                 .build())
        logger.info(f"Single table focus: {len(schema.tables)} tables discovered")
        
        # Example 3: Exclude specific tables
        logger.info("--- Example 3: Exclude Unwanted Tables ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .exclude_tables(['temp_data', 'logs', 'audit_trail'])
                 .build())
        logger.info(f"Excluding tables: {len(schema.tables)} tables discovered")
        
    except Exception as e:
        logger.error(f"Table filtering examples failed: {e}")


def demonstrate_schema_filtering(bridge, logger):
    """Demonstrate database schema/owner filtering."""
    logger.info("=== SCHEMA/OWNER FILTERING EXAMPLES ===")
    
    try:
        # Example 1: Include only specific schemas
        logger.info("--- Example 1: Include Only Specific Schemas ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .only_schemas(['dbo', 'sales'])
                 .build())
        logger.info(f"Schema filtering: {len(schema.tables)} tables discovered")
        
        # Example 2: Exclude test/temp schemas
        logger.info("--- Example 2: Exclude Test/Temp Schemas ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .exclude_schemas(['test', 'temp', 'staging'])
                 .build())
        logger.info(f"Excluding schemas: {len(schema.tables)} tables discovered")
        
        # Example 3: Focus on single schema
        logger.info("--- Example 3: Focus on Single Schema ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .focus_on('dbo', 'schemas')
                 .build())
        logger.info(f"Single schema focus: {len(schema.tables)} tables discovered")
        
    except Exception as e:
        logger.error(f"Schema filtering examples failed: {e}")


def demonstrate_pattern_filtering(bridge, logger):
    """Demonstrate regex pattern-based filtering."""
    logger.info("=== PATTERN-BASED FILTERING EXAMPLES ===")
    
    try:
        # Example 1: Include tables matching pattern
        logger.info("--- Example 1: Include Tables Matching Pattern ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .matching_pattern(r'^(customer|order|product).*')
                 .build())
        logger.info(f"Pattern matching: {len(schema.tables)} tables discovered")
        for table_name in schema.tables.keys():
            print(f"  ✓ {table_name}")
        
        # Example 2: Exclude temporary tables
        logger.info("--- Example 2: Exclude Temporary Tables ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .excluding_pattern([r'^temp_.*', r'.*_temp$', r'.*_backup$'])
                 .build())
        logger.info(f"Excluding temp tables: {len(schema.tables)} tables discovered")
        
        # Example 3: Focus on audit/log tables
        logger.info("--- Example 3: Focus on Audit/Log Tables ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .focus_on([r'.*_log$', r'.*_audit$'], 'patterns')
                 .build())
        logger.info(f"Audit/log focus: {len(schema.tables)} tables discovered")
        
    except Exception as e:
        logger.error(f"Pattern filtering examples failed: {e}")


def demonstrate_combined_filtering(bridge, logger):
    """Demonstrate combining multiple filtering approaches."""
    logger.info("=== COMBINED FILTERING EXAMPLES ===")
    
    try:
        # Example 1: Combine table and schema filtering
        logger.info("--- Example 1: Combine Table and Schema Filtering ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .only_schemas(['dbo'])
                 .exclude_tables(['temp_data', 'logs'])
                 .excluding_pattern(r'^test_.*')
                 .build())
        logger.info(f"Combined filtering: {len(schema.tables)} tables discovered")
        
        # Example 2: Complex business logic filtering
        logger.info("--- Example 2: Business Logic Filtering ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .matching_pattern(r'^(customer|order|product|inventory).*')
                 .exclude_tables(['customer_temp', 'order_backup'])
                 .with_relationships_from_csv('data/relationships.csv')
                 .build())
        logger.info(f"Business logic filtering: {len(schema.tables)} tables discovered")
        
    except Exception as e:
        logger.error(f"Combined filtering examples failed: {e}")


def demonstrate_query_filtering(bridge, logger):
    """Demonstrate query generation with table filtering."""
    logger.info("=== QUERY GENERATION WITH FILTERING ===")
    
    try:
        # Example 1: Query with table inclusion
        logger.info("--- Example 1: Query Only Specific Tables ---")
        query = (bridge.generate_query()
                .select_all()
                .where({'customers': ['customer_id']})
                .only_from_tables(['customers', 'orders'])
                .build())
        logger.info("Query with table inclusion:")
        print("\n" + "="*60)
        print("FILTERED QUERY (INCLUDE TABLES):")
        print("="*60)
        print(query)
        print("="*60 + "\n")
        
        # Example 2: Query with table exclusion
        logger.info("--- Example 2: Query Excluding Tables ---")
        query = (bridge.generate_query()
                .select_all()
                .where({'customers': ['customer_id']})
                .excluding_tables(['temp_data', 'logs', 'audit_trail'])
                .build())
        logger.info("Query with table exclusion:")
        print("\n" + "="*60)
        print("FILTERED QUERY (EXCLUDE TABLES):")
        print("="*60)
        print(query)
        print("="*60 + "\n")
        
        # Example 3: Use filtered schema for query
        logger.info("--- Example 3: Query Using Filtered Schema ---")
        filtered_schema = (bridge.discover_schema()
                          .from_database()
                          .only_tables(['customers', 'orders', 'products'])
                          .build())
        
        query = (bridge.generate_query()
                .select_all()
                .where({'customers': ['customer_id']})
                .using_schema(filtered_schema)
                .limit_to_filtered_schema()
                .build())
        logger.info("Query using pre-filtered schema:")
        print("\n" + "="*60)
        print("QUERY WITH FILTERED SCHEMA:")
        print("="*60)
        print(query)
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Query filtering examples failed: {e}")


def demonstrate_convenience_methods(bridge, logger):
    """Demonstrate convenience methods for common filtering scenarios."""
    logger.info("=== CONVENIENCE METHOD EXAMPLES ===")
    
    try:
        # Example 1: Quick single table focus
        logger.info("--- Example 1: Quick Single Table Focus ---")
        schema = bridge.discover_schema().focus_on('customers').build()
        logger.info(f"Quick focus: {len(schema.tables)} tables")
        
        # Example 2: Quick ignore unwanted tables
        logger.info("--- Example 2: Quick Ignore Unwanted ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .ignore(['temp_data', 'logs', 'audit_trail'])
                 .build())
        logger.info(f"Quick ignore: {len(schema.tables)} tables")
        
        # Example 3: Pattern-based convenience
        logger.info("--- Example 3: Pattern-Based Convenience ---")
        schema = (bridge.discover_schema()
                 .from_database()
                 .focus_on(r'^user_.*', 'patterns')
                 .build())
        logger.info(f"Pattern focus: {len(schema.tables)} tables")
        
    except Exception as e:
        logger.error(f"Convenience method examples failed: {e}")


def main():
    """Main function to run all filtering examples."""
    logger = setup_databridge_logger()
    logger.info("Starting DataBridge filtering examples")
    
    # Database connection
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=pocdb;UID=sa;PWD=Two3RobotDuckTag!'
    
    try:
        db_conn = pyodbc.connect(conn_str)
        logger.info("Connected to database successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return

    try:
        # Initialize DataBridge
        bridge = DataBridge(db_conn, logger)
        
        # Run all filtering examples
        demonstrate_table_filtering(bridge, logger)
        print("\n" + "="*80 + "\n")
        
        demonstrate_schema_filtering(bridge, logger)
        print("\n" + "="*80 + "\n")
        
        demonstrate_pattern_filtering(bridge, logger)
        print("\n" + "="*80 + "\n")
        
        demonstrate_combined_filtering(bridge, logger)
        print("\n" + "="*80 + "\n")
        
        demonstrate_query_filtering(bridge, logger)
        print("\n" + "="*80 + "\n")
        
        demonstrate_convenience_methods(bridge, logger)
        
    except Exception as e:
        logger.error(f"Filtering examples failed: {e}")
    finally:
        # Clean up
        db_conn.close()
        logger.info("Filtering examples completed successfully")


if __name__ == "__main__":
    main()
