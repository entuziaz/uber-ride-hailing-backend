from drf_spectacular.utils import extend_schema, OpenApiExample
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from .models import Driver
from django.core.exceptions import ValidationError


class AddDriverView(APIView):
    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "test@example.com"},
                    "phone": {"type": "string", "example": "+1234567890"},
                    "first_name": {"type": "string", "example": "John"},
                    "last_name": {"type": "string", "example": "Doe"},
                },
                "required": ["email", "phone", "first_name", "last_name"]
            }
        },
        responses={
            201: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Driver created successfully."},
                    "data": {
                        "type": "object",
                        "properties": {
                            "driver_id": {"type": "integer", "example": 1},
                            "email": {"type": "string", "example": "test@example.com"},
                            "phone": {"type": "string", "example": "+1234567890"},
                            "first_name": {"type": "string", "example": "John"},
                            "last_name": {"type": "string", "example": "Doe"},
                            "created_at": {"type": "string", "example": "2023-01-01T00:00:00Z"},
                            "updated_at": {"type": "string", "example": "2023-01-01T00:00:00Z"},
                        }
                    },
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Validation error."},
                    "details": {"type": "string", "example": "The email field is required."}
                }
            },
        },
        description="API endpoint to create a new driver."
    )

    def post(self, request):
        email = request.data.get('email').strip().lower()
        phone = request.data.get('phone')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not all([email, phone, first_name, last_name]):
            return JsonResponse({
                "error": "The [email, phone, first_name, last_name] fields are required.",
                "code": "BAD_REQUEST"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if Driver.objects.filter(email=email).exists():
            return JsonResponse(
                {
                    "error": "A user with this email address already exists."
                 }, status=status.HTTP_400_BAD_REQUEST,
            )
        if Driver.objects.filter(phone=phone).exists():
            return JsonResponse(
                {
                    "error": "A user with this phone number already exists."
                 }, status=status.HTTP_400_BAD_REQUEST,
            )
        
        try: 
            driver = Driver.objects.create(
                email=email,
                phone=phone,
                first_name=first_name,
                last_name=last_name
            )
            driver_data = {
                "driver_id": driver.driver_id,
                "email": driver.email,
                "phone": driver.phone,
                "first_name": driver.first_name,
                "last_name": driver.last_name,
                "created_at": driver.created_at,  
                "updated_at": driver.updated_at,
            }
            return JsonResponse(
                {
                    "message": "Driver created successfully.",
                    "data": driver_data
                },
                status=status.HTTP_201_CREATED
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
        
