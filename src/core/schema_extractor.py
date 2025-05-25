"""
Schema extraction from database.
Responsible only for fetching raw schema metadata from the database.
"""
from .dtos import SchemaDTO, TableDTO, ColumnDTO, IndexDTO
import logging


class SchemaExtractor:
    """Extracts schema metadata from database connections."""
    
    def __init__(self, db_conn, logger=None):
        self.db_conn = db_conn
        self.logger = logger or logging.getLogger(__name__)

    def extract_schema(self) -> SchemaDTO:
        """
        Fetches schema metadata from the database and returns a SchemaDTO.
        """
        cursor = self.db_conn.cursor()
        self.logger.info("Extracting schema metadata from database...")

        # Get all tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_type = 'BASE TABLE'
        """)
        tables = [row.table_name for row in cursor.fetchall()]

        schema_dto = SchemaDTO()

        for table in tables:
            self.logger.debug(f"Processing table: {table}")
            
            # Extract columns
            columns = self._extract_columns(cursor, table)
            
            # Extract primary key
            primary_key = self._extract_primary_key(cursor, table)
            
            # Extract indexes
            indexes = self._extract_indexes(cursor, table)

            schema_dto.tables[table] = TableDTO(
                name=table,
                columns=columns,
                primary_key=primary_key,
                indexes=indexes,
                relationships=[]  # Will be populated by RelationshipManager
            )

        self.logger.info(f"Schema extraction completed. Found {len(schema_dto.tables)} tables.")
        return schema_dto

    def _extract_columns(self, cursor, table_name) -> dict:
        """Extract column metadata for a table."""
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, character_maximum_length, 
                   numeric_precision, numeric_scale, ordinal_position
            FROM information_schema.columns
            WHERE table_name = ?
            ORDER BY ordinal_position
        """, table_name)
        
        columns = {}
        for row in cursor.fetchall():
            columns[row.column_name] = ColumnDTO(
                name=row.column_name,
                type=row.data_type,
                nullable=row.is_nullable.lower() == "yes",
                ordinal_position=row.ordinal_position,
                max_length=("MAX" if row.character_maximum_length is not None and row.character_maximum_length < 0 else row.character_maximum_length),
                precision=row.numeric_precision,
                scale=row.numeric_scale
            )
        return columns

    def _extract_primary_key(self, cursor, table_name) -> list:
        """Extract primary key columns for a table."""
        cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = ? AND tc.constraint_type = 'PRIMARY KEY'
            ORDER BY kcu.ordinal_position
        """, table_name)
        
        return [row.column_name for row in cursor.fetchall()]

    def _extract_indexes(self, cursor, table_name) -> list:
        """Extract index metadata for a table."""
        cursor.execute("""
            SELECT i.name, i.type_desc, c.name as column_name
            FROM sys.indexes i
            JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
            JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
            JOIN sys.tables t ON i.object_id = t.object_id
            WHERE t.name = ? AND i.is_primary_key = 0
            ORDER BY i.name, ic.key_ordinal
        """, table_name)
        
        idx_map = {}
        for row in cursor.fetchall():
            if row.name not in idx_map:
                idx_map[row.name] = IndexDTO(name=row.name, type=row.type_desc, columns=[])
            idx_map[row.name].columns.append(row.column_name)
        
        return list(idx_map.values())
