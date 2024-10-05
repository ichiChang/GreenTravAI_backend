import requests
import os

# Your SERP API key

API_KEY = os.getenv("SERP_API_KEY")


def search_hotels(query: str, location: str = "Taipei") -> str:
    """
    Function to call SERP API and return hotel search results with titles and links.
    """
    # Query parameters
    params = {
        "engine": "google",
        "q": query,  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": API_KEY,
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print(data)

    # Extract the results
    # results = []

    if "ads" in data:
        ads_results = []
        for result in data["ads"]:

            if int(result.get("position")) <= 3:
                ad_entry = {
                    "title": result.get("title"),
                    "price": result.get("price") or None,
                    "rating": result.get("rating") or None,
                    "extensions": result.get("extensions") or None,
                    "link": result.get("tracking_link") or None,
                    "address": result.get("address") or None,
                    "snippet": result.get("snippet") or None,
                    "place_id": result.get("place_id") or None,
                }
                if ad_entry["title"] and ad_entry["link"]:
                    # print(ad_entry)
                    ads_results.append(ad_entry)
        print(ads_results)
        result = {"results": ads_results}

    elif "local_results" in data:
        local_results = []
        local_res = data["local_results"]
        places = local_res["places"]

        for place in places:

            local_entry = {
                "title": place.get("title"),
                "price": place.get("price") or None,
                "rating": place.get("rating"),
                "extensions": place.get("extensions") or None,
                "link": place.get("tracking_link") or None,
                "address": place.get("address"),
                "snippet": place.get("snippet") or None,
                "place_id": place.get("place_id") or None,
            }
            if local_entry["title"] and local_entry["address"]:
                local_results.append(local_entry)
                result = {"results": local_results}

    elif "organic_results" in data:
        organic_results = []
        for res in data["organic_results"]:
            if res.get("position") <= 3:
                organic_entry = {
                    "title": res.get("title"),
                    "price": res.get("price") or None,
                    "rating": res.get("rating") or None,
                    "extensions": res.get("extensions") or None,
                    "link": res.get("link"),
                    "address": res.get("address") or None,
                    "snippet": res.get("snippet") or None,
                    "place_id": res.get("place_id") or None,
                }
                if organic_entry["title"]:
                    organic_results.append(organic_entry)
                    result = {"results": organic_results}

    else:
        return "No results found."

    # Join all results into a single string
    # print(result)
    return result


def search_hotels_green(query: str, location: str = "Taipei") -> str:
    """
    Function to call SERP API and return hotel search results with titles and links.
    """
    # Query parameters
    params = {
        "engine": "google",
        "q": f"{query} 低碳 環保",  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": API_KEY,
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    print(data)

    # Extract the results
    # results = []

    if "ads" in data:
        ads_results = []
        for result in data["ads"]:

            if int(result.get("position")) <= 3:
                ad_entry = {
                    "title": result.get("title"),
                    "price": result.get("price") or None,
                    "rating": result.get("rating") or None,
                    "extensions": result.get("extensions") or None,
                    "link": result.get("tracking_link") or None,
                    "address": result.get("address") or None,
                    "snippet": result.get("snippet") or None,
                    "place_id": result.get("place_id") or None,
                }
                if ad_entry["title"] and ad_entry["link"]:
                    # print(ad_entry)
                    ads_results.append(ad_entry)
        print(ads_results)
        result = {"results": ads_results}

    elif "local_results" in data:
        local_results = []
        local_res = data["local_results"]
        places = local_res["places"]

        for place in places:

            local_entry = {
                "title": place.get("title"),
                "price": place.get("price") or None,
                "rating": place.get("rating"),
                "extensions": place.get("extensions") or None,
                "link": place.get("tracking_link") or None,
                "address": place.get("address"),
                "snippet": place.get("snippet") or None,
                "place_id": place.get("place_id") or None,
            }
            if local_entry["title"] and local_entry["address"]:
                local_results.append(local_entry)
                result = {"results": local_results}

    elif "organic_results" in data:
        organic_results = []
        for res in data["organic_results"]:
            if res.get("position") <= 3:
                organic_entry = {
                    "title": res.get("title"),
                    "price": res.get("price") or None,
                    "rating": res.get("rating") or None,
                    "extensions": res.get("extensions") or None,
                    "link": res.get("link"),
                    "address": res.get("address") or None,
                    "snippet": res.get("snippet") or None,
                    "place_id": res.get("place_id") or None,
                }
                if organic_entry["title"]:
                    organic_results.append(organic_entry)
                    result = {"results": organic_results}

    else:
        return "No results found."

    # Join all results into a single string
    # print(result)
    return result
