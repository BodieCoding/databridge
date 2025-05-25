"""
SQL query builder for generating SELECT statements with JOINs.
Enhanced with sophisticated query optimization through index analysis.
"""
from .dtos import SchemaDTO
from .relationship_manager import RelationshipManager
from .index_analyzer import IndexAnalyzer, QueryPlan
import logging
from typing import Dict, List, Union, Set, Optional


class QueryBuilder:
    """Builds optimized SQL queries from schema information using index analysis."""
    
    def __init__(self, logger=None, db_conn=None):
        self.logger = logger or logging.getLogger(__name__)
        self.relationship_manager = RelationshipManager(logger)
        self.index_analyzer = IndexAnalyzer(db_conn, logger) if db_conn else None

    def generate_optimized_select(
        self,
        schema_dto: SchemaDTO,
        filter_spec: Union[Dict[str, List[str]], Dict[str, str]],
        root_table: str = None,
        enable_optimization: bool = True
    ) -> Dict[str, Union[str, QueryPlan]]:
        """
        Generate an optimized SELECT statement with comprehensive query planning.
        
        Args:
            schema_dto: The schema containing table and relationship information
            filter_spec: Either {'table': ['col1', 'col2']} or {'table.col': 'value'}
            root_table: Optional root table to start from
            enable_optimization: Whether to use index-based optimization
            
        Returns:
            Dictionary containing:
            - 'sql': The optimized SQL query
            - 'plan': QueryPlan object with optimization details
            - 'visualization': Text-based DAG visualization
        """
        if not self.index_analyzer or not enable_optimization:
            # Fallback to basic query generation
            sql = self.generate_select_with_joins(schema_dto, filter_spec, root_table)
            return {'sql': sql, 'plan': None, 'visualization': 'Optimization disabled'}
        
        try:
            # Extract filter information for optimization
            filter_columns = self._extract_filter_columns(filter_spec)
            
            # Get all related tables
            all_tables = set(schema_dto.tables.keys())
            if filter_columns:
                # Start with tables that have filters
                related_tables = set(filter_columns.keys())
                
                # Add related tables through relationships
                for table in list(related_tables):
                    if table in schema_dto.relationships:
                        for rel in schema_dto.relationships[table]:
                            if rel.parent in all_tables:
                                related_tables.add(rel.parent)
                    
                    # Also check reverse relationships
                    for other_table, rels in schema_dto.relationships.items():
                        for rel in rels:
                            if rel.parent == table and other_table in all_tables:
                                related_tables.add(other_table)
            else:
                related_tables = all_tables
            
            # Generate optimized query plan
            query_plan = self.index_analyzer.generate_query_plan(
                tables=list(related_tables),
                relationships=schema_dto.relationships,
                filter_columns=filter_columns
            )
            
            # Generate SQL using the optimized plan
            sql = self._build_optimized_sql(
                schema_dto, 
                query_plan, 
                filter_spec, 
                root_table
            )
            
            # Generate visualization
            visualization = self.index_analyzer.visualize_query_plan(query_plan)
            
            return {
                'sql': sql,
                'plan': query_plan,
                'visualization': visualization
            }
            
        except Exception as e:
            self.logger.error(f"Query optimization failed, falling back to basic generation: {e}")
            sql = self.generate_select_with_joins(schema_dto, filter_spec, root_table)
            return {'sql': sql, 'plan': None, 'visualization': f'Optimization failed: {e}'}
    
    def _extract_filter_columns(self, filter_spec: Union[Dict[str, List[str]], Dict[str, str]]) -> Dict[str, List[str]]:
        """Extract filter columns in standardized format."""
        filter_columns = {}
        
        if isinstance(filter_spec, dict):
            for key, value in filter_spec.items():
                if '.' in key:
                    # Format: {'table.column': 'value'}
                    table, column = key.split('.', 1)
                    if table not in filter_columns:
                        filter_columns[table] = []
                    filter_columns[table].append(column)
                else:
                    # Format: {'table': ['col1', 'col2']}
                    if isinstance(value, list):
                        filter_columns[key] = value
                    else:
                        filter_columns[key] = [value] if value else []
        
        return filter_columns
    
    def _build_optimized_sql(
        self,
        schema_dto: SchemaDTO,
        query_plan: QueryPlan,
        filter_spec: Union[Dict[str, List[str]], Dict[str, str]],
        root_table: str = None
    ) -> str:
        """Build SQL query using the optimized query plan."""
        
        if not query_plan.tables:
            return "-- No tables to query"
        
        # Determine root table from plan or specification
        if root_table and root_table in query_plan.tables:
            start_table = root_table
        elif query_plan.join_order:
            # Use the first table in the optimized join order
            start_table = query_plan.join_order[0][0]
        else:
            start_table = query_plan.tables[0]
        
        # Generate table aliases
        table_aliases = {}
        alias_counter = 1
        
        # Root table gets T1
        table_aliases[start_table] = f"T{alias_counter}"
        alias_counter += 1
        
        # Assign aliases based on optimized join order
        for parent, child in query_plan.join_order:
            if parent not in table_aliases:
                table_aliases[parent] = f"T{alias_counter}"
                alias_counter += 1
            if child not in table_aliases:
                table_aliases[child] = f"T{alias_counter}"
                alias_counter += 1
        
        # Ensure all tables have aliases
        for table in query_plan.tables:
            if table not in table_aliases:
                table_aliases[table] = f"T{alias_counter}"
                alias_counter += 1
        
        # Build SELECT clause with optimized column order
        select_parts = []
        for table in query_plan.tables:
            if table in schema_dto.tables:
                alias = table_aliases[table]
                for column_name in schema_dto.tables[table].columns.keys():
                    select_parts.append(f"{alias}.{column_name} AS {alias}_{column_name}")
        
        select_clause = "SELECT\n  " + ",\n  ".join(select_parts)
        
        # Build FROM clause
        from_clause = f"FROM {start_table} {table_aliases[start_table]}"
        
        # Build JOIN clauses using optimized order
        join_clauses = []
        for parent, child in query_plan.join_order:
            if parent == start_table:
                continue  # Skip the root table
                
            parent_alias = table_aliases[parent]
            child_alias = table_aliases[child]
            
            # Find the relationship to determine join condition
            join_condition = self._find_join_condition(
                schema_dto, parent, child, parent_alias, child_alias
            )
            
            if join_condition:
                join_clauses.append(f"LEFT JOIN {child} {child_alias} ON {join_condition}")
        
        # Build WHERE clause using optimized predicate order
        where_conditions = []
        for table, column in query_plan.predicate_order:
            alias = table_aliases.get(table, table)
            
            # Check if this is in the original filter spec
            if isinstance(filter_spec, dict):
                for key, value in filter_spec.items():
                    if '.' in key:
                        spec_table, spec_column = key.split('.', 1)
                        if spec_table == table and spec_column == column:
                            where_conditions.append(f"{alias}.{column} = ?")
                    elif key == table and isinstance(value, list) and column in value:
                        where_conditions.append(f"{alias}.{column} = ?")
        
        # Combine all parts
        sql_parts = [select_clause, from_clause]
        
        if join_clauses:
            sql_parts.extend(join_clauses)
        
        if where_conditions:
            sql_parts.append("WHERE " + " AND ".join(where_conditions))
        
        # Add optimization comments
        sql_parts.insert(0, "-- Optimized query based on index analysis")
        sql_parts.insert(1, f"-- Estimated cost: {query_plan.estimated_cost:.0f}")
        if query_plan.recommended_indexes:
            sql_parts.insert(2, f"-- Recommended indexes: {len(query_plan.recommended_indexes)}")
        sql_parts.insert(-1, "")  # Empty line before main query
        
        return "\n".join(sql_parts)
    
    def _find_join_condition(
        self, 
        schema_dto: SchemaDTO, 
        parent: str, 
        child: str, 
        parent_alias: str, 
        child_alias: str
    ) -> str:
        """Find the appropriate join condition between two tables."""
        
        # Check direct relationship
        if child in schema_dto.relationships:
            for rel in schema_dto.relationships[child]:
                if rel.parent == parent and hasattr(rel, 'join') and rel.join:
                    parent_col = rel.join.get('parent', 'id')
                    child_col = rel.join.get('child', f"{parent}_id")
                    return f"{parent_alias}.{parent_col} = {child_alias}.{child_col}"
        
        # Check reverse relationship
        if parent in schema_dto.relationships:
            for rel in schema_dto.relationships[parent]:
                if rel.parent == child and hasattr(rel, 'join') and rel.join:
                    parent_col = rel.join.get('child', 'id')  # Reversed
                    child_col = rel.join.get('parent', f"{child}_id")  # Reversed
                    return f"{parent_alias}.{parent_col} = {child_alias}.{child_col}"
        
        # Fallback: try common naming conventions
        return f"{parent_alias}.id = {child_alias}.{parent}_id"
    
    def create_query_plan_visualization(
        self,
        schema_dto: SchemaDTO,
        filter_spec: Union[Dict[str, List[str]], Dict[str, str]],
        output_path: str,
        graphical: bool = True
    ) -> str:
        """
        Create a standalone visualization of the query plan.
        
        Args:
            schema_dto: Schema information
            filter_spec: Filter specification
            output_path: Path to save visualization
            graphical: Whether to create graphical (True) or text (False) visualization
            
        Returns:
            Path to saved visualization or visualization content
        """
        if not self.index_analyzer:
            return "Index analyzer not available for visualization"
        
        try:
            filter_columns = self._extract_filter_columns(filter_spec)
            
            # Get related tables
            related_tables = set()
            if filter_columns:
                related_tables.update(filter_columns.keys())
                for table in list(related_tables):
                    if table in schema_dto.relationships:
                        for rel in schema_dto.relationships[table]:
                            related_tables.add(rel.parent)
            
            if not related_tables:
                related_tables = set(schema_dto.tables.keys())
            
            # Generate query plan
            query_plan = self.index_analyzer.generate_query_plan(
                tables=list(related_tables),
                relationships=schema_dto.relationships,
                filter_columns=filter_columns
            )
            
            # Create visualization
            if graphical:
                return self.index_analyzer.create_graphical_visualization(query_plan, output_path)
            else:
                return self.index_analyzer.visualize_query_plan(query_plan, output_path)
                
        except Exception as e:
            self.logger.error(f"Visualization creation failed: {e}")
            return f"Visualization failed: {e}"

    # Keep the original method for backward compatibility
    def generate_select_with_joins(
        self, 
        schema_dto: SchemaDTO, 
        filter_spec: Union[Dict[str, List[str]], Dict[str, str]],
        root_table: str = None
    ) -> str:
        """
        Generate a SELECT statement with JOINs for all related tables.
        
        Args:
            schema_dto: The schema containing table and relationship information
            filter_spec: Either {'table': ['col1', 'col2']} or {'table.col': 'value'}
            root_table: Optional root table to start from (auto-detected if not provided)
        
        Returns:
            SQL SELECT statement with JOINs
        """
        self.logger.info("Generating SELECT statement with JOINs")
        
        # Determine root table
        if root_table is None:
            root_table = self._determine_root_table(filter_spec, schema_dto)
        
        # Build relationship graph
        parent_to_child = self.relationship_manager.build_relationship_graph(schema_dto)
        
        # Generate aliases and build query
        alias_generator = AliasGenerator()
        query_parts = QueryParts()
        
        # Build the query recursively
        self._build_recursive_query(
            table=root_table,
            schema_dto=schema_dto,
            parent_to_child=parent_to_child,
            alias_generator=alias_generator,
            query_parts=query_parts,
            visited=set()
        )
        
        # Build WHERE clause
        where_clause = self._build_where_clause(filter_spec, alias_generator)
        
        # Assemble final query
        sql = self._assemble_query(query_parts, root_table, alias_generator, where_clause)
        
        self.logger.debug(f"Generated SQL: {sql}")
        return sql

    def _determine_root_table(self, filter_spec: Dict, schema_dto: SchemaDTO) -> str:
        """Determine the root table from filter specification."""
        if isinstance(next(iter(filter_spec)), str) and '.' in next(iter(filter_spec)):
            # Format: {'table.column': value}
            filter_tables = [k.split('.')[0] for k in filter_spec.keys()]
        else:
            # Format: {'table': ['col1', 'col2']}
            filter_tables = list(filter_spec.keys())
        
        # Use the first table in filter as root
        root_table = filter_tables[0]
        
        if root_table not in schema_dto.tables:
            raise ValueError(f"Root table '{root_table}' not found in schema")
        
        return root_table

    def _build_recursive_query(
        self, 
        table: str, 
        schema_dto: SchemaDTO, 
        parent_to_child: Dict, 
        alias_generator: 'AliasGenerator', 
        query_parts: 'QueryParts',
        visited: Set[str]
    ):
        """Recursively build query parts for a table and its children."""
        if table in visited:
            return
        
        visited.add(table)
        alias = alias_generator.get_alias(table)
        
        # Add columns for this table
        table_dto = schema_dto.tables[table]
        for column_dto in table_dto.columns.values():
            query_parts.select_columns.append(f"{alias}.{column_dto.name} AS {alias}_{column_dto.name}")
        
        # Process child tables
        for child_table, relationship in parent_to_child.get(table, []):
            if child_table in visited:
                continue
            
            child_alias = alias_generator.get_alias(child_table)
            
            # Build JOIN condition for multi-column relationships
            join_conditions = []
            for col_dto in relationship.columns:
                join_conditions.append(f"{child_alias}.{col_dto.from_column} = {alias}.{col_dto.to_column}")
            
            join_condition = " AND ".join(join_conditions)
            query_parts.joins.append(f"LEFT JOIN {child_table} {child_alias} ON {join_condition}")
            
            # Recursively process child table
            self._build_recursive_query(
                child_table, schema_dto, parent_to_child, 
                alias_generator, query_parts, visited
            )

    def _build_where_clause(self, filter_spec: Dict, alias_generator: 'AliasGenerator') -> str:
        """Build WHERE clause from filter specification."""
        where_clauses = []
        
        if isinstance(next(iter(filter_spec)), str) and '.' in next(iter(filter_spec)):
            # Format: {'table.column': value}
            for table_column in filter_spec.keys():
                table, column = table_column.split('.', 1)
                alias = alias_generator.get_alias(table)
                where_clauses.append(f"{alias}.{column} = ?")
        else:
            # Format: {'table': ['col1', 'col2']}
            for table, columns in filter_spec.items():
                alias = alias_generator.get_alias(table)
                for column in columns:
                    where_clauses.append(f"{alias}.{column} = ?")
        
        return " AND ".join(where_clauses) if where_clauses else ""

    def _assemble_query(
        self, 
        query_parts: 'QueryParts', 
        root_table: str, 
        alias_generator: 'AliasGenerator',
        where_clause: str
    ) -> str:
        """Assemble the final SQL query."""
        root_alias = alias_generator.get_alias(root_table)
        
        sql_parts = [
            "SELECT",
            "  " + ",\n  ".join(query_parts.select_columns),
            f"FROM {root_table} {root_alias}"
        ]
        
        if query_parts.joins:
            sql_parts.extend(query_parts.joins)
        
        if where_clause:
            sql_parts.append(f"WHERE {where_clause}")
        
        return "\n".join(sql_parts)


class AliasGenerator:
    """Generates and manages table aliases (T1, T2, T3, ...)."""
    
    def __init__(self):
        self.alias_map = {}
        self.counter = 1

    def get_alias(self, table_name: str) -> str:
        """Get alias for a table, creating one if it doesn't exist."""
        if table_name not in self.alias_map:
            self.alias_map[table_name] = f"T{self.counter}"
            self.counter += 1
        return self.alias_map[table_name]


class QueryParts:
    """Container for query parts during building process."""
    
    def __init__(self):
        self.select_columns: List[str] = []
        self.joins: List[str] = []
