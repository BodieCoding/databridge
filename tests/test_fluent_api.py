"""
Test suite for the DataBridge fluent API.
Validates that all fluent methods are accessible and follow naming conventions.
"""
import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.datamodel_service import DataBridge


class TestFluentAPI(unittest.TestCase):
    """Test the fluent API functionality and naming conventions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_conn = Mock()
        self.mock_logger = Mock()
        self.bridge = DataBridge(self.mock_db_conn, self.mock_logger)
    
    def test_main_class_renamed_correctly(self):
        """Test that main class follows DataBridge naming."""
        # Test DataBridge class
        self.assertIsInstance(self.bridge, DataBridge)
        self.assertEqual(self.bridge.__class__.__name__, 'DataBridge')
    
    def test_fluent_schema_discovery_methods_exist(self):
        """Test that all schema discovery fluent methods exist."""
        schema_discovery = self.bridge.discover_schema()
        
        # Core fluent methods
        self.assertTrue(hasattr(schema_discovery, 'from_database'))
        self.assertTrue(hasattr(schema_discovery, 'with_relationships_from_csv'))
        self.assertTrue(hasattr(schema_discovery, 'with_relationships_from_database'))
        self.assertTrue(hasattr(schema_discovery, 'build'))
        
        # Filtering methods
        self.assertTrue(hasattr(schema_discovery, 'only_tables'))
        self.assertTrue(hasattr(schema_discovery, 'exclude_tables'))
        self.assertTrue(hasattr(schema_discovery, 'only_schemas'))
        self.assertTrue(hasattr(schema_discovery, 'exclude_schemas'))
        self.assertTrue(hasattr(schema_discovery, 'matching_pattern'))
        self.assertTrue(hasattr(schema_discovery, 'excluding_pattern'))
    
    def test_fluent_query_generation_methods_exist(self):
        """Test that all query generation fluent methods exist."""
        query_bridge = self.bridge.generate_query()
        
        # Core query methods
        self.assertTrue(hasattr(query_bridge, 'select_all'))
        self.assertTrue(hasattr(query_bridge, 'where'))
        self.assertTrue(hasattr(query_bridge, 'with_joins'))
        self.assertTrue(hasattr(query_bridge, 'build'))
        
        # Filtering methods
        self.assertTrue(hasattr(query_bridge, 'only_from_tables'))
        self.assertTrue(hasattr(query_bridge, 'excluding_tables'))
    
    def test_fluent_export_methods_exist(self):
        """Test that all export fluent methods exist."""
        export_bridge = self.bridge.export_schema_fluent()
        
        # Export format methods
        self.assertTrue(hasattr(export_bridge, 'to_yaml'))
        self.assertTrue(hasattr(export_bridge, 'to_xml'))
        self.assertTrue(hasattr(export_bridge, 'to_json'))
    
    def test_convenience_bridge_methods_exist(self):
        """Test that convenience bridge methods exist and follow naming."""
        # Bridge operations
        self.assertTrue(hasattr(self.bridge, 'bridge_schema'))
        self.assertTrue(hasattr(self.bridge, 'bridge_query'))
        self.assertTrue(hasattr(self.bridge, 'bridge_to_format'))
      def test_modern_api_methods_exist(self):
        """Test that all modern API methods exist (backward compatibility removed)."""
        # Modern fluent API methods
        self.assertTrue(hasattr(self.bridge, 'discover_schema'))
        self.assertTrue(hasattr(self.bridge, 'generate_query'))
        self.assertTrue(hasattr(self.bridge, 'export_schema_fluent'))
        
        # Bridge convenience methods
        self.assertTrue(hasattr(self.bridge, 'bridge_schema'))
        self.assertTrue(hasattr(self.bridge, 'bridge_query'))
        self.assertTrue(hasattr(self.bridge, 'bridge_to_format'))
    
    def test_fluent_method_chaining_returns_builders(self):
        """Test that fluent methods return appropriate builder objects."""
        # Schema discovery should return SchemaDiscovery builder
        schema_discovery = self.bridge.discover_schema()
        self.assertEqual(schema_discovery.__class__.__name__, 'SchemaDiscovery')
        
        # Query generation should return QueryBridge builder
        query_bridge = self.bridge.generate_query()
        self.assertEqual(query_bridge.__class__.__name__, 'QueryBridge')
        
        # Export should return ExportBridge builder
        export_bridge = self.bridge.export_schema_fluent()
        self.assertEqual(export_bridge.__class__.__name__, 'ExportBridge')
    
    def test_filtering_aliases_exist(self):
        """Test that filtering method aliases exist for natural reading."""
        schema_discovery = self.bridge.discover_schema()
        
        # Table filtering aliases
        self.assertTrue(hasattr(schema_discovery, 'include_tables'))  # alias for only_tables
        self.assertTrue(hasattr(schema_discovery, 'without_tables'))  # alias for exclude_tables
        
        # Schema filtering aliases
        self.assertTrue(hasattr(schema_discovery, 'without_schemas'))  # alias for exclude_schemas
        
        # Pattern filtering aliases
        self.assertTrue(hasattr(schema_discovery, 'without_pattern'))  # alias for excluding_pattern
        
        # Convenience aliases
        self.assertTrue(hasattr(schema_discovery, 'focus_on'))
        self.assertTrue(hasattr(schema_discovery, 'ignore'))


if __name__ == '__main__':
    unittest.main()
