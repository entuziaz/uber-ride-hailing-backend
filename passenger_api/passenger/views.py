from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .models import Passenger
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class AddPassengerView(APIView):
    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not all([email, phone, first_name, last_name]):
            return JsonResponse({
                "error": "The [email, phone, first_name, last_name] fields are required.",
                "code": "BAD_REQUEST"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if Passenger.objects.filter(email=email).exists():
            return JsonResponse(
                {
                    "error": "A user with this email address already exists."
                 }, status=status.HTTP_400_BAD_REQUEST,
            )
        if Passenger.objects.filter(phone=phone).exists():
            return JsonResponse(
                {
                    "error": "A user with this phone number already exists."
                 }, status=status.HTTP_400_BAD_REQUEST,
            )
        
        try: 
            passenger = Passenger.objects.create(
                email=email,
                phone=phone,
                first_name=first_name,
                last_name=last_name
            )
        except ValidationError as e:
            return JsonResponse({
                "error": "Validation error.",
                "details": e.message_dict
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return JsonResponse({
                "error": "An error occured while creating your user profile.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR,)
        
