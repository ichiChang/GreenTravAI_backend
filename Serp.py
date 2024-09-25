import requests
import os
# Your SERP API key

API_KEY = os.getenv('SERP_API_KEY')

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
        "api_key": API_KEY
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()


    # Extract the results
    # results = []

    if 'ads' in data:
        ads_results = []
        for result in data['ads']:

            if int(result.get('position')) <=3:
                ad_entry = {
                    "title": result.get('title'),
                    "price": result.get('price'),
                    "rating": result.get('rating'),
                    "extensions": result.get('extensions'),
                    "link": result.get('tracking_link')
                }
                if ad_entry["title"] and ad_entry["link"]:
                    # print(ad_entry)
                    ads_results.append(ad_entry)
        print(ads_results)
        result = {"results": ads_results}

    elif 'local_results' in data:
          local_results = []
          local_res = data['local_results']
          places = local_res['places']

          for place in places:

                local_entry = {
                "title": place.get('title'),
                "address": place.get('address'),
                "rating": place.get('rating')
            }
                if local_entry["title"] and local_entry["address"]:
                  local_results.append(local_entry)
                  result = {"local_results": local_results}

    elif 'organic_results' in data:
      organic_results = []
      for res in data['organic_results']:
        if res.get('position') <=10:
          organic_entry = {
                    "title": res.get('title'),
                    "link": res.get('link'),
                    "snippet": res.get('snippet')
                }
          if organic_entry["title"]:
                    organic_results.append(organic_entry)
                    result = {"organic_results": organic_results}

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
        "q": f'{query} 環保 綠色',  # The search query
        "location": location,
        "hl": "zh-TW",
        "api_key": API_KEY
    }

    # Make the request to SERP API
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()


    # Extract the results
    # results = []

    if 'ads' in data:
        ads_results = []
        for result in data['ads']:

            if int(result.get('position')) <=3:
                ad_entry = {
                    "title": result.get('title'),
                    "price": result.get('price'),
                    "rating": result.get('rating'),
                    "extensions": result.get('extensions'),
                    "link": result.get('tracking_link')
                }
                if ad_entry["title"] and ad_entry["link"]:
                    # print(ad_entry)
                    ads_results.append(ad_entry)
        print(ads_results)
        result = {"results": ads_results}

    elif 'local_results' in data:
          local_results = []
          local_res = data['local_results']
          places = local_res['places']

          for place in places:

                local_entry = {
                "title": place.get('title'),
                "address": place.get('address'),
                "rating": place.get('rating')
            }
                if local_entry["title"] and local_entry["address"]:
                  local_results.append(local_entry)
                  result = {"local_results": local_results}

    elif 'organic_results' in data:
      organic_results = []
      for res in data['organic_results']:
        if res.get('position') <=10:
          organic_entry = {
                    "title": res.get('title'),
                    "link": res.get('link'),
                    "snippet": res.get('snippet')
                }
          if organic_entry["title"]:
                    organic_results.append(organic_entry)
                    result = {"organic_results": organic_results}

    else:
        return "No results found."

    # Join all results into a single string
    # print(result)
    return result
