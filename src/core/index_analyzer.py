"""
Index Analyzer - Sophisticated query optimization through index analysis and statistics.

This module provides:
- Index metadata extraction and caching
- Query optimization recommendations
- Join order optimization based on index availability
- Predicate ordering for optimal index usage
- DAG visualization of query execution plans
"""

import pyodbc
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64


@dataclass
class IndexStatistics:
    """Statistics for a specific index."""
    index_name: str
    table_name: str
    schema_name: str
    columns: List[str]
    included_columns: List[str] = field(default_factory=list)
    is_unique: bool = False
    is_primary: bool = False
    is_clustered: bool = False
    fill_factor: int = 100
    page_count: int = 0
    row_count: int = 0
    avg_fragmentation: float = 0.0
    seek_count: int = 0
    scan_count: int = 0
    lookup_count: int = 0
    update_count: int = 0
    last_seek: Optional[datetime] = None
    last_scan: Optional[datetime] = None
    size_mb: float = 0.0
    selectivity_score: float = 1.0  # Lower is more selective
    usage_score: float = 0.0  # Higher indicates more frequent usage
    
    def get_efficiency_score(self) -> float:
        """Calculate overall index efficiency score."""
        if self.row_count == 0:
            return 0.0
            
        # Factor in selectivity, usage, and fragmentation
        selectivity_factor = 1 / max(self.selectivity_score, 0.001)
        usage_factor = self.usage_score
        fragmentation_factor = max(0.1, 1 - (self.avg_fragmentation / 100))
        
        return (selectivity_factor * usage_factor * fragmentation_factor) / 3


@dataclass
class TableStatistics:
    """Statistics for a table including all its indexes."""
    table_name: str
    schema_name: str
    row_count: int = 0
    data_size_mb: float = 0.0
    index_size_mb: float = 0.0
    indexes: Dict[str, IndexStatistics] = field(default_factory=dict)
    column_statistics: Dict[str, dict] = field(default_factory=dict)
    foreign_keys: List[dict] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    
    def get_best_index_for_columns(self, columns: List[str]) -> Optional[IndexStatistics]:
        """Find the best index for a set of columns."""
        best_index = None
        best_score = 0.0
        
        for index in self.indexes.values():
            # Check if index covers the required columns
            if all(col in index.columns for col in columns):
                score = index.get_efficiency_score()
                # Bonus for exact column match
                if set(index.columns[:len(columns)]) == set(columns):
                    score *= 1.5
                
                if score > best_score:
                    best_score = score
                    best_index = index
                    
        return best_index


@dataclass
class QueryPlan:
    """Represents an optimized query execution plan."""
    tables: List[str]
    join_order: List[Tuple[str, str]]  # (parent, child) pairs in execution order
    predicate_order: List[Tuple[str, str]]  # (table, column) pairs for WHERE clause
    recommended_indexes: List[str]
    estimated_cost: float
    plan_rationale: List[str]
    dag: nx.DiGraph = field(default_factory=nx.DiGraph)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'tables': self.tables,
            'join_order': self.join_order,
            'predicate_order': self.predicate_order,
            'recommended_indexes': self.recommended_indexes,
            'estimated_cost': self.estimated_cost,
            'plan_rationale': self.plan_rationale
        }


