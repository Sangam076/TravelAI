from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.formats import date_format
from django.views.generic import ListView, TemplateView, View
from .models import Message
from .forms import (
    ProfileForm,
    UserCreationForm,
)
from .models import  Profile
from django.shortcuts import render, redirect

import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
import os
from django.conf import settings
from .models import TravelPlan
from .forms import TravelPlanForm
import requests
import http.client






genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def fetch_place_info(place):
    """Fetch travel insights for a given place using Google Gemini API."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(f"Give a short travel guide for {place}.")
        return response.text
    except Exception as e:
        return f"Error fetching details: {str(e)}"

def travel_guide(request):
    """Render the travel guide page."""
    return render(request, "travel_guide.html")
def format_text_with_html(text):
    # Remove ** and * markers
    cleaned_text = text.replace('**', '').replace('*', '')
    
    # Split text into sections (assuming sections are separated by markers like "Getting There:", "What to See:", etc.)
    sections = cleaned_text.split(':')
    
    formatted_html = ""
    for i in range(0, len(sections)-1, 2):
        if i+1 < len(sections):
            title = sections[i].strip()
            content = sections[i+1].strip()
            # Create HTML structure for each section
            formatted_html += f"""
                <div class="mb-4">
                    <h3 class="text-xl font-semibold mb-2">{title}</h3>
                    <p class="text-gray-700">{content}</p>
                </div>
            """
    
    return formatted_html
def get_place_info(request):
    """Handle AJAX request to fetch place insights dynamically."""
    place = request.GET.get("place", "")
    if place:
        info = fetch_place_info(place)
        return JsonResponse({"info": info})
    return JsonResponse({"info": "No place provided."})

from django.utils.timezone import make_aware
from datetime import datetime
@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '') 
    users = User.objects.exclude(id=request.user.id) 
    

    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))  

    chats = chats.order_by('timestamp') 
    user_last_messages = []

    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Fix sorting issue
    user_last_messages.sort(
    key=lambda x: x['last_message'].timestamp if x['last_message'] else make_aware(datetime.min),
    reverse=True
)

    return render(request, 'user_profile.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query 
    })
from django.urls import reverse
from .models import TravelPlan, PlanInvite, Message
@login_required
def share_plan(request, pk):
    """
    Invite a user to collaborate on a travel plan.
    """
    travel_plan = get_object_or_404(TravelPlan, pk=pk)

    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')

        try:
            receiver = User.objects.get(username=receiver_username)

            # Create an invite entry
            invite = PlanInvite.objects.create(
                plan=travel_plan,
                sender=request.user,
                receiver=receiver
            )

            # Generate invite link
            invite_url = request.build_absolute_uri(invite.get_invite_url())

            # Send message with invite
            message_content = f"""
📩 **You're Invited to a Travel Plan!** 🌍

**{travel_plan.destination}**
• Duration: {travel_plan.duration} days
• Budget: {travel_plan.budget.capitalize()}

