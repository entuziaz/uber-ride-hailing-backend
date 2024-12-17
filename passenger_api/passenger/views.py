from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Passenger
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import datetime
import uuid 
from .tasks import send_welcome_email


ERROR_MESSAGES = {
    "MISSING_FIELDS_PASSENGER_CREATE": "The [email, phone, first_name, last_name] fields are required.",
    "DUPLICATE_EMAIL": "A user with this email address already exists.",
    "DUPLICATE_PHONE": "A user with this phone number already exists.",

    "MISSING_FIELDS_RIDE_BOOOKING": "The [pickup_location, dropoff_location, ride_type] fields are required.",
    "INVALID_RIDE_TYPE": "Invalid ride_type '{ride_type}'. Allowed values are {valid_ride_types}.",
    "INVALID_LOCATION": "pickup_location and dropoff_location must include 'latitude' and 'longitude'.",
    "SERVER_ERROR": "An unexpected error occurred. Please try again later."
}

class PassengerCreateView(APIView):
    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not all([email, phone, first_name, last_name]):
            return Response({
                "error": ERROR_MESSAGES["MISSING_FIELDS_PASSENGER_CREATE"],
                "code": "BAD_REQUEST"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if Passenger.objects.filter(email=email).exists():
            return Response(
                {"error": ERROR_MESSAGES["DUPLICATE_EMAIL"]},
               status=status.HTTP_400_BAD_REQUEST,
            )
        if Passenger.objects.filter(phone=phone).exists():
            return Response(
                {"error": ERROR_MESSAGES["DUPLICATE_PHONE"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try: 
            passenger = Passenger.objects.create(
                email=email,
                phone=phone,
                first_name=first_name,
                last_name=last_name
            )
            passenger_data = {
                "passenger_id": passenger.passenger_id,
                "email": passenger.email,
                "phone": passenger.phone,
                "first_name": passenger.first_name,
                "last_name": passenger.last_name,
                "created_at": passenger.created_at,  
                "updated_at": passenger.updated_at,
            }

            # send_welcome_email.delay(passenger.passenger_id)

            return Response(
                {
                    "message": "Passenger created successfully.",
                    "data": passenger_data
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response({
                "error": "Validation error.",
                "details": e.message_dict,
                "code": "VALIDATION_ERROR"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except IntegrityError as e:
            return Response({
                "error": "Database Integrity Error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": ERROR_MESSAGES["SERVER_ERROR"],
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# {
#   "pickup_location": { "latitude": 37.7749, "longitude": -122.4194 },
#   "dropoff_location": { "latitude": 37.8044, "longitude": -122.2711 },
#   "ride_type": "standard",
#   "booking_time": "2024-12-16T14:00:00Z"
# }
    

class PassengerRideBookingView(APIView):
    def post(self, request):
        pickup_location = request.data.get('pickup_location')
        dropoff_location =  request.data.get('dropoff_location')
        ride_type = request.data.get('ride_type')

        if not all([pickup_location, dropoff_location, ride_type]):
            return Response({
                "error": ERROR_MESSAGES["MISSING_FIELDS_RIDE_BOOOKING"],
                "code": "BAD_REQUEST"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_ride_types = ["standard", "premium"]
        if ride_type not in valid_ride_types:
            return Response({
                "error": ERROR_MESSAGES["INVALID_RIDE_TYPE"].format(ride_type=ride_type, valid_ride_types=valid_ride_types),
                "code": "INVALID_RIDE_TYPE"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            pickup_latitude = pickup_location['latitude']
            pickup_longitude = pickup_location['longitude']
            dropoff_latitude = dropoff_location['latitude']
            dropoff_longitude = dropoff_location['longitude']
        except (TypeError, KeyError):
            return Response({
                "error": ERROR_MESSAGES["INVALID_LOCATION"],
                "code": "INVALID_LOCATION"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            ride_request_data = {
                "ride_id": str(uuid.uuid4()),
                "pickup_location": {
                    "latitude": pickup_latitude,
                    "longitude": pickup_longitude,
                },
                "dropoff_location": {
                    "latitude": dropoff_latitude,
                    "longitude": dropoff_longitude,
                },
                "ride_type": ride_type,
                "booking_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        # TODO: Check if ride_id has been added to DB already: avoid race-condition
        # Ensure to generate the uuid before checking for existing entries.

            return Response({
                "message": "Ride request created successfully.",
                "data": ride_request_data
            }, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response({
                "error": "Validation error.",
                "details": e.message_dict,
                "code": "VALIDATION_ERROR"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(f"Server error: {e}")
            return Response({
                "error": ERROR_MESSAGES["SERVER_ERROR"],
                "details": str(e),
                "code": "SERVER_ERROR",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

