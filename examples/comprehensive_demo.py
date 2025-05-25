"""
DataBridge Comprehensive Demonstration

This comprehensive example showcases all major DataBridge capabilities:
- Schema discovery with advanced filtering
- Relationship mapping from multiple sources  
- Query optimization and generation
- Multi-format exports (YAML, XML, JSON)
- Index analysis and performance optimization
- Enterprise workflow patterns
"""
import os
import sys
import logging
import pyodbc

# Add the src directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.datamodel_service import DataBridge


def setup_databridge_logger():
    """Setup DataBridge logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('databridge_comprehensive.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('databridge_comprehensive')


def demonstrate_schema_discovery(db_conn, db_logger):
    """Demonstrate comprehensive schema discovery capabilities."""
    db_logger.info("=== SCHEMA DISCOVERY EXAMPLES ===")
    
    # Initialize DataBridge
    bridge = DataBridge(db_conn, db_logger)
    
    # EXAMPLE 1: Basic schema discovery
    db_logger.info("--- Example 1: Basic Schema Discovery ---")
    try:
        schema = (bridge.discover_schema()
                 .from_database()
                 .build())
        db_logger.info(f"Discovered {len(schema.tables)} tables")
        
        # Show discovered tables
        for table_name in sorted(list(schema.tables.keys())[:5]):  # Show first 5
            table = schema.tables[table_name]
            db_logger.info(f"  ✓ {table_name} ({len(table.columns)} columns)")
        
    except Exception as e:
        db_logger.error(f"Basic schema discovery failed: {e}")

    # EXAMPLE 2: Filtered schema discovery
    db_logger.info("--- Example 2: Advanced Filtering ---")
    try:
        # Filter to specific business tables
        business_schema = (bridge.discover_schema()
                          .from_database()
                          .matching_pattern(r'^(loan|customer|lender).*')
                          .excluding_pattern([r'.*_temp$', r'.*_backup$'])
                          .with_relationships_from_csv('../data/relationships.csv')
                          .build())
        
        db_logger.info(f"Business tables: {len(business_schema.tables)} tables")
        for table_name in sorted(business_schema.tables.keys()):
            db_logger.info(f"  ✓ {table_name}")
        
    except Exception as e:
        db_logger.error(f"Filtered schema discovery failed: {e}")


def demonstrate_query_optimization(db_conn, db_logger):
    """Demonstrate intelligent query generation and optimization."""
    db_logger.info("=== QUERY OPTIMIZATION EXAMPLES ===")
    
    bridge = DataBridge(db_conn, db_logger)
    
    # EXAMPLE 1: Basic query generation
    db_logger.info("--- Example 1: Basic Query Generation ---")
    try:
        query_result = (bridge.generate_query()
                       .select_all()
                       .where({'loan_data': ['loan_id'], 'lender_customer': ['customer_id']})
                       .with_joins()
                       .build())
        
        db_logger.info("Generated optimized SQL query:")
        db_logger.info(f"Query type: {query_result.get('type', 'SELECT')}")
        db_logger.info(f"Tables involved: {len(query_result.get('tables', []))}")
        
        if 'query' in query_result:
            print("\n--- OPTIMIZED QUERY ---")
            print(query_result['query'])
            print("--- END QUERY ---\n")
        
    except Exception as e:
        db_logger.error(f"Basic query generation failed: {e}")


def demonstrate_multi_format_export(db_conn, db_logger):
    """Demonstrate comprehensive export capabilities."""
    db_logger.info("=== MULTI-FORMAT EXPORT EXAMPLES ===")
    
    bridge = DataBridge(db_conn, db_logger)
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # EXAMPLE 1: Standard format exports
    db_logger.info("--- Example 1: Standard Format Exports ---")
    try:
        # Get schema for export
        schema = (bridge.discover_schema()
                 .from_database()
                 .only_tables(['loan_data', 'lender_customer'])
                 .with_relationships_from_database()
                 .build())
        
        # Export to multiple formats using modern API
        bridge.export_schema().to_yaml('output/comprehensive_schema.yaml')
        bridge.export_schema().to_xml('output/comprehensive_schema.xml')  
        bridge.export_schema().to_json('output/comprehensive_schema.json')
        
        db_logger.info("Schema exported to YAML, XML, and JSON formats")
        
        # Verify file sizes
        for format_name in ['yaml', 'xml', 'json']:
            file_path = f'output/comprehensive_schema.{format_name}'
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                db_logger.info(f"  {format_name.upper()}: {size} bytes")
        
    except Exception as e:
        db_logger.error(f"Standard format export failed: {e}")


def demonstrate_enterprise_workflows(db_conn, db_logger):
    """Demonstrate enterprise-level workflow patterns."""
    db_logger.info("=== ENTERPRISE WORKFLOW EXAMPLES ===")
    
    bridge = DataBridge(db_conn, db_logger)
    
    # EXAMPLE 1: Data discovery workflow
    db_logger.info("--- Example 1: Data Discovery Workflow ---")
    try:
        # Step 1: Discover all schemas
        full_discovery = (bridge.discover_schema()
                         .from_database()
                         .excluding_pattern([r'^sys.*', r'^information_schema.*'])
                         .build())
        
        # Step 2: Analyze business critical tables
        business_tables = [name for name in full_discovery.tables.keys() 
                          if any(keyword in name.lower() for keyword in ['loan', 'customer', 'account'])]
        
        db_logger.info(f"Business critical tables identified: {len(business_tables)}")
        
        # Step 3: Deep dive analysis
        if business_tables:
            critical_schema = (bridge.discover_schema()
                              .from_database()
                              .only_tables(business_tables[:10])  # Limit for demo
                              .with_relationships_from_database()
                              .build())
            
            db_logger.info(f"Deep analysis completed for {len(critical_schema.tables)} critical tables")
        
    except Exception as e:
        db_logger.error(f"Data discovery workflow failed: {e}")


def main():
    """Main execution function demonstrating comprehensive DataBridge capabilities."""
    db_logger = setup_databridge_logger()
    db_logger.info("Starting DataBridge Comprehensive Demonstration")
    
    # Database connection configuration
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=pocdb;UID=sa;PWD=Two3RobotDuckTag!'
    
    try:
        db_conn = pyodbc.connect(conn_str)
        db_logger.info("Database connection established successfully")
    except Exception as e:
        db_logger.error(f"Database connection failed: {e}")
        db_logger.info("Some examples will run with limited functionality")
        db_conn = None

    if db_conn:
        try:
            # Demonstrate core capabilities
            demonstrate_schema_discovery(db_conn, db_logger)
            db_logger.info("\n" + "="*80 + "\n")
            
            demonstrate_query_optimization(db_conn, db_logger)  
            db_logger.info("\n" + "="*80 + "\n")
            
            demonstrate_multi_format_export(db_conn, db_logger)
            db_logger.info("\n" + "="*80 + "\n")
            
            demonstrate_enterprise_workflows(db_conn, db_logger)
            
        except Exception as e:
            db_logger.error(f"Comprehensive demonstration failed: {e}")
        finally:
            db_conn.close()
            db_logger.info("Database connection closed")
    
    db_logger.info("DataBridge Comprehensive Demonstration completed successfully")


if __name__ == "__main__":
    main()
