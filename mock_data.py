def build_payload():
    """
    This function mocks the payload sent to external APIs based on the user's cleaned input.
    """
    user_input = {
        "type": "relaxing",
        "start_date": "01.06.2025",
        "end_date": "10.06.2025",
        "origin": "Berlin"
    }
    payload = {
        "travel_type": user_input["type"],
        "start_date": user_input["start_date"],
        "end_date": user_input["end_date"],
        "origin": user_input["origin"]
    }
    return payload
