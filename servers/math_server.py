import logging
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MathService", transport_mode="streamable-http", port=8050)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers.
    Args:
        a: First number
        b: Second number
    """
    logger.info(f"Executing add({a}, {b})")
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract one number from another number.
    Args:
        a: First number
        b: Second number
    """
    logger.info(f"Executing subtract({a}, {b})")
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers
    Args:
        a: First number
        b: Second number
    """
    logger.info(f"Executing multiply({a}, {b})")
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers. Raises an error if dividing by zero.
    Args:
        a: The dividend.
        b: The divisor.
    Returns:
        The result of the division as a float, or an error message if division by zero occurs.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed")

    return a / b


if __name__ == "__main__":
    logger.info("Starting MathService server with tools: add, subtract, multiply, divide")
    mcp.run(transport="streamable-http")
