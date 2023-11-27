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
    print(eventsPath)