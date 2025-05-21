def build_payload(user_input):
    """
    This function mocks the payload sent to external APIs based on the user's cleaned input.
    """
    payload = {
        "travel_type": user_input["type"],
        "start_date": user_input["start_date"],
        "end_date": user_input["end_date"],
        "origin": user_input["origin"]
    }
    return payload