class IndexAnalyzer:
    """
    Sophisticated index analyzer for query optimization.
    
    Features:
    - Extracts and caches index metadata and statistics
    - Provides join order optimization
    - Recommends predicate ordering for index usage
    - Generates DAG visualizations of query plans
    """
    
    def __init__(self, db_conn, logger, cache_ttl_hours: int = 24):
        self.db_conn = db_conn
        self.logger = logger
        self.cache_ttl_hours = cache_ttl_hours
        self._statistics_cache: Dict[str, TableStatistics] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
    def _is_cache_valid(self, table_name: str) -> bool:
        """Check if cached statistics are still valid."""
        if table_name not in self._cache_timestamps:
            return False
        
        cache_time = self._cache_timestamps[table_name]
        return datetime.now() - cache_time < timedelta(hours=self.cache_ttl_hours)
    
    def _extract_index_metadata(self, schema_name: str = 'dbo') -> Dict[str, TableStatistics]:
        """Extract comprehensive index metadata from SQL Server."""
        self.logger.info(f"Extracting index metadata for schema: {schema_name}")
        
        # Complex query to get comprehensive index information
        query = """
        SELECT 
            t.name AS table_name,
            SCHEMA_NAME(t.schema_id) AS schema_name,
            i.name AS index_name,
            i.is_unique,
            i.is_primary_key,
            i.type_desc,
            i.fill_factor,
            CASE WHEN i.type = 1 THEN 1 ELSE 0 END AS is_clustered,
            p.rows AS row_count,
            p.data_compression_desc,
            ius.user_seeks,
            ius.user_scans,
            ius.user_lookups,
            ius.user_updates,
            ius.last_user_seek,
            ius.last_user_scan,
            ps.page_count,
            ps.avg_fragmentation_in_percent,
            ps.avg_page_space_used_in_percent,
            (ps.page_count * 8.0) / 1024 AS size_mb,
            STRING_AGG(CASE WHEN ic.is_included_column = 0 THEN c.name END, ',') 
                WITHIN GROUP (ORDER BY ic.key_ordinal) AS key_columns,
            STRING_AGG(CASE WHEN ic.is_included_column = 1 THEN c.name END, ',') 
                WITHIN GROUP (ORDER BY ic.included_column_id) AS included_columns
        FROM sys.tables t
        INNER JOIN sys.indexes i ON t.object_id = i.object_id
        INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        LEFT JOIN sys.dm_db_index_usage_stats ius ON i.object_id = ius.object_id AND i.index_id = ius.index_id
        LEFT JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
        LEFT JOIN sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ps 
            ON i.object_id = ps.object_id AND i.index_id = ps.index_id
        WHERE SCHEMA_NAME(t.schema_id) = ?
            AND i.name IS NOT NULL
            AND p.partition_number = 1
        GROUP BY t.name, SCHEMA_NAME(t.schema_id), i.name, i.is_unique, i.is_primary_key, 
                 i.type_desc, i.fill_factor, i.type, p.rows, p.data_compression_desc,
                 ius.user_seeks, ius.user_scans, ius.user_lookups, ius.user_updates,
                 ius.last_user_seek, ius.last_user_scan, ps.page_count,
                 ps.avg_fragmentation_in_percent, ps.avg_page_space_used_in_percent
        ORDER BY t.name, i.name
        """
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(query, schema_name)
            results = cursor.fetchall()
            
            table_stats = defaultdict(lambda: TableStatistics("", schema_name))
            
            for row in results:
                table_name = row.table_name
                
                # Initialize table statistics if not exists
                if table_name not in table_stats:
                    table_stats[table_name] = TableStatistics(
                        table_name=table_name,
                        schema_name=row.schema_name,
                        row_count=row.row_count or 0,
                        last_updated=datetime.now()
                    )
                
                # Parse column lists
                key_columns = [col.strip() for col in (row.key_columns or "").split(',') if col.strip()]
                included_columns = [col.strip() for col in (row.included_columns or "").split(',') if col.strip()]
                
                # Calculate selectivity and usage scores
                total_operations = (row.user_seeks or 0) + (row.user_scans or 0) + (row.user_lookups or 0)
                usage_score = total_operations / max(row.row_count, 1) if row.row_count else 0
                
                # Estimate selectivity based on index type and uniqueness
                selectivity_score = 1.0
                if row.is_unique:
                    selectivity_score = 1.0 / max(row.row_count, 1)
                elif row.is_primary_key:
                    selectivity_score = 1.0 / max(row.row_count, 1)
                else:
                    # Estimate based on index usage patterns
                    if row.user_seeks and row.user_seeks > row.user_scans:
                        selectivity_score = 0.1  # Likely selective
                    else:
                        selectivity_score = 0.5  # Less selective
                
                # Create index statistics
                index_stats = IndexStatistics(
                    index_name=row.index_name,
                    table_name=table_name,
                    schema_name=row.schema_name,
                    columns=key_columns,
                    included_columns=included_columns,
                    is_unique=row.is_unique,
                    is_primary=row.is_primary_key,
                    is_clustered=row.is_clustered,
                    fill_factor=row.fill_factor or 100,
                    page_count=row.page_count or 0,
                    row_count=row.row_count or 0,
                    avg_fragmentation=row.avg_fragmentation_in_percent or 0.0,
                    seek_count=row.user_seeks or 0,
                    scan_count=row.user_scans or 0,
                    lookup_count=row.user_lookups or 0,
                    update_count=row.user_updates or 0,
                    last_seek=row.last_user_seek,
                    last_scan=row.last_user_scan,
                    size_mb=row.size_mb or 0.0,
                    selectivity_score=selectivity_score,
                    usage_score=usage_score
                )
                
                table_stats[table_name].indexes[row.index_name] = index_stats
                
            self.logger.info(f"Extracted metadata for {len(table_stats)} tables")
            return dict(table_stats)
            
        except Exception as e:
            self.logger.error(f"Error extracting index metadata: {e}")
            return {}
    
    def get_table_statistics(self, table_name: str, schema_name: str = 'dbo', force_refresh: bool = False) -> Optional[TableStatistics]:
        """Get cached or fresh table statistics."""
        cache_key = f"{schema_name}.{table_name}"
        
        if not force_refresh and self._is_cache_valid(cache_key):
            return self._statistics_cache.get(cache_key)
        
        # Refresh cache for this schema
        schema_stats = self._extract_index_metadata(schema_name)
        
        for table, stats in schema_stats.items():
            cache_key = f"{schema_name}.{table}"
            self._statistics_cache[cache_key] = stats
            self._cache_timestamps[cache_key] = datetime.now()
        
        return self._statistics_cache.get(f"{schema_name}.{table_name}")
    
    def optimize_join_order(self, tables: List[str], relationships: Dict[str, List], 
                          filter_columns: Dict[str, List[str]] = None) -> List[Tuple[str, str]]:
        """
        Optimize join order based on table sizes, indexes, and selectivity.
        
        Returns list of (parent, child) join pairs in optimal execution order.
        """
        if len(tables) < 2:
            return []
        
        filter_columns = filter_columns or {}
        self.logger.info(f"Optimizing join order for tables: {tables}")
        
        # Get statistics for all tables
        table_stats = {}
        for table in tables:
            stats = self.get_table_statistics(table)
            if stats:
                table_stats[table] = stats
        
        # Build relationship graph
        graph = nx.DiGraph()
        for table in tables:
            graph.add_node(table)
        
        # Add edges based on relationships
        for table, rels in relationships.items():
            if table in tables:
                for rel in rels:
                    if rel.parent in tables:
                        graph.add_edge(rel.parent, table, relationship=rel)
        
        # Calculate join cost for each potential join
        join_costs = {}
        for edge in graph.edges(data=True):
            parent, child = edge[0], edge[1]
            cost = self._calculate_join_cost(parent, child, table_stats, filter_columns)
            join_costs[(parent, child)] = cost
        
        # Use a greedy approach to build optimal join order
        # Start with the most selective table (smallest after filters)
        remaining_tables = set(tables)
        joined_tables = set()
        join_order = []
        
        # Find the best starting table (most selective or smallest)
        start_table = self._find_best_start_table(tables, table_stats, filter_columns)
        joined_tables.add(start_table)
        remaining_tables.remove(start_table)
        
        # Greedily add tables in order of lowest join cost
        while remaining_tables:
            best_join = None
            best_cost = float('inf')
            
            for joined_table in joined_tables:
                for remaining_table in remaining_tables:
                    # Check both directions for join possibility
                    cost1 = join_costs.get((joined_table, remaining_table), float('inf'))
                    cost2 = join_costs.get((remaining_table, joined_table), float('inf'))
                    
                    if cost1 < best_cost:
                        best_cost = cost1
                        best_join = (joined_table, remaining_table)
                    elif cost2 < best_cost:
                        best_cost = cost2
                        best_join = (remaining_table, joined_table)
            
            if best_join:
                join_order.append(best_join)
                joined_tables.add(best_join[1])
                remaining_tables.remove(best_join[1])
            else:
                # No more joins possible, add remaining tables arbitrarily
                if remaining_tables:
                    next_table = remaining_tables.pop()
                    # Try to connect to any joined table
                    for joined_table in joined_tables:
                        join_order.append((joined_table, next_table))
                        joined_tables.add(next_table)
                        break
        
        self.logger.info(f"Optimized join order: {join_order}")
        return join_order
    
    def _find_best_start_table(self, tables: List[str], table_stats: Dict[str, TableStatistics], 
                              filter_columns: Dict[str, List[str]]) -> str:
        """Find the best table to start the join with."""
        best_table = tables[0]
        best_score = float('inf')
        
        for table in tables:
            stats = table_stats.get(table)
            if not stats:
                continue
                
            # Calculate estimated rows after filtering
            estimated_rows = stats.row_count
            if table in filter_columns:
                # Rough estimation: assume each filter reduces rows by 10x
                estimated_rows = estimated_rows / (10 ** len(filter_columns[table]))
            
            # Prefer smaller tables with good indexes
            index_score = sum(idx.get_efficiency_score() for idx in stats.indexes.values())
            total_score = estimated_rows / max(index_score, 0.1)
            
            if total_score < best_score:
                best_score = total_score
                best_table = table
                
                return best_table
    
    def _calculate_join_cost(self, parent: str, child: str, table_stats: Dict[str, TableStatistics],
                           filter_columns: Dict[str, List[str]]) -> float:
        """Calculate estimated cost of joining two tables."""
        parent_stats = table_stats.get(parent)
        child_stats = table_stats.get(child)
        
        if not parent_stats or not child_stats:
            return float('inf')
        
        # Estimate rows after filtering
        parent_rows = parent_stats.row_count
        child_rows = child_stats.row_count
        
        if parent in filter_columns:
            parent_rows = parent_rows / (10 ** len(filter_columns[parent]))
        if child in filter_columns:
            child_rows = child_rows / (10 ** len(filter_columns[child]))
        
        # Basic cost model: rows * rows (nested loop) with index adjustment
        base_cost = parent_rows * child_rows
        
        # Adjust for available indexes (lower cost with better indexes)
        parent_index_factor = max(0.1, 1 / max(len(parent_stats.indexes), 1))
        child_index_factor = max(0.1, 1 / max(len(child_stats.indexes), 1))
        
        return base_cost * parent_index_factor * child_index_factor
    
    def optimize_predicate_order(self, table: str, columns: List[str]) -> List[str]:
        """
        Optimize the order of WHERE clause predicates for a table.
        
        Returns columns in order of optimal predicate evaluation.
        """
        stats = self.get_table_statistics(table)
        if not stats:
            return columns
        
        # Score each column based on available indexes
        column_scores = {}
        
        for column in columns:
            score = 0.0
            
            # Find indexes that can help with this column
            for index in stats.indexes.values():
                if column in index.columns:
                    # Higher score for leading columns in index
                    position = index.columns.index(column)
                    position_score = 1.0 / (position + 1)  # Leading columns get higher score
                    
                    # Factor in index efficiency
                    efficiency = index.get_efficiency_score()
                    score += position_score * efficiency
            
            column_scores[column] = score
        
        # Sort columns by score (highest first - most selective/indexed)
        optimized_order = sorted(columns, key=lambda col: column_scores.get(col, 0), reverse=True)
        
        self.logger.info(f"Optimized predicate order for {table}: {optimized_order}")
        return optimized_order
    
    def generate_query_plan(self, tables: List[str], relationships: Dict[str, List],
                          filter_columns: Dict[str, List[str]] = None) -> QueryPlan:
        """Generate optimized query execution plan."""
        filter_columns = filter_columns or {}
        
        # Optimize join order
        join_order = self.optimize_join_order(tables, relationships, filter_columns)
        
        # Optimize predicate order for each table
        predicate_order = []
        for table, columns in filter_columns.items():
            optimized_predicates = self.optimize_predicate_order(table, columns)
            predicate_order.extend([(table, col) for col in optimized_predicates])
        
        # Calculate estimated cost
        estimated_cost = self._estimate_total_cost(tables, join_order, filter_columns)
        
        # Generate rationale
        rationale = self._generate_plan_rationale(tables, join_order, predicate_order)
        
        # Build DAG for visualization
        dag = self._build_plan_dag(tables, join_order)
        
        # Find recommended indexes
        recommended_indexes = self._recommend_missing_indexes(tables, filter_columns, relationships)
        
        return QueryPlan(
            tables=tables,
            join_order=join_order,
            predicate_order=predicate_order,
            recommended_indexes=recommended_indexes,
            estimated_cost=estimated_cost,
            plan_rationale=rationale,
            dag=dag
        )
    
    def _estimate_total_cost(self, tables: List[str], join_order: List[Tuple[str, str]],
                           filter_columns: Dict[str, List[str]]) -> float:
        """Estimate total query cost."""
        total_cost = 0.0
        
        for parent, child in join_order:
            table_stats = {}
            for table in [parent, child]:
                stats = self.get_table_statistics(table)
                if stats:
                    table_stats[table] = stats
            
            join_cost = self._calculate_join_cost(parent, child, table_stats, filter_columns)
            total_cost += join_cost
        
        return total_cost
    
    def _generate_plan_rationale(self, tables: List[str], join_order: List[Tuple[str, str]],
                               predicate_order: List[Tuple[str, str]]) -> List[str]:
        """Generate human-readable rationale for the query plan."""
        rationale = []
        
        if join_order:
            rationale.append(f"Join order optimized based on table sizes and index availability")
            for i, (parent, child) in enumerate(join_order):
                parent_stats = self.get_table_statistics(parent)
                child_stats = self.get_table_statistics(child)
                
                parent_size = parent_stats.row_count if parent_stats else "unknown"
                child_size = child_stats.row_count if child_stats else "unknown"
                
                rationale.append(f"  {i+1}. Join {parent} ({parent_size} rows) → {child} ({child_size} rows)")
        
        if predicate_order:
            rationale.append("Predicate evaluation order optimized for index usage:")
            current_table = None
            for table, column in predicate_order:
                if table != current_table:
                    rationale.append(f"  Table {table}:")
                    current_table = table
                
                stats = self.get_table_statistics(table)
                index_info = "no index"
                if stats:
                    for index in stats.indexes.values():
                        if column in index.columns:
                            pos = index.columns.index(column)
                            index_info = f"index {index.index_name} (position {pos+1})"
                            break
                
                rationale.append(f"    - {column} ({index_info})")
        
        return rationale
    
    def _build_plan_dag(self, tables: List[str], join_order: List[Tuple[str, str]]) -> nx.DiGraph:
        """Build directed acyclic graph representing the query plan."""
        dag = nx.DiGraph()
        
        # Add all tables as nodes
        for table in tables:
            stats = self.get_table_statistics(table)
            dag.add_node(table, 
                        rows=stats.row_count if stats else 0,
                        indexes=len(stats.indexes) if stats else 0)
        
        # Add edges representing join order
        for i, (parent, child) in enumerate(join_order):
            dag.add_edge(parent, child, 
                        join_step=i+1,
                        join_type="LEFT JOIN")
        
        return dag
    
    def _recommend_missing_indexes(self, tables: List[str], filter_columns: Dict[str, List[str]],
                                 relationships: Dict[str, List]) -> List[str]:
        """Recommend indexes that could improve query performance."""
        recommendations = []
        
        # Check for missing indexes on filter columns
        for table, columns in filter_columns.items():
            stats = self.get_table_statistics(table)
            if not stats:
                continue
                
            for column in columns:
                has_useful_index = False
                for index in stats.indexes.values():
                    if column in index.columns[:2]:  # Leading or second column
                        has_useful_index = True
                        break
                
                if not has_useful_index:
                    recommendations.append(f"CREATE INDEX IX_{table}_{column} ON {table} ({column})")
        
        # Check for missing indexes on join columns
        for table, rels in relationships.items():
            if table in tables:
                stats = self.get_table_statistics(table)
                if not stats:
                    continue
                    
                for rel in rels:
                    if hasattr(rel, 'join') and 'child' in rel.join:
                        child_col = rel.join['child']
                        has_useful_index = False
                        
                        for index in stats.indexes.values():
                            if child_col in index.columns[:1]:  # Leading column
                                has_useful_index = True
                                break
                        
                        if not has_useful_index:
                            recommendations.append(f"CREATE INDEX IX_{table}_{child_col}_FK ON {table} ({child_col})")
        
        return recommendations
    
    def visualize_query_plan(self, query_plan: QueryPlan, output_path: str = None) -> str:
        """
        Generate visualization of the query execution plan DAG.
        
        Returns the visualization as text or saves to file if output_path provided.
        """
        if not query_plan.dag.nodes():
            return "No query plan to visualize"
        
        # Create text-based visualization
        viz_lines = []
        viz_lines.append("Query Execution Plan DAG")
        viz_lines.append("=" * 50)
        viz_lines.append("")
        
        # Show execution order
        viz_lines.append("Execution Order:")
        viz_lines.append("-" * 20)
        
        # Find root nodes (no incoming edges)
        root_nodes = [n for n in query_plan.dag.nodes() if query_plan.dag.in_degree(n) == 0]
        
        if not root_nodes and query_plan.dag.nodes():
            root_nodes = [list(query_plan.dag.nodes())[0]]  # Fallback
        
        # Traverse DAG to show execution flow
        visited = set()
        level = 0
        current_level = root_nodes
        
        while current_level:
            viz_lines.append(f"Level {level}:")
            for node in current_level:
                if node not in visited:
                    stats = self.get_table_statistics(node)
                    row_info = f" ({stats.row_count:,} rows)" if stats else ""
                    index_info = f" [{len(stats.indexes)} indexes]" if stats else ""
                    viz_lines.append(f"  └─ {node}{row_info}{index_info}")
                    visited.add(node)
            
            # Find next level
            next_level = []
            for node in current_level:
                for successor in query_plan.dag.successors(node):
                    if successor not in visited:
                        next_level.append(successor)
            
            current_level = list(set(next_level))
            level += 1
            viz_lines.append("")
        
        # Show join relationships
        if query_plan.join_order:
            viz_lines.append("Join Sequence:")
            viz_lines.append("-" * 20)
            for i, (parent, child) in enumerate(query_plan.join_order):
                viz_lines.append(f"  {i+1}. {parent} LEFT JOIN {child}")
            viz_lines.append("")
        
        # Show optimized predicates
        if query_plan.predicate_order:
            viz_lines.append("Predicate Order (optimized for indexes):")
            viz_lines.append("-" * 20)
            current_table = None
            for table, column in query_plan.predicate_order:
                if table != current_table:
                    if current_table is not None:
                        viz_lines.append("")
                    viz_lines.append(f"  {table}:")
                    current_table = table
                viz_lines.append(f"    WHERE {table}.{column} = ?")
            viz_lines.append("")
        
        # Show recommendations
        if query_plan.recommended_indexes:
            viz_lines.append("Index Recommendations:")
            viz_lines.append("-" * 20)
            for recommendation in query_plan.recommended_indexes:
                viz_lines.append(f"  • {recommendation}")
            viz_lines.append("")
        
        # Show plan rationale
        if query_plan.plan_rationale:
            viz_lines.append("Plan Rationale:")
            viz_lines.append("-" * 20)
            for rationale in query_plan.plan_rationale:
                viz_lines.append(f"  {rationale}")
        
        viz_text = "\n".join(viz_lines)
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(viz_text)
                self.logger.info(f"Query plan visualization saved to: {output_path}")
            except Exception as e:
                self.logger.error(f"Error saving visualization: {e}")
        
        return viz_text
    
    def create_graphical_visualization(self, query_plan: QueryPlan, output_path: str = None) -> str:
        """
        Create a graphical visualization using matplotlib/networkx.
        
        Returns path to saved image or base64 encoded image data.
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            
            if not query_plan.dag.nodes():
                return "No query plan to visualize"
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Use hierarchical layout
            pos = nx.spring_layout(query_plan.dag, k=3, iterations=50)
            
            # Draw nodes with different colors based on table size
            node_colors = []
            node_sizes = []
            
            for node in query_plan.dag.nodes():
                stats = self.get_table_statistics(node)
                if stats:
                    # Color based on table size
                    if stats.row_count > 100000:
                        node_colors.append('red')  # Large table
                    elif stats.row_count > 10000:
                        node_colors.append('orange')  # Medium table
                    else:
                        node_colors.append('lightgreen')  # Small table
                    
                    # Size based on number of indexes
                    size = 1000 + (len(stats.indexes) * 200)
                    node_sizes.append(size)
                else:
                    node_colors.append('lightgray')
                    node_sizes.append(1000)
            
            # Draw the graph
            nx.draw_networkx_nodes(query_plan.dag, pos, 
                                 node_color=node_colors, 
                                 node_size=node_sizes,
                                 alpha=0.8)
            
            nx.draw_networkx_labels(query_plan.dag, pos, font_size=10, font_weight='bold')
            
            # Draw edges with labels for join order
            edge_labels = {}
            for i, (parent, child) in enumerate(query_plan.join_order):
                if query_plan.dag.has_edge(parent, child):
                    edge_labels[(parent, child)] = f"Join {i+1}"
            
            nx.draw_networkx_edges(query_plan.dag, pos, 
                                 edge_color='gray', 
                                 arrows=True, 
                                 arrowsize=20,
                                 alpha=0.6)
            
            nx.draw_networkx_edge_labels(query_plan.dag, pos, edge_labels, font_size=8)
            
            # Add legend
            red_patch = mpatches.Patch(color='red', label='Large Table (>100K rows)')
            orange_patch = mpatches.Patch(color='orange', label='Medium Table (10K-100K rows)')
            green_patch = mpatches.Patch(color='lightgreen', label='Small Table (<10K rows)')
            gray_patch = mpatches.Patch(color='lightgray', label='Unknown Size')
            
            plt.legend(handles=[red_patch, orange_patch, green_patch, gray_patch], 
                      loc='upper right')
            
            plt.title("Query Execution Plan DAG\n(Node size = index count, Color = table size)", 
                     fontsize=14, fontweight='bold')
            plt.axis('off')
            
            # Save or return
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                self.logger.info(f"Graphical visualization saved to: {output_path}")
                return output_path
            else:
                # Return as base64 encoded string
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
                buffer.seek(0)
                image_data = base64.b64encode(buffer.getvalue()).decode()
                plt.close()
                return f"data:image/png;base64,{image_data}"
                
        except ImportError:
            self.logger.warning("matplotlib not available for graphical visualization")
            return self.visualize_query_plan(query_plan, output_path)
        except Exception as e:
            self.logger.error(f"Error creating graphical visualization: {e}")
            return self.visualize_query_plan(query_plan, output_path)
    
    def analyze_indexes(self, schema_name: str = 'dbo') -> Dict[str, TableStatistics]:
        """
        Main entry point for index analysis.
        
        Returns comprehensive statistics for all tables in the schema.
        """
        self.logger.info(f"Starting comprehensive index analysis for schema: {schema_name}")
        
        # Extract fresh statistics
        stats = self._extract_index_metadata(schema_name)
        
        # Cache the results
        for table_name, table_stats in stats.items():
            cache_key = f"{schema_name}.{table_name}"
            self._statistics_cache[cache_key] = table_stats
            self._cache_timestamps[cache_key] = datetime.now()
        
        # Log summary
        total_tables = len(stats)
        total_indexes = sum(len(table.indexes) for table in stats.values())
        total_rows = sum(table.row_count for table in stats.values())
        
        self.logger.info(f"Analysis complete: {total_tables} tables, {total_indexes} indexes, {total_rows:,} total rows")
        
        return stats
    
    def get_optimization_report(self, schema_name: str = 'dbo') -> str:
        """Generate a comprehensive optimization report."""
        stats = self.analyze_indexes(schema_name)
        
        report_lines = []
        report_lines.append("DATABASE INDEX OPTIMIZATION REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Schema: {schema_name}")
        report_lines.append("")
        
        # Summary statistics
        total_tables = len(stats)
        total_indexes = sum(len(table.indexes) for table in stats.values())
        total_rows = sum(table.row_count for table in stats.values())
        total_size_mb = sum(table.data_size_mb + table.index_size_mb for table in stats.values())
        
        report_lines.append("SUMMARY")
        report_lines.append("-" * 20)
        report_lines.append(f"Tables: {total_tables}")
        report_lines.append(f"Total Indexes: {total_indexes}")
        report_lines.append(f"Total Rows: {total_rows:,}")
        report_lines.append(f"Total Size: {total_size_mb:.1f} MB")
        report_lines.append("")
        
        # Table-by-table analysis
        report_lines.append("TABLE ANALYSIS")
        report_lines.append("-" * 20)
        
        for table_name, table_stats in sorted(stats.items()):
            report_lines.append(f"\n{table_name.upper()}")
            report_lines.append(f"  Rows: {table_stats.row_count:,}")
            report_lines.append(f"  Indexes: {len(table_stats.indexes)}")
            
            if table_stats.indexes:
                report_lines.append("  Index Efficiency Scores:")
                for idx_name, idx_stats in table_stats.indexes.items():
                    efficiency = idx_stats.get_efficiency_score()
                    usage = idx_stats.usage_score
                    report_lines.append(f"    {idx_name}: {efficiency:.3f} (usage: {usage:.3f})")
            else:
                report_lines.append("  ⚠️  No indexes found!")
        
        # Recommendations
        report_lines.append("\n\nRECOMMENDATIONS")
        report_lines.append("-" * 20)
        
        # Find tables with poor indexing
        poorly_indexed = []
        for table_name, table_stats in stats.items():
            if len(table_stats.indexes) < 2 and table_stats.row_count > 1000:
                poorly_indexed.append(table_name)
        
        if poorly_indexed:
            report_lines.append("Tables needing more indexes:")
            for table in poorly_indexed:
                report_lines.append(f"  • {table}")
        
        # Find fragmented indexes
        fragmented = []
        for table_name, table_stats in stats.items():
            for idx_name, idx_stats in table_stats.indexes.items():
                if idx_stats.avg_fragmentation > 30:
                    fragmented.append(f"{table_name}.{idx_name} ({idx_stats.avg_fragmentation:.1f}%)")
        
        if fragmented:
            report_lines.append("\nHighly fragmented indexes (>30%):")
            for idx in fragmented:
                report_lines.append(f"  • {idx}")
        
        return "\n".join(report_lines)
