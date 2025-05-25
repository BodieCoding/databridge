"""
Schema serialization to different formats (YAML, XML, JSON).
Responsible only for converting schema DTOs to various output formats.
"""
from .dtos import SchemaDTO
import yaml
import xml.etree.ElementTree as ET
import json
import logging
from typing import Dict, Any


class SchemaSerializer:
    """Serializes schema DTOs to various formats."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def to_yaml_dict(self, schema: SchemaDTO) -> Dict[str, Any]:
        """Convert SchemaDTO to a dictionary suitable for YAML output."""
        yaml_dict = {
            "database_name": schema.database_name,
            "tables": {},
            "relationships": []
        }
        
        # Collect all relationships globally
        all_relationships = []
        
        for table_name, table in schema.tables.items():
            # Sort columns by ordinal_position
            sorted_columns = sorted(table.columns.values(), key=lambda c: c.ordinal_position)
            columns_dict = {}
            
            for col in sorted_columns:
                # Check if this column is a primary key
                is_primary_key = col.name in table.primary_key
                
                col_dict = {
                    "name": col.name,
                    "data_type": col.type,
                    "is_nullable": col.nullable,
                    "is_primary_key": is_primary_key,
                    "ordinal_position": col.ordinal_position
                }
                if col.max_length is not None:
                    col_dict["max_length"] = col.max_length
                if col.precision is not None:
                    col_dict["precision"] = col.precision
                if col.scale is not None:
                    col_dict["scale"] = col.scale
                columns_dict[col.name] = col_dict
            
            # Indexes
            indexes = []
            for idx in table.indexes:
                indexes.append({
                    "name": idx.name,
                    "type": idx.type,
                    "columns": idx.columns
                })
            
            # Add relationships to global list with expected format
            for rel in table.relationships:
                # Convert to expected format
                parent_columns = []
                child_columns = []
                for col_dto in rel.columns:
                    parent_columns.append(col_dto.from_column)
                    child_columns.append(col_dto.to_column)
                
                all_relationships.append({
                    "parent_table": rel.from_table,
                    "child_table": rel.to_table,
                    "relationship_type": rel.relationship_type,
                    "parent_columns": parent_columns,
                    "child_columns": child_columns
                })
            
            table_dict = {
                "name": table_name,
                "schema": table.schema,
                "columns": columns_dict,
                "primary_keys": table.primary_key,  # Note: plural as expected by test
                "indexes": indexes
            }
                
            yaml_dict["tables"][table_name] = table_dict
        
        # Add global relationships from table relationships
        yaml_dict["relationships"] = all_relationships
        
        # Also add any schema-level relationships
        if schema.relationships:
            for rel_list in schema.relationships.values():
                for rel in rel_list:
                    parent_columns = []
                    child_columns = []
                    for col_dto in rel.columns:
                        parent_columns.append(col_dto.from_column)
                        child_columns.append(col_dto.to_column)
                    
                    yaml_dict["relationships"].append({
                        "parent_table": rel.from_table,
                        "child_table": rel.to_table,
                        "relationship_type": rel.relationship_type,
                        "parent_columns": parent_columns,
                        "child_columns": child_columns
                    })
        
        return yaml_dict

    def to_yaml_file(self, schema: SchemaDTO, file_path: str):
        """Write schema to YAML file."""
        self.logger.info(f"Writing schema to YAML file: {file_path}")
        
        yaml_dict = self.to_yaml_dict(schema)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_dict, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
            self.logger.info(f"YAML schema written successfully to {file_path}")
        except Exception as e:
            self.logger.error(f"Error writing YAML file: {e}")
            raise

    def to_xml_dict(self, schema: SchemaDTO) -> Dict[str, Any]:
        """Convert SchemaDTO to a dictionary suitable for XML output."""
        xml_dict = {
            "schema": {
                "database_name": schema.database_name,
                "tables": [],
                "relationships": []
            }
        }
        
        # Collect all relationships globally
        all_relationships = []
        
        for table_name, table in schema.tables.items():
            # Sort columns by ordinal_position
            sorted_columns = sorted(table.columns.values(), key=lambda c: c.ordinal_position)
            columns_list = []
            
            for col in sorted_columns:
                # Check if this column is a primary key
                is_primary_key = col.name in table.primary_key
                
                col_dict = {
                    "@name": col.name,
                    "@data_type": col.type,
                    "@is_nullable": str(col.nullable).lower(),
                    "@is_primary_key": str(is_primary_key).lower(),
                    "@ordinal_position": col.ordinal_position
                }
                if col.max_length is not None:
                    col_dict["@max_length"] = col.max_length
                if col.precision is not None:
                    col_dict["@precision"] = col.precision
                if col.scale is not None:
                    col_dict["@scale"] = col.scale
                columns_list.append(col_dict)
            
            # Indexes
            indexes_list = []
            for idx in table.indexes:
                indexes_list.append({
                    "@name": idx.name,
                    "@type": idx.type,
                    "columns": [{"@name": col} for col in idx.columns]
                })
            
            # Add relationships to global list
            for rel in table.relationships:
                parent_columns = []
                child_columns = []
                for col_dto in rel.columns:
                    parent_columns.append(col_dto.from_column)
                    child_columns.append(col_dto.to_column)
                
                all_relationships.append({
                    "@parent_table": rel.from_table,
                    "@child_table": rel.to_table,
                    "@relationship_type": rel.relationship_type,
                    "parent_columns": [{"@name": col} for col in parent_columns],
                    "child_columns": [{"@name": col} for col in child_columns]
                })
            
            table_dict = {
                "@name": table_name,
                "@schema": table.schema or "",
                "columns": columns_list,
                "primary_keys": [{"@name": pk} for pk in table.primary_key],
                "indexes": indexes_list
            }
                
            xml_dict["schema"]["tables"].append(table_dict)
        
        # Add global relationships
        xml_dict["schema"]["relationships"] = all_relationships
        
        # Also add any schema-level relationships
        if schema.relationships:
            for rel_list in schema.relationships.values():
                for rel in rel_list:
                    parent_columns = []
                    child_columns = []
                    for col_dto in rel.columns:
                        parent_columns.append(col_dto.from_column)
                        child_columns.append(col_dto.to_column)
                    
                    xml_dict["schema"]["relationships"].append({
                        "@parent_table": rel.from_table,
                        "@child_table": rel.to_table,
                        "@relationship_type": rel.relationship_type,
                        "parent_columns": [{"@name": col} for col in parent_columns],
                        "child_columns": [{"@name": col} for col in child_columns]
                    })
          return xml_dict

    def to_xml_file(self, schema: SchemaDTO, file_path: str):
        """Write schema to XML file."""
        self.logger.info(f"Writing schema to XML file: {file_path}")
        
        xml_dict = self.to_xml_dict(schema)
        
        try:
            root = ET.Element("schema")
            
            # Don't add database name as attribute - keep it in content instead
            
            # Add tables
            for table in xml_dict["schema"]["tables"]:
                table_elem = ET.SubElement(root, "table", {k[1:]: str(v) for k, v in table.items() if k.startswith("@")})
                
                # Columns
                columns_elem = ET.SubElement(table_elem, "columns")
                for col in table["columns"]:
                    ET.SubElement(columns_elem, "column", {k[1:]: str(v) for k, v in col.items() if k.startswith("@")})
                
                # Primary Key
                pk_elem = ET.SubElement(table_elem, "primary_keys")
                for pk in table["primary_keys"]:
                    ET.SubElement(pk_elem, "column", {k[1:]: str(v) for k, v in pk.items() if k.startswith("@")})
                
                # Indexes
                indexes_elem = ET.SubElement(table_elem, "indexes")
                for idx in table["indexes"]:
                    idx_elem = ET.SubElement(indexes_elem, "index", {k[1:]: str(v) for k, v in idx.items() if k.startswith("@")})
                    for col in idx["columns"]:
                        ET.SubElement(idx_elem, "column", {k[1:]: str(v) for k, v in col.items() if k.startswith("@")})
            
            # Add relationships
            rels_elem = ET.SubElement(root, "relationships")
            for rel in xml_dict["schema"]["relationships"]:
                rel_elem = ET.SubElement(rels_elem, "relationship", {k[1:]: str(v) for k, v in rel.items() if k.startswith("@")})
                
                # Parent columns
                parent_cols_elem = ET.SubElement(rel_elem, "parent_columns")
                for col in rel["parent_columns"]:
                    ET.SubElement(parent_cols_elem, "column", {k[1:]: str(v) for k, v in col.items() if k.startswith("@")})
                
                # Child columns
                child_cols_elem = ET.SubElement(rel_elem, "child_columns")
                for col in rel["child_columns"]:
                    ET.SubElement(child_cols_elem, "column", {k[1:]: str(v) for k, v in col.items() if k.startswith("@")})
            
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            self.logger.info(f"XML schema written successfully to {file_path}")
        except Exception as e:
            self.logger.error(f"Error writing XML file: {e}")
            raise

    def to_json_dict(self, schema: SchemaDTO) -> Dict[str, Any]:
        """Convert SchemaDTO to a dictionary suitable for JSON output."""
        # JSON format matches YAML format
        return self.to_yaml_dict(schema)

    def to_json_file(self, schema: SchemaDTO, file_path: str):
        """Write schema to JSON file."""
        self.logger.info(f"Writing schema to JSON file: {file_path}")
        
        json_dict = self.to_json_dict(schema)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_dict, f, indent=2, ensure_ascii=False)
            self.logger.info(f"JSON schema written successfully to {file_path}")
        except Exception as e:
            self.logger.error(f"Error writing JSON file: {e}")
            raise

    def export_to_file(self, schema: SchemaDTO, format: str, file_path: str):
        """Export schema to file in specified format."""
        format = format.lower()
        
        if format == 'yaml':
            self.to_yaml_file(schema, file_path)
        elif format == 'json':
            self.to_json_file(schema, file_path)
        elif format == 'xml':
            self.to_xml_file(schema, file_path)
        else:
            raise ValueError(f"Unsupported format: {format}. Supported formats: yaml, json, xml")

    def from_yaml_file(self, file_path: str) -> SchemaDTO:
        """Load schema from YAML file."""
        self.logger.info(f"Loading schema from YAML file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Convert YAML data back to SchemaDTO
            # This would require implementing the reverse conversion
            # For now, this is a placeholder
            self.logger.warning("Loading from YAML file not yet implemented")
            return SchemaDTO()
        except Exception as e:
            self.logger.error(f"Error reading YAML file: {e}")
            raise
