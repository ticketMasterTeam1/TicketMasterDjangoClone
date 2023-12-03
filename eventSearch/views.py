from django.shortcuts import render, redirect
from datetime import datetime
import requests
from .forms import SubmitReview
from .models import Band, Reviews

# card info holds data to be displayed on each card - 2D array for each event with all info
card_info = []


# Gets events through JSON request then renders card
def event_search(request):
    if request.method == 'POST':
        # get search terms
        city = request.POST['city']
        classification_name = request.POST['classification_name']
        print(city)
        print(classification_name)

        if not city or not classification_name:
            print("redirected: not city or not classification name")
            return redirect('event_search')

        get_events(city, classification_name)
        print(card_info)
        if card_info is None:
            return redirect('event_search')
        else:
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
    count = 0
    for item in eventsPath:
        name = item["name"]
        venue_path = item["_embedded"]["venues"][0]
        venue_city = venue_path["city"]["name"]
        venue_state = venue_path["state"]["name"]
        venue_address = venue_path["address"]["line1"]
        venue_name = venue_path["name"]

        best_image = item["images"][0]
        for image in item["images"]:
            this_image = image
            if (this_image["width"] > best_image["width"]):
                best_image = this_image
        image = best_image["url"]

        # need to format into date and time
        dateloc = item["dates"]["start"]
        try:
            date_time = dateloc['dateTime']
        except:
            date_time = "no date or time set"

        venue_ticket_link = item["url"]
        id = count
        count += 1
        event_data = [name, image, venue_ticket_link, venue_city, venue_state, venue_address, date_time, venue_name, id]
        card_info.append(event_data)


def band(request, band_id):
    band_name = card_info[band_id][0]
    print(band_name)

    this_band = Band.objects.filter(name=band_name)
    print(this_band)
    if len(this_band) == 0:
        add_band = Band(name=band_name)
        add_band.save()

    form = SubmitReview(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()

    review_query_set = Reviews.objects.filter(band__name=band_name)
    context = {
        'name': band_name,
        'form': form,
        'reviews': review_query_set
    }

    print(context)

    return render(request, 'band.html', context)
