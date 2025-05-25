import pyodbc
import networkx as nx
import os
import xml.etree.ElementTree as ET

class SchemaCloner:
    def __init__(self, db_conn, logger):
        self.db_conn = db_conn
        self.logger = logger

    def clone_schema(self, config, include_relationships=True, include_indexes=True):
        self.logger.info("Cloning schema with dependency order...")
        schema = config['database'].get('schema', 'dbo')
        include_tables = config['database'].get('include_tables', [])
        exclude_tables = config['database'].get('exclude_tables', [])
        self.db_conn.connect()
        cursor = self.db_conn.conn.cursor()
        # Load relationships from XML
        rel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'data', 'relationships.xml')
        rel_path = os.path.abspath(rel_path)
        tree = ET.parse(rel_path)
        root = tree.getroot()
        G = nx.DiGraph()
        # Build dependency graph
        for table_elem in root.findall('Table'):
            table = table_elem.get('name')
            G.add_node(table)
            for parent_elem in table_elem.findall('Parent'):
                parent = parent_elem.get('name')
                G.add_edge(parent, table)  # parent must be created before child
        # Get tables in dependency order
        try:
            ordered_tables = list(nx.topological_sort(G))
        except nx.NetworkXUnfeasible:
            self.logger.error("Cyclic dependency detected in relationships.xml!")
            self.db_conn.close()
            return
        # Filter tables
        if include_tables:
            ordered_tables = [t for t in ordered_tables if t in include_tables]
        if exclude_tables:
            ordered_tables = [t for t in ordered_tables if t not in exclude_tables]
        # Clone tables in order
        for table in ordered_tables:
            ddl = self._get_table_ddl(cursor, schema, table)
            self.logger.info(f"DDL for {table}:\n{ddl}")
            # Here you would execute the DDL in the target DB
        # Optionally handle relationships and indexes
        if include_relationships:
            self._clone_relationships(cursor, schema, ordered_tables)
        if include_indexes:
            self._clone_indexes(cursor, schema, ordered_tables)
        self.db_conn.close()

    def _get_primary_keys(self, cursor, schema, table):
        pk_query = '''
            SELECT k.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS t
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
              ON t.CONSTRAINT_NAME = k.CONSTRAINT_NAME
            WHERE t.TABLE_SCHEMA = ? AND t.TABLE_NAME = ? AND t.CONSTRAINT_TYPE = 'PRIMARY KEY'
        '''
        cursor.execute(pk_query, (schema, table))
        return [row[0] for row in cursor.fetchall()]

    def _get_table_ddl(self, cursor, schema, table):
        columns_query = '''
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        '''
        cursor.execute(columns_query, (schema, table))
        columns = cursor.fetchall()
        col_defs = []
        for col in columns:
            name, dtype, maxlen, nullable = col
            if maxlen and dtype in ('varchar', 'nvarchar', 'char', 'nchar'):
                dtype_str = f"{dtype}({maxlen})"
            else:
                dtype_str = dtype
            null_str = "NULL" if nullable == "YES" else "NOT NULL"
            col_defs.append(f"[{name}] {dtype_str} {null_str}")
        # Add primary key constraint
        pks = self._get_primary_keys(cursor, schema, table)
        pk_str = f",\n  PRIMARY KEY ({', '.join(f'[{pk}]' for pk in pks)})" if pks else ""
        ddl = f"CREATE TABLE [{schema}].[{table}] (\n  " + ",\n  ".join(col_defs) + pk_str + "\n);"
        return ddl

    def _clone_relationships(self, cursor, schema, tables):
        # Placeholder: log foreign key relationships
        fk_query = f"""
            SELECT fk.name, tp.name AS parent_table, tr.name AS ref_table
            FROM sys.foreign_keys fk
            JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
            JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
            WHERE tp.schema_id = SCHEMA_ID(?)
        """
        cursor.execute(fk_query, (schema,))
        for row in cursor.fetchall():
            self.logger.info(f"Foreign key: {row}")

    def _clone_indexes(self, cursor, schema, tables):
        # Placeholder: log indexes
        idx_query = f"""
            SELECT t.name AS table_name, ind.name AS index_name, ind.type_desc
            FROM sys.indexes ind
            INNER JOIN sys.tables t ON ind.object_id = t.object_id
            WHERE t.schema_id = SCHEMA_ID(?) AND ind.is_primary_key = 0
        """
        cursor.execute(idx_query, (schema,))
        for row in cursor.fetchall():
            self.logger.info(f"Index: {row}")
