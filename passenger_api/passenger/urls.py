from django.urls import path
from .views import PassengerCreateView, PassengerRideBookingView

urlpatterns = [
    path("passengers/", PassengerCreateView.as_view(), name="add-passenger"),
    path('rides/book/', PassengerRideBookingView.as_view(), name='book-ride-passenger'),
]