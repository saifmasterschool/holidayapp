import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

from mock_data import build_payload
from open_ia import get_openai_response
from weather import get_weather_forecast

load_dotenv()


def extract_trip_details(ai_response: str):
    try:
        destination = re.search(r"\*\*Destination:\*\*\s*(.*?)\s*\*\*Why it's a good fit:\*\*", ai_response).group(
            1).strip()
        description = re.search(
            r"\*\*Why it's a good fit:\*\*\s*(.*?)\s*\*\*Top 3 Activities:\*\*",
            ai_response,
            re.DOTALL
        ).group(1).strip()
        activities = re.findall(r"\d+\.\s*(.*)", ai_response)
        return destination, description, activities
    except AttributeError:
        raise ValueError("Failed to parse OpenAI response format")


def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}, expected dd.mm.yyyy")


def main():
    try:
        payload = build_payload({
            "type": "relaxing",
            "start_date": "25.05.2025",
            "end_date": "07.06.2025",
            "origin": "Hamburg"
        })

        print("Requesting destination recommendation...")
        ai_response = get_openai_response(payload)
        location, location_description, location_activities = extract_trip_details(ai_response)

        print(f"\nRecommended Destination: {location}")
        print(f"Why it's a good fit: {location_description}")
        print("Top 3 Activities:")
        for i, act in enumerate(location_activities, start=1):
            print(f"   {i}. {act}")

        start_date = parse_date(payload["start_date"])
        end_date = parse_date(payload["end_date"])
        today = datetime.today()

        forecast_limit = 16
        delta_days = (start_date - today).days
        print(f"s date {start_date}")
        print(f"today {today}")
        print(f"delta days {delta_days}")
        trip_duration = (end_date - start_date).days + 1

        if delta_days > forecast_limit:
            print(
                f"\nWeather forecast for {location} is not available — it's more than {forecast_limit} days ahead.")
        else:
            # Total days from today that are available from API
            available_end = today + timedelta(days=forecast_limit)

            # Limit forecast range: only show days from start_date to min(end_date, available_end)
            forecast_start = max(start_date, today)
            forecast_end = min(end_date, available_end)

            days_to_fetch = (available_end - today).days  # still fetch full API range
            print(
                f"\nFetching weather forecast for {location} (only available from {forecast_start.date()} to {forecast_end.date()})...")

            weather = get_weather_forecast(location, days=days_to_fetch)

            if weather:
                print(f"\nWeather Forecast for {weather['location']}, {weather['country']}:")
                for day in weather["forecast"]:
                    forecast_date = datetime.strptime(day["date"], "%Y-%m-%d")
                    if forecast_start <= forecast_date <= forecast_end:
                        print(
                            f"{day['date']}: {day['condition']} | "
                            f"{day['min_temp']}°C - {day['max_temp']}°C | "
                            f"Rain chance: {day['rain_chance']}%"
                        )
            else:
                print("Could not retrieve weather data.")

    except Exception as e:
        print(f"\n Error: {e}")


if __name__ == "__main__":
    main()
