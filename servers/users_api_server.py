from mcp.server.fastmcp import FastMCP
import requests
import logging
import os  # For managing sensitive information like API keys

mcp = FastMCP("UserAPIService", transport_mode="streamable-http", port=8080)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL for your FastAPI application
# IMPORTANT: Replace this with the actual URL of your API
BASE_URL = "http://localhost:8000"

# If your FastAPI application required authentication, you'd configure it here.
# For example, if it used an API key in a header:
# API_KEY = os.getenv("FASTAPI_API_KEY", "YOUR_FASTAPI_API_KEY_HERE")
# HEADERS = {"X-API-Key": API_KEY}
# Since the provided OpenAPI JSON doesn't specify security schemes, we'll assume no auth for now.
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


def _handle_response(response):
    """Helper to handle common response logic."""
    try:
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {response.status_code} - {response.text}")
        return {"error": f"API request failed with status {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return {"error": f"API request failed: {e}"}


@mcp.tool()
def get_all_users():
    """
    Retrieves information about users.

    This tool corresponds to the GET /users endpoint. It fetches a list or
    general information about users from the API.

    Args:
        None

    Returns:
        dict: A dictionary containing the API response, typically a list of users,
              or an error message if the API call fails.
    """
    url = f"{BASE_URL}/users"
    response = requests.get(url, headers=HEADERS)
    return _handle_response(response)


@mcp.tool()
def modify_user(user: dict):
    """
    Modifies an existing user's information.

    This tool corresponds to the PUT /users endpoint. It is used to update
    user data in the system.

    Note: The OpenAPI specification provided for this endpoint does not define
    any request body parameters. If your API expects data for modification,
    you will need to manually add parameters to this function and include
    a 'json=' argument in the requests.put() call.

    Args:
        user (dict): dict containing the details of new user to be added to the file.

    Returns:
        dict: The response from the API, typically confirming the update,
              or an error message.
    """
    url = f"{BASE_URL}/users"
    # Assuming no request body based on provided OpenAPI spec.
    # If your API expects a body, add it like: json={"key": "value"}
    response = requests.put(url, headers=HEADERS, json=user)
    return _handle_response(response)


@mcp.tool()
def add_new_user(user: dict):
    """
    Adds a new user to the system.

    This tool corresponds to the POST /users endpoint. It creates a new
    user record in the system.

    Note: The OpenAPI specification provided for this endpoint does not define
    any request body parameters. If your API expects data for adding a user,
    you will need to manually add parameters to this function and include
    a 'json=' argument in the requests.post() call.

    Args:
        user (dict): dict containing the details of new user to be added to the file.

    Returns:
        str: The response from the API, typically confirming user creation,
              or an error message.
    """
    url = f"{BASE_URL}/users"
    # Assuming no request body based on provided OpenAPI spec.
    # If your API expects a body, add it like: json={"name": "New User"}
    response = requests.post(url, headers=HEADERS, json=user)
    return _handle_response(response)


@mcp.tool()
def get_one_user(user_id: int):
    """
    Retrieves details for a specific user by their ID.

    This tool corresponds to the GET /users/{user_id} endpoint. It fetches
    the complete profile for a single user.

    Args:
        user_id (int): The unique integer identifier of the user to retrieve.

    Returns:
        dict: A dictionary containing the user's details, or an error message
              if the user is not found or the API call fails.
    """
    url = f"{BASE_URL}/users/{user_id}"
    response = requests.get(url, headers=HEADERS)
    return _handle_response(response)


@mcp.tool()
def remove_user(user_id: int):
    """
    Removes a user from the system by their ID.

    This tool corresponds to the DELETE /users/{user_id} endpoint. It
    deletes a user record permanently.

    Args:
        user_id (int): The unique integer identifier of the user to remove.

    Returns:
        dict: The response from the API, typically confirming deletion,
              or an error message.
    """
    url = f"{BASE_URL}/users/{user_id}"
    response = requests.delete(url, headers=HEADERS)
    return _handle_response(response)


if __name__ == "__main__":
    # IMPORTANT: Replace "[PLACEHOLDER_YOUR_API_BASE_URL]" above with your actual FastAPI base URL.
    # For example: BASE_URL = "http://127.0.0.1:8000" if running locally.
    # Choose your transport type: "stdio" for standard input/output, or "streamable-http" for HTTP.
    # print(f"Starting MCP server with transport: stdio")
    # print("Remember to set BASE_URL to your FastAPI application's URL.")
    logger.info("Starting UserService server with tools: get_all_users, get_one_user, add_new_user, modify_user, "
                "remove_user")
    mcp.run(transport="streamable-http")
