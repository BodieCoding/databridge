"""
Relationship management for database schemas.
Handles loading relationships from various sources and managing relationship data.
"""
from .dtos import SchemaDTO, RelationshipDTO, RelationshipColumnDTO
import csv
import logging
from collections import defaultdict
from typing import Dict, List


class RelationshipManager:
    """Manages relationships between tables in a schema."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def load_from_csv(self, schema_dto: SchemaDTO, csv_path: str) -> SchemaDTO:
        """
        Loads relationships from a CSV file and adds them to the schema_dto.
        CSV columns: from_table,to_table,relationship_type,from_column,to_column,ordinal (ordinal optional)
        """
        self.logger.info(f"Loading relationships from CSV: {csv_path}")
        
        # Group by (from_table, to_table, relationship_type) to handle multi-column joins
        rel_map = defaultdict(list)
        
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    from_table = row['from_table']
                    to_table = row['to_table']
                    rel_type = row.get('relationship_type', 'unknown')
                    from_column = row['from_column']
                    to_column = row['to_column']
                    ordinal = int(row['ordinal']) if 'ordinal' in row and row['ordinal'] else None
                    
                    rel_map[(from_table, to_table, rel_type)].append(
                        RelationshipColumnDTO(
                            from_column=from_column, 
                            to_column=to_column, 
                            ordinal=ordinal
                        )
                    )
        except FileNotFoundError:
            self.logger.error(f"Relationship CSV file not found: {csv_path}")
            return schema_dto
        except Exception as e:
            self.logger.error(f"Error reading relationships CSV: {e}")
            return schema_dto
        
        # Add RelationshipDTOs to the from_table's relationships
        for (from_table, to_table, rel_type), columns in rel_map.items():
            rel_dto = RelationshipDTO(
                from_table=from_table,
                to_table=to_table,
                relationship_type=rel_type,
                columns=sorted(columns, key=lambda c: c.ordinal if c.ordinal is not None else 0)
            )
            
            if from_table in schema_dto.tables:
                schema_dto.tables[from_table].relationships.append(rel_dto)
                self.logger.debug(
                    f"Added relationship: {from_table} -> {to_table} ({rel_type}) "
                    f"with columns {[(c.from_column, c.to_column) for c in columns]}"
                )
            else:
                self.logger.warning(f"Table '{from_table}' from relationships CSV not found in schema.")
        
        self.logger.info(f"Loaded {len(rel_map)} relationships from CSV")
        return schema_dto

    def extract_from_database(self, schema_dto: SchemaDTO, db_conn) -> SchemaDTO:
        """
        Extracts foreign key relationships directly from the database.
        """
        self.logger.info("Extracting relationships from database foreign keys")
        cursor = db_conn.cursor()
        
        for table_name in schema_dto.tables.keys():
            cursor.execute("""
                SELECT
                    kcu.table_name AS child_table,
                    kcu.column_name AS child_column,
                    ccu.table_name AS parent_table,
                    ccu.column_name AS parent_column
                FROM information_schema.referential_constraints rc
                JOIN information_schema.key_column_usage kcu
                  ON rc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                  ON rc.unique_constraint_name = ccu.constraint_name
                WHERE kcu.table_name = ?
            """, table_name)
            
            # Group by parent table to handle multi-column foreign keys
            parent_relationships = defaultdict(list)
            for row in cursor.fetchall():
                parent_table = row.parent_table
                parent_relationships[parent_table].append(
                    RelationshipColumnDTO(
                        from_column=row.child_column,
                        to_column=row.parent_column,
                        ordinal=None
                    )
                )
            
            # Create RelationshipDTO for each parent
            for parent_table, columns in parent_relationships.items():
                rel_dto = RelationshipDTO(
                    from_table=table_name,
                    to_table=parent_table,
                    relationship_type="many-to-one",  # Default for FK relationships
                    columns=columns
                )
                schema_dto.tables[table_name].relationships.append(rel_dto)
        
        return schema_dto

    def build_relationship_graph(self, schema_dto: SchemaDTO):
        """
        Builds a relationship graph from the schema using networkx.
        Returns: networkx.DiGraph object
        """
        try:
            import networkx as nx
        except ImportError:
            self.logger.warning("networkx not available, returning simple dict representation")
            # Fallback to simple dict
            parent_to_child = defaultdict(list)
            
            for table_name, table_dto in schema_dto.tables.items():
                for relationship in table_dto.relationships:
                    parent_table = relationship.to_table
                    parent_to_child[parent_table].append((table_name, relationship))
            
            return dict(parent_to_child)
        
        # Create directed graph with networkx
        graph = nx.DiGraph()
        
        # Add all tables as nodes
        for table_name in schema_dto.tables.keys():
            graph.add_node(table_name)
        
        # Add relationships as edges
        for table_name, table_dto in schema_dto.tables.items():
            for relationship in table_dto.relationships:
                graph.add_edge(
                    relationship.to_table,  # parent (from)
                    table_name,             # child (to)
                    relationship=relationship
                )
        
        return graph

    def find_top_level_tables(self, schema_dto: SchemaDTO) -> List[str]:
        """
        Find tables that are not referenced by any other table (top-level in hierarchy).
        """
        referenced_tables = set()
        
        for table_dto in schema_dto.tables.values():
            for relationship in table_dto.relationships:
                referenced_tables.add(relationship.to_table)
        
        all_tables = set(schema_dto.tables.keys())
        top_tables = list(all_tables - referenced_tables)
        
        if not top_tables:
            self.logger.warning("No top-level tables found. This might indicate circular references.")
            # Return all tables as a fallback
            return list(all_tables)
        
        return top_tables

    def get_table_children(self, schema_dto: SchemaDTO, table_name: str) -> List[str]:
        """
        Get all child tables (tables that reference this table) for a given table.
        """
        children = []
        
        for other_table_name, table_dto in schema_dto.tables.items():
            for relationship in table_dto.relationships:
                if relationship.to_table == table_name:
                    children.append(other_table_name)
        
        return children

    def get_table_parents(self, schema_dto: SchemaDTO, table_name: str) -> List[str]:
        """
        Get all parent tables (tables that this table references) for a given table.
        """
        parents = []
        
        if table_name in schema_dto.tables:
            table_dto = schema_dto.tables[table_name]
            for relationship in table_dto.relationships:
                parents.append(relationship.to_table)
        
        return parents    def validate_relationships(self, schema_dto: SchemaDTO) -> Dict[str, any]:
        """
        Validate relationships in the schema and return validation results.
        Returns: {
            'is_valid': boolean,
            'valid': [list of valid relationship descriptions],
            'invalid': [list of invalid relationship descriptions],
            'warnings': [list of warning messages]
        }
        """
        validation_result = {
            'valid': [],
            'invalid': [],
            'warnings': []
        }
        
        for table_name, table_dto in schema_dto.tables.items():
            for relationship in table_dto.relationships:
                # Check if referenced table exists
                if relationship.to_table not in schema_dto.tables:
                    validation_result['invalid'].append(
                        f"Table '{table_name}' references non-existent table '{relationship.to_table}'"
                    )
                    continue
                
                # Check if referenced columns exist
                to_table_dto = schema_dto.tables[relationship.to_table]
                from_table_dto = table_dto
                
                valid_relationship = True
                for rel_column in relationship.columns:
                    # Check from_column exists in from_table
                    if rel_column.from_column not in from_table_dto.columns:
                        validation_result['invalid'].append(
                            f"Column '{rel_column.from_column}' not found in table '{table_name}'"
                        )
                        valid_relationship = False
                    
                    # Check to_column exists in to_table
                    if rel_column.to_column not in to_table_dto.columns:
                        validation_result['invalid'].append(
                            f"Column '{rel_column.to_column}' not found in table '{relationship.to_table}'"
                        )
                        valid_relationship = False
                
                if valid_relationship:
                    validation_result['valid'].append(
                        f"Valid relationship: {table_name}.{[c.from_column for c in relationship.columns]} -> "
                        f"{relationship.to_table}.{[c.to_column for c in relationship.columns]}"
                    )
        
        # Add is_valid boolean field
        validation_result['is_valid'] = len(validation_result['invalid']) == 0
        
        return validation_result