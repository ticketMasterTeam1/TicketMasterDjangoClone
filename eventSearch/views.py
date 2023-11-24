from django.shortcuts import render
import requests

#response = requests.get("https://app.ticketmaster.com/discovery/v2/events.json?size=20&apikey=Ij0EiPF3QAJv6NvdHh92ALlIHgMK8a7U&city=${city}&keyword=${classificationName}&sort=date,asc")

# Create your views here.

def event_search(request):
    get_events("hartford","music")
    return render(request, 'event-search.html')

def get_events(city, classification_name):
    try:
        response = requests.get("https://app.ticketmaster.com/discovery/v2/events.json?size=20&apikey=Ij0EiPF3QAJv6NvdHh92ALlIHgMK8a7U&city=${city}&keyword=${classification_name}&sort=date,asc")

        """
        url = "https://app.ticketmaster.com/discovery/v2/events.json?size=20&apikey=Ij0EiPF3QAJv6NvdHh92ALlIHgMK8a7U"
        parameters = {
            "size": = 20,
            "api_key":= Ij0EiPF3QAJv6NvdHh92ALlIHgMK8a7U,
            "city": = city,
            "keyword": = classification_name,
            "sort": "date,asc",
        }
        """

        #send GET request to URL w/ params
        #response = requests.get(url, params=parameters)
        #Raise exception for 4xx and 5xx status code
        response.raise_for_status()
        data = response.json()
        print(data)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

