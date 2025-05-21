import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Loads .env file variables

def get_weather_forecast(city: str, days: int):
    url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": os.getenv("WEATHER_API_KEY"),
        "q": city,
        "days": days,
        "aqi": "no",
        "alerts": "no"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        forecast_data = {
            "location": data["location"]["name"],
            "country": data["location"]["country"],
            "forecast": []
        }

        for day in data["forecast"]["forecastday"]:
            forecast_data["forecast"].append({
                "date": day["date"],
                "condition": day["day"]["condition"]["text"],
                "max_temp": day["day"]["maxtemp_c"],
                "min_temp": day["day"]["mintemp_c"],
                "rain_chance": day["day"].get("daily_chance_of_rain", "N/A")
            })

        return forecast_data

    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
