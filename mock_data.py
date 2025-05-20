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
        "travel_type": user_input.get("type", "relaxing"),
        "start_date": user_input.get("start_date", "01.06.2025"),
        "end_date": user_input.get("end_date", "10.06.2025"),
        "origin": user_input.get("origin", "Berlin"),
    }
    return payload