👉 [Click here to accept the invite]({invite_url})
"""

            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=message_content
            )

            messages.success(request, f'Invite sent to {receiver_username}!')
            return redirect('view_plan', pk=pk)

        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('view_plan', pk=pk)

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'share_plan.html', {'plan': travel_plan, 'users': users})

@login_required
def accept_invite(request, token):
    """
    Accept a travel plan invite and grant the user access.
    """
    invite = get_object_or_404(PlanInvite, token=token, accepted=False)

    # Mark invite as accepted
    invite.accepted = True
    invite.save()

    # Redirect to the plan page
    messages.success(request, 'You have joined the travel plan!')
    return redirect('view_plan', pk=invite.plan.pk)


# Home Page View
from django.views.generic import ListView
from .models import TravelPlan  # Import your TravelPlan model

class HomeView(ListView):
    model = TravelPlan  # ✅ Fetch Travel Plans
    template_name = "index.html"
    context_object_name = "plans"  # ✅ Update context name to 'plans'
    ordering = ["-created_at"]  # ✅ Ensure 'created_at' exists in TravelPlan

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_saved=True)  # ✅ Show only saved plans

        destination = self.request.GET.get('destination')  # ✅ Search by destination
        category = self.request.GET.get('category')  # ✅ Filter by category if applicable

        if destination:
            queryset = queryset.filter(destination__icontains=destination)
        if category and category != "All Categories":
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context




# Logout User View
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')


# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user:
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('home')
            else:
                messages.error(request, 'Authentication failed after registration.')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# About Page View
class AboutView(TemplateView):
    template_name = "about.html"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@login_required
def create_plan(request):
    """Handles travel plan creation with AI-generated details."""
    if request.method == 'POST':
        form = TravelPlanForm(request.POST)
        if form.is_valid():
            travel_plan = form.save(commit=False)
            travel_plan.user = request.user
            
            # Create budget-specific prompts
            budget_details = {
                'low': {
                    'daily_budget': '$50-100 per day',
                    'accommodation': 'Budget hostels, shared rooms, or affordable guesthouses',
                    'dining': 'Street food, local markets, budget-friendly cafes',
                    'activities': 'Free walking tours, public parks, free museum days',
                    'transport': 'Public transportation, budget bus or train options'
                },
                'moderate': {
                    'daily_budget': '$100-250 per day',
                    'accommodation': 'Mid-range hotels, comfortable Airbnb, budget-friendly boutique hotels',
                    'dining': 'Mix of local restaurants and mid-range dining',
                    'activities': 'Guided tours, museum entries, some paid attractions',
                    'transport': 'Mix of public transport and occasional taxi/rideshare'
                },
                'high': {
                    'daily_budget': '$250-500+ per day',
                    'accommodation': 'Luxury hotels, high-end resorts, premium Airbnb',
                    'dining': 'Fine dining, michelin-starred restaurants, gourmet experiences',
                    'activities': 'Private tours, exclusive experiences, premium attractions',
                    'transport': 'Private transfers, first-class train, business class flights'
                }
            }
            
            # Get the specific budget details
            budget_info = budget_details.get(travel_plan.budget, budget_details['moderate'])
            
            # Construct a structured prompt for better API performance
            prompt = f"""
            Create a comprehensive travel plan for {travel_plan.destination}.
            Budget Level: {travel_plan.budget.capitalize()}
            
            BUDGET PARAMETERS:
            • Daily Budget: {budget_info['daily_budget']}
            • Accommodation: {budget_info['accommodation']}
            • Dining: {budget_info['dining']}
            • Activities: {budget_info['activities']}
            • Transportation: {budget_info['transport']}

            Travel Details:
            - Duration: {travel_plan.duration} days
            - Interests: {travel_plan.interests}
            - Group Type: {travel_plan.group_type}

            Provide the following information with clear section headers:

            1. MUST-VISIT PLACES: List 5-7 key places aligned with the budget level
            2. SUGGESTED ACTIVITIES: List 5-7 activities matching the budget constraints
            3. LOCAL RESTAURANTS: List 5-7 restaurants that fit the budget range
            4. BUDGET BREAKDOWN: Provide a detailed budget allocation with:
               - Estimated daily expenses
               - Accommodation strategy
               - Food and dining budget
               - Transportation expenses
               - Activity and entrance fees
               - Miscellaneous and emergency funds
               - Specific money-saving tips for this budget level
            5. BEST TIME TO VISIT: Write a short paragraph about the best seasons to visit
            6. DAILY ITINERARY: Create a day-by-day plan with paragraphs for each day
            7. PACKING CHECKLIST: Create a list of essential items to pack

            Format each section with its header in ALL CAPS.
            Ensure all recommendations are tailored to the {travel_plan.budget} budget level.
            """
            
            try:
                # Create a new Gemini model instance inside the function
                model = genai.GenerativeModel("gemini-1.5-pro")
                response = model.generate_content(prompt)
                
                if hasattr(response, 'text'):
                    ai_content = response.text
                else:
                    raise ValueError("Unexpected response format from Gemini API")
                
                # Parse the AI content into sections
                sections = parse_ai_content(ai_content)
                
                # Assign the parsed sections to the travel plan fields
                travel_plan.places_to_visit = sections.get('MUST-VISIT PLACES', '')
                travel_plan.activities = sections.get('SUGGESTED ACTIVITIES', '')
                travel_plan.restaurants = sections.get('LOCAL RESTAURANTS', '')
                travel_plan.budget_breakdown = sections.get('BUDGET BREAKDOWN', '')
                travel_plan.itinerary = sections.get('DAILY ITINERARY', '')
                travel_plan.packing_checklist = sections.get('PACKING CHECKLIST', '')
                travel_plan.best_time_to_visit = sections.get('BEST TIME TO VISIT', '')
                
                travel_plan.save()
                return redirect('view_plan', pk=travel_plan.pk)
                
            except Exception as e:
                import traceback
                print(f"Error generating AI content: {str(e)}")
                traceback.print_exc()
                form.add_error(None, f"Error generating travel plan: {str(e)}")
    else:
        form = TravelPlanForm()
    
    return render(request, 'create_plan.html', {'form': form})
def parse_ai_content(content):
    """
    Parse AI-generated content into structured sections based on ALL CAPS headers.
    Also cleans up formatting issues like excessive asterisks.
    """
    sections = {}
    current_section = None
    current_content = []
    
    # Split the content into lines
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Clean up excessive asterisks and other decorative symbols
        line = line.replace('**', '').replace('****', '').replace('*****', '')
        
        # Check if this line is a section header (in ALL CAPS)
        potential_header = line.strip(':#-*1234567890. ')
        if potential_header.isupper() and len(potential_header) > 3:
            # If we were collecting content for a previous section, save it
            if current_section:
                sections[current_section] = '\n'.join(current_content)
                current_content = []
            
            # Start a new section
            current_section = potential_header
        elif current_section:
            # Clean up bullet points if they're using asterisks
            if line.startswith('* '):
                line = '• ' + line[2:]  # Replace * with proper bullet point
            elif line.startswith('** '):
                line = '• ' + line[3:]
            elif line.startswith('- '):
                line = '• ' + line[2:]  # Standardize different bullet styles
                
            # Add this line to the current section's content
            current_content.append(line)
    
    # Save the last section if there is one
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections
@login_required
def view_plan(request, pk):
    """Displays a generated travel plan."""
    travel_plan = get_object_or_404(TravelPlan, pk=pk)
    return render(request, 'view_plan.html', {'plan': travel_plan})


@login_required
def save_plan(request, pk):
    """Saves a travel plan for future reference."""
    travel_plan = get_object_or_404(TravelPlan, pk=pk)
    
    # Check if the user owns this plan
    if travel_plan.user != request.user:
        messages.error(request, "You don't have permission to save this plan.")
        return redirect('home')
    
    # Mark the plan as saved
    travel_plan.is_saved = True
    travel_plan.save()
    
    messages.success(request, f"Your travel plan for {travel_plan.destination} has been saved!")
    return redirect('view_plan', pk=travel_plan.pk)




@login_required
def saved_plans(request):
    """Displays all saved travel plans for the user."""
    plans = TravelPlan.objects.filter(user=request.user, is_saved=True).order_by('-updated_at')
    return render(request, 'saved_plans.html', {'plans': plans})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user=request.user)
        profile.bio = request.POST.get('bio')
        profile.twitter = request.POST.get('twitter')
        profile.instagram = request.POST.get('instagram')
        profile.linkedin = request.POST.get('linkedin')
        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']
        profile.save()

        return JsonResponse({
            'success': True,
            'bio': profile.bio,
            'photo_url': profile.photo.url,
            'twitter': profile.twitter,
            'instagram': profile.instagram,
            'linkedin': profile.linkedin,
        })
    return JsonResponse({'success': False})
from datetime import datetime
import json


RAPIDAPI_KEY = ""
RAPIDAPI_HOST = ""




def search_hotels_page(request):
    return render(request, "search.html")

def get_destination_id(city_name):
    url = "https://booking-com.p.rapidapi.com/v1/hotels/locations"
        
    querystring = {
        "name": city_name,
        "locale": "en-gb"
    }
    
    headers = {
        "x-rapidapi-key": "",
        "x-rapidapi-host": ""
    }
    
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    
    if data and isinstance(data, list):
        return data[0].get("dest_id", None)  
    return None  # No match found

def search_hotels(request):
    print("Received GET parameters:", request.GET)  # Debugging line
    
    checkin_date = request.GET.get("checkin_date", "2025-06-16")
    checkout_date = request.GET.get("checkout_date", "2025-06-17")
    adults_number = request.GET.get("adults_number", "2")
    children_number = request.GET.get("children_number", "0")  # Default to 0
    children_ages = request.GET.get("children_ages", "")  # Allow empty if 0 children
    city = request.GET.get("city", "New York")  # Default city
    currency = request.GET.get("currency", "USD")
    page_number = request.GET.get("page", "0")
    
    # Calculate number of nights
    try:
        check_in = datetime.strptime(checkin_date, "%Y-%m-%d")
        check_out = datetime.strptime(checkout_date, "%Y-%m-%d")
        total_nights = (check_out - check_in).days
    except:
        total_nights = 1  # Default if dates are invalid
    
    # Step 1: Get the destination ID from the city name
    dest_id = get_destination_id(city)
    if not dest_id:
        return render(request, "hotel_results.html", {
            "error": "Invalid city name or city not found",
            "city_name": city,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "adults_number": adults_number,
            "children_number": children_number,
            "total_nights": total_nights,
            "results": {"count": 0}
        })
    
    # Step 2: Search hotels using the destination ID
    url = "https://booking-com.p.rapidapi.com/v1/hotels/search"
    
    querystring = {
        "page_number": page_number,
        "order_by": "popularity",
        "categories_filter_ids": "class::2,class::4,free_cancellation::1",
        "adults_number": adults_number,
        "units": "metric",
        "dest_id": dest_id,  # Use the correct destination ID
        "room_number": "1",
        "checkin_date": checkin_date,
        "include_adjacency": "true",
        "filter_by_currency": currency,
        "locale": "en-gb",
        "dest_type": "city",
        "checkout_date": checkout_date,
    }

    # Add children parameters only if children_number > 0
    if int(children_number) > 0:
        querystring["children_number"] = children_number
        querystring["children_ages"] = children_ages  # Include ages only if there are children
    
    headers = {
        "x-rapidapi-key": "",
        "x-rapidapi-host": ""
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        results = response.json()
    except Exception as e:
        print(f"API Error: {e}")
        results = {"count": 0, "result": []}
    
    # If the request is an AJAX request, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(results, safe=False)
    
    # Calculate total pages for pagination
    total_pages = 1
    if results.get("count", 0) > 0:
        total_pages = (results.get("count", 0) // 25) + (1 if results.get("count", 0) % 25 > 0 else 0)
    
    # Add template context functions
    # This is for the Django template to handle star ratings
    def star_range(count):
        return range(int(count))
    
    # Render the template with the results
    context = {
        "results": results,
        "city_name": city,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "adults_number": adults_number,
        "children_number": children_number,
        "total_nights": total_nights,
        "page": int(page_number),
        "total_pages": total_pages,
        "currency": currency,
        "star_range": star_range,
    }
    
    return render(request, "hotel_results.html", context)

def get_hotel_data(request, hotel_id):
    # API headers
    headers = {
        "x-rapidapi-key": "",
        "x-rapidapi-host": ""
    }

    # Fetch hotel details
    hotel_url = "https://booking-com.p.rapidapi.com/v1/hotels/data"
    hotel_query = {"hotel_id": hotel_id, "locale": "en-gb"}
    hotel_response = requests.get(hotel_url, headers=headers, params=hotel_query)

    # Fetch hotel description
    description_url = "https://booking-com.p.rapidapi.com/v1/hotels/description"
    description_query = {"hotel_id": hotel_id, "locale": "en-gb"}
    description_response = requests.get(description_url, headers=headers, params=description_query)

    # Initialize data variables
    hotel_details, hotel_description = {}, "Description not available."

    # Process hotel details response
    if hotel_response.status_code == 200:
        data = hotel_response.json()
        hotel_details = {
            "hotel_id": data.get("hotel_id"),
            "name": data.get("name"),
            "address": data.get("address"),
            "city": data.get("city"),
            "country": data.get("country"),
            "zip_code": data.get("zip"),
            "url": data.get("url"),
            "latitude": data.get("location", {}).get("latitude"),
            "longitude": data.get("location", {}).get("longitude"),
            "review_score": data.get("review_score"),
            "review_text": data.get("review_score_word"),
            "num_reviews": data.get("review_nr"),
            "star_rating": data.get("class"),
            "ranking": data.get("ranking"),
            "facilities": data.get("hotel_facilities_filtered", "Not provided"),
            "checkin_from": data.get("checkin", {}).get("from", "N/A"),
            "checkin_to": data.get("checkin", {}).get("to", "N/A"),
            "checkout_from": data.get("checkout", {}).get("from", "N/A"),
            "checkout_to": data.get("checkout", {}).get("to", "N/A"),
            "main_photo": data.get("main_photo_url"),
            "entrance_photo": data.get("entrance_photo_url"),
            "languages_spoken": data.get("languages_spoken", {}).get("languagecode", []),
            "preferred": data.get("preferred"),
        }

    # Process hotel description response
    if description_response.status_code == 200:
        description_data = description_response.json()
        hotel_description = description_data.get("description", "Description not available.")

    # Render the hotel detail page
    return render(request, "hotel_detail.html", {
        "hotel": hotel_details,
        "description": hotel_description
    })



API_KEY = ""
API_HOST = ""



def get_entity_id(request):
    location = request.GET.get("pickup_location")
    if not location:
        return JsonResponse({"error": "Missing pickup_location parameter"}, status=400)

    url = "https://sky-scanner3.p.rapidapi.com/cars/auto-complete"
    querystring = {"query": location}

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch entity ID from API"}, status=500)

    data = response.json()

    if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
        entity_id = data["data"][0].get("entity_id")
        if entity_id:
            return car_rental_search(request, entity_id)

    return JsonResponse({"error": "No valid entity_id found"}, status=404)

def get_entity_id(request):
    location = request.GET.get("pickup_location")
    pickup_date = request.GET.get("pickup_date")
    dropoff_date = request.GET.get("dropoff_date")
    pickup_time = request.GET.get("pickup_time")
    dropoff_time = request.GET.get("dropoff_time")
    country = request.GET.get("from_country")
    if not location:
        return JsonResponse({"error": "Missing pickup_location parameter"}, status=400)

    url = "https://sky-scanner3.p.rapidapi.com/cars/auto-complete"
    querystring = {"query": location}

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code != 200:
        return JsonResponse({"error": "Failed to fetch entity ID from API"}, status=500)

    data = response.json()

    if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
        entity_id = data["data"][0].get("entity_id")
        if entity_id:
            return car_rental_search(request, entity_id, pickup_date, dropoff_date, pickup_time, dropoff_time, country)

    return JsonResponse({"error": "No valid entity_id found"}, status=404)

def car_rental_search(request, entity_id, pickup_date, dropoff_date, pickup_time, dropoff_time, country):
    url = "https://sky-scanner3.p.rapidapi.com/cars/search"
    
    querystring = {
        "pickUpDate": pickup_date,
        "dropOffDate": dropoff_date,
        "pickUpTime": pickup_time,
        "dropOffTime": dropoff_time,
        "pickUpEntityId": entity_id,
        "currency": "INR",
        "locale": "en-IN",
        "country": country,
    }

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        return render(request, "car_list.html", {
            "error": f"Failed to fetch data from API. Status code: {response.status_code}",
            "response_text": response.text[:200]  # Get first 200 chars of response
        })

    try:
        result = response.json()
        
        # Debug information
        debug_info = {
            "response_keys": list(result.keys()),
            "has_carList": "carList" in result,
            "carList_type": type(result.get("carList", "Not found")).__name__,
            "carList_length": len(result.get("carList", [])) if isinstance(result.get("carList"), list) else "N/A",
            "raw_sample": str(result)[:500]  # First 500 chars of the raw response
        }
        
        all_deals = []
        
        # Check if carList is directly at the root
        if "carList" in result and isinstance(result["carList"], list):
            carlist = result["carList"]
        # Otherwise check if it's under the data key
        elif "data" in result and isinstance(result["data"], dict) and "carList" in result["data"]:
            carlist = result["data"]["carList"]
        else:
            carlist = []
            
        # Process each car in the carList
        for car_index, car in enumerate(carlist):
            if "deals" in car and isinstance(car["deals"], list):
                for deal_index, deal in enumerate(car["deals"]):
                    # Get the deeplink and always add https://www.skyscanner.com at the beginning
                    original_deeplink = deal.get("dplnk", "")
                    if original_deeplink:
                        # Always prepend the Skyscanner domain, regardless of current format
                        fixed_deeplink = f"https://www.skyscanner.com{original_deeplink}"
                    else:
                        fixed_deeplink = ""
                    
                    # Extract ONLY the deal properties - not the outer car properties
                    deal_details = {
                        "index": deal_index,
                        "car_index": car_index,
                        
                        # These are the deal-specific properties from your JSON example
                        "fuel_policy": deal.get("fuel_pol", ""),
                        "sipp": deal.get("sipp", ""),
                        "pickup_route_node_id": deal.get("pu_rn_id", ""),
                        "guid": deal.get("guid", ""),
                        "booking_panel_option_guid": deal.get("booking_panel_option_guid", ""),
                        "pickup_type": deal.get("pickup_type", ""),
                        "pickup_location": deal.get("pu", ""),
                        "score": deal.get("score", ""),
                        "new_score": deal.get("new_score", ""),
                        "vendor_image": deal.get("vndr_img", ""),
                        "vendor_image_rounded": deal.get("vndr_img_rounded", ""),
                        "vendor": deal.get("vndr", ""),
                        "dropoff_location": deal.get("do", ""),
                        "bags": deal.get("bags", ""),
                        "price": deal.get("price", ""),
                        "provider_id": deal.get("prv_id", ""),
                        "car_name": deal.get("car_name", ""),
                        "original_car_name": deal.get("original_car_name", ""),
                        "group": deal.get("group", ""),
                        "deeplink": fixed_deeplink,  # Always use the modified deeplink
                        "dropoff_route_node_id": deal.get("do_rn_id", ""),
                        "pickup_method": deal.get("pickup_method", ""),
                        "office_id": deal.get("office_id", ""),
                        "seats": deal.get("seat", "")
                    }
                    
                    # Handle nested loc data if available
                    if "loc" in deal and isinstance(deal["loc"], dict):
                        # If pickup_type isn't already set, try to get it from loc
                        if not deal_details["pickup_type"] and "pickup_type" in deal["loc"]:
                            deal_details["pickup_type"] = deal["loc"]["pickup_type"]
                        
                    all_deals.append(deal_details)

        context = {
            "deals": all_deals,
            "location": request.GET.get("pickup_location", ""),
            "pickup_date": querystring.get("pickUpDate", ""),
            "dropoff_date": querystring.get("dropOffDate", ""),
            "total_deals": len(all_deals),
            "debug_info": debug_info
        }

        return render(request, "car_list.html", context)
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        
        return render(request, "car_list.html", {
            "error": f"Error processing API response: {str(e)}",
            "traceback": error_traceback,
            "response_sample": response.text[:500]  # First 500 chars of response
        })
    

#flight booking



def get_flightid(request):
    if request is None:
        return JsonResponse({"error": "Invalid request object"}, status=400)
    
    from_location = request.GET.get("origin", "").strip()
    to_location = request.GET.get("destination", "").strip()
    departure_date = request.GET.get("departure_date", "").strip()
    
    flight_class = request.GET.get("flight_class", "economy").strip()
    stop_flight = request.GET.get("stop_flight", "0").strip()
    
    if not from_location or not to_location:
        return JsonResponse({"error": "Missing origin or destination parameter"}, status=400)
    
    url = "https://booking-com18.p.rapidapi.com/flights/auto-complete"
    headers = {
        "x-rapidapi-key": "",
        "x-rapidapi-host": ""
    }
    
    try:
        from_response = requests.get(url, headers=headers, params={"query": from_location})
        from_response.raise_for_status()
        from_data = from_response.json()
        
        to_response = requests.get(url, headers=headers, params={"query": to_location})
        to_response.raise_for_status()
        to_data = to_response.json()
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Failed to fetch location data: {str(e)}"}, status=500)
    
    from_id = from_data.get("data", [{}])[0].get("iataCode") if from_data.get("data") else None
    to_id = to_data.get("data", [{}])[0].get("iataCode") if to_data.get("data") else None
    
    if not from_id or not to_id:
        return JsonResponse({"error": "No valid IATA codes found."}, status=404)
    
    return flight_booking(request, from_id, to_id, departure_date, flight_class, stop_flight)

import requests
from django.http import JsonResponse
import os
import logging

import logging
import requests
from django.http import JsonResponse
import traceback

# Create logger for this module
logger = logging.getLogger(__name__)

def flight_booking(request, from_id, to_id, departure_date, flight_class, stop_flight):
    from datetime import datetime
    import requests
    import traceback
    
    url = "https://booking-com18.p.rapidapi.com/flights/search-oneway"
    
    headers = {
        "X-RapidAPI-Key": "",
        "X-RapidAPI-Host": ""
    }
    
    query = {
        "fromId": from_id,
        "toId": to_id,
        "departureDate": departure_date,
        "cabinClass": flight_class,
        "numberOfStops": stop_flight,
    }
    
    try:
        response = requests.get(url, headers=headers, params=query)
        response.raise_for_status()
        api_response = response.json()
        
        # Extract flight data according to the correct structure
        flight_data = []
        error_message = None
        
        # First check if there are errors in the response
        if "errors" in api_response and api_response["errors"]:
            error_message = f"API returned errors: {api_response.get('errors')}"
            return render(request, 'flights.html', {
                'flights': [],
                'error_message': error_message,
                'api_status': api_response.get("status", "Unknown")
            })
            
        # Now check for the data field
        if "data" not in api_response:
            error_message = "No data field found in API response"
            return render(request, 'flights.html', {
                'flights': [],
                'error_message': error_message,
                'keys_available': str(api_response.keys())
            })
        
        data = api_response["data"]
        
        # If data is None or not a dictionary, handle accordingly
        if data is None or not isinstance(data, dict):
            error_message = f"Data field is {type(data).__name__}, expected dictionary"
            return render(request, 'flights.html', {
                'flights': [],
                'error_message': error_message,
                'api_status': api_response.get("status", "Unknown")
            })
        
        # Check if 'flights' exists in data
        if "flights" not in data:
            error_message = "No flights field found in data"
            return render(request, 'flights.html', {
                'flights': [],
                'error_message': error_message,
                'data_keys': str(data.keys())
            })
        
        flights = data["flights"]
        
        if not flights or not isinstance(flights, list):
            error_message = f"Flights field is {type(flights).__name__} with {len(flights) if hasattr(flights, '__len__') else 'unknown'} items"
            return render(request, 'flights.html', {
                'flights': [],
                'error_message': error_message,
                'api_status': api_response.get("status", "Unknown")
            })
        
        for flight in flights:
            if not isinstance(flight, dict):
                continue
                
            flight_id = flight.get("id", "N/A")
            shareableUrl = flight.get("shareableUrl", "N/A")
            
            # Check if bounds exists before proceeding
            bounds = flight.get("bounds", [])
            if bounds is None:
                bounds = []
            
            for bound in bounds:
                if not isinstance(bound, dict):
                    continue
                    
                # Check if segments exists before proceeding
                segments = bound.get("segments", [])
                if segments is None:
                    segments = []
                
                for segment in segments:
                    if not isinstance(segment, dict):
                        continue
                    
                    # Create flight info with proper nested structure access
                    flight_info = {
                        "flight_id": segment.get("flightNumber", "N/A"),
                        "shareable_url": shareableUrl,
                        "departure_time": segment.get("departuredAt", "N/A"),
                        "arrival_time": segment.get("arrivedAt", "N/A"),
                        "cabin_class": segment.get("cabinClassName", "N/A"),
                        "equipment_code": segment.get("equipmentCode", "N/A"),
                        "aircraft_type": segment.get("aircraftType", "N/A")
                    }
                    
                    # Calculating duration
                    try:
                        departure_datetime = datetime.fromisoformat(segment.get("departuredAt", "").replace("Z", "+00:00"))
                        arrival_datetime = datetime.fromisoformat(segment.get("arrivedAt", "").replace("Z", "+00:00"))
                        
                        # Calculate duration as timedelta
                        duration = arrival_datetime - departure_datetime
                        
                        # Format duration as hours and minutes
                        duration_hours = duration.total_seconds() // 3600
                        duration_minutes = (duration.total_seconds() % 3600) // 60
                        flight_info["duration"] = f"{int(duration_hours)}h {int(duration_minutes)}m"
                    except (ValueError, TypeError, AttributeError):
                        # Handle cases where time parsing fails
                        flight_info["duration"] = "N/A"
                    
                    # Safely add origin info - check if None first
                    origin = segment.get("origin")
                    if origin and isinstance(origin, dict):
                        flight_info["departure_airport"] = origin.get("name", "N/A")
                        flight_info["departure_code"] = origin.get("code", "N/A")
                    else:
                        flight_info["departure_airport"] = "N/A"
                        flight_info["departure_code"] = "N/A"
                    
                    # Safely add destination info - check if None first
                    destination = segment.get("destination")
                    if destination and isinstance(destination, dict):
                        flight_info["arrival_airport"] = destination.get("name", "N/A")
                        flight_info["arrival_code"] = destination.get("code", "N/A")
                    else:
                        flight_info["arrival_airport"] = "N/A"
                        flight_info["arrival_code"] = "N/A"
                    
                    # Safely add marketing carrier info - check if None first
                    marketing_carrier = segment.get("marketingCarrier")
                    if marketing_carrier and isinstance(marketing_carrier, dict):
                        flight_info["airline"] = marketing_carrier.get("name", "N/A")
                        flight_info["airline_code"] = marketing_carrier.get("code", "N/A")
                    else:
                        flight_info["airline"] = "N/A"
                        flight_info["airline_code"] = "N/A"
                    
                    # Safely add operating carrier info - check if None first
                    operating_carrier = segment.get("operatingCarrier")
                    if operating_carrier and isinstance(operating_carrier, dict):
                        flight_info["operating_airline"] = operating_carrier.get("name", "N/A")
                        flight_info["operating_airline_code"] = operating_carrier.get("code", "N/A")
                    else:
                        flight_info["operating_airline"] = "N/A"
                        flight_info["operating_airline_code"] = "N/A"
                    
                    flight_data.append(flight_info)
        
        # If no flights were found, add a descriptive message
        if not flight_data:
            error_message = "Successfully processed the response, but no flight data could be extracted"
            return render(request, 'flights.html', {
                'flights': [],
                'error_message': error_message,
                'api_status': api_response.get("status", "Unknown")
            })
        
        # Get search parameters to display in the template
        search_details = {
            'from_id': from_id,
            'to_id': to_id,
            'departure_date': departure_date,
            'flight_class': flight_class,
            'number_of_stops': stop_flight
        }
        
        return render(request, 'flights.html', {
            'flights': flight_data,
            'search_details': search_details
        })
    
    except Exception as e:
        # Add detailed error information
        error_traceback = traceback.format_exc()
        return render(request, 'flights.html', {
            'flights': [],
            'error_message': f"Error: {str(e)}",
            'error_traceback': error_traceback
        })