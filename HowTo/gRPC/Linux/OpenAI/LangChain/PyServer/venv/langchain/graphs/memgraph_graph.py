from langchain.graphs.neo4j_graph import Neo4jGraph

SCHEMA_QUERY = """
CALL llm_util.schema("prompt_ready")
YIELD *
RETURN *
"""


class MemgraphGraph(Neo4jGraph):
    """Memgraph wrapper for graph operations."""

    def __init__(
        self, url: str, username: str, password: str, *, database: str = "memgraph"
    ) -> None:
        """Create a new Memgraph graph wrapper instance."""
        super().__init__(url, username, password, database=database)

    def refresh_schema(self) -> None:
        """
        Refreshes the Memgraph graph schema information.
        """

        db_schema = self.query(SCHEMA_QUERY)[0].get("schema")
        assert db_schema is not None
        self.schema = db_schema
