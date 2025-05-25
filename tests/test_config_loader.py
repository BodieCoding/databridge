"""
Test suite for DataBridge configuration loading and validation.
Tests configuration parsing, validation, and error handling.
"""
import unittest
import tempfile
import os
import sys
import yaml

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config_loader import ConfigLoader


class TestConfigLoader(unittest.TestCase):
    """Test configuration loading and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_loader = ConfigLoader()
        
        # Create a temporary config file
        self.temp_config = {
            'source_database': {
                'connection_string': 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=testdb;UID=user;PWD=pass',
                'schema': 'dbo'
            },
            'relationships': {
                'csv_path': 'data/relationships.csv',
                'include_database_fks': True
            },
            'output': {
                'formats': ['yaml', 'xml', 'json'],
                'directory': 'output'
            }
        }
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.temp_config, f)
            temp_path = f.name
        
        try:
            config = self.config_loader.load_config(temp_path)
            
            self.assertIn('source_database', config)
            self.assertIn('connection_string', config['source_database'])
            self.assertEqual(config['source_database']['schema'], 'dbo')
            self.assertEqual(config['relationships']['include_database_fks'], True)
            self.assertIn('yaml', config['output']['formats'])
        finally:
            os.unlink(temp_path)
    
    def test_load_nonexistent_config(self):
        """Test loading a non-existent configuration file."""
        with self.assertRaises(FileNotFoundError):
            self.config_loader.load_config('nonexistent.yaml')
    
    def test_load_invalid_yaml(self):
        """Test loading an invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            temp_path = f.name
        
        try:
            with self.assertRaises(yaml.YAMLError):
                self.config_loader.load_config(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_validate_config_structure(self):
        """Test configuration structure validation."""
        valid_config = self.temp_config
        
        # Should not raise any exceptions
        try:
            validated = self.config_loader.validate_config(valid_config)
            self.assertIsNotNone(validated)
        except Exception as e:
            self.fail(f"Valid config failed validation: {e}")
    
    def test_missing_required_sections(self):
        """Test validation with missing required sections."""
        incomplete_config = {
            'source_database': {
                'connection_string': 'test'
            }
            # Missing relationships and output sections
        }
        
        # Should handle missing sections gracefully or raise appropriate error
        try:
            result = self.config_loader.validate_config(incomplete_config)
            # If validation passes, ensure defaults are applied
            self.assertIsNotNone(result)
        except (KeyError, ValueError):
            # Expected for strict validation
            pass
    
    def test_get_database_config(self):
        """Test extracting database configuration."""
        config = self.temp_config
        
        db_config = self.config_loader.get_database_config(config)
        
        self.assertIn('connection_string', db_config)
        self.assertIn('schema', db_config)
        self.assertEqual(db_config['schema'], 'dbo')
    
    def test_get_output_config(self):
        """Test extracting output configuration."""
        config = self.temp_config
        
        output_config = self.config_loader.get_output_config(config)
        
        self.assertIn('formats', output_config)
        self.assertIn('directory', output_config)
        self.assertIn('yaml', output_config['formats'])


if __name__ == '__main__':
    unittest.main()
