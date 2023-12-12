from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
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
    card_info.clear()
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

    try:
        eventsPath = data["_embedded"]["events"]
    except KeyError:
        return
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
            date_obj = datetime.strptime(dateloc['localDate'], "%Y-%m-%d")
            formatted_date = date_obj.strftime("%a %b %d %Y")
        except KeyError:
            formatted_date = "No Date Set"

        try:
            time_obj = datetime.strptime(dateloc['localTime'], "%H:%M:%S")
            formatted_time = time_obj.strftime("%I:%M %p")
        except KeyError:
            formatted_time = "No Time Set"


        venue_ticket_link = item["url"]
        try:
            lowest_price = f"${item['priceRanges'][0]['min']}+" if 'priceRanges' in item and item['priceRanges'] else ''
        except KeyError:
            lowest_price = ""

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

def band(request, band_id, from_account):
    if from_account == 0:
        band_name = card_info[band_id]["name"]
        band_img_url = card_info[band_id]["image_url"]
        this_band, created = Band.objects.get_or_create(name=band_name, image_url=band_img_url)
    else:
        this_band = Band.objects.get(id=band_id)
        band_name = this_band.name
        band_img_url = this_band.image_url


    form = SubmitReview(request.POST or None)

    star_range = range(1, 6)

    if request.method == 'POST':
        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            action = request.POST.get('action')
            review_id = request.POST.get('review_id')
            review = get_object_or_404(Reviews, id=review_id)

            if request.user != review.author:
                return JsonResponse({'error': 'Unauthorized'}, status=403)

            if action == 'delete':
                review.delete()
                return JsonResponse({'status': 'success'})
            elif action == 'edit':
                edit_form = SubmitReview(request.POST, instance=review)
                if edit_form.is_valid():
                    edited_review = edit_form.save(commit=False)
                    edited_review.rating = request.POST.get('rating')  # Update the rating
                    edited_review.save()
                    return JsonResponse({'status': 'success', 'new_text': edited_review.review, 'new_rating': edited_review.rating})
                else:
                    return JsonResponse({'status': 'error', 'errors': edit_form.errors}, status=400)
        else:
            if form.is_valid():
                new_review = form.save(commit=False)
                new_review.author = request.user
                new_review.band = this_band
                new_review.save()
                return redirect('band', band_id=band_id, from_account=0)

    review_query_set = Reviews.objects.filter(band=this_band).order_by('-created_on')
    reviews = [{
        'id': review.id,
        'review': review.review,
        'rating': review.rating,
        'author': review.author.username,
        'is_author': review.author == request.user
    } for review in review_query_set]

    context = {
        'name': band_name,
        'form': form,
        'reviews': reviews,
        'star_range': star_range,
        'image_url': band_img_url
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
@login_required(login_url='/login/')
def account(request):
    user_reviews = Reviews.objects.filter(author=request.user)
    return render(request, 'account/index.html', {'user_reviews': user_reviews})