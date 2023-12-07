from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
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
    # Function to get social media links with Font Awesome icons
    def get_social_media_links(event):
        icon_map = {
            'youtube': 'fa-brands fa-youtube',
            'twitter': 'fa-brands fa-twitter',
            'facebook': 'fa-brands fa-facebook',
            'instagram': 'fa-brands fa-instagram',
            'spotify': 'fa-brands fa-spotify',
            'homepage': 'fa-solid fa-house',
            'musicbrainz': 'fa-solid fa-music',
            'wiki': 'fa-brands fa-wikipedia-w',
            'itunes': 'fa-brands fa-apple',
            'lastfm': 'fa-solid fa-tower-broadcast',
        }
        social_media_links = {}
        if event.get('_embedded') and event['_embedded'].get('attractions') and event['_embedded']['attractions']:
            first_attraction = event['_embedded']['attractions'][0]
            if first_attraction.get('externalLinks'):
                for key, value in first_attraction['externalLinks'].items():
                    if value and value[0].get('url'):
                        social_media_links[key] = {
                            "url": value[0]['url'],
                            "icon": icon_map.get(key, 'fa-question-circle')  # Default icon
                        }
        return social_media_links
    

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
        print(dateloc)
        try:
            # Parse the dateTime string into a datetime object
            date_time_obj = datetime.fromisoformat(dateloc['dateTime'])

            # Format the date and time
            formatted_date = date_time_obj.strftime("%a %b %d %Y")
            formatted_time = date_time_obj.strftime("%I:%M %p")
        except KeyError:
            formatted_date = "No date set"
            formatted_time = ""
        except ValueError:
            formatted_date = "Value error requires resolution"
            formatted_time = ""


        venue_ticket_link = item["url"]
        lowest_price = f"${item['priceRanges'][0]['min']}+" if 'priceRanges' in item and item['priceRanges'] else ''

        id = count
        count += 1
        # Named Card Data
        event_data = {
            "name": name,
            "image_url": image,
            "venue_ticket_link": venue_ticket_link,
            "venue_city": venue_city,
            "venue_state": venue_state,
            "venue_address": venue_address,
            "date": formatted_date,
            "time": formatted_time,
            "venue_name": venue_name,
            "social_media_links": get_social_media_links(item),
            "lowest_price": lowest_price,
            "id": id
        }
        card_info.append(event_data)


def band(request, band_id):
    band_name = card_info[band_id]["name"]

    this_band = Band.objects.filter(name=band_name)
    if len(this_band) == 0:
        add_band = Band(name=band_name)
        add_band.save()

    form = SubmitReview(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form_review = form.cleaned_data["review"]
            form_rating = form.cleaned_data["rating"]
            this_review = Reviews(band=this_band[0], review=form_review, rating=form_rating)
            this_review.save()

    review_query_set = Reviews.objects.filter(band__name=band_name)
    context = {
        'name': band_name,
        'form': form,
        'reviews': review_query_set
    }
    return render(request, 'band.html', context)


#Account Registration

#Register -> Instantly Login
def register_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('event_search') 
    return render(request, 'account/register.html', {'form': form})

#Login Fn    
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST) 
        if form.is_valid():
        # get the user info from the form data and log in the user
            user = form.get_user() 
            login(request, user) 
            return redirect('event_search')
    else:
        form = AuthenticationForm()
        return render(request, 'account/login.html', {'form': form})
                  
#Logout
def logout_view(request):
    logout(request)
    return redirect('event_search')

#Restricted Access Account Page
@login_required(login_url='/account/login/')
def account(request):
    return render(request, 'account/index.html')
