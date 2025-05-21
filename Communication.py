import Twilio_Setup
import user_input
from Twilio_Setup import identify_conversation
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from mock_data import build_payload
from open_ia import get_openai_response
from weather import get_weather_forecast

load_dotenv()
WEATHER_EMOJIS = {
    "sun": "☀️",
    "clear": "☀️",
    "partly cloudy": "🌤️",
    "cloud": "☁️",
    "rain": "🌧️",
    "thunder": "⛈️",
    "snow": "❄️",
    "wind": "🌬️",
    "fog": "🌫️",
}

def get_weather_emoji(condition: str) -> str:
    condition_lower = condition.lower()
    for keyword, emoji in WEATHER_EMOJIS.items():
        if keyword in condition_lower:
            return emoji
    return "🌦️"

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


def get_holiday_data(data):
    try:
        payload = build_payload(data)

        send_message("Requesting destination recommendation...")
        ai_response = get_openai_response(payload)
        location, location_description, location_activities = extract_trip_details(ai_response)

        send_message(f"*🌍 Recommended Destination:* *{location}*")
        send_message(f"*✨ Why it's a good fit:*\n{location_description}")
        send_message("*🎯 Top 3 Activities:*")
        for i, act in enumerate(location_activities, start=1):
            send_message(f"   {i}. {act}")

        start_date = parse_date(payload["start_date"])
        end_date = parse_date(payload["end_date"])
        today = datetime.today()

        forecast_limit = 16
        delta_days = (start_date - today).days

        if delta_days > forecast_limit:
            send_message(
                f"\nWeather forecast for {location} is not available — it's more than {forecast_limit} days ahead.")
        else:
            available_end = today + timedelta(days=forecast_limit)

            forecast_start = max(start_date, today)
            forecast_end = min(end_date, available_end)

            days_to_fetch = (available_end - today).days
            send_message(
                f"\n🌤️ *Fetching weather forecast for {location}* "
                f"(only available from *{forecast_start.date()}* to *{forecast_end.date()}*)..."
            )

            weather = get_weather_forecast(location, days=days_to_fetch)

            if weather:
                send_message(f"*📍 Location:* {location}")
                send_message("*Weather Forecast:*")
                for day in weather["forecast"]:
                    forecast_date = datetime.strptime(day["date"], "%Y-%m-%d")
                    if forecast_start <= forecast_date <= forecast_end:
                        emoji = get_weather_emoji(day["condition"])
                        send_message(
                            f"*{emoji}  {day['date']}*:\n"
                            f"  • *Condition:* {day['condition']}\n"
                            f"  • *Temp:* {day['min_temp']}°C - {day['max_temp']}°C\n"
                            f"  • *Rain Chance:* {day['rain_chance']}%"
                        )
            else:
                send_message("❌ Could not retrieve weather data.")

    except Exception as e:
        send_message(f"\n Error: {e}")


def send_message(message_text):
    """Takes the conversation and sends a new Message"""
    Twilio_Setup.identify_conversation().messages.create(body=message_text)


def get_new_message():
    """While loop, to check if there are new messages, if so - return the whole message object"""
    conversation = Twilio_Setup.identify_conversation().messages.list()
    new_message_indicator = len(conversation)
    while len(conversation) <= new_message_indicator:
        conversation = Twilio_Setup.identify_conversation().messages.list()
    return conversation[-1]


def main():
    get_new_message()
    send_message("*👋 Hello!* " + user_input.generate_greeting_response())
    send_message(
        "*🧳 Let's Make a Plan Together!*\n"
        "An agent will get in touch with you shortly.\n"
        "In the meantime, we'll process your answers and suggest the perfect holiday package! 🌴"
    )
    while True:
        vacation_data_dict = user_input.ask_user_questions()
        get_holiday_data(vacation_data_dict)
        send_message("Do want to make another Plan? (Y/N)")
        answer = get_new_message().body
        if answer == "Y":
            pass
        if answer == "N":
            exit()


if __name__ == "__main__":
    main()




