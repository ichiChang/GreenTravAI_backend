from langchain_openai import ChatOpenAI
import requests
import os
import openai
import googlemaps
from datetime import datetime, timedelta
from langchain import PromptTemplate, LLMChain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore

from langchain.llms import OpenAI
import json
import re
import html
from dotenv import load_dotenv
import pytz
from bs4 import BeautifulSoup
from zenrows import ZenRowsClient

# load_dotenv()
load_dotenv(dotenv_path="./.env")

API_KEY = os.getenv("SERP_API_KEY")


def get_ticket_price_and_details(link: str) -> dict:
    """
    Function to fetch the ticket page and extract the price, description, and other details.
    """
    client = ZenRowsClient(os.getenv('ZENROWS_API_KEY'))
    url = link

    response = client.get(url)

    html_source = response.text
    soup = BeautifulSoup(html_source, 'html.parser')
    status = False
    price_content = soup.find('meta', {'property': 'product:price:amount'}).get('content', None) if soup.find('meta', {'property': 'product:price:amount'}) else None
    price_content = int(price_content) if price_content and price_content.isdigit() else None
    description_content = soup.find('meta', {'name': 'description'}).get('content', None) if soup.find('meta', {'name': 'description'}) else None
    if price_content and description_content:
      status = True

    return {"price":price_content, "description":description_content,"status":status}

llm = ChatOpenAI(
    temperature=0.2, model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY")
)


def get_retriever(index_name, top_k, min_budget, max_budget):
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    # Update the dynamic filter to include price constraints
    dynamic_filter = {
        "price": {
            "$gte": min_budget,
            "$lte": max_budget,
        }  # Filter price within budget range
    }

    # Create the retriever
    retriever = PineconeVectorStore.from_existing_index(
        index_name=index_name, embedding=embeddings, text_key="name"
    )

    # Set the filter and top_k
    retriever = retriever.as_retriever(
        search_kwargs={
            "filter": dynamic_filter,
            "k": top_k,
        }
    )
    return retriever


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
        "q": f"{query} site: booking.com",  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": API_KEY
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    # print(data)

    # Extract hotel information
    hotels = []
    for result in data.get("organic_results", [])[:3]:  # Limit results to top 3
        hotel = {
            "title": result.get("title") or None,
            "price": result.get("price") or None,
            "extensions": result.get("extensions") or None,
            "link": result.get("link") or None,
            "address": result.get("address") or None,
            "rating": result.get("rating") or None,
            "snippet": result.get("description") or None,
            "place_id": result.get("place_id") or None,
        }
        hotels.append(hotel)

    return {"results": hotels}


def search_hotels_green(
    query: str, location: str = "Taipei", budget: str = None
) -> dict:
    """
    Function to call SERP API and return hotel search results with titles and links, including a budget.
    """
    # Add budget to query if provided
    # if budget:
    #     query += f" {budget}"

    # Query parameters
    params = {
        "engine": "google",
        "q": f"{query} site: booking.com",  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": API_KEY
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    # print(data)

    # Extract hotel information
    hotels = []
    for result in data.get("local_results", [])[:3]:  # Limit results to top 3
        hotel = {
            "title": result.get("title") or None,
            "price": result.get("price") or None,
            "extensions": result.get("extensions") or None,
            "link": result.get("link") or None,
            "address": result.get("address") or None,
            "rating": result.get("rating") or None,
            "snippet": result.get("description") or None,
            "place_id": result.get("place_id") or None,
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
        "q": f"{query}",  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": API_KEY
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    # print(data)
    places = []
    for result in data.get("local_results", [])[:3]:
        prompt_parts = []
        if result.get("title"):
            prompt_parts.append(f"Title: {result.get('title')}")
        if result.get("snippet"):
            prompt_parts.append(f"Snippet: {result.get('snippet')}")
        if result.get("extensions"):
            prompt_parts.append(f"Extensions: {result.get('extensions')}")
        if result.get("rating"):
            prompt_parts.append(f"Rating: {result.get('rating')}")
        prompt = "\n".join(prompt_parts) + "\nSummary:"
        summary = llm.invoke(
                    "the resposne must in traditional Chinese please remove any markdown tags and also the newline tags more that 20 words"
                    + prompt).content
        place = {
            "name": result.get("title") or None,
            # "price": result.get("price") or None,
            # "extensions": result.get("extensions") or None,
            "link": result.get("link") or None,
            # "address": result.get("address") or None,
            # "rating": result.get("rating") or None,
            "summary": f"店名:{result.get('title')} {summary}",
            # "place_id": result.get("place_id") or None,
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
        "q": f"{query} 有機 環保 素",  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key":API_KEY
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    # print(data)
    places = []
    for result in data.get("local_results", [])[:3]:
        prompt_parts = []
        if result.get("title"):
            prompt_parts.append(f"Title: {result.get('title')}")
        if result.get("snippet"):
            prompt_parts.append(f"Snippet: {result.get('snippet')}")
        if result.get("extensions"):
            prompt_parts.append(f"Extensions: {result.get('extensions')}")
        if result.get("rating"):
            prompt_parts.append(f"Rating: {result.get('rating')}")
        prompt = "\n".join(prompt_parts) + "\nSummary:"
        summary = llm.invoke(
                    "the resposne must in traditional Chinese please remove any markdown tags and also the newline tags more that 20 words"
                    + prompt).content
        place = {
            "name": result.get("title") or None,
            # "price": result.get("price") or None,
            # "extensions": result.get("extensions") or None,
            "link": result.get("link") or None,
            # "address": result.get("address") or None,
            # "rating": result.get("rating") or None,
            # "snippet": result.get("description") or None,
            "summary": f"店名:{result.get('title')} {summary}",
            # "place_id": result.get("place_id") or None,
        }
        places.append(place)

    return {"results": places}


# ticket planner
def search_ticket(query: str, location: str = "Taipei") -> str:
    """
    Function to call SERP API and return hotel search results with titles and links.
    """
    # Query parameters
    params = {
        "engine": "google",
        "q": f"{query} site: klook.com",  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": API_KEY,
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    if "organic_results" in data:
        organic_results = []
        for res in data["organic_results"]:
            if res.get("position") <= 5:
              if res.get("link"):
                # print(res.get("link"))
                ticket_detail = get_ticket_price_and_details(res.get("link"))
                if ticket_detail.get("status"):
                    prompt_parts = []
                    if res.get("title"):
                        prompt_parts.append(f"Title: {res.get('title')}")
                    if ticket_detail.get("description"):
                        prompt_parts.append(f"Snippet: {ticket_detail.get('description')}")
                    if ticket_detail.get("price"):
                        prompt_parts.append(f"Price: {ticket_detail.get('price')}")
                    if res.get("link"):
                        prompt_parts.append(f"link: {res.get('link')}")
                    
                    prompt = "\n".join(prompt_parts) + "\nSummary:"
                    summary = llm.invoke(
                                "the resposne must in traditional Chinese please remove any markdown tags and also the newline tags more that 20 words and highlight the ticket price with **, also attacht the link with markdown link tag"
                                + prompt).content   
                  
                    organic_entry = {
                            # "name": res.get("title"),
                            # "price": ticket_detail.get("price") or None,
                            # "rating": res.get("rating") or None,
                            # "extensions": res.get("extensions") or None,
                            # "link": res.get("link"),
                            # "address": res.get("address") or None,
                            "summary": f'{summary}',
                            # "place_id": res.get("place_id") or None,
                        }
                    organic_results.append(organic_entry)
                    if len(organic_results)==1:
                        break
        # result = {"results": organic_results}
        return organic_results[0]['summary']

                  


def validate_time_format(time_str: str) -> bool:
    # Regular expression for 24-hour time format hh:mm
    time_pattern = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
    return bool(time_pattern.match(time_str))


def extract_travel_details(query: str) -> dict:
    prompt_template = """
        Extract the travel details from the following query:
        If there is no specified departure_location using "台北市中正區北平西路3號100臺灣"
        If there is no specified departure_time using "10:00"
        If there is no specified departure_date using "2024-12-22"
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
        # print(travel_details)
        travel_details_dict = json.loads(travel_details)
        if "arrival_time" in travel_details_dict:
            if not validate_time_format(travel_details_dict["arrival_time"]):
                travel_details_dict["arrival_time"] = None

        return travel_details_dict

    except Exception as e:
        return f"Error occurred while extracting travel details: {e}"

    except Exception as e:
        return f"Error occurred while extracting travel details: {e}"


def get_google_maps_route(
    departure_location: str,
    destination: str,
    departure_time: datetime = None,
    arrival_time: datetime = None,
    mode: str = "transit",
):
    key = os.getenv("GOOGLE_MAP_API_KEY")
    gmaps = googlemaps.Client(key=key)
    try:
        if arrival_time:
            directions_result = gmaps.directions(
                origin=departure_location,
                destination=destination,
                mode=mode,  # You can also use 'transit', 'walking', 'bicycling', etc.
                arrival_time=arrival_time,
                language="zh-TW",
            )
        else:
            directions_result = gmaps.directions(
                origin=departure_location,
                destination=destination,
                mode=mode,  # You can also use 'transit', 'walking', 'bicycling', etc.
                departure_time=departure_time,
                language="zh-TW",
            )
        if directions_result:
            route_description = directions_result[0]["legs"][0]["steps"]
            directions = ""
            for idx, step in enumerate(route_description, 1):
                instructions = step["html_instructions"]
                # Remove HTML tags
                instructions = re.sub("<[^<]+?>", "", instructions)
                # Unescape HTML entities
                instructions = html.unescape(instructions)
                distance = step["distance"]["text"]
                duration = step["duration"]["text"]
                directions += (
                    f"{idx}. {instructions} （距離：{distance}，時間：{duration}）\n"
                )
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
    departure_location = travel_details.get(
        "departure_location", "台北市中正區北平西路3號100臺灣"
    )
    departure_date = travel_details.get("departure_date")
    departure_time = travel_details.get("departure_time")
    mode = travel_details.get("mode")
    arrival_time = travel_details.get("arrival_time")

    # Parse date and time for Google Maps
    if arrival_time:
        arrival_datetime = datetime.strptime(
            f"{departure_date} {arrival_time}", "%Y-%m-%d %H:%M"
        )
        route = get_google_maps_route(
            departure_location=departure_location,
            destination=destination,
            arrival_time=arrival_datetime,
            mode=mode,
        )
        return route
    else:
        departure_datetime = datetime.strptime(
            f"{departure_date} {departure_time}", "%Y-%m-%d %H:%M"
        )
        route = get_google_maps_route(
            departure_location=departure_location,
            destination=destination,
            departure_time=departure_datetime,
            mode=mode,
        )
        return route

    return route


def get_travel_route_with_google_maps_green(query: str):
    # Extract travel details using LLM
    travel_details = extract_travel_details(query)

    if isinstance(travel_details, str):  # Error handling
        return travel_details

    destination = travel_details.get("destination")
    departure_location = travel_details.get(
        "departure_location", "台北市中正區北平西路3號100臺灣"
    )
    departure_date = travel_details.get("departure_date")
    departure_time = travel_details.get("departure_time")
    # mode = travel_details.get("mode")
    arrival_time = travel_details.get("arrival_time")

    # Parse date and time for Google Maps
    if arrival_time:
        arrival_datetime = datetime.strptime(
            f"{departure_date} {arrival_time}", "%Y-%m-%d %H:%M"
        )
        route = get_google_maps_route(
            departure_location=departure_location,
            destination=destination,
            arrival_time=arrival_datetime,
        )
        return route
    else:
        departure_datetime = datetime.strptime(
            f"{departure_date} {departure_time}", "%Y-%m-%d %H:%M"
        )
        route = get_google_maps_route(
            departure_location=departure_location,
            destination=destination,
            departure_time=departure_datetime,
        )
        return route


def get_current_date_in_taipei() -> str:
    taipei_tz = pytz.timezone("Asia/Taipei")
    return datetime.now(taipei_tz).strftime("%Y-%m-%d")


def validate_date_format(date_str: str) -> bool:
    """Helper function to validate if a string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def extract_hotel_info(query: str) -> dict:
    prompt_template = """
        回答中請勿包含```json或```格式。
        Extract the hotel booking details from the following query:
        If there is no specified check-in date, fill "no offer".
        If there is no specified check-out date, fill "no offer.
        If there is no specified min_price, use Null.
        If there is no specified max_price, use Null.
        If there is no specified hotel_type, use 飯店.
        The current is 2024, if there is no specified year in date/


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
        # print(hotel_details)
        hotel_details_dict = json.loads(hotel_details)

        # Get current date and next day in Taipei timezone
        current_date = get_current_date_in_taipei()
        next_day = (
            datetime.strptime(current_date, "%Y-%m-%d") + timedelta(days=1)
        ).strftime("%Y-%m-%d")

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
    return int(price_str.replace("$", "").replace(",", ""))


def get_address(latitude, longitude, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{latitude},{longitude}",
        "key": api_key,
        "language": "zh-TW",  # Traditional Chinese
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        result = response.json()
        if result["status"] == "OK":
            address = result["results"][0]["formatted_address"]
            return str(address)
        else:
            return f"Error: {result['status']}"
    else:
        return f"HTTP Error: {response.status_code}"


def search_hotel_new(
    query: str,
    location: str = "Taipei",
    min_price=None,
    max_price=None,
    hotel_type: str = None,
    check_in_date=None,
    check_out_date=None,
    eco_certified=False,
):
    """
    Function to call SERP API and return hotel search results with titles and links,
    and filter based on a given price range.

    Args:
    - query: The search query for hotels
    - location: The location to search in
    - min_price: Minimum price for hotels
    - max_price: Maximum price for hotels
    """
    if hotel_type not in ["飯店", "民宿"]:
        hotel_type = "飯店"
    # print(type(min_price))
    if not isinstance(min_price, int):
        min_price = 0  # Default value if min_price is not an integer
    if not isinstance(max_price, int):
        max_price = 1000000  # Default
    # Query parameters for SerpAPI using Google Hotels
    params = {
        "engine": "google_hotels",
        "q": f"{query} {hotel_type}",
        "location": location,
        "price_min": min_price,
        "price_max": max_price,
        "api_key": API_KEY,
        "hl": "zh-TW",
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": "TWD",
        "gl": "tw",
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    # print(data)
    # hotels = []
    # hotels['properties']
    # print(data)
    # print(data['properties'])
    result = []
    properties = data.get("properties", [])
    for hotel in properties:
        # print(type(min_price))
        # print(type(max_price))
        # print(int(hotel.get('rate_per_night').get('lowest')))
        price = convert_price_to_int(hotel.get("rate_per_night").get("lowest"))
        if min_price <= price <= max_price:
            prompt_parts = []
            if hotel.get("link"):
                address = get_address(
                        hotel.get("gps_coordinates")["latitude"],
                        hotel.get("gps_coordinates")["longitude"],
                        os.getenv("GOOGLE_MAP_API_KEY"),
                    )or None
                
                if hotel["name"]:
                    prompt_parts.append(f"Title: {hotel['name']}")
                if hotel.get("description"):
                    prompt_parts.append(f"Snippet: {hotel.get('description')}")
                if hotel.get("location_rating"):
                    prompt_parts.append(f"Rating: {hotel.get('location_rating')}")
                if hotel.get("address"):
                    prompt_parts.append(f"address: {address}")
                if price:
                    prompt_parts.append(f"price: {price}")
                prompt = "\n".join(prompt_parts) + "\nSummary:"
                summary = llm.invoke(
                            "the resposne must in traditional Chinese please remove any markdown tags and also the newline tags more that 20 words, please hightlight the price with ** "
                            + prompt).content    
                # print(hotel)
                res = {
                    "name": hotel["name"] or None,
                    # "price": price or None,
                    # "extensions": hotel.get("extension") or None,
                    "link": hotel.get("link") or None,
                    # "address": get_address(
                    #     hotel.get("gps_coordinates")["latitude"],
                    #     hotel.get("gps_coordinates")["longitude"],
                    #     os.getenv("GOOGLE_MAP_API_KEY"),
                    # )
                    # or None,
                    # "address": hotel.get("address") or None,
                    # "rating": hotel.get("location_rating") or None,
                    "summary": f'住宿:{hotel["name"]} {summary}',
                    # "place_id": hotel.get("place_id") or None,
                }

                result.append(res)
            if len(result) == 3:
                break
    return {"results": result}


def search_hotel_new_green(query, min_price, max_price):
    # print(type(min_price))
    if not isinstance(min_price, int):
        min_price = 0  # Default value if min_price is not an integer
    if not isinstance(max_price, int):
        max_price = 1000000  # Default
    green_hotel_retriever_for_search = get_retriever(
        index_name="green-hotel-for-search", min_budget=min_price, max_budget=max_price, top_k=3
    )
    green_hotel_for_search = green_hotel_retriever_for_search.get_relevant_documents(
        query
    )
    result = []

    for hotel in green_hotel_for_search:
        prompt_parts = []
        name = hotel.page_content or None
        detail = hotel.metadata
        if name:
            prompt_parts.append(f"Title: {name}")
        if detail.get("description"):
            prompt_parts.append(f"Snippet: {detail.get('description')}")
        if detail.get("location_rating"):
            prompt_parts.append(f"Rating: {detail.get('location_rating')}")
        if detail.get("price"):
            prompt_parts.append(f"price: {detail.get('price')}")

        prompt = "\n".join(prompt_parts) + "\nSummary:"
        summary = llm.invoke(
                    "the resposne must in traditional Chinese please remove any markdown tags and also the newline tags more that 20 words, please hightlight the price with ** "
                    + prompt).content
        res = {
            "name": name,
            # "price": result.get("price") or None,
            # "extensions": result.get("extensions") or None,
            "link": detail.get("link") or None,
            # "address": result.get("address") or None,
            # "rating": result.get("rating") or None,
            # "snippet": result.get("description") or None,
            "summary": f"住宿:{name} {summary}",
            # "place_id": result.get("place_id") or None,
        }
        # res = {
        #     "title": name,
        #     "price": detail.get("price") or None,
        #     "extensions": detail.get("extension") or None,
        #     "link": detail.get("link") or None,
        #     "address": detail.get("address") or None,
        #     "rating": detail.get("location_rating") or None,
        #     "snippet": detail.get("description") or None,
        #     "place_id": detail.get("place_id") or None,
        # }

        result.append(res)
    return {"results": result}


def execute_hotel_query(query):
    hotel_info = extract_hotel_info(query)
    # print(hotel_info)
    # print(hotel_info)
    return search_hotel_new(
        query=hotel_info.get("query"),
        min_price=hotel_info.get("min_price"),
        max_price=hotel_info.get("max_price"),
        hotel_type=hotel_info.get("hotel_type"),
        check_in_date=hotel_info.get("check_in_date"),
        check_out_date=hotel_info.get("check_out_date"),
    )


def execute_hotel_query_green(query):
    hotel_info = extract_hotel_info(query)
    # print(hotel_info)

    return search_hotel_new_green(
        query=hotel_info.get("query"),
        min_price=hotel_info.get("min_price"),
        max_price=hotel_info.get("max_price"),
       
    )


