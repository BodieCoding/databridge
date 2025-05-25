"""
Test suite for DataBridge DTOs and data structures.
Validates data transfer objects and their validation logic.
"""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.dtos import SchemaDTO, TableDTO, ColumnDTO, RelationshipDTO, IndexDTO


class TestDTOs(unittest.TestCase):
    """Test DataBridge DTO classes and their validation."""
    
    def test_column_dto_creation(self):
        """Test ColumnDTO creation and validation."""
        column = ColumnDTO(
            name="customer_id",
            type="int",
            nullable=False,
            ordinal_position=1,
            max_length=None
        )
        
        self.assertEqual(column.name, "customer_id")
        self.assertEqual(column.type, "int")
        self.assertFalse(column.nullable)
        self.assertEqual(column.ordinal_position, 1)
    
    def test_table_dto_creation(self):
        """Test TableDTO creation and column management."""
        table = TableDTO(
            name="customers",
            schema="dbo",
            columns={},
            indexes=[],
            primary_key=[]
        )
        
        # Add column
        column = ColumnDTO(
            name="id",
            type="int",
            nullable=False,
            ordinal_position=1,
            max_length=None
        )
        table.columns["id"] = column
        
        self.assertEqual(table.name, "customers")
        self.assertEqual(table.schema, "dbo")
        self.assertIn("id", table.columns)
        self.assertEqual(table.columns["id"].name, "id")
    
    def test_relationship_dto_creation(self):
        """Test RelationshipDTO creation and validation."""
        relationship = RelationshipDTO(
            from_table="orders",
            to_table="customers",
            relationship_type="many-to-one"
        )
        
        self.assertEqual(relationship.from_table, "orders")
        self.assertEqual(relationship.to_table, "customers")
        self.assertEqual(relationship.relationship_type, "many-to-one")
    
    def test_schema_dto_creation(self):
        """Test SchemaDTO creation and table management."""
        schema = SchemaDTO(
            database_name="testdb",
            tables={},
            relationships={}
        )
        
        # Add table
        table = TableDTO(
            name="customers",
            schema="dbo",
            columns={},
            indexes=[],
            primary_key=[]
        )
        schema.tables["customers"] = table
        
        self.assertEqual(schema.database_name, "testdb")
        self.assertIn("customers", schema.tables)
        self.assertEqual(len(schema.relationships), 0)
    
    def test_index_dto_creation(self):
        """Test IndexDTO creation and validation."""
        index = IndexDTO(
            name="IX_customer_name",
            type="nonclustered",
            columns=["last_name", "first_name"]
        )
        
        self.assertEqual(index.name, "IX_customer_name")
        self.assertEqual(index.type, "nonclustered")
        self.assertEqual(index.columns, ["last_name", "first_name"])


if __name__ == '__main__':
    unittest.main()
