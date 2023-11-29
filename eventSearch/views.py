from django.shortcuts import render
from datetime import datetime
import requests

# my javascript json response -> response = requests.get("https://app.ticketmaster.com/discovery/v2/events.json?size=20&apikey=Ij0EiPF3QAJv6NvdHh92ALlIHgMK8a7U&city=${city}&keyword=${classificationName}&sort=date,asc")

# Create your views here.

# card info holds data to be displayed on each card
card_info = []


# Gets events through JSON request then renders card
def event_search(request):
    get_events("hartford", "music")
    print(card_info)
    return render(request, 'event-search.html', context={'cards': card_info})


# JSON request -> event_search_format
def get_events(city, classification_name):
    try:
        response = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json?size=20&apikey=Ij0EiPF3QAJv6NvdHh92ALlIHgMK8a7U&city=" + city + "&keyword=" + classification_name + "&sort=date,asc")

        # send GET request to URL w/ params
        # response = requests.get(url, params=parameters)
        # Raise exception for 4xx and 5xx status code
        response.raise_for_status()
        data = response.json()
        # print(data)
        event_search_format(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


# using JSON data create data for cards
def event_search_format(data):
    total_elements = data["page"]["totalElements"]
    total_results = data["page"]["size"]
    eventsPath = data["_embedded"]["events"]
    for item in eventsPath:
        name = item["name"]
        venue_path = item["_embedded"]["venues"][0]
        venue_city = venue_path["city"]["name"]
        venue_state = venue_path["state"]["name"]
        venue_address = venue_path["address"]["line1"]
        venue_name = venue_path["name"]

        print(venue_city)

        best_image = item["images"][0]
        for image in item["images"]:
            this_image = image
            if (this_image["width"] > best_image["width"]):
                best_image = this_image
        image = best_image["url"]

        # need to format into date and time
        dateloc = item["dates"]["start"]
        print(dateloc)
        try:
            date_time = dateloc['dateTime']
        except:
            date_time = "no date or time set"

        print(date_time)

        venue_ticket_link = item["url"]

        event_data = [name, image, venue_ticket_link, venue_city, venue_state, venue_address, date_time, venue_name]
        card_info.append(event_data)
