"""
DataBridge: A modular Python utility for cloning and analyzing SQL database schemas.

This module provides the main orchestration service for datamodel operations,
offering a fluent API for bridging between databases and various data representations.
Supports schema extraction, relationship mapping, query generation, and multi-format exports.
"""
from .schema_extractor import SchemaExtractor
from .relationship_manager import RelationshipManager
from .query_builder import QueryBuilder
from .schema_serializer import SchemaSerializer
from .dtos import SchemaDTO
import logging
from typing import Dict, List, Union, Optional


class DataBridge:
    """
    Main bridge service for database schema operations.
    
    Provides a fluent API for:
    - Schema discovery and extraction from databases
    - Relationship mapping and analysis
    - Optimized SQL query generation with index analysis
    - Multi-format schema export (YAML, XML, JSON)
    - Table filtering and pattern matching
    
    Usage:
        bridge = DataBridge(db_conn, logger)
        
        # Discover schema with filtering
        schema = (bridge.discover_schema()
                 .from_database()
                 .only_tables(['users', 'orders'])
                 .with_relationships_from_csv('data/relationships.csv')
                 .build())
        
        # Generate optimized queries
        result = (bridge.generate_query()
                 .select_all()
                 .where({'users': ['user_id']})
                 .with_joins()
                 .build())
          # Export to multiple formats
        bridge.export_schema().to_yaml('output/schema.yaml')
    """
    
    def __init__(self, db_conn=None, logger=None):
        self.db_conn = db_conn
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize specialized components
        self.schema_extractor = SchemaExtractor(db_conn, logger) if db_conn else None
        self.relationship_manager = RelationshipManager(logger)
        self.query_builder = QueryBuilder(logger, db_conn)
        self.schema_serializer = SchemaSerializer(logger)
        
        # Cache for schema
        self._schema_cache: Optional[SchemaDTO] = None

    # ============================================================================
    # FLUENT API METHODS (New Naming Convention)
    # ============================================================================
    
    def discover_schema(self):
        """
        Start a fluent schema discovery operation.
        Returns a SchemaDiscovery builder for chaining operations.
        """
        return SchemaDiscovery(self)
    
    def bridge_schema(
        self, 
        from_database: bool = True,
        with_db_relationships: bool = True,
        with_csv_relationships: str = None
    ) -> SchemaDTO:
        """
        Bridge schema data from database to DTO (convenience method).
        
        Args:
            from_database: Extract schema from connected database
            with_db_relationships: Include foreign key relationships from database
            with_csv_relationships: Path to CSV file with additional relationships
            
        Returns:
            Complete SchemaDTO with all metadata
        """
        if not from_database:
            raise ValueError("Only database source is currently supported")
            
        return self.extract_full_schema(
            include_db_relationships=with_db_relationships,
            csv_relationships_path=with_csv_relationships
        )
    
    def generate_query(self):
        """
        Start a fluent query generation operation.
        Returns a QueryBridge builder for chaining operations.
        """
        return QueryBridge(self)
    
    def bridge_query(
        self,
        where: Union[Dict[str, List[str]], Dict[str, str]],
        starting_from: str = None,
        using_schema: SchemaDTO = None
    ) -> str:
        """
        Bridge query generation with fluent parameters (convenience method).
        
        Args:
            where: Filter specification - either {'table': ['col1', 'col2']} or {'table.col': 'value'}
            starting_from: Optional root table to start from
            using_schema: Optional schema to use (uses cached if not provided)
            
        Returns:
            SQL SELECT statement with JOINs
        """
        return self.generate_select_query(
            filter_spec=where,
            root_table=starting_from,
            schema_dto=using_schema
        )
    
    def export_schema_fluent(self):
        """
        Start a fluent schema export operation.
        Returns an ExportBridge builder for chaining operations.
        """
        return ExportBridge(self)
    
    def bridge_to_format(
        self,
        format_type: str,
        output_path: str,
        using_schema: SchemaDTO = None
    ) -> None:
        """
        Bridge schema to specified format (convenience method).
        
        Args:
            format_type: 'yaml', 'xml', or 'json'
            output_path: Path to output file
            using_schema: Optional schema to export (uses cached if not provided)
        """
        return self.export_schema(format_type, output_path, using_schema)
    
    def analyze_relationships(self, using_schema: SchemaDTO = None) -> Dict:
        """
        Analyze relationship structure in the schema.
        
        Args:
            using_schema: Optional schema to analyze (uses cached if not provided)
            
        Returns:
            Dictionary with relationship analysis
        """
        return self.get_relationship_info(using_schema)
    
    def discover_top_level_tables(self, using_schema: SchemaDTO = None) -> List[str]:
        """
        Discover top-level tables (those not referenced by others).
        
        Args:
            using_schema: Optional schema to analyze (uses cached if not provided)
            
        Returns:
            List of top-level table names
        """
        return self.find_top_level_tables(using_schema)
    
    def validate_schema_integrity(self, using_schema: SchemaDTO = None) -> Dict:
        """
        Validate schema for structural integrity and common issues.
        
        Args:
            using_schema: Optional schema to validate (uses cached if not provided)
            
        Returns:
            Dictionary with validation results
        """
        return self.validate_schema(using_schema)

    # ============================================================================
    # CORE IMPLEMENTATION METHODS
    # ============================================================================
    
    def extract_full_schema(
        self, 
        include_db_relationships: bool = True,
        csv_relationships_path: str = None
    ) -> SchemaDTO:
        """
        Extract complete schema including tables, columns, indexes, and relationships.
        
        Args:
            include_db_relationships: Whether to extract FK relationships from database
            csv_relationships_path: Optional path to CSV file with additional relationships
        
        Returns:
            Complete SchemaDTO with all metadata
        """
        if not self.schema_extractor:
            raise ValueError("Database connection required for schema extraction")
        
        self.logger.info("Starting full schema extraction")
        
        # Extract basic schema (tables, columns, indexes)
        schema_dto = self.schema_extractor.extract_schema()
        
        # Add database relationships if requested
        if include_db_relationships:
            self.logger.info("Adding database foreign key relationships")
            schema_dto = self.relationship_manager.extract_from_database(schema_dto, self.db_conn)
        
        # Add CSV relationships if provided
        if csv_relationships_path:
            self.logger.info(f"Adding relationships from CSV: {csv_relationships_path}")
            schema_dto = self.relationship_manager.load_from_csv(schema_dto, csv_relationships_path)
        
        # Cache the schema
        self._schema_cache = schema_dto
        
        self.logger.info(f"Schema extraction complete. Found {len(schema_dto.tables)} tables")
        return schema_dto

    def extract_filtered_schema(
        self,
        include_db_relationships: bool = True,
        csv_relationships_path: str = None,
        include_tables: List[str] = None,
        exclude_tables: List[str] = None,
        include_schemas: List[str] = None,
        exclude_schemas: List[str] = None,
        table_patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> SchemaDTO:
        """
        Extract schema with filtering options applied.
        
        Args:
            include_db_relationships: Whether to extract FK relationships from database
            csv_relationships_path: Optional path to CSV file with additional relationships
            include_tables: List of table names to include (None = all)
            exclude_tables: List of table names to exclude
            include_schemas: List of schema names to include (None = all)
            exclude_schemas: List of schema names to exclude
            table_patterns: List of regex patterns for table names to include
            exclude_patterns: List of regex patterns for table names to exclude
            
        Returns:
            Filtered SchemaDTO with all metadata
        """
        if not self.schema_extractor:
            raise ValueError("Database connection required for schema extraction")
        
        self.logger.info("Starting filtered schema extraction")
        
        # Extract basic schema with filters
        schema_dto = self.schema_extractor.extract_schema_with_filters(
            include_tables=include_tables,
            exclude_tables=exclude_tables,
            include_schemas=include_schemas,
            exclude_schemas=exclude_schemas,
            table_patterns=table_patterns,
            exclude_patterns=exclude_patterns
        )
        
        # Add database relationships if requested
        if include_db_relationships:
            self.logger.info("Adding database foreign key relationships")
            schema_dto = self.relationship_manager.extract_from_database(schema_dto, self.db_conn)
        
        # Add CSV relationships if provided
        if csv_relationships_path:
            self.logger.info(f"Adding relationships from CSV: {csv_relationships_path}")
            schema_dto = self.relationship_manager.load_from_csv(schema_dto, csv_relationships_path)
        
        # Cache the schema
        self._schema_cache = schema_dto
        
        self.logger.info(f"Filtered schema extraction complete. Found {len(schema_dto.tables)} tables")
        return schema_dto

    def generate_select_query(
        self,
        filter_spec: Union[Dict[str, List[str]], Dict[str, str]],
        root_table: str = None,
        schema_dto: SchemaDTO = None
    ) -> str:
        """
        Generate a SELECT query with JOINs based on filter specification.
        
        Args:
            filter_spec: Filter specification - either {'table': ['col1', 'col2']} or {'table.col': 'value'}
            root_table: Optional root table to start from
            schema_dto: Optional schema to use (uses cached if not provided)
            
        Returns:
            SQL SELECT statement with JOINs
        """
        # Use provided schema or cached schema
        schema = schema_dto or self._schema_cache
        if schema is None:
            raise ValueError("No schema available. Call extract_full_schema() first or provide schema_dto")
        
        self.logger.info("Generating SELECT query with relationships")
        return self.query_builder.build_select_query(filter_spec, schema, root_table)

    def export_schema(
        self,
        format_type: str,
        output_path: str,
        schema_dto: SchemaDTO = None
    ) -> None:
        """
        Export schema to specified format.
        
        Args:
            format_type: 'yaml', 'xml', or 'json'
            output_path: Path to output file
            schema_dto: Optional schema to export (uses cached if not provided)
        """
        # Use provided schema or cached schema
        schema = schema_dto or self._schema_cache
        if schema is None:
            raise ValueError("No schema available. Call extract_full_schema() first or provide schema_dto")
        
        self.logger.info(f"Exporting schema to {format_type}: {output_path}")
        
        if format_type.lower() == 'yaml':
            self.schema_serializer.to_yaml_file(schema, output_path)
        elif format_type.lower() == 'xml':
            self.schema_serializer.to_xml_file(schema, output_path)
        elif format_type.lower() == 'json':
            self.schema_serializer.to_json_file(schema, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}. Use 'yaml', 'xml', or 'json'")

    def get_relationship_info(self, schema_dto: SchemaDTO = None) -> Dict:
        """
        Get relationship analysis information.
        
        Args:
            schema_dto: Optional schema to analyze (uses cached if not provided)
            
        Returns:
            Dictionary with relationship analysis
        """
        # Use provided schema or cached schema
        schema = schema_dto or self._schema_cache
        if schema is None:
            raise ValueError("No schema available. Call extract_full_schema() first or provide schema_dto")
        
        return self.relationship_manager.analyze_relationships(schema)

    def find_top_level_tables(self, schema_dto: SchemaDTO = None) -> List[str]:
        """
        Find top-level tables (those not referenced by others).
        
        Args:
            schema_dto: Optional schema to analyze (uses cached if not provided)
            
        Returns:
            List of top-level table names
        """
        # Use provided schema or cached schema
        schema = schema_dto or self._schema_cache
        if schema is None:
            raise ValueError("No schema available. Call extract_full_schema() first or provide schema_dto")
        
        return self.relationship_manager.find_top_level_tables(schema)

    def validate_schema(self, schema_dto: SchemaDTO = None) -> Dict:
        """
        Validate schema for structural integrity and common issues.
        
        Args:
            schema_dto: Optional schema to validate (uses cached if not provided)
            
        Returns:
            Dictionary with validation results
        """
        # Use provided schema or cached schema
        schema = schema_dto or self._schema_cache
        if schema is None:
            raise ValueError("No schema available. Call extract_full_schema() first or provide schema_dto")
        
        return self.relationship_manager.validate_schema(schema)

    # ============================================================================
    # FLUENT BUILDER CLASSES
    # ============================================================================

class SchemaDiscovery:
    """Fluent builder for schema discovery operations with inclusion/exclusion support."""
    
    def __init__(self, bridge: DataBridge):
        self.bridge = bridge
        self._include_db_relationships = True
        self._csv_relationships_path = None
        self._include_tables = None  # None means all tables
        self._exclude_tables = None
        self._include_schemas = None  # Database schemas/owners
        self._exclude_schemas = None
        self._table_patterns = None  # Regex patterns for table names
        self._exclude_patterns = None
        
    def from_database(self, include_relationships: bool = True):
        """Configure to extract schema from the connected database."""
        self._include_db_relationships = include_relationships
        return self
        
    def with_csv_relationships(self, csv_path: str):
        """Add relationships from a CSV file."""
        self._csv_relationships_path = csv_path
        return self
        
    def with_relationships_from_csv(self, csv_path: str):
        """Alias for with_csv_relationships for more natural reading."""
        return self.with_csv_relationships(csv_path)
    
    def with_relationships_from_database(self):
        """Include foreign key relationships from the database."""
        self._include_db_relationships = True
        return self

    # ============================================================================
    # TABLE INCLUSION/EXCLUSION MODIFIERS
    # ============================================================================
    
    def only_tables(self, tables: Union[str, List[str]]):
        """Include only the specified tables in the schema discovery.
        
        Args:
            tables: Single table name or list of table names to include
            
        Examples:
            .only_tables('customers')
            .only_tables(['customers', 'orders', 'products'])
        """
        if isinstance(tables, str):
            tables = [tables]
        self._include_tables = tables
        return self
        
    def include_tables(self, tables: Union[str, List[str]]):
        """Alias for only_tables for more natural reading."""
        return self.only_tables(tables)
        
    def exclude_tables(self, tables: Union[str, List[str]]):
        """Exclude the specified tables from schema discovery.
        
        Args:
            tables: Single table name or list of table names to exclude
            
        Examples:
            .exclude_tables('temp_data')
            .exclude_tables(['logs', 'audit_trail', 'temp_tables'])
        """
        if isinstance(tables, str):
            tables = [tables]
        self._exclude_tables = tables
        return self
        
    def without_tables(self, tables: Union[str, List[str]]):
        """Alias for exclude_tables for more natural reading."""
        return self.exclude_tables(tables)
    
    # ============================================================================
    # SCHEMA/OWNER INCLUSION/EXCLUSION MODIFIERS
    # ============================================================================
    
    def only_schemas(self, schemas: Union[str, List[str]]):
        """Include only tables from the specified database schemas/owners.
        
        Args:
            schemas: Single schema name or list of schema names to include
            
        Examples:
            .only_schemas('dbo')
            .only_schemas(['sales', 'inventory', 'hr'])
        """
        if isinstance(schemas, str):
            schemas = [schemas]
        self._include_schemas = schemas
        return self
        
    def exclude_schemas(self, schemas: Union[str, List[str]]):
        """Exclude tables from the specified database schemas/owners.
        
        Args:
            schemas: Single schema name or list of schema names to exclude
            
        Examples:
            .exclude_schemas('temp')
            .exclude_schemas(['test', 'staging', 'backup'])
        """
        if isinstance(schemas, str):
            schemas = [schemas]
        self._exclude_schemas = schemas
        return self
        
    def without_schemas(self, schemas: Union[str, List[str]]):
        """Alias for exclude_schemas for more natural reading."""
        return self.exclude_schemas(schemas)
    
    # ============================================================================
    # PATTERN-BASED INCLUSION/EXCLUSION MODIFIERS
    # ============================================================================
    
    def matching_pattern(self, patterns: Union[str, List[str]]):
        """Include only tables whose names match the specified regex patterns.
        
        Args:
            patterns: Single regex pattern or list of patterns to match
            
        Examples:
            .matching_pattern(r'^user_.*')  # Tables starting with 'user_'
            .matching_pattern([r'.*_log$', r'.*_audit$'])  # Tables ending with '_log' or '_audit'
        """
        if isinstance(patterns, str):
            patterns = [patterns]
        self._table_patterns = patterns
        return self
        
    def excluding_pattern(self, patterns: Union[str, List[str]]):
        """Exclude tables whose names match the specified regex patterns.
        
        Args:
            patterns: Single regex pattern or list of patterns to exclude
            
        Examples:
            .excluding_pattern(r'^temp_.*')  # Exclude temporary tables
            .excluding_pattern([r'.*_backup$', r'.*_old$'])  # Exclude backup/old tables
        """
        if isinstance(patterns, str):
            patterns = [patterns]
        self._exclude_patterns = patterns
        return self
        
    def without_pattern(self, patterns: Union[str, List[str]]):
        """Alias for excluding_pattern for more natural reading."""
        return self.excluding_pattern(patterns)
    
    # ============================================================================
    # COMBINATION METHODS
    # ============================================================================
    
    def focus_on(self, target: Union[str, List[str]], target_type: str = 'tables'):
        """Focus the discovery on specific targets (convenience method).
        
        Args:
            target: Single target or list of targets
            target_type: Type of target - 'tables', 'schemas', or 'patterns'
            
        Examples:
            .focus_on('customers')  # Single table
            .focus_on(['orders', 'products'])  # Multiple tables
            .focus_on('dbo', 'schemas')  # Single schema
            .focus_on(r'^user_.*', 'patterns')  # Pattern matching
        """
        if target_type == 'tables':
            return self.only_tables(target)
        elif target_type == 'schemas':
            return self.only_schemas(target)
        elif target_type == 'patterns':
            return self.matching_pattern(target)
        else:
            raise ValueError(f"Invalid target_type: {target_type}. Use 'tables', 'schemas', or 'patterns'")
    
    def ignore(self, target: Union[str, List[str]], target_type: str = 'tables'):
        """Ignore specific targets during discovery (convenience method).
        
        Args:
            target: Single target or list of targets to ignore
            target_type: Type of target - 'tables', 'schemas', or 'patterns'
            
        Examples:
            .ignore('temp_data')  # Single table
            .ignore(['logs', 'audit'])  # Multiple tables
            .ignore('test', 'schemas')  # Single schema
            .ignore(r'^temp_.*', 'patterns')  # Pattern matching
        """
        if target_type == 'tables':
            return self.exclude_tables(target)
        elif target_type == 'schemas':
            return self.exclude_schemas(target)
        elif target_type == 'patterns':
            return self.excluding_pattern(target)
        else:
            raise ValueError(f"Invalid target_type: {target_type}. Use 'tables', 'schemas', or 'patterns'")
        
    def build(self) -> SchemaDTO:
        """Build and return the discovered schema with applied filters."""
        return self.bridge.extract_filtered_schema(
            include_db_relationships=self._include_db_relationships,
            csv_relationships_path=self._csv_relationships_path,
            include_tables=self._include_tables,
            exclude_tables=self._exclude_tables,
            include_schemas=self._include_schemas,
            exclude_schemas=self._exclude_schemas,
            table_patterns=self._table_patterns,
            exclude_patterns=self._exclude_patterns
        )


class QueryBridge:
    """Fluent builder for SQL query generation with table filtering support."""
    
    def __init__(self, bridge: DataBridge):
        self.bridge = bridge
        self._filter_spec = None
        self._root_table = None
        self._schema_dto = None
        self._include_tables = None
        self._exclude_tables = None
        self._include_only_filtered = False
        
    def select_all(self):
        """Configure to select all columns from all related tables."""
        # This is the default behavior, so no special configuration needed
        return self
        
    def where(self, filter_spec: Union[Dict[str, List[str]], Dict[str, str]]):
        """Specify the WHERE clause filter specification."""
        self._filter_spec = filter_spec
        return self
        
    def starting_from(self, root_table: str):
        """Specify the root table to start the query from."""
        self._root_table = root_table
        return self
        
    def using_schema(self, schema_dto: SchemaDTO):
        """Use a specific schema instead of the cached one."""
        self._schema_dto = schema_dto
        return self
        
    def with_joins(self):
        """Configure to include JOINs for all related tables."""
        # This is the default behavior, so no special configuration needed
        return self
    
    # ============================================================================
    # TABLE FILTERING MODIFIERS FOR QUERIES
    # ============================================================================
    
    def only_from_tables(self, tables: Union[str, List[str]]):
        """Include only the specified tables in the generated query.
        
        Args:
            tables: Single table name or list of table names to include in query
            
        Examples:
            .only_from_tables('customers')
            .only_from_tables(['customers', 'orders'])
        """
        if isinstance(tables, str):
            tables = [tables]
        self._include_tables = tables
        return self
        
    def excluding_tables(self, tables: Union[str, List[str]]):
        """Exclude the specified tables from the generated query.
        
        Args:
            tables: Single table name or list of table names to exclude from query
            
        Examples:
            .excluding_tables('temp_data')
            .excluding_tables(['logs', 'audit_trail'])
        """
        if isinstance(tables, str):
            tables = [tables]
        self._exclude_tables = tables
        return self
        
    def without_tables(self, tables: Union[str, List[str]]):
        """Alias for excluding_tables for more natural reading."""
        return self.excluding_tables(tables)
    
    def limit_to_filtered_schema(self):
        """When using a filtered schema, only generate queries for tables in that schema.
        
        This is useful when you've used discover_schema().only_tables() and want
        queries to respect the same filtering.
        """
        self._include_only_filtered = True
        return self
        
    def build(self) -> str:
        """Build and return the SQL query with applied table filters."""
        if self._filter_spec is None:
            raise ValueError("Filter specification is required. Use .where() to specify filters.")
        
        # Get the schema to use
        schema_dto = self._schema_dto or self.bridge._schema_cache
        
        # Apply table filtering to the schema if specified
        if (self._include_tables or self._exclude_tables or self._include_only_filtered) and schema_dto:
            schema_dto = self._apply_query_table_filters(schema_dto)
            
        return self.bridge.generate_select_query(
            filter_spec=self._filter_spec,
            root_table=self._root_table,
            schema_dto=schema_dto
        )
    
    def _apply_query_table_filters(self, schema_dto: SchemaDTO) -> SchemaDTO:
        """Apply table inclusion/exclusion filters to a schema for query generation."""
        from .dtos import SchemaDTO
        
        filtered_tables = {}
        
        for table_name, table_dto in schema_dto.tables.items():
            # Apply inclusion filter
            if self._include_tables and table_name not in self._include_tables:
                continue
                
            # Apply exclusion filter
            if self._exclude_tables and table_name in self._exclude_tables:
                continue
                
            # Include this table
            filtered_tables[table_name] = table_dto
          # Create filtered schema for query generation
        return SchemaDTO(
            database_name=getattr(schema_dto, 'database_name', None),
            tables=filtered_tables,
            relationships=getattr(schema_dto, 'relationships', {})
        )
            
        return self.bridge.generate_select_query(
            filter_spec=self._filter_spec,
            root_table=self._root_table,
            schema_dto=self._schema_dto
        )


class ExportBridge:
    """Fluent builder for schema export operations."""
    
    def __init__(self, bridge: DataBridge):
        self.bridge = bridge
        self._schema_dto = None
        
    def using_schema(self, schema_dto: SchemaDTO):
        """Use a specific schema instead of the cached one."""
        self._schema_dto = schema_dto
        return self
        
    def to_yaml(self, output_path: str) -> None:
        """Export schema to YAML format."""
        self.bridge.export_schema('yaml', output_path, self._schema_dto)
        
    def to_xml(self, output_path: str) -> None:
        """Export schema to XML format."""
        self.bridge.export_schema('xml', output_path, self._schema_dto)
        
    def to_json(self, output_path: str) -> None:
        """Export schema to JSON format."""
        self.bridge.export_schema('json', output_path, self._schema_dto)
        
    def to_dict(self) -> dict:
        """Export schema to dictionary format."""
        schema_dto = self._schema_dto or self.bridge._schema_cache
        if schema_dto is None:
            raise ValueError("No schema available. Call bridge_schema() first or use using_schema()")
        return self.bridge.schema_serializer.to_dict(schema_dto)


