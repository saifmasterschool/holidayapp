from datetime import datetime
from amadeus import Client, ResponseError
import os
from dotenv import load_dotenv
import requests

load_dotenv()

CURRENT_API_KEY = os.getenv('CLIENT_API_KEY')
CURRENT_SECRET_KEY = os.getenv('CLIENT_SECRET_KEY')

amadeus = Client(client_id=CURRENT_API_KEY, client_secret=CURRENT_SECRET_KEY,hostname='test')

TOKEN_URL = 'https://test.api.amadeus.com/v1/security/oauth2/token'
FLIGHT_OFFERS_URL = 'https://test.api.amadeus.com/v2/shopping/flight-offers'
LOCATIONS_URL = 'https://test.api.amadeus.com/v1/reference-data/locations'


def get_access_token(client_id, client_secret):
    """Obtain OAuth2 access token from Amadeus API."""
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'client_credentials','client_id': client_id,'client_secret': client_secret}
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.RequestException as e:
        print(f"Error obtaining access token: {e}")
    return None


# Higher-order function to retry API call with a new token if token expires
def retry_with_new_token(api_call: callable, client_id: str, client_secret: str, *args, **kwargs):
    try:
        return api_call(*args, **kwargs)
    except Exception as e:
        if str(e) == "TokenExpired":
            new_token = get_access_token(client_id, client_secret)
            if not new_token:
                return None
            kwargs['access_token'] = new_token # Update the token in kwargs and retry
            return api_call(*args, **kwargs)
    return None


def search_city_and_airport(location, access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'subType': 'CITY,AIRPORT','keyword': location}
    try:
        response = requests.get(LOCATIONS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        cities = [loc["iataCode"] for loc in data.get("data", []) if "iataCode" in loc and loc['subType'] == 'CITY']
        airports = [loc["iataCode"] for loc in data.get("data", []) if "iataCode" in loc and loc['subType'] == 'AIRPORT']
        return {'cities': cities, 'airports': airports}
    except (IndexError, KeyError, requests.RequestException) as e:
        print(f"No IATA code data available for {location}: {e}")
    return None


def input_data_to_search(payload, access_token):
    # Convert dates
    start_date = datetime.strptime(payload['start_date'], "%d.%m.%Y").strftime("%Y-%m-%d")
    end_date = datetime.strptime(payload["end_date"], "%d.%m.%Y").strftime("%Y-%m-%d")
    # Get IATA codes
    origin_iata = search_city_and_airport(payload["origin"], access_token)
    dest_iata = search_city_and_airport(payload["destination"], access_token)

    return {'origin':origin_iata, 'destination':dest_iata, 'start':start_date, 'end': end_date,
            'n_adults':payload['number_of_adults']}


def get_flight_price(origin, destination, departure_date, access_token, n_person):
    """Get the nearest flight price for a given route and date."""
    headers = {'Authorization': f'Bearer {access_token}'}
    for origin_code in origin:
        for dest_code in destination:
            params = {'originLocationCode': origin_code,'destinationLocationCode': dest_code,
                'departureDate': departure_date,'adults': n_person,'max': 1}
            try:
                response = requests.get(FLIGHT_OFFERS_URL, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()['data']
                return float(data[0]['price']['total']) # get price
            except ResponseError as error:
                    print(f"No flights found on {departure_date}: {error}")
    return None


def search_for_hotel(start_date, end_date, access_token, n_people, hotel_ids):
    """Get the nearest hotel price for the stay in the destination city."""
    url = 'https://test.api.amadeus.com/v3/shopping/hotel-offers'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'hotelIds': ','.join(hotel_ids),'checkInDate': start_date,'checkOutDate': end_date,'adults': n_people,
        'roomQuantity': 1,'bestRateOnly': 'true'}
    try:
        response = requests.get(url, headers=headers, params=params)  # get multiple hotels in the city as a list
        return response.json()['data'][0]  # return one hotel data only from the list
    except ResponseError as error:
        print(f"No Hotels found on: {error}")
    return None


def get_hotel_price_by_city(cities, start_date, end_date, access_token, n_people):
    url = 'https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city'
    for city_code in cities:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'cityCode': city_code, 'hotelSource': 'ALL'}
        try:
            response = requests.get(url, headers=headers, params=params)  # get multiple hotels data (id)
            hotel_ids = [loc["hotelId"] for loc in response.json()['data'] if "hotelId" in loc]# only 5 hotels id
            limit = 0
            while True: # check at lest 5 hotels available in the city
                hotel = search_for_hotel(start_date, end_date, access_token, n_people, hotel_ids[limit:limit + 5])
                if not hotel:
                    limit =+ 5
                else:
                    price = float(hotel['offers'][0]['price']['total']) # including room services
                    return price
        except ResponseError as error:
            print(f"No Hotels found: {error}")
    return None


def get_total_budgets(payload, access_token):
    origin_airports, dest_airports = payload['origin']['airports'], payload['destination']['airports']
    dest_cities = payload['destination']['cities']
    start_date, end_date = payload['start'], payload['end']
    n_adults = payload['n_adults']
    # Get flights (origin to destination and vice versa) and hotel prices
    outbound_price= get_flight_price(origin_airports, dest_airports, start_date, access_token, n_adults)
    return_price = get_flight_price(dest_airports, origin_airports, end_date, access_token, n_adults)
    print(f"For Flight - outbound price: {outbound_price}, return price: {return_price}")
    #  hotel price
    hotel_price = get_hotel_price_by_city(dest_cities, start_date, end_date, access_token, n_adults)
    print(f"For hotel - price: {hotel_price}")

    # Calculate total price
    total_price = outbound_price + return_price + hotel_price
    return total_price


def set_up_base(payload):
    access_token = get_access_token(os.getenv('CLIENT_API_KEY'), os.getenv('CLIENT_SECRET_KEY'))
    input_data = input_data_to_search(payload, access_token)
    return get_total_budgets(input_data, access_token)


# TEST the code
user_data = {
        "start_date": "01.06.2025",
        "end_date": "10.06.2025",
        "origin": "Berlin",
        "destination": "Rome",
        "number_of_adults": 3
    }
print(set_up_base(user_data))