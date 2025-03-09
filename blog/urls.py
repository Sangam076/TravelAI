from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import HomeView, AboutView, travel_guide, get_place_info
from . import views
from .views import register
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')), 
    path('register/', register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    
    
    path('', HomeView.as_view(), name='home'),               
    path('about/', AboutView.as_view(), name='about'),       
    path('users/<str:room_name>', views.chat_room, name='chat'),
    path("travel-guide/", travel_guide, name="travel_guide"),
    path("get-place-info/", get_place_info, name="get_place_info"),
    path('create/', views.create_plan, name='create_plan'),
    path('view/<int:pk>/', views.view_plan, name='view_plan'),

    #path("search-hotels/", search_hotels, name="search_hotels"),
    #path("search-flights/", search_flights, name="search_flights"),
    #path("book-hotel/", book_hotel, name="book_hotel"),
    
    #path("book-flight/", book_flight, name="book_flight"),
    #path("hotel-search/", hotel_search_form, name="hotel_search_form"),
    path("travel-booking/", views.search_hotels_page, name="travel_booking"),
    path("search", views.search_hotels, name="search_hotels"),
    path('hotel/<int:hotel_id>/', views.get_hotel_data, name='hotel_detail'),
    path('car-rental/', views.get_entity_id, name="get_entity_id" ),
    path('flight/', views.get_flightid, name="get_flightid"),
    path('save/<int:pk>/', views.save_plan, name='save_plan'),  # New URL
    path('saved-plans/', views.saved_plans, name='saved_plans'), 
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('share_plan/<int:pk>/', views.share_plan, name='share_plan'),
    path('invite/accept/<uuid:token>/', views.accept_invite, name='accept_invite'),

    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
