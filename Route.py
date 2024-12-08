import requests


def get_directions(origin, destination, mode, api_key):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode={mode}&key={api_key}"
    response = requests.get(url)
    return response.json()


def get_duration_in_seconds(directions):
    if directions["status"] == "OK":
        leg = directions["routes"][0]["legs"][0]
        duration = leg["duration"]["value"]  # in seconds
        distance = leg["distance"]["value"]  # in meters
        distance_km = distance / 1000  # convert to kilometers
        return duration, distance_km
    return int(0), int(0)


def print_detailed_route_info(directions):
    if directions["status"] == "OK":
        steps = directions["routes"][0]["legs"][0]["steps"]
        for step in steps:
            instructions = step["html_instructions"]
            distance = step["distance"]["text"]
            duration = step["duration"]["text"]

            # If using transit, provide additional details
            if "transit_details" in step:
                line_name = step["transit_details"]["line"]["name"]
                vehicle_type = step["transit_details"]["line"]["vehicle"]["type"]
                departure_stop = step["transit_details"]["departure_stop"]["name"]
                arrival_stop = step["transit_details"]["arrival_stop"]["name"]
                # print(
                #     f"Take {vehicle_type} ({line_name}) from {departure_stop} to {arrival_stop}."
                # )
            else:
                print(f"{instructions} for {distance}, taking about {duration}.")
    else:
        print("No route found.")


def find_optimal_mode(origin, destination, api_key):
    modes = ["driving", "walking", "bicycling", "transit", "TWO_WHEELER"]
    optimal_mode = None
    shortest_duration = float("inf")
    best_directions = None
    best_distance_km = float("inf")


    for mode in modes:
        directions = get_directions(origin, destination, mode, api_key)
        duration, distance_km = get_duration_in_seconds(directions)

        # print(f"Mode: {mode}, Duration: {duration} seconds")

        if duration < shortest_duration:
            shortest_duration = duration
            optimal_mode = mode
            best_directions = directions
            best_distance_km = distance_km

    return optimal_mode, shortest_duration, best_directions, best_distance_km


def get_lat_long(address, api_key):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            # Extract latitude and longitude from the response
            latitude = data["results"][0]["geometry"]["location"]["lat"]
            longitude = data["results"][0]["geometry"]["location"]["lng"]
            return  longitude, latitude
        else:
            print("Error:", data["status"])
    else:
        print("Request failed with status code:", response.status_code)
    return None, None
