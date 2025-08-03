from mcp.server.fastmcp import FastMCP
import psycopg2
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
DB_PARAMS = {
    "host": "localhost",
    "port": "5432",
    "database": "northwind",
    "user": "postgres",
    "password": "suraj7177"  # Update with your actual password
}

mcp = FastMCP("NorthWindService", transport_mode="streamable-http", port=8060)


@mcp.tool()
def run_query(query: str) -> List[Dict[str, Any]]:
    """Execute a SQL query on the Northwind PostgreSQL database and return the results."""
    logger.info(f"Executing query: {query}")
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch results if it's a SELECT query
        if query.strip().lower().startswith("select"):
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            # For non-SELECT queries, return affected row count
            results = [{"affected_rows": cursor.rowcount}]
            conn.commit()

        cursor.close()
        conn.close()
        logger.info(f"Query successful, results: {results}")
        return results
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise Exception(f"Database error: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting NorthwindService MCP server with tools: run_query")
    mcp.run(transport="streamable-http")
