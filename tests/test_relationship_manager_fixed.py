"""
Test suite for DataBridge Relationship Manager.
Tests relationship loading, graph building, and analysis.
"""
import unittest
import tempfile
import csv
import sys
import os
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.relationship_manager import RelationshipManager
from core.dtos import SchemaDTO, TableDTO, ColumnDTO, RelationshipDTO, RelationshipColumnDTO


class TestRelationshipManager(unittest.TestCase):
    """Test relationship management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.relationship_manager = RelationshipManager(self.mock_logger)
        
        # Create test schema
        self.schema = SchemaDTO(
            database_name="testdb",
            tables={},
            relationships={}
        )
        
        # Add test tables
        customers_table = TableDTO(
            name="customers",
            schema="dbo",
            columns={},
            indexes=[],
            primary_key=["customer_id"]
        )
        
        orders_table = TableDTO(
            name="orders",
            schema="dbo",
            columns={},
            indexes=[],
            primary_key=["order_id"]
        )
        
        self.schema.tables["customers"] = customers_table
        self.schema.tables["orders"] = orders_table
    
    def test_load_relationships_from_csv(self):
        """Test loading relationships from CSV file."""
        # Create temporary CSV file
        csv_data = [
            ['from_table', 'to_table', 'relationship_type', 'from_column', 'to_column'],
            ['orders', 'customers', 'many-to-one', 'customer_id', 'customer_id']
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            csv_path = f.name
        
        try:
            updated_schema = self.relationship_manager.load_from_csv(self.schema, csv_path)
            
            self.assertIsInstance(updated_schema, SchemaDTO)
            # Check that the relationship was added to the orders table
            self.assertEqual(len(updated_schema.tables['orders'].relationships), 1)
            
            relationship = updated_schema.tables['orders'].relationships[0]
            self.assertEqual(relationship.from_table, 'orders')
            self.assertEqual(relationship.to_table, 'customers')
            self.assertEqual(len(relationship.columns), 1)
            self.assertEqual(relationship.columns[0].from_column, 'customer_id')
            self.assertEqual(relationship.columns[0].to_column, 'customer_id')
        finally:
            os.unlink(csv_path)
    
    def test_load_relationships_nonexistent_file(self):
        """Test loading relationships from non-existent CSV file."""
        # The load_from_csv method returns the original schema if file is not found
        # It doesn't raise FileNotFoundError based on the implementation
        result = self.relationship_manager.load_from_csv(self.schema, 'nonexistent.csv')
        self.assertEqual(result, self.schema)
    
    def test_build_relationship_graph(self):
        """Test building relationship graph from schema."""
        # Add a relationship to the orders table
        relationship_column = RelationshipColumnDTO(
            from_column="customer_id",
            to_column="customer_id"
        )
        relationship = RelationshipDTO(
            from_table="orders",
            to_table="customers",
            relationship_type="many-to-one",
            columns=[relationship_column]
        )
        self.schema.tables["orders"].relationships.append(relationship)
        
        graph = self.relationship_manager.build_relationship_graph(self.schema)
        
        self.assertIsNotNone(graph)
        # Graph should contain both tables
        self.assertIn("customers", graph.nodes())
        self.assertIn("orders", graph.nodes())
        
        # Should have edge between tables
        self.assertTrue(graph.has_edge("orders", "customers"))
    
    def test_find_top_level_tables(self):
        """Test finding top-level tables in relationship hierarchy."""
        # Add relationship - orders references customers
        relationship_column = RelationshipColumnDTO(
            from_column="customer_id",
            to_column="customer_id"
        )
        relationship = RelationshipDTO(
            from_table="orders",
            to_table="customers",
            relationship_type="many-to-one",
            columns=[relationship_column]
        )
        self.schema.tables["orders"].relationships.append(relationship)
        
        top_level_tables = self.relationship_manager.find_top_level_tables(self.schema)
        
        self.assertIsInstance(top_level_tables, list)
        self.assertIn("customers", top_level_tables)
        # Orders should not be top-level since it references customers
        self.assertNotIn("orders", top_level_tables)
    
    def test_get_table_children(self):
        """Test getting child tables for a given table."""
        # Add relationship - orders references customers, so customers has orders as children
        relationship_column = RelationshipColumnDTO(
            from_column="customer_id",
            to_column="customer_id"
        )
        relationship = RelationshipDTO(
            from_table="orders",
            to_table="customers",
            relationship_type="many-to-one",
            columns=[relationship_column]
        )
        self.schema.tables["orders"].relationships.append(relationship)
        
        children = self.relationship_manager.get_table_children(self.schema, "customers")
        
        self.assertIsInstance(children, list)
        self.assertIn("orders", children)
    
    def test_get_table_parents(self):
        """Test getting parent tables for a given table."""
        # Add relationship - orders references customers, so orders has customers as parent
        relationship_column = RelationshipColumnDTO(
            from_column="customer_id",
            to_column="customer_id"
        )
        relationship = RelationshipDTO(
            from_table="orders",
            to_table="customers",
            relationship_type="many-to-one",
            columns=[relationship_column]
        )
        self.schema.tables["orders"].relationships.append(relationship)
        
        parents = self.relationship_manager.get_table_parents(self.schema, "orders")
        
        self.assertIsInstance(parents, list)
        self.assertIn("customers", parents)
    
    def test_validate_relationships(self):
        """Test relationship validation."""
        # Add valid relationship
        relationship_column = RelationshipColumnDTO(
            from_column="customer_id",
            to_column="customer_id"
        )
        relationship = RelationshipDTO(
            from_table="orders",
            to_table="customers",
            relationship_type="many-to-one",
            columns=[relationship_column]
        )
        self.schema.tables["orders"].relationships.append(relationship)
        
        validation = self.relationship_manager.validate_relationships(self.schema)
        
        self.assertIsInstance(validation, dict)
        self.assertIn('is_valid', validation)
        self.assertTrue(validation['is_valid'])
    
    def test_malformed_csv_handling(self):
        """Test handling of malformed CSV files."""
        # Create CSV with missing columns
        csv_data = [
            ['from_table', 'to_table'],  # Missing required columns
            ['orders', 'customers']
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            csv_path = f.name
        
        try:
            # Should handle gracefully and return original schema
            result = self.relationship_manager.load_from_csv(self.schema, csv_path)
            self.assertEqual(result, self.schema)
        finally:
            os.unlink(csv_path)


if __name__ == '__main__':
    unittest.main()
