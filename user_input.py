
import Communication

def is_valid_input(user_input):
   return user_input.strip().lower() == "hello smart holiday app"


def generate_greeting_response():
    return (
        "Hello! Welcome to the smart holiday App!\n"
        "We offer the best holiday packages worldwide!\n"
    )


def clean_user_input(user_input):
    return user_input.strip().lower()


def validate_user_selection(user_input):
    return user_input in ["adventure", "culture", "relaxing"]


def validate_user_date(user_date):
    splitdate = user_date.split(".")
    if 0 < int(splitdate[0]) < 32 and 0 < int(splitdate[1]) < 13 and  int(splitdate[2]) >= 2025:
        return True
    else:
        return False


def generate_payload(user_input):
    cleaned_input = clean_user_input(user_input)
    return {"query": cleaned_input}

CURRENCY_RATES = {
    "canada": ("CAD", 1.25),
    "japan": ("JPY", 160),
    "europe": ("EUR", 0.91),
    "usa": ("USD",1.0),
    "uk": ("GBP", 0.77),
    "ghana":("GHS",13.0),

}


def get_currency_by_location(location):
    location = location.strip().lower()
    return CURRENCY_RATES.get(location, ("USD", 1.0))

def ask_user_questions():
    while True:
        try:
            Communication.send_message("Holiday Agent: What type of trip do you want?\n 1) Adventure\n 2) Culture\n 3) Relaxing\n ")
            type = Communication.get_new_message().body
            if not validate_user_selection(clean_user_input(type)):
                 Communication.send_message("Sry your answer was not what we expected, please try again.")
            if validate_user_selection(clean_user_input(type)):
                break
        except TypeError:
            pass
    while True:
        try:
            Communication.send_message("Holiday Agent: When do you want your journey to start? (DD.MM.YYYY) ")
            start_date = Communication.get_new_message().body
            if not validate_user_date(start_date):
                Communication.send_message("Sry your answer was not what we expected, please try again.")
            if validate_user_date(start_date):
                break
        except ValueError:
            Communication.send_message("Sry your answer was not what we expected, please try again.")
            pass
    while True:
        try:
            Communication.send_message("Holiday Agent: Until when should your journey go? (DD.MM.YYYY) ")
            end_date = Communication.get_new_message().body
            if not validate_user_date(end_date):
                Communication.send_message("Sry your answer was not what we expected, please try again.")
            if validate_user_date(end_date):
                break
        except ValueError:
            Communication.send_message("Sry your answer was not what we expected, please try again.")
            pass

    Communication.send_message("Holiday Agent: Whats your Origin City? ")
    origin = Communication.get_new_message().body
    #while not validate_user_selection(trip_type.lower()):
    #    trip_type = input("Server: Invalid choice. Please enter 1, 2, 3, or trip type (adventure, culture, relaxing):\nUser: ")
    #start_point = input("Server: What is your starting point?\nUser: ")
    #destination = input("Server: What is your destination?\nUser: ")
    #num_people = input("Server: How many people traveling?\nUser:")
    #travel_date = input("Server: When do you want to travel? (Day, Month, Year)\nUser: ")
    #prices = input("Server: What is your price range?\nUser: ")
    #too_expensive = input("Server: Are the prices too expensive for you? (yes/no)\nUser: ")
    #budget = input("Server: What is your budget?\nUser: ")
    #currency,rate = get_currency_by_location(start_point)

    return{
        "type": type,
        "start_date": start_date,
        "end_date": end_date,
        "origin": origin,
        #"Travel date":travel_date,
        #"Price range": f"{prices} {currency}",
        #"Currency used": currency,
        #"Exchange rate": rate,
        #"Too expensive": too_expensive,
        #"Budget": f"{budget} {currency}"

    }

def process_user_message(user_input):
    if not is_valid_input(user_input):
        return "Please start by saying 'Hello smart holiday App'"
    print(generate_greeting_response())
    ask_user_questions()


