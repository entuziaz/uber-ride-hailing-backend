
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
# from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse, OpenApiTypes
from rest_framework.response import Response
from .models import Passenger
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import datetime
import uuid 
from .tasks import send_welcome_email
from .services import get_fare_and_hashed_location
import logging

logger = logging.getLogger('passenger')



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
    @extend_schema(
        request={
            "application/json": {
                "example": {
                    "email": "passenger@example.com",
                    "phone": "+1234567890",
                    "first_name": "John",
                    "last_name": "Doe",
                }
            }
        },
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                description="Passenger created successfully.",
                response={
                    "message": "Passenger created successfully.",
                    "data": {
                        "passenger_id": "uuid",
                        "email": "passenger@example.com",
                        "phone": "+1234567890",
                        "first_name": "John",
                        "last_name": "Doe",
                        "created_at": "2023-10-01T12:34:56Z",
                        "updated_at": "2023-10-01T12:34:56Z",
                    },
                },
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Validation or integrity error.",
                response={
                    "error": "Validation or integrity error.",
                    "details": {
                        "missing_fields": ["email", "phone", "first_name", "last_name"],
                        "message": "The provided data is invalid or duplicates exist.",
                    },
                    "code": "BAD_REQUEST",
                },
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                description="Internal server error.",
                response={
                    "error": "Internal server error occurred.",
                    "details": "An unexpected error occurred.",
                    "code": "SERVER_ERROR",
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Valid Request",
                value={
                    "email": "passenger@example.com",
                    "phone": "+1234567890",
                    "first_name": "John",
                    "last_name": "Doe",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid Request - Missing Fields",
                value={},
                request_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Invalid Request - Duplicate Email",
                value={
                    "email": "existing@example.com",  # Assuming this email already exists
                    "phone": "+1234567890",
                    "first_name": "John",
                    "last_name": "Doe",
                },
                request_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Invalid Request - Duplicate Phone",
                value={
                    "email": "passenger@example.com",
                    "phone": "+0987654321",  # Assuming this phone already exists
                    "first_name": "John",
                    "last_name": "Doe",
                },
                request_only=True,
                status_codes=["400"],
            ),
        ],
    )
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
    VALID_RIDE_TYPES = ["standard", "premium"]

    def validate_request_data(self, pickup_location, dropoff_location, ride_type):
        """Validate the request data."""
        if not all([pickup_location, dropoff_location, ride_type]):
            raise ValidationError({
                "error": ERROR_MESSAGES["MISSING_FIELDS_RIDE_BOOOKING"],
                "code": "BAD_REQUEST"
            })

        if ride_type not in self.VALID_RIDE_TYPES:
            raise ValidationError({
                "error": ERROR_MESSAGES["INVALID_RIDE_TYPE"].format(
                    ride_type=ride_type, valid_ride_types=self.VALID_RIDE_TYPES
                ),
                "code": "INVALID_RIDE_TYPE"
            })

        for location in [pickup_location, dropoff_location]:
            lat, lon = location.get("latitude"), location.get("longitude")
            if lat is None or lon is None:
                raise ValidationError({
                    "error": ERROR_MESSAGES["INVALID_LOCATION"],
                    "details": f"Latitude or longitude is missing for location: {location}",
                    "code": "INVALID_LOCATION"
                })
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValidationError({
                    "error": ERROR_MESSAGES["INVALID_LOCATION"],
                    "details": f"Invalid latitude ({lat}) or longitude ({lon}) range.",
                    "code": "INVALID_LOCATION"
                })

    @extend_schema(
        request={
            "application/json": {
                "example": {
                    "pickup_location": {"latitude": 40.7128, "longitude": -74.0060},
                    "dropoff_location": {"latitude": 34.0522, "longitude": -118.2437},
                    "ride_type": "standard",
                }
            }
        },
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                description="Ride request created successfully.",
                response={
                    "message": "Ride request created successfully.",
                    "data": {
                        "ride_id": "uuid",
                        "pickup_location": {"latitude": 40.7128, "longitude": -74.0060},
                        "dropoff_location": {"latitude": 34.0522, "longitude": -118.2437},
                        "ride_type": "standard",
                        "booking_time": "2023-10-01 12:34:56",
                        "estimated_fare": 25.50,
                        "distance_km": 10.5,
                        "pickup_geohash": "example_geohash",
                        "dropoff_geohash": "example_geohash",
                    },
                },
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Validation error.",
                response={
                    "error": "Validation error.",
                    "details": {
                        "missing_fields": ["pickup_location", "dropoff_location", "ride_type"],
                        "message": "The provided data is invalid.",
                    },
                    "code": "VALIDATION_ERROR",
                },
            ),
            status.HTTP_502_BAD_GATEWAY: OpenApiResponse(
                description="External API error.",
                response={
                    "error": "Failed to get fare estimates and location data.",
                    "details": "The external API did not return any data.",
                    "code": "EXTERNAL_API_ERROR",
                },
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
                description="Internal server error.",
                response={
                    "error": "Internal server error occurred.",
                    "details": "An unexpected error occurred.",
                    "code": "SERVER_ERROR",
                },
            ),
        },
        examples=[
            OpenApiExample(
                "Valid Request",
                value={
                    "pickup_location": {"latitude": 40.7128, "longitude": -74.0060},
                    "dropoff_location": {"latitude": 34.0522, "longitude": -118.2437},
                    "ride_type": "standard",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Invalid Request - Missing Fields",
                value={},
                request_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        pickup_location = request.data.get("pickup_location")
        dropoff_location = request.data.get("dropoff_location")
        ride_type = request.data.get("ride_type")

        try:
            self.validate_request_data(pickup_location, dropoff_location, ride_type)

            pickup_lat = pickup_location.get("latitude")
            pickup_lng = pickup_location.get("longitude")
            dropoff_lat = dropoff_location.get("latitude")
            dropoff_lng = dropoff_location.get("longitude")


            ride_request_data = {
                "ride_id": str(uuid.uuid4()),
                "pickup_location": {
                    "latitude": pickup_lat,
                    "longitude": pickup_lng
                },
                "dropoff_location": {
                    "latitude": dropoff_lat,
                    "longitude": dropoff_lng
                },
                "ride_type": ride_type,
                "booking_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            estimates_and_geohashes = get_fare_and_hashed_location(ride_request_data)

            if not estimates_and_geohashes:
                return Response({
                    "error": "Failed to get fare estimates and location data.",
                    "details": "The external API did not return any data.",
                    "code": "EXTERNAL_API_ERROR"
                }, status=status.HTTP_502_BAD_GATEWAY)
            
            print(estimates_and_geohashes)
           
            ride_request_data.update({
                "estimated_fare": estimates_and_geohashes["data"]["estimated_fare"],
                "distance_km": estimates_and_geohashes["data"]["distance_km"],
                "pickup_geohash": estimates_and_geohashes["data"]["pickup_geohash"],
                "dropoff_geohash": estimates_and_geohashes["data"]["dropoff_geohash"],
            })

            logger.debug(f"Updated ride_request_data: {ride_request_data}")

            return Response({
                "message": "Ride request created successfully.",
                "data": ride_request_data
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            missing_fields = [field for field in ["pickup_location", "dropoff_location", "ride_type"] if not request.data.get(field)]
            return Response({
                "error": e.message_dict.get("error", "Validation error."),
                "details": {
                    "missing_fields": missing_fields,
                    "message": e.message_dict.get("details", "The provided data is invalid.")
                },
                "code": e.message_dict.get("code", "VALIDATION_ERROR")
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.debug(f"Error Updated ride_request_data: {e}")
            return Response({
                "error": ERROR_MESSAGES["SERVER_ERROR"],
                "details": str(e),
                "code": "SERVER_ERROR",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


