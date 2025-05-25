"""
Practical demonstration of DataBridge filtering modifiers using actual database tables.
This shows real-world usage patterns with the tables in our pocdb database.
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
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('getting_started')


def demo_actual_table_filtering(bridge, logger):
    """Demonstrate filtering with actual database tables."""
    logger.info("=== ACTUAL TABLE FILTERING EXAMPLES ===")
    
    # First, let's see all tables
    logger.info("--- All Tables in Database ---")
    all_schema = bridge.discover_schema().from_database().build()
    logger.info(f"Total tables: {len(all_schema.tables)}")
    for table_name in sorted(all_schema.tables.keys()):
        print(f"  ✓ {table_name}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 1: Focus on loan-related tables only
    logger.info("--- Example 1: Focus on Loan Tables Only ---")
    loan_schema = (bridge.discover_schema()
                  .from_database()
                  .matching_pattern(r'^loan_.*')
                  .build())
    logger.info(f"Loan tables: {len(loan_schema.tables)} tables")
    for table_name in sorted(loan_schema.tables.keys()):
        print(f"  ✓ {table_name}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Include only specific tables
    logger.info("--- Example 2: Include Only Core Tables ---")
    core_schema = (bridge.discover_schema()
                  .from_database()
                  .only_tables(['loan_data', 'loan_borrower_data', 'lender_customer'])
                  .build())
    logger.info(f"Core tables: {len(core_schema.tables)} tables")
    for table_name in sorted(core_schema.tables.keys()):
        print(f"  ✓ {table_name}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 3: Exclude comments and scores
    logger.info("--- Example 3: Exclude Comments and Credit Score Data ---")
    main_schema = (bridge.discover_schema()
                  .from_database()
                  .exclude_tables(['loan_comments', 'loan_borrower_creditscore_data'])
                  .build())
    logger.info(f"Main business tables: {len(main_schema.tables)} tables")
    for table_name in sorted(main_schema.tables.keys()):
        print(f"  ✓ {table_name}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 4: Use convenience methods
    logger.info("--- Example 4: Quick Focus and Ignore ---")
    
    # Quick focus on loan data
    quick_focus = bridge.discover_schema().focus_on('loan_data').build()
    logger.info(f"Quick focus on loan_data: {len(quick_focus.tables)} table")
    
    # Quick ignore comments
    no_comments = bridge.discover_schema().ignore('loan_comments').build()
    logger.info(f"Without comments: {len(no_comments.tables)} tables")


def demo_query_filtering(bridge, logger):
    """Demonstrate query generation with table filtering."""
    logger.info("=== QUERY FILTERING EXAMPLES ===")
    
    try:
        # Example 1: Query only loan core tables
        logger.info("--- Example 1: Query Only Core Loan Tables ---")
        query = (bridge.generate_query()
                .select_all()
                .where({'loan_data': ['loan_id']})
                .only_from_tables(['loan_data', 'loan_borrower_data'])
                .build())
        
        print("\n" + "="*60)
        print("FILTERED QUERY (CORE LOAN TABLES):")
        print("="*60)
        print(query)
        print("="*60 + "\n")
        
        # Example 2: Query excluding comments
        logger.info("--- Example 2: Query Excluding Comments ---")
        query = (bridge.generate_query()
                .select_all()
                .where({'loan_data': ['loan_id']})
                .excluding_tables(['loan_comments'])
                .build())
        
        print("\n" + "="*60)
        print("FILTERED QUERY (NO COMMENTS):")
        print("="*60)
        print(query)
        print("="*60 + "\n")
        
        # Example 3: Use pre-filtered schema
        logger.info("--- Example 3: Query with Pre-filtered Schema ---")
        core_schema = (bridge.discover_schema()
                      .from_database()
                      .only_tables(['loan_data', 'loan_borrower_data', 'lender_customer'])
                      .build())
        
        query = (bridge.generate_query()
                .select_all()
                .where({'loan_data': ['loan_id']})
                .using_schema(core_schema)
                .limit_to_filtered_schema()
                .build())
        
        print("\n" + "="*60)
        print("QUERY WITH PRE-FILTERED SCHEMA:")
        print("="*60)
        print(query)
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Query filtering failed: {e}")


def demo_pattern_filtering(bridge, logger):
    """Demonstrate regex pattern filtering."""
    logger.info("=== PATTERN FILTERING EXAMPLES ===")
    
    # Example 1: All tables with 'borrower' in the name
    logger.info("--- Example 1: Tables with 'borrower' ---")
    borrower_schema = (bridge.discover_schema()
                      .from_database()
                      .matching_pattern(r'.*borrower.*')
                      .build())
    logger.info(f"Borrower tables: {len(borrower_schema.tables)} tables")
    for table_name in sorted(borrower_schema.tables.keys()):
        print(f"  ✓ {table_name}")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Exclude data tables (ending with '_data')
    logger.info("--- Example 2: Exclude _data Tables ---")
    no_data_schema = (bridge.discover_schema()
                     .from_database()
                     .excluding_pattern(r'.*_data$')
                     .build())
    logger.info(f"Non-data tables: {len(no_data_schema.tables)} tables")
    for table_name in sorted(no_data_schema.tables.keys()):
        print(f"  ✓ {table_name}")


def demo_combined_filtering(bridge, logger):
    """Demonstrate combining multiple filtering approaches."""
    logger.info("=== COMBINED FILTERING EXAMPLES ===")
    
    # Example: Loan tables but exclude credit score data
    logger.info("--- Example: Loan Tables (No Credit Scores) ---")
    filtered_schema = (bridge.discover_schema()
                      .from_database()
                      .matching_pattern(r'^loan_.*')
                      .exclude_tables(['loan_borrower_creditscore_data'])
                      .with_relationships_from_csv('data/relationships.csv')
                      .build())
    
    logger.info(f"Filtered loan tables: {len(filtered_schema.tables)} tables")
    for table_name in sorted(filtered_schema.tables.keys()):
        print(f"  ✓ {table_name}")


def main():
    """Main demonstration function."""
    logger = setup_databridge_logger()
    logger.info("Starting Practical DataBridge Filtering Demonstration")
    
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
        
        # Run all demonstrations
        demo_actual_table_filtering(bridge, logger)
        print("\n" + "="*80 + "\n")
        
        demo_pattern_filtering(bridge, logger)
        print("\n" + "="*80 + "\n")
        
        demo_combined_filtering(bridge, logger)
        print("\n" + "="*80 + "\n")
        
        demo_query_filtering(bridge, logger)
        
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        db_conn.close()
        logger.info("Practical filtering demonstration completed")


if __name__ == "__main__":
    main()
