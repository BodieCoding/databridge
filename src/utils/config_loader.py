"""
Configuration loader for DataBridge.
Handles loading and validating configuration files.
"""
import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """Handles configuration loading and validation."""
    
    def load_config(self, config_path: str = 'config.yaml') -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration structure."""
        # Basic validation - could be expanded
        validated_config = config.copy()
        
        # Ensure required sections exist with defaults
        if 'source_database' not in validated_config:
            validated_config['source_database'] = {}
        
        if 'relationships' not in validated_config:
            validated_config['relationships'] = {
                'include_database_fks': True,
                'csv_path': None
            }
        
        if 'output' not in validated_config:
            validated_config['output'] = {
                'formats': ['yaml'],
                'directory': 'output'
            }
        
        return validated_config
    
    def get_database_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract database configuration."""
        return config.get('source_database', {})
    
    def get_output_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract output configuration."""
        return config.get('output', {})


# Backward compatibility function
def load_config(config_path='config.yaml'):
    """Load configuration (backward compatibility)."""
    loader = ConfigLoader()
    return loader.load_config(config_path)
