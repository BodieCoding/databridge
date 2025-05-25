from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class ColumnDTO:
    name: str
    type: str
    nullable: bool
    ordinal_position: int  # New field for column order
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None

@dataclass
class IndexDTO:
    name: str
    type: str
    columns: List[str] = field(default_factory=list)

@dataclass
class RelationshipColumnDTO:
    from_column: str
    to_column: str
    ordinal: Optional[int] = None

@dataclass
class RelationshipDTO:
    from_table: str # e.g., "orders"
    to_table: str # e.g., "users"
    relationship_type: str  # e.g., "one-to-many", "many-to-many", etc.
    columns: List[RelationshipColumnDTO] = field(default_factory=list) # Supports multi-column joins
  

@dataclass
class TableDTO:
    name: str
    columns: Dict[str, ColumnDTO] = field(default_factory=dict)
    primary_key: List[str] = field(default_factory=list)
    indexes: List[IndexDTO] = field(default_factory=list)
    relationships: List[RelationshipDTO] = field(default_factory=list)
    schema: Optional[str] = None  # Optional schema name

@dataclass
class SchemaDTO:
    tables: Dict[str, TableDTO] = field(default_factory=dict)
    database_name: Optional[str] = None
    relationships: Dict[str, List[RelationshipDTO]] = field(default_factory=dict)

# For each layer, you can use these DTOs:
# - SchemaLayer: uses SchemaDTO (with TableDTO and ColumnDTO)
# - RelationshipLayer: uses RelationshipDTO (inside TableDTO)
# - IndexLayer: uses IndexDTO (inside TableDTO)
