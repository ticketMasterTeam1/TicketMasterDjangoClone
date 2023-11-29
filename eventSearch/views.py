from django.shortcuts import render
from datetime import datetime
import requests

#my javascript json response -> response = requests.get("https://app.ticketmaster.com/discovery/v2/events.json?size=20&apikey=Ij0EiPF3QAJv6NvdHh92ALlIHgMK8a7U&city=${city}&keyword=${classificationName}&sort=date,asc")

# Create your views here.

#card info holds data to be displayed on each card
card_info=[]

#Gets events through JSON request then renders card
def event_search(request):

    get_events("hartford","music")
    return render(request, 'event-search.html', context={'cards': card_info})

#JSON request -> event_search_format
def get_events(city, classification_name):
    try:
        response = requests.get("https://app.ticketmaster.com/discovery/v2/events.json?size=20&apikey=Ij0EiPF3QAJv6NvdHh92ALlIHgMK8a7U&city=" + city + "&keyword=" + classification_name +"&sort=date,asc")

        #send GET request to URL w/ params
        #response = requests.get(url, params=parameters)
        #Raise exception for 4xx and 5xx status code
        response.raise_for_status()
        data = response.json()
        #print(data)
        event_search_format(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

#using JSON data create data for cards
def event_search_format(data):
    total_elements = data["page"]["totalElements"]
    total_results = data["page"]["size"]
    eventsPath = data["_embedded"]["events"]
    for item in eventsPath:
        name = item["name"]

        best_image = item["images"][0]
        print(best_image)
        for image in item["images"]:
            this_image = image
            if (this_image["width"] > best_image["width"]):
                best_image = this_image
        image = best_image["url"]

        #need to format into date and time
        #dateTime = item["dates"]["start"]["dateTime"]

        #venue_path = item["_embedded"]["venues"]
        #venue_city = item["_embedded"]["venues"]["city"]["name"]
        #venue_state = item["_embedded"]["venues"]["state"]["name"]
        #venue_address_l1 = item["_embedded"]["venues"]["address"]["line1"]
        venue_ticket_link = item["url"]

        event_data = [name,image,venue_ticket_link]
        card_info.append(event_data)
