from django.urls import path
from .views import AddDriverView

urlpatterns = [
    path('', AddDriverView.as_view(), name='add-driver')
]