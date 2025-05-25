"""
DataBridge - Main entry point for the modular SQL database schema analysis utility.

Demonstrates the fluent API for schema discovery, relationship analysis, 
optimized query generation, and multi-format export capabilities.
"""
import os
import pyodbc
from utils.databridge_logger import setup_databridge_logger
from utils.config_loader import load_config
from core.datamodel_service import DataBridge


def demonstrate_databridge():
    """
    Comprehensive demonstration of DataBridge capabilities.
    Shows schema discovery, filtering, query optimization, and export features.
    """
    config = load_config()
    logger = setup_databridge_logger(config)
    
    logger.info("=== DATABRIDGE DEMONSTRATION ===")
    
    # Get database connection
    source_db_conf = config.get('source_database', {})
    connection_string = source_db_conf.get('connection_string')
    
    if not connection_string:
        # Fallback to a default connection for demo
        connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=pocdb;UID=sa;PWD=Two3RobotDuckTag!'
        logger.warning("Using fallback connection string")
    
    try:
        db_conn = pyodbc.connect(connection_string)
        logger.info("Connected to database successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.info("Continuing with limited functionality...")
        db_conn = None

    # Initialize DataBridge
    bridge = DataBridge(db_conn, logger)
    
    # Example 1: Comprehensive Schema Discovery
    if db_conn:
        try:
            logger.info("Discovering schema with advanced filtering...")
            schema = (bridge.discover_schema()
                     .from_database()
                     .excluding_pattern([r'^sys.*', r'^INFORMATION_SCHEMA.*'])
                     .with_relationships_from_csv('data/relationships.csv')
                     .build())
            logger.info(f"Discovered schema with {len(schema.tables)} tables")
            
        except Exception as e:
            logger.error(f"Schema discovery failed: {e}")
            return

        # Example 2: Optimized Query Generation with Index Analysis
        try:
            logger.info("Generating optimized query with index analysis...")
            result = (bridge.generate_query()
                     .select_all()
                     .where({'lender_customer': ['customer_id']})
                     .with_joins()
                     .build())
            
            if isinstance(result, dict) and 'sql' in result:
                sql_query = result['sql']
                query_plan = result.get('plan')
                visualization = result.get('visualization')
                
                logger.info("Generated optimized SQL query:")
                print("\n" + "="*80)
                print("OPTIMIZED SQL QUERY WITH INDEX ANALYSIS:")
                print("="*80)
                print(sql_query)
                print("="*80)
                
                if query_plan:
                    print(f"\nQuery Plan - Estimated Cost: {query_plan.estimated_cost:.0f}")
                    print(f"Join Order: {' -> '.join([f'{p}->{c}' for p, c in query_plan.join_order])}")
                    if query_plan.recommended_indexes:
                        print(f"Recommended Indexes: {len(query_plan.recommended_indexes)}")
                
                if visualization:
                    print("\nQuery Execution Plan Visualization:")
                    print(visualization)
                print("="*80 + "\n")
            else:
                # Fallback for basic query generation
                logger.info("Generated basic SQL query:")
                print("\n" + "="*60)
                print("BASIC SQL QUERY:")
                print("="*60)
                print(result)
                print("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"Query generation failed: {e}")

        # Example 3: Multi-format Schema Export
        try:
            logger.info("Exporting schema to multiple formats...")
            
            os.makedirs('output', exist_ok=True)
            
            # Export to all supported formats
            bridge.export_schema().to_yaml('output/databridge_schema.yaml')
            bridge.export_schema().to_xml('output/databridge_schema.xml')
            bridge.export_schema().to_json('output/databridge_schema.json')
            
            logger.info("Schema exported to YAML, XML, and JSON formats")
            
        except Exception as e:
            logger.error(f"Schema export failed: {e}")

        # Example 4: Advanced Filtering Demonstration
        try:
            logger.info("Demonstrating advanced table filtering...")
            
            # Filter to specific business domains
            filtered_schema = (bridge.discover_schema()
                              .from_database()
                              .only_tables(['users', 'orders', 'products', 'customers'])
                              .with_relationships_from_csv('data/relationships.csv')
                              .build())
            
            logger.info(f"Filtered schema: {len(filtered_schema.tables)} business tables")
            
            # Generate domain-specific query
            domain_query = (bridge.generate_query()
                           .using_schema(filtered_schema)
                           .select_all()
                           .where({'users': ['user_id']})
                           .with_joins()
                           .build())
            
            logger.info("Generated domain-specific query for business tables")
            
        except Exception as e:
            logger.error(f"Advanced filtering demonstration failed: {e}")

        # Example 5: Relationship Analysis
        try:
            logger.info("Analyzing database relationships...")
            
            # Bridge schema operation with comprehensive analysis
            complete_schema = bridge.bridge_schema(
                include_db_relationships=True,
                csv_relationships_path='data/relationships.csv'
            )
            
            # Get detailed relationship information
            rel_info = bridge.get_relationship_info()
            logger.info("Relationship Analysis Results:")
            logger.info(f"  - Total tables: {rel_info['total_tables']}")
            logger.info(f"  - Total relationships: {rel_info['total_relationships']}")
            logger.info(f"  - Top-level tables: {rel_info['top_level_tables']}")
            logger.info(f"  - Tables with children: {len(rel_info['tables_with_children'])}")
            logger.info(f"  - Orphaned tables: {len(rel_info['orphaned_tables'])}")
            
        except Exception as e:
            logger.error(f"Relationship analysis failed: {e}")

        # Example 6: Query Plan Visualization
        try:
            logger.info("Creating query plan visualization...")
            
            # Create graphical visualization if possible
            visualization_path = bridge.query_builder.create_query_plan_visualization(
                schema,
                {'lender_customer': ['customer_id']},
                'output/query_plan_dag.png',
                graphical=True
            )
            
            if visualization_path:
                logger.info(f"Query plan visualization saved to: {visualization_path}")
            
        except Exception as e:
            logger.info(f"Query plan visualization not available: {e}")

        # Clean up
        db_conn.close()

    else:
        logger.info("Skipping database operations due to connection failure")
        logger.info("DataBridge can still work with cached schemas and CSV relationships")
    
    logger.info("=== DATABRIDGE DEMONSTRATION COMPLETED ===")


def main():
    """
    Main entry point for DataBridge demonstration.
    """
    config = load_config()
    logger = setup_databridge_logger(config)
    
    logger.info("Starting DataBridge - Modular SQL Database Schema Analysis Utility")
    
    try:
        demonstrate_databridge()
    except Exception as e:
        logger.error(f"DataBridge demonstration failed: {e}")
    
    logger.info("DataBridge demonstration completed")


if __name__ == "__main__":
    main()
