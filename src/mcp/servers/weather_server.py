#!/usr/bin/env python3
"""
Weather MCP Server
Provides weather data using OpenWeatherMap API (or mock data for MVP)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
import requests
from datetime import datetime, timedelta
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Weather MCP Server",
    description="Weather data for URE MVP",
    version="1.0.0"
)

# OpenWeatherMap API key (optional - will use mock data if not available)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# Request models
class CurrentWeatherRequest(BaseModel):
    location: str
    units: Optional[str] = "metric"


class WeatherForecastRequest(BaseModel):
    location: str
    days: Optional[int] = 3


# Response models
class CurrentWeatherResponse(BaseModel):
    success: bool
    location: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    description: str
    timestamp: str
    message: Optional[str] = None


class WeatherForecastResponse(BaseModel):
    success: bool
    location: str
    forecast: List[Dict[str, Any]]
    message: Optional[str] = None


def get_mock_weather_data(location: str) -> Dict[str, Any]:
    """Generate mock weather data for testing"""
    import random
    
    # Base temperature varies by location
    base_temp = 25 if "maharashtra" in location.lower() else 22
    
    return {
        "temperature": round(base_temp + random.uniform(-5, 5), 1),
        "feels_like": round(base_temp + random.uniform(-3, 3), 1),
        "humidity": random.randint(40, 80),
        "wind_speed": round(random.uniform(2, 15), 1),
        "description": random.choice([
            "Clear sky",
            "Partly cloudy",
            "Scattered clouds",
            "Light rain expected"
        ])
    }


def get_mock_forecast(location: str, days: int) -> List[Dict[str, Any]]:
    """Generate mock forecast data"""
    import random
    
    forecast = []
    base_temp = 25 if "maharashtra" in location.lower() else 22
    
    for i in range(days):
        date = datetime.now() + timedelta(days=i+1)
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%A"),
            "temperature_min": round(base_temp + random.uniform(-3, 0), 1),
            "temperature_max": round(base_temp + random.uniform(0, 8), 1),
            "humidity": random.randint(40, 80),
            "precipitation_chance": random.randint(0, 60),
            "description": random.choice([
                "Clear sky",
                "Partly cloudy",
                "Scattered clouds",
                "Light rain possible"
            ])
        })
    
    return forecast


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "Weather MCP Server",
        "status": "running",
        "version": "1.0.0",
        "api_key_configured": OPENWEATHER_API_KEY is not None,
        "mode": "live" if OPENWEATHER_API_KEY else "mock"
    }


@app.post("/get_current_weather", response_model=CurrentWeatherResponse)
def get_current_weather(request: CurrentWeatherRequest):
    """
    Get current weather conditions for a location
    """
    try:
        # Try to use OpenWeatherMap API if key is available
        if OPENWEATHER_API_KEY:
            try:
                import requests as req
                url = f"http://api.openweathermap.org/data/2.5/weather"
                params = {
                    "q": request.location,
                    "appid": OPENWEATHER_API_KEY,
                    "units": request.units
                }
                response = req.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    return CurrentWeatherResponse(
                        success=True,
                        location=request.location,
                        temperature=round(data['main']['temp'], 1),
                        feels_like=round(data['main']['feels_like'], 1),
                        humidity=data['main']['humidity'],
                        wind_speed=round(data['wind']['speed'], 1),
                        description=data['weather'][0]['description'],
                        timestamp=datetime.now().isoformat(),
                        message="Weather data from OpenWeatherMap"
                    )
            except Exception as e:
                logger.warning(f"OpenWeatherMap API failed, using mock data: {e}")
        
        # Fallback to mock data
        weather_data = get_mock_weather_data(request.location)
        
        return CurrentWeatherResponse(
            success=True,
            location=request.location,
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            description=weather_data["description"],
            timestamp=datetime.now().isoformat(),
            message="Weather data retrieved successfully (mock data for MVP)"
        )
    
    except Exception as e:
        logger.error(f"Error getting current weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_weather_forecast", response_model=WeatherForecastResponse)
def get_weather_forecast(request: WeatherForecastRequest):
    """
    Get weather forecast for next N days
    """
    try:
        # Validate days parameter
        if request.days < 1 or request.days > 7:
            raise HTTPException(
                status_code=400,
                detail="Days must be between 1 and 7"
            )
        
        # Try to use OpenWeatherMap API if key is available
        if OPENWEATHER_API_KEY:
            try:
                import requests as req
                url = f"http://api.openweathermap.org/data/2.5/forecast"
                params = {
                    "q": request.location,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                    "cnt": request.days * 8  # 8 forecasts per day (3-hour intervals)
                }
                response = req.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Group by day
                    forecast_by_day = {}
                    for item in data['list']:
                        date = datetime.fromtimestamp(item['dt']).strftime("%Y-%m-%d")
                        if date not in forecast_by_day:
                            forecast_by_day[date] = []
                        forecast_by_day[date].append(item)
                    
                    # Build forecast
                    forecast_data = []
                    for date, items in list(forecast_by_day.items())[:request.days]:
                        temps = [item['main']['temp'] for item in items]
                        humidities = [item['main']['humidity'] for item in items]
                        
                        forecast_data.append({
                            "date": date,
                            "day": datetime.strptime(date, "%Y-%m-%d").strftime("%A"),
                            "temperature_min": round(min(temps), 1),
                            "temperature_max": round(max(temps), 1),
                            "humidity": int(sum(humidities) / len(humidities)),
                            "precipitation_chance": int(items[0]['pop'] * 100) if 'pop' in items[0] else 0,
                            "description": items[0]['weather'][0]['description']
                        })
                    
                    return WeatherForecastResponse(
                        success=True,
                        location=request.location,
                        forecast=forecast_data,
                        message=f"{request.days}-day forecast from OpenWeatherMap"
                    )
            except Exception as e:
                logger.warning(f"OpenWeatherMap API failed, using mock data: {e}")
        
        # Fallback to mock data
        forecast_data = get_mock_forecast(request.location, request.days)
        
        return WeatherForecastResponse(
            success=True,
            location=request.location,
            forecast=forecast_data,
            message=f"{request.days}-day forecast retrieved successfully (mock data for MVP)"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weather forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("Starting Weather MCP Server on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
