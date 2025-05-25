"""
Integration test suite for DataBridge.
Tests end-to-end workflows and component integration.
"""
import unittest
import tempfile
import os
import sys
import csv
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.datamodel_service import DataBridge


class TestDataBridgeIntegration(unittest.TestCase):
    """Test DataBridge integration and end-to-end workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_conn = Mock()
        self.mock_logger = Mock()
        
        # Mock database cursor and results
        self.mock_cursor = Mock()
        self.mock_db_conn.cursor.return_value = self.mock_cursor
        
        # Set up mock data for schema extraction
        self.setup_mock_database_responses()
    
    def setup_mock_database_responses(self):
        """Set up mock responses for database queries."""
        # Mock table list
        self.mock_cursor.fetchall.side_effect = [
            # Tables query
            [('customers', 'dbo'), ('orders', 'dbo')],
            # Columns query for customers
            [('customer_id', 'int', 0, 1, None, None)],
            # Columns query for orders  
            [('order_id', 'int', 0, 1, None, None), ('customer_id', 'int', 0, 0, None, None)],
            # Primary keys
            [('customers', 'customer_id'), ('orders', 'order_id')],
            # Foreign keys
            [('customers', 'customer_id', 'orders', 'customer_id')],
            # Indexes
            []
        ]
    
    @patch('core.schema_extractor.SchemaExtractor')
    def test_full_workflow_with_csv_relationships(self, mock_extractor_class):
        """Test complete workflow: extract schema, load relationships, generate query, export."""
        # Setup mock extractor
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        
        # Create a basic schema DTO for mocking
        from core.dtos import SchemaDTO, TableDTO, ColumnDTO
        mock_schema = SchemaDTO(database_name="testdb", tables={}, relationships=[])
        
        # Add mock table
        mock_table = TableDTO(
            name="customers",
            schema="dbo", 
            columns={},
            indexes={},
            primary_keys=["customer_id"]
        )
        mock_schema.tables["customers"] = mock_table
        mock_extractor.extract_schema.return_value = mock_schema
        
        # Create temporary CSV file
        csv_data = [
            ['parent_table', 'child_table', 'parent_columns', 'child_columns', 'relationship_type'],
            ['customers', 'orders', 'customer_id', 'customer_id', 'one-to-many']
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            csv_path = f.name
        
        try:
            # Initialize DataBridge
            bridge = DataBridge(self.mock_db_conn, self.mock_logger)
            
            # Extract schema with relationships
            schema = bridge.extract_full_schema(
                include_db_relationships=True,
                csv_relationships_path=csv_path
            )
            
            # Should return a schema DTO
            self.assertIsNotNone(schema)
            
            # Generate query
            sql = bridge.generate_select_query({'customers': ['customer_id']})
            self.assertIsInstance(sql, str)
            self.assertIn('SELECT', sql.upper())
            
            # Export schema
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as export_file:
                export_path = export_file.name
            
            try:
                bridge.export_schema('yaml', export_path)
                self.assertTrue(os.path.exists(export_path))
            finally:
                if os.path.exists(export_path):
                    os.unlink(export_path)
                    
        finally:
            os.unlink(csv_path)
    
    def test_error_handling_invalid_connection(self):
        """Test error handling with invalid database connection."""
        # Test with None connection
        with self.assertRaises((ValueError, AttributeError)):
            bridge = DataBridge(None, self.mock_logger)
            bridge.extract_full_schema()
      def test_graceful_degradation_no_relationships(self):
        """Test that system works without relationship files."""
        with patch('core.schema_extractor.SchemaExtractor') as mock_extractor_class:
            from core.dtos import SchemaDTO
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            
            mock_schema = SchemaDTO(database_name="testdb", tables={}, relationships=[])
            mock_extractor.extract_schema.return_value = mock_schema
            
            bridge = DataBridge(self.mock_db_conn, self.mock_logger)
            
            # Should work without relationships
            schema = bridge.extract_full_schema(include_db_relationships=False)
            self.assertIsNotNone(schema)
    
    def test_validation_workflow(self):        """Test schema validation workflow."""
        with patch('core.schema_extractor.SchemaExtractor') as mock_extractor_class:
            from core.dtos import SchemaDTO, TableDTO
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            
            mock_schema = SchemaDTO(database_name="testdb", tables={}, relationships=[])
            mock_table = TableDTO(
                name="customers",
                schema="dbo",
                columns={},
                indexes={},
                primary_keys=["customer_id"]
            )
            mock_schema.tables["customers"] = mock_table
            mock_extractor.extract_schema.return_value = mock_schema
            
            bridge = DataBridge(self.mock_db_conn, self.mock_logger)
            bridge._cached_schema = mock_schema
            
            # Test validation
            validation = bridge.validate_schema()
            self.assertIsInstance(validation, dict)
            self.assertIn('is_valid', validation)
    
    def test_relationship_analysis_workflow(self):
        """Test relationship analysis workflow."""        with patch('core.schema_extractor.SchemaExtractor') as mock_extractor_class:
            from core.dtos import SchemaDTO, RelationshipDTO
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            
            mock_schema = SchemaDTO(database_name="testdb", tables={}, relationships=[])
            
            # Add a relationship
            relationship = RelationshipDTO(
                parent_table="customers",
                child_table="orders", 
                parent_columns=["customer_id"],
                child_columns=["customer_id"],
                relationship_type="one-to-many"
            )
            mock_schema.relationships.append(relationship)
            mock_extractor.extract_schema.return_value = mock_schema
            
            bridge = DataBridge(self.mock_db_conn, self.mock_logger)
            bridge._cached_schema = mock_schema
            
            # Test relationship analysis
            rel_info = bridge.get_relationship_info()
            self.assertIsInstance(rel_info, dict)
            self.assertIn('total_relationships', rel_info)
            self.assertIn('top_level_tables', rel_info)
      def test_caching_behavior(self):
        """Test that schema caching works correctly."""
        with patch('core.schema_extractor.SchemaExtractor') as mock_extractor_class:
            from core.dtos import SchemaDTO
            mock_extractor = Mock()
            mock_extractor_class.return_value = mock_extractor
            
            mock_schema = SchemaDTO(database_name="testdb", tables={}, relationships=[])
            mock_extractor.extract_schema.return_value = mock_schema
            
            bridge = DataBridge(self.mock_db_conn, self.mock_logger)
            
            # First call should extract schema
            schema1 = bridge.extract_full_schema()
            
            # Second call should use cached version
            schema2 = bridge.extract_full_schema()
            
            # Should be the same object (cached)
            self.assertIs(schema1, schema2)
            
            # Extractor should only be called once
            self.assertEqual(mock_extractor.extract_schema.call_count, 1)


if __name__ == '__main__':
    unittest.main()
