from langchain_openai import ChatOpenAI
import requests
import os
import openai
import googlemaps
from datetime import datetime
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI
import json
import re
import html
from dotenv import load_dotenv

# load_dotenv()
load_dotenv(dotenv_path='./.env')

API_KEY = os.getenv("SERP_API_KEY")
# print('ooook')
# print(API_KEY)

llm = ChatOpenAI(
        temperature=0.2, model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY")
    )


def search_hotels(query: str, location: str = "Taipei", budget: str = None) -> dict:
    """
    Function to call SERP API and return hotel search results with titles and links, including a budget.
    """
    # Add budget to query if provided
    # if budget:
    #     query += f" {budget}"

    # Query parameters
    params = {
        "engine": "google",
        "q": f'{query} site: booking.com',  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": '4be3db34b5ea94bbf897bf2b05dd9427b1baeb18f2cc7eb24a5332439fc6f046'
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print(data)

    # Extract hotel information
    hotels = []
    for result in data.get("organic_results", [])[:3]:  # Limit results to top 3
        hotel = {
            "title": result.get("title") or None,
            "price": result.get("price") or None,
            "extensions": result.get('extensions') or None,
            "link": result.get('link') or None,
            "address": result.get("address") or None,
            "rating": result.get("rating") or None,
            "snippet": result.get("description") or None,
            "place_id": result.get('place_id') or None
        }
        hotels.append(hotel)

    return {"results": hotels}


def search_hotels_green(query: str, location: str = "Taipei", budget: str = None) -> dict:
    """
    Function to call SERP API and return hotel search results with titles and links, including a budget.
    """
    # Add budget to query if provided
    # if budget:
    #     query += f" {budget}"

    # Query parameters
    params = {
        "engine": "google",
        "q": f'{query} site: booking.com',  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": '4be3db34b5ea94bbf897bf2b05dd9427b1baeb18f2cc7eb24a5332439fc6f046'
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print(data)

    # Extract hotel information
    hotels = []
    for result in data.get("local_results", [])[:3]:  # Limit results to top 3
        hotel = {
            "title": result.get("title") or None,
            "price": result.get("price") or None,
            "extensions": result.get('extensions') or None,
            "link": result.get('link') or None,
            "address": result.get("address") or None,
            "rating": result.get("rating") or None,
            "snippet": result.get("description") or None,
            "place_id": result.get('place_id') or None
        }
        hotels.append(hotel)

    return {"results": hotels}


# place planner

def search_dining(query: str, location: str = "Taipei") -> str:
    """
    Function to call SERP API and return hotel search results with titles and links.
    """
    # Query parameters
    params = {
        "engine": "google_maps",
        "q": f'{query}',  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": '4be3db34b5ea94bbf897bf2b05dd9427b1baeb18f2cc7eb24a5332439fc6f046'
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print(data)
    places = []
    for result in data.get("local_results", [])[:3]:
        prompt_parts = []
        if result.get('title'):
                prompt_parts.append(f"Title: {result.get('title')}")
        if result.get('snippet'):
                prompt_parts.append(f"Snippet: {result.get('snippet')}")
        if result.get('extensions'):
                prompt_parts.append(f"Extensions: {result.get('extensions')}")
        if result.get('rating'):
                prompt_parts.append(f"Rating: {result.get('rating')}")
        prompt = "\n".join(prompt_parts) + "\nSummary:"
        place = {
            "title": result.get("title") or None,
            "price": result.get("price") or None,
            "extensions": result.get('extensions') or None,
            "link": result.get('link') or None,
            "address": result.get("address") or None,
            "rating": result.get("rating") or None,
            "snippet": result.get("description") or None,
            "place_id": result.get('place_id') or None,
            "summary": (llm.invoke('the resposne must in traditional Chinese please remove any markdown tags and also the newline tags' + prompt )).content
        }
        places.append(place)

    return {"results": places}



# place planner

def search_dining_green(query: str, location: str = "Taipei") -> str:
    """
    Function to call SERP API and return hotel search results with titles and links.
    """
    # Query parameters
    params = {
        "engine": "google_maps",
        "q": f'{query} 有機 環保 素',  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": '4be3db34b5ea94bbf897bf2b05dd9427b1baeb18f2cc7eb24a5332439fc6f046'
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print(data)
    places = []
    for result in data.get("local_results", [])[:3]:
        prompt_parts = []
        if result.get('title'):
                prompt_parts.append(f"Title: {result.get('title')}")
        if result.get('snippet'):
                prompt_parts.append(f"Snippet: {result.get('snippet')}")
        if result.get('extensions'):
                prompt_parts.append(f"Extensions: {result.get('extensions')}")
        if result.get('rating'):
                prompt_parts.append(f"Rating: {result.get('rating')}")
        prompt = "\n".join(prompt_parts) + "\nSummary:"
        place = {
            "title": result.get("title") or None,
            "price": result.get("price") or None,
            "extensions": result.get('extensions') or None,
            "link": result.get('link') or None,
            "address": result.get("address") or None,
            "rating": result.get("rating") or None,
            "snippet": result.get("description") or None,
            "place_id": result.get('place_id') or None,
            "summary": (llm.invoke('the resposne must in traditional Chinese please remove any markdown tags and also the newline tags' + prompt )).content
        }
        places.append(place)

    return {"results": places}


#ticket planner
def search_ticket(query: str, location: str = "Taipei") -> str:
    """
    Function to call SERP API and return hotel search results with titles and links.
    """
    # Query parameters
    params = {
        "engine": "google",
        "q": f'{query} site: klook.com',  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": '4be3db34b5ea94bbf897bf2b05dd9427b1baeb18f2cc7eb24a5332439fc6f046'
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print(data)
    # print(data)

    if 'organic_results' in data:
      organic_results = []
      for res in data['organic_results']:
        if res.get('position') <=2:
            prompt_parts = []
            if res.get('title'):
                    prompt_parts.append(f"Title: {res.get('title')}")
            if res.get('snippet'):
                    prompt_parts.append(f"Snippet: {res.get('snippet')}")
            if res.get('extensions'):
                    prompt_parts.append(f"Extensions: {res.get('extensions')}")
            if res.get('rating'):
                    prompt_parts.append(f"Rating: {res.get('rating')}")
            prompt = "\n".join(prompt_parts) + "\nSummary:"
            organic_entry = {
                    "title": res.get('title') ,
                    "price": res.get('price') or None,
                    "rating": res.get('rating') or None,
                    "extensions": res.get('extensions') or None,
                    "link": res.get('link'),
                    "address": res.get('address') or None,
                    "snippet": res.get('snippet') or None,
                    "place_id": res.get('place_id') or None,
                    "summary": (llm.invoke('the resposne must in traditional Chinese please remove any markdown tags and also the newline tags' + prompt )).content
                    
                }
            if organic_entry["title"]:
                    organic_results.append(organic_entry)
                    result = {"results": organic_results}
                    return result
            else:
                 return {"error":"ticket not found"}
    

def validate_time_format(time_str: str) -> bool:
    # Regular expression for 24-hour time format hh:mm
    time_pattern = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    return bool(time_pattern.match(time_str))


def extract_travel_details(query: str) -> dict:
    prompt_template = """
        Extract the travel details from the following query:
        If there is no specified departure_location using "台北市中正區北平西路3號100臺灣"
        If there is no specified departure_time using "10:00"
        If there is no specified departure_date using "2024-10-22"
        If there is so specified arrival_time using "no specified"
        If the departure_time is in words please fill a estimated time
        If mode can not be selected from "transit", "walking", "driving", "TOW_WHEELER", "bicycling", please use "transit"
        Resposne do not contain ```json



        "{query}"

        Return the following details in JSON format:
        - "destination": where the user wants to go
        - "departure_date": the date they want to depart (in 2024-mm-dd format)
        - "departure_time": the time they want to depart (in 24-hour hh:mm format)
        - "arrival_time": the time they want to arrive at destination (in 24-hour hh:mm format)
        - "departure_location": (if specified) where the user is departing from
        - "mode" : the means of transportation they want to use (please select from, "transit", "walking", "driving", "TOW_WHEELER", "bicycling")
        """
    try:
        # Step 4: Initialize the prompt template
        template = PromptTemplate(input_variables=["query"], template=prompt_template)
        
        # Step 5: Create an LLMChain with the prompt and the OpenAI model
        chain = LLMChain(llm=llm, prompt=template)
      
        # Step 6: Run the chain with the query input
        travel_details = chain.run(query)
        
        # Parse the result into a dictionary
        print(travel_details)
        travel_details_dict = json.loads(travel_details)
        if "arrival_time" in travel_details_dict:
            if not validate_time_format(travel_details_dict["arrival_time"]):
                travel_details_dict["arrival_time"] = None
        
        return travel_details_dict
    
    except Exception as e:
        return f"Error occurred while extracting travel details: {e}"
    
    except Exception as e:
        return f"Error occurred while extracting travel details: {e}"
    

def get_google_maps_route(departure_location: str, destination: str, departure_time: datetime = None, arrival_time: datetime = None, mode:str ='transit'):
    gmaps = googlemaps.Client(key='AIzaSyAMncPb3INeUVKzl3gA8S0DRwgVUUvecwE') 
    try:
        if arrival_time:
            directions_result = gmaps.directions(
                origin=departure_location,
                destination=destination,
                mode=mode,  # You can also use 'transit', 'walking', 'bicycling', etc.
                arrival_time=arrival_time,
                language="zh-TW"
            )
        else:
            directions_result = gmaps.directions(
                origin=departure_location,
                destination=destination,
                mode=mode,  # You can also use 'transit', 'walking', 'bicycling', etc.
                departure_time=departure_time,
                language="zh-TW"
            )
        if directions_result:
            route_description = directions_result[0]['legs'][0]['steps']
            directions = ""
            for idx, step in enumerate(route_description, 1):
                instructions = step['html_instructions']
                # Remove HTML tags
                instructions = re.sub('<[^<]+?>', '', instructions)
                # Unescape HTML entities
                instructions = html.unescape(instructions)
                distance = step['distance']['text']
                duration = step['duration']['text']
                directions += f"{idx}. {instructions} （距離：{distance}，時間：{duration}）\n"
            return directions.strip()
        else:
            return "No route found."
    
    except Exception as e:
        return f"Error occurred while fetching route: {e}"
 
  

# route planner
def get_travel_route_with_google_maps(query: str):
    # Extract travel details using LLM
    travel_details = extract_travel_details(query)
    
    if isinstance(travel_details, str):  # Error handling
        return travel_details
    
    destination = travel_details.get("destination")
    departure_location = travel_details.get("departure_location", "台北市中正區北平西路3號100臺灣")
    departure_date = travel_details.get("departure_date")
    departure_time = travel_details.get("departure_time")
    mode = travel_details.get("mode")
    arrival_time = travel_details.get("arrival_time")
    
    # Parse date and time for Google Maps
    if arrival_time:
        arrival_datetime = datetime.strptime(f"{departure_date} {arrival_time}", "%Y-%m-%d %H:%M")
        route = get_google_maps_route(departure_location=departure_location, destination=destination,arrival_time=arrival_datetime, mode=mode)
        return route
    else:
        departure_datetime = datetime.strptime(f"{departure_date} {departure_time}", "%Y-%m-%d %H:%M")
        route = get_google_maps_route(departure_location=departure_location, destination=destination, departure_time=departure_datetime, mode=mode)
        return route

    return route

def get_travel_route_with_google_maps_green(query: str):
    # Extract travel details using LLM
    travel_details = extract_travel_details(query)
    
    if isinstance(travel_details, str):  # Error handling
        return travel_details
    
    destination = travel_details.get("destination")
    departure_location = travel_details.get("departure_location", "台北市中正區北平西路3號100臺灣")
    departure_date = travel_details.get("departure_date")
    departure_time = travel_details.get("departure_time")
    # mode = travel_details.get("mode")
    arrival_time = travel_details.get("arrival_time")
    
    # Parse date and time for Google Maps
    if arrival_time:
        arrival_datetime = datetime.strptime(f"{departure_date} {arrival_time}", "%Y-%m-%d %H:%M")
        route = get_google_maps_route(departure_location=departure_location, destination=destination,arrival_time=arrival_datetime)
        return route
    else:
        departure_datetime = datetime.strptime(f"{departure_date} {departure_time}", "%Y-%m-%d %H:%M")
        route = get_google_maps_route(departure_location=departure_location, destination=destination, departure_time=departure_datetime)
        return route

<<<<<<< HEAD
=======


def get_current_date_in_taipei() -> str:
    taipei_tz = pytz.timezone('Asia/Taipei')
    return datetime.now(taipei_tz).strftime('%Y-%m-%d')

def validate_date_format(date_str: str) -> bool:
    """Helper function to validate if a string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def extract_hotel_info(query: str) -> dict:
    prompt_template = """
        回答中請勿包含```json
        回答中請勿包含 \n
        Extract the hotel booking details from the following query:
        If there is no specified check-in date, fill "no offer".
        If there is no specified check-out date, fill "no offer.
        If there is no specified min_price, use Null.
        If there is no specified max_price, use Null.
        If there is no specified hotel_type, use 飯店.


        Query:
        "{query}"

        Return the following details in JSON format:
        - "query": the search query for the hotel (e.g., '5-star hotel in Taipei')
        - "check_in_date": the check-in date in YYYY-MM-DD format
        - "check_out_date": the check-out date in YYYY-MM-DD format
        - "min_price": minimum price (integer)
        - "max_price": maximum price (integer)
        - "hotel_type": hotel type (e.g., 飯店, 民宿)
        """

    try:
        # Initialize the prompt template
        template = PromptTemplate(input_variables=["query"], template=prompt_template)

        # Create an LLMChain with the prompt and the OpenAI model
        chain = LLMChain(llm=llm, prompt=template)

        # Run the chain with the query input
        hotel_details = chain.run(query)

        # Parse the result into a dictionary
        print(hotel_details)
        hotel_details_dict = json.loads(hotel_details)

        # Get current date and next day in Taipei timezone
        current_date = get_current_date_in_taipei()
        next_day = (datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        # Validate and set default check-in and check-out dates
        if "check_in_date" in hotel_details_dict:
            if not validate_date_format(hotel_details_dict["check_in_date"]):
                hotel_details_dict["check_in_date"] = current_date

        if "check_out_date" in hotel_details_dict:
            if not validate_date_format(hotel_details_dict["check_out_date"]):
                hotel_details_dict["check_out_date"] = next_day

        return hotel_details_dict

    except Exception as e:
        return f"Error occurred while extracting hotel details: {e}"
    


def convert_price_to_int(price_str):
    # Remove the dollar sign and commas, then convert to an integer
    return int(price_str.replace('$', '').replace(',', ''))

def search_hotel_new(query: str, location: str = "Taipei", min_price=None, max_price=None, hotel_type: str = None,check_in_date=None,check_out_date=None):
    """
    Function to call SERP API and return hotel search results with titles and links,
    and filter based on a given price range.

    Args:
    - query: The search query for hotels
    - location: The location to search in
    - min_price: Minimum price for hotels
    - max_price: Maximum price for hotels
    """
    if hotel_type not in ['飯店','民宿']:
        hotel_type = '飯店'
    print(type(min_price))
    if not isinstance(min_price, int):
        min_price = 0  # Default value if min_price is not an integer
    if not isinstance(max_price, int):
        max_price = 1000000  # Default
    # Query parameters for SerpAPI using Google Hotels
    params = {
        "engine": "google_hotels",
        "q": f'{query} hotel_type',
        "location": location,
        "price_min": min_price,
        "price_max": max_price,
        "api_key": API_KEY,
        "hl": "zh-TW" ,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency":"TWD"
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    # print(data)
    # hotels = []
    # hotels['properties']
    # print(data)
    # print(data['properties'])
    result =[]
    properties = data.get('properties', [])
    for hotel in properties:
        # print(type(min_price))
        # print(type(max_price))
        # print(int(hotel.get('rate_per_night').get('lowest')))
        price = convert_price_to_int(hotel.get('rate_per_night').get('lowest'))
        if min_price <= price <= max_price:
        # print(hotel)
            res = {
                    "title": hotel["name"] or None,
                    "price": price or None,
                    "extensions": hotel.get('extension') or None,
                    "link": hotel.get('link') or None,
                    "address": hotel.get("address") or None,
                    "rating": hotel.get("location_rating") or None,
                    "snippet": hotel.get("description") or None,
                    "place_id": hotel.get('place_id') or None
                }
            result.append(res)
        if len(result)==3:
             break
    return {"results":result}


def execute_hotel_query(query):
    hotel_info = extract_hotel_info(query)
    print(type(hotel_info))
    print(hotel_info)
    return search_hotel_new(query=hotel_info.get('query'),min_price=hotel_info.get('min_price'), max_price=hotel_info.get('max_price'), hotel_type=hotel_info.get('hotel_type'),check_in_date=hotel_info.get('check_in_date'),check_out_date=hotel_info.get('check_out_date'))
    
def execute_hotel_query_green(query):
    hotel_info = extract_hotel_info(query)
    user_input = f"{hotel_info.get('query')} 環保 綠色 低碳"
    return search_hotel_new(query=user_input,min_price=hotel_info.get('min_price'), max_price=hotel_info.get('max_price'), hotel_type=hotel_info.get('hotel_type'),check_in_date=hotel_info.get('check_in_date'),check_out_date=hotel_info.get('check_out_date'))


>>>>>>> 7b86e5b... add hotel search and fix choose trans bug
   


