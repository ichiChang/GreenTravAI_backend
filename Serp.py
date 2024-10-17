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

   


