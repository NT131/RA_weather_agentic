
from datetime import datetime
from typing import Any

import httpx

from weather_outfit_ai.config import config
from weather_outfit_ai.models.schemas import WeatherData

# HTTP status code constants
HTTP_OK = 200


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""

    def __init__(self) -> None:
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.geo_url = "https://api.openweathermap.org/geo/1.0/direct"
        self.api_key = config.WEATHER_API_KEY

    async def get_weather(self, location: str) -> WeatherData:
        """
        Fetch weather data for a given location.

        Args:
            location: Location name (city, country)

        Returns:
            WeatherData object with current weather information

        Raises:
            Exception: If weather data cannot be fetched
        """
        try:
            coords = await self._get_coordinates(location)
            if not coords:
                coords = await self._get_demo_coordinates(location)

            if not coords:
                raise ValueError(f"Could not find coordinates for location: {location}")

            weather_data = await self._get_weather_by_coords(
                coords["lat"], coords["lon"]
            )

            return WeatherData(
                location=location,
                temperature=round(weather_data["main"]["temp"] - 273.15, 1),
                feels_like=round(weather_data["main"]["feels_like"] - 273.15, 1),
                humidity=weather_data["main"]["humidity"],
                wind_speed=round(weather_data["wind"]["speed"] * 3.6, 1),
                description=weather_data["weather"][0]["description"],
                conditions=[weather_data["weather"][0]["main"]],
                timestamp=datetime.now(),
            )

        except Exception as e:
            raise Exception(
                f"Failed to fetch weather data for {location}: {e!s}"
            ) from e

    async def _get_coordinates(self, location: str) -> dict[str, float] | None:
        """Get coordinates for a location using geocoding API."""
        async with httpx.AsyncClient() as client:
            params = {"q": str(location), "limit": str(1), "appid": str(self.api_key)}
            response = await client.get(self.geo_url, params=params)

            if response.status_code == HTTP_OK:
                data = response.json()
                if data:
                    return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
            return None

    async def _get_weather_by_coords(self, lat: float, lon: float) -> dict[str, Any]:
        """Fetch weather data using coordinates."""
        async with httpx.AsyncClient() as client:
            params = {
                "lat": str(lat),
                "lon": str(lon),
                "appid": str(self.api_key),
                "units": "standard",  # Kelvin for temperature
            }
            response = await client.get(self.base_url, params=params)
            if response.status_code == HTTP_OK:
                result: dict[str, Any] = response.json()
                return result
            else:
                raise Exception(
                    f"Weather API error: {response.status_code} - {response.text}"
                )

    async def _get_demo_coordinates(self, location: str) -> dict[str, float]:
        """Get demo coordinates for common locations."""
        demo_locations = {
            "new york": {"lat": 40.7128, "lon": -74.0060},
            "london": {"lat": 51.5074, "lon": -0.1278},
            "paris": {"lat": 48.8566, "lon": 2.3522},
            "tokyo": {"lat": 35.6762, "lon": 139.6503},
            "sydney": {"lat": -33.8688, "lon": 151.2093},
            "leuven": {"lat": 50.8798, "lon": 4.7005},
            "greenland": {"lat": 72.0, "lon": -40.0},
        }

        location_key = location.lower().strip()
        return demo_locations.get(location_key, {"lat": 40.7128, "lon": -74.0060})
