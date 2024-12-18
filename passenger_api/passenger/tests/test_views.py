
import pytest
import uuid
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from passenger.models import Passenger 


# @pytest.mark.django_db
@pytest.fixture
def create_passenger():
    return Passenger.objects.create(
        email="test@example.com",
        phone="1234567890",
        first_name="John",
        last_name="Doe"
    )

@pytest.fixture
def api_client():
    return APIClient()


def test_passenger_create_missing_fields(api_client):
    """Test missing required fields"""
    data = {
        "email": "new_email@example.com",
        "phone": "9876543210",
        "first_name": "Jane"
        # last_name is missing
    }
    response = api_client.post('/passenger/passengers/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"] == "BAD_REQUEST"
    assert "The [email, phone, first_name, last_name] fields are required." in response.data["error"]

@pytest.mark.django_db
def test_passenger_create_duplicate_email(api_client, create_passenger):
    """Test duplicate email"""
    existing_passenger = Passenger.objects.create(
        email="existing_email@example.com",
        phone="1234567890",
        first_name="John",
        last_name="Doe"
    )
    data = {
        "email": "existing_email@example.com", 
        "phone": "9876543210",
        "first_name": "Jane",
        "last_name": "Doe"
    }
    response = api_client.post('/passenger/passengers/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "A user with this email address already exists."

@pytest.mark.django_db
def test_passenger_create_duplicate_phone(api_client, create_passenger):
    """Test duplicate phone"""
    existing_passenger = Passenger.objects.create(
        email="email@example.com",
        phone="1234567890",
        first_name="John",
        last_name="Doe"
    )
    data = {
        "email": "new_email@example.com",
        "phone": "1234567890",  # Already in database
        "first_name": "Jane",
        "last_name": "Doe"
    }
    response = api_client.post('/passenger/passengers/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "A user with this phone number already exists."

@pytest.mark.django_db
def test_passenger_create_success(api_client):
    """Test successful passenger creation"""
    data = {
        "email": "new_email@example.com",
        "phone": "9876543210",
        "first_name": "Jane",
        "last_name": "Doe"
    }
    response = api_client.post('/passenger/passengers/', data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["message"] == "Passenger created successfully."
    assert "passenger_id" in response.data["data"]
    assert response.data["data"]["email"] == "new_email@example.com"

@pytest.mark.django_db
def test_passenger_create_server_error(api_client, monkeypatch):
    """Test when an unexpected server error occurs"""
    def mock_create(*args, **kwargs):
        raise Exception("Test server error")
    
    monkeypatch.setattr(Passenger.objects, 'create', mock_create)
    
    data = {
        "email": "new_email@example.com",
        "phone": "9876543210",
        "first_name": "Jane",
        "last_name": "Doe"
    }
    response = api_client.post('/passenger/passengers/', data, format='json')
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "An unexpected error occurred. Please try again later." in response.data["error"]






















# def test_book_ride_missing_fields(api_client):
#     """Test when pickup_location, dropoff_location, or ride_type is missing"""
#     data = {
#         "pickup_location": {"latitude": 10.0, "longitude": 20.0},
#         "ride_type": "standard"
#     }  # dropoff_location is missing
#     response = api_client.post('/passenger/rides/book/', data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.data["code"] == "BAD_REQUEST"
#     # assert "MISSING_FIELDS_RIDE_BOOOKING" in response.data["error"]
#     assert "The [pickup_location, dropoff_location, ride_type] fields are required." in response.data["error"]

# def test_book_ride_invalid_type(api_client):
#     """Test when an invalid ride_type is provided"""
#     data = {
#         "pickup_location": {"latitude": 10.0, "longitude": 20.0},
#         "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
#         "ride_type": "luxury" # invalid ride_type
#     }
#     response = api_client.post('/passenger/rides/book/', data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.data['code'] == 'INVALID_RIDE_TYPE'
#     assert "Invalid ride_type 'luxury'. Allowed values are ['standard', 'premium']." in response.data['error']

# def test_book_ride_invalid_location(api_client):
#     """Test when pickup_location or dropoff_location is invalid"""
#     data = {
#         "pickup_location": {"latitude": 10.0},  # missing longitude
#         "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
#         "ride_type": "standard"
#     }
#     response = api_client.post('/passenger/rides/book/', data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.data["code"] == "INVALID_LOCATION"
#     assert "pickup_location and dropoff_location must include 'latitude' and 'longitude'." in response.data["error"]

# def test_book_ride_missing_dropoff_location(api_client):
#     """Test when dropoff_location is missing"""
#     data = {
#         "pickup_location": {"latitude": 10.0, "longitude": 20.0},
#         "ride_type": "standard"
#     }  # dropoff_location is missing
#     response = api_client.post('/passenger/rides/book/', data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.data["code"] == "BAD_REQUEST"
#     assert "The [pickup_location, dropoff_location, ride_type] fields are required." in response.data["error"]

# def test_book_ride_missing_pickup_location(api_client):
#     """Test when pickup_location is missing"""
#     data = {
#         "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
#         "ride_type": "standard"
#     }  # pickup_location is missing
#     response = api_client.post('/passenger/rides/book/', data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.data["code"] == "BAD_REQUEST"
#     assert "The [pickup_location, dropoff_location, ride_type] fields are required." in response.data["error"]

# def test_book_ride_valid(api_client):
#     """Test when all fields are valid"""
#     data = {
#         "pickup_location": {"latitude": 10.0, "longitude": 20.0},
#         "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
#         "ride_type": "standard"
#     }
#     response = api_client.post('/passenger/rides/book/', data, format='json')
#     assert response.status_code == status.HTTP_201_CREATED
#     assert response.data["message"] == "Ride request created successfully."
#     assert "ride_id" in response.data["data"]
#     assert response.data["data"]["pickup_location"]["latitude"] == 10.0
#     assert response.data["data"]["dropoff_location"]["longitude"] == 40.0

# def test_book_ride_server_error(api_client):
    # """Test when an unexpected server error occurs"""
    # data = {
    #     "pickup_location": {"latitude": 10.0, "longitude": 20.0},
    #     "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
    #     "ride_type": "standard"
    # }

    # # Mock the UUID generation or any other function that might raise the error
    # with patch('uuid.uuid4', side_effect=Exception("Test server error")):
    #     response = api_client.post('/passenger/rides/book/', data, format='json')

    # # Assert that a 500 Internal Server Error is returned
    # assert response.status_code == 500
    # assert response.data['error'] == 'An unexpected error occurred. Please try again later.'
    # assert 'Test server error' in response.data['details']







def test_book_ride_missing_fields(api_client):
    """Test when pickup_location, dropoff_location, or ride_type is missing"""
    data = {
        "pickup_location": {"latitude": 10.0, "longitude": 20.0},
        "ride_type": "standard"
    }  # dropoff_location is missing
    response = api_client.post('/passenger/rides/book/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"][0] == "BAD_REQUEST"



def test_book_ride_invalid_type(api_client):
    """Test when an invalid ride_type is provided"""
    data = {
        "pickup_location": {"latitude": 10.0, "longitude": 20.0},
        "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
        "ride_type": "luxury"  # invalid ride_type
    }
    response = api_client.post('/passenger/rides/book/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"][0] == "INVALID_RIDE_TYPE" 




def test_book_ride_missing_dropoff_location(api_client):
    """Test when dropoff_location is missing"""
    data = {
        "pickup_location": {"latitude": 10.0, "longitude": 20.0},
        "ride_type": "standard"
    }  # dropoff_location is missing
    response = api_client.post('/passenger/rides/book/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"][0] == "BAD_REQUEST"



def test_book_ride_missing_pickup_location(api_client):
    """Test when pickup_location is missing"""
    data = {
        "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
        "ride_type": "standard"
    }  # pickup_location is missing
    response = api_client.post('/passenger/rides/book/', data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"][0] == "BAD_REQUEST"



# def test_book_ride_valid(api_client):
#     """Test when all fields are valid"""
#     data = {
#         # "pickup_location": {"latitude": 10.0, "longitude": 20.0},
#         "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
#         "ride_type": "standard"
#     }

#     with patch('uuid.uuid4', return_value=uuid.UUID('12345678-1234-1234-1234-1234567890ab')):
#         response = api_client.post('/passenger/rides/book/', data, format='json')
#         assert response.status_code == status.HTTP_201_CREATED
#         assert response.data["ride_id"] == "12345678-1234-1234-1234-1234567890ab"




def test_book_ride_server_error(api_client):
    """Test when an unexpected server error occurs"""
    data = {
        "pickup_location": {"latitude": 10.0, "longitude": 20.0},
        "dropoff_location": {"latitude": 30.0, "longitude": 40.0},
        "ride_type": "standard"
    }

    with patch('passenger.views.get_fare_and_hashed_location', side_effect=Exception("Test server error")):
        response = api_client.post('/passenger/rides/book/', data, format='json')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["code"] == "SERVER_ERROR"



