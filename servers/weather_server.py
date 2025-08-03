import json
import os
import logging
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import logging
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("WeatherService", transport_mode="streamable-http", port=8070)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the API key from environment variables
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')


@mcp.tool()
def get_weather(location: str, unit: Optional[str] = "metric"):
    """Fetch weather data for a given city using OpenWeatherMap API."""
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}&units={unit}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") == "404":
            return f"Weather information not found for {location}. Please check the location."

        main = data.get("main", {})
        weather_desc = data.get("weather", [{}])[0].get("description", "N/A")
        temp = main.get("temp", "N/A")
        humidity = main.get("humidity", "N/A")
        wind_speed = data.get("wind", {}).get("speed", "N/A")
        city_name = data.get("name", location)

        return (
            f"Current weather in {city_name}: "
            f"{weather_desc.capitalize()}. "
            f"Temperature: {temp}°{'C' if unit == 'metric' else 'F'}. "
            f"Humidity: {humidity}%. "
            f"Wind Speed: {wind_speed} {'m/s' if unit == 'metric' else 'mph'}."
        )

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather for {location}: {e}"
    except json.JSONDecodeError:
        return f"Error decoding JSON response from weather API for {location}."


if __name__ == "__main__":
    logger.info("Starting WeatherService MCP server with tools: get_weather")
    mcp.run(transport="streamable-http")
