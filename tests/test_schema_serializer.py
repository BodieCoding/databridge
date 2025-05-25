"""
Test suite for DataBridge Schema Serializer.
Tests serialization to YAML, XML, and JSON formats.
"""
import unittest
import tempfile
import os
import sys
import json
import yaml
from unittest.mock import Mock

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.schema_serializer import SchemaSerializer
from core.dtos import SchemaDTO, TableDTO, ColumnDTO, RelationshipDTO, RelationshipColumnDTO


class TestSchemaSerializer(unittest.TestCase):
    """Test schema serialization functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_logger = Mock()
        self.serializer = SchemaSerializer(self.mock_logger)
        
        # Create test schema
        self.schema = SchemaDTO(
            database_name="testdb",
            tables={},
            relationships=[]
        )
          # Add test table
        table = TableDTO(
            name="customers",
            schema="dbo",
            columns={},
            indexes=[],
            primary_key=["customer_id"]
        )
          # Add test column
        column = ColumnDTO(
            name="customer_id",
            type="int",
            nullable=False,
            ordinal_position=1
        )
        table.columns["customer_id"] = column
        
        self.schema.tables["customers"] = table
          # Add test relationship
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
        table.relationships.append(relationship)
    
    def test_to_yaml_dict(self):
        """Test converting schema to YAML dictionary format."""
        yaml_dict = self.serializer.to_yaml_dict(self.schema)
        
        self.assertIsInstance(yaml_dict, dict)
        self.assertIn('database_name', yaml_dict)
        self.assertIn('tables', yaml_dict)
        self.assertIn('relationships', yaml_dict)
        
        self.assertEqual(yaml_dict['database_name'], 'testdb')
        self.assertIn('customers', yaml_dict['tables'])
        self.assertEqual(len(yaml_dict['relationships']), 1)
    
    def test_to_xml_dict(self):
        """Test converting schema to XML dictionary format."""
        xml_dict = self.serializer.to_xml_dict(self.schema)
        
        self.assertIsInstance(xml_dict, dict)
        self.assertIn('schema', xml_dict)
        
        schema_element = xml_dict['schema']
        self.assertIn('database_name', schema_element)
        self.assertIn('tables', schema_element)
        self.assertIn('relationships', schema_element)
    
    def test_to_json_dict(self):
        """Test converting schema to JSON dictionary format."""
        json_dict = self.serializer.to_json_dict(self.schema)
        
        self.assertIsInstance(json_dict, dict)
        self.assertIn('database_name', json_dict)
        self.assertIn('tables', json_dict)
        self.assertIn('relationships', json_dict)
        
        # Ensure JSON serializable
        json_str = json.dumps(json_dict)
        self.assertIsInstance(json_str, str)
    
    def test_export_to_yaml_file(self):
        """Test exporting schema to YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_path = f.name
        
        try:
            self.serializer.export_to_file(self.schema, 'yaml', yaml_path)
            
            # Verify file was created
            self.assertTrue(os.path.exists(yaml_path))
            
            # Verify content is valid YAML
            with open(yaml_path, 'r') as f:
                loaded_data = yaml.safe_load(f)
                self.assertIsInstance(loaded_data, dict)
                self.assertIn('database_name', loaded_data)
                self.assertEqual(loaded_data['database_name'], 'testdb')
        finally:
            if os.path.exists(yaml_path):
                os.unlink(yaml_path)
    
    def test_export_to_json_file(self):
        """Test exporting schema to JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name
        
        try:
            self.serializer.export_to_file(self.schema, 'json', json_path)
            
            # Verify file was created
            self.assertTrue(os.path.exists(json_path))
            
            # Verify content is valid JSON
            with open(json_path, 'r') as f:
                loaded_data = json.load(f)
                self.assertIsInstance(loaded_data, dict)
                self.assertIn('database_name', loaded_data)
                self.assertEqual(loaded_data['database_name'], 'testdb')
        finally:
            if os.path.exists(json_path):
                os.unlink(json_path)
    
    def test_export_to_xml_file(self):
        """Test exporting schema to XML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            xml_path = f.name
        
        try:
            self.serializer.export_to_file(self.schema, 'xml', xml_path)
            
            # Verify file was created
            self.assertTrue(os.path.exists(xml_path))
            
            # Verify content is valid XML
            with open(xml_path, 'r') as f:
                content = f.read()
                self.assertIn('<?xml', content)
                self.assertIn('<schema>', content)
                self.assertIn('testdb', content)
        finally:
            if os.path.exists(xml_path):
                os.unlink(xml_path)
    
    def test_unsupported_format(self):
        """Test handling of unsupported export formats."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            txt_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                self.serializer.export_to_file(self.schema, 'txt', txt_path)
        finally:
            if os.path.exists(txt_path):
                os.unlink(txt_path)
    
    def test_table_serialization_completeness(self):
        """Test that table serialization includes all necessary fields."""
        yaml_dict = self.serializer.to_yaml_dict(self.schema)
        
        table_data = yaml_dict['tables']['customers']
        self.assertIn('name', table_data)
        self.assertIn('schema', table_data)
        self.assertIn('columns', table_data)
        self.assertIn('primary_keys', table_data)
        
        # Check column data
        column_data = table_data['columns']['customer_id']
        self.assertIn('name', column_data)
        self.assertIn('data_type', column_data)
        self.assertIn('is_nullable', column_data)
        self.assertIn('is_primary_key', column_data)
    
    def test_relationship_serialization_completeness(self):
        """Test that relationship serialization includes all necessary fields."""
        yaml_dict = self.serializer.to_yaml_dict(self.schema)
        
        relationship_data = yaml_dict['relationships'][0]
        self.assertIn('parent_table', relationship_data)
        self.assertIn('child_table', relationship_data)
        self.assertIn('parent_columns', relationship_data)
        self.assertIn('child_columns', relationship_data)
        self.assertIn('relationship_type', relationship_data)


if __name__ == '__main__':
    unittest.main()
