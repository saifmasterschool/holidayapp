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

        send_message(f"\nRecommended Destination: {location}")
        send_message(f"Why it's a good fit: {location_description}")
        send_message("Top 3 Activities:")
        # print(f"\nRecommended Destination: {location}")
        # print(f"Why it's a good fit: {location_description}")
        # print("Top 3 Activities:")
        for i, act in enumerate(location_activities, start=1):
            send_message(f"   {i}. {act}")

        start_date = parse_date(payload["start_date"])
        end_date = parse_date(payload["end_date"])
        today = datetime.today()

        forecast_limit = 16
        delta_days = (start_date - today).days
        trip_duration = (end_date - start_date).days + 1

        if delta_days > forecast_limit:
            send_message(
                f"\nWeather forecast for {location} is not available — it's more than {forecast_limit} days ahead.")
        else:
            available_end = today + timedelta(days=forecast_limit)

            forecast_start = max(start_date, today)
            forecast_end = min(end_date, available_end)

            days_to_fetch = (available_end - today).days
            send_message(
                f"\nFetching weather forecast for {location} (only available from {forecast_start.date()} to {forecast_end.date()})...")

            weather = get_weather_forecast(location, days=days_to_fetch)

            if weather:
                send_message(f"\nWeather Forecast for {weather['location']}, {weather['country']}:")
                for day in weather["forecast"]:
                    forecast_date = datetime.strptime(day["date"], "%Y-%m-%d")
                    if forecast_start <= forecast_date <= forecast_end:
                        send_message(
                            f"{day['date']}: {day['condition']} | "
                            f"{day['min_temp']}°C - {day['max_temp']}°C | "
                            f"Rain chance: {day['rain_chance']}%"
                        )
            else:
                send_message("Could not retrieve weather data.")

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
    get_new_message() #Waiting till a message comes inn
    send_message(user_input.generate_greeting_response())
    send_message("Lets Make a Plan together!\nThe next available Agent will get in touch with you!\n")
    send_message("We will process your answer and provide you with the best Holiday Package in the next Step")
    vacation_data_dict = user_input.ask_user_questions()
    get_holiday_data(vacation_data_dict)




if __name__ == "__main__":
    main()




