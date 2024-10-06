from django.urls import path
from .views import AddPassengerView

urlpatterns = [
    path("", AddPassengerView.as_view(), name="add-passenger")
]