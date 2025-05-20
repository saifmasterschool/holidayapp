import os
from dotenv import load_dotenv
from openai import OpenAI
from mock_data import build_payload

load_dotenv()  # Loads .env file variables

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_openai_response(payload):
    models = client.models.list()
    for model in models.data:
        print(model.id)
    prompt = (
        f"You are a travel expert. Recommend one ideal destination for a {payload['travel_type']} vacation "
        f"starting from {payload['origin']}, between {payload['start_date']} and {payload['end_date']}. "
        "Consider the season and typical weather in potential destinations during this time. "
        "If the travel duration is short, suggest a location near the origin to avoid long travel times. "
        "Make sure the destination is well-suited for the selected travel type and has favorable weather conditions during the dates. "
        "Provide your answer in the following format:\n\n"
        "**Destination:** <destination name>\n\n"
        "**Why it's a good fit:**\n<short explanation>\n\n"
        "**Top 3 Activities:**\n1. <activity>\n2. <activity>\n3. <activity>"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

print(get_openai_response(build_payload()))