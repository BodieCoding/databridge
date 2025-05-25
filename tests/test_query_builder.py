"""
Test suite for DataBridge Query Builder.
Tests SQL query generation, JOIN logic, and filtering.
"""
import unittest
import sys
import os
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.query_builder import QueryBuilder
from core.dtos import SchemaDTO, TableDTO, ColumnDTO, RelationshipDTO


class TestQueryBuilder(unittest.TestCase):
    """Test query building functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.query_builder = QueryBuilder(self.mock_logger)
          # Create test schema
        self.schema = SchemaDTO(
            database_name="testdb",
            tables={},
            relationships={}
        )

        # Add customers table
        customers_table = TableDTO(
            name="customers",
            schema="dbo",
            columns={},
            indexes=[],
            primary_key=["customer_id"]
        )        customers_table.columns["customer_id"] = ColumnDTO(
            name="customer_id",
            type="int",
            nullable=False,
            ordinal_position=1,
            max_length=None
        )
        customers_table.columns["customer_name"] = ColumnDTO(
            name="customer_name",
            type="varchar",
            nullable=False,
            ordinal_position=2,
            max_length=100
        )
        
        # Add orders table
        orders_table = TableDTO(
            name="orders",
            schema="dbo",
            columns={},
            indexes={},
            primary_keys=["order_id"]
        )
        orders_table.columns["order_id"] = ColumnDTO(
            name="order_id",
            data_type="int",
            is_nullable=False,
            is_primary_key=True,
            default_value=None,
            max_length=None
        )
        orders_table.columns["customer_id"] = ColumnDTO(
            name="customer_id",
            data_type="int",
            is_nullable=False,
            is_primary_key=False,
            default_value=None,
            max_length=None
        )
        
        self.schema.tables["customers"] = customers_table
        self.schema.tables["orders"] = orders_table
        
        # Add relationship
        relationship = RelationshipDTO(
            parent_table="customers",
            child_table="orders",
            parent_columns=["customer_id"],
            child_columns=["customer_id"],
            relationship_type="one-to-many"
        )
        self.schema.relationships.append(relationship)
    
    def test_generate_simple_select(self):
        """Test generating a simple SELECT statement."""
        filter_spec = {'customers': ['customer_id']}
        
        sql = self.query_builder.generate_select_with_joins(self.schema, filter_spec)
        
        self.assertIsInstance(sql, str)
        self.assertIn("SELECT", sql.upper())
        self.assertIn("customers", sql.lower())
        self.assertIn("customer_id", sql.lower())
    
    def test_generate_select_with_joins(self):
        """Test generating SELECT with JOIN statements."""
        filter_spec = {'customers': ['customer_id'], 'orders': ['order_id']}
        
        sql = self.query_builder.generate_select_with_joins(self.schema, filter_spec)
        
        self.assertIsInstance(sql, str)
        self.assertIn("SELECT", sql.upper())
        self.assertIn("JOIN", sql.upper())
        self.assertIn("customers", sql.lower())
        self.assertIn("orders", sql.lower())
    
    def test_build_where_clause_simple(self):
        """Test building simple WHERE clauses."""
        filter_spec = {'customers.customer_id': '123'}
        
        where_clause = self.query_builder.build_where_clause(filter_spec)
        
        self.assertIsInstance(where_clause, str)
        self.assertIn("WHERE", where_clause.upper())
        self.assertIn("customer_id", where_clause.lower())
        self.assertIn("123", where_clause)
    
    def test_build_where_clause_multiple_conditions(self):
        """Test building WHERE clauses with multiple conditions."""
        filter_spec = {
            'customers.customer_id': '123',
            'orders.order_id': '456'
        }
        
        where_clause = self.query_builder.build_where_clause(filter_spec)
        
        self.assertIsInstance(where_clause, str)
        self.assertIn("WHERE", where_clause.upper())
        self.assertIn("AND", where_clause.upper())
        self.assertIn("customer_id", where_clause.lower())
        self.assertIn("order_id", where_clause.lower())
    
    def test_generate_table_aliases(self):
        """Test table alias generation."""
        tables = ["customers", "orders", "products"]
        
        aliases = self.query_builder.generate_table_aliases(tables)
        
        self.assertIsInstance(aliases, dict)
        self.assertEqual(len(aliases), 3)
        self.assertIn("customers", aliases)
        self.assertIn("orders", aliases)
        self.assertIn("products", aliases)
        
        # Check alias format (T1, T2, T3...)
        alias_values = list(aliases.values())
        self.assertTrue(all(alias.startswith('T') for alias in alias_values))
    
    def test_build_join_conditions(self):
        """Test building JOIN conditions from relationships."""
        tables_in_query = ["customers", "orders"]
        
        join_conditions = self.query_builder.build_join_conditions(
            self.schema, tables_in_query
        )
        
        self.assertIsInstance(join_conditions, list)
        self.assertTrue(len(join_conditions) > 0)
        
        # Check that JOIN condition contains table references
        join_str = ' '.join(join_conditions)
        self.assertIn("customers", join_str.lower())
        self.assertIn("orders", join_str.lower())
    
    def test_empty_filter_spec(self):
        """Test handling empty filter specifications."""
        filter_spec = {}
        
        sql = self.query_builder.generate_select_with_joins(self.schema, filter_spec)
        
        self.assertIsInstance(sql, str)
        self.assertIn("SELECT", sql.upper())
        # Should handle gracefully without errors
    
    def test_invalid_table_in_filter(self):
        """Test handling invalid table names in filter."""
        filter_spec = {'nonexistent_table': ['some_column']}
        
        # Should handle gracefully without crashing
        try:
            sql = self.query_builder.generate_select_with_joins(self.schema, filter_spec)
            self.assertIsInstance(sql, str)
        except KeyError:
            # Acceptable to raise KeyError for invalid tables
            pass


if __name__ == '__main__':
    unittest.main()
