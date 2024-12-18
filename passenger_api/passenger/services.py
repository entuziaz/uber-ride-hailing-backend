import requests
from django.conf import settings


class NodeAPIError(Exception):
    pass

def get_fare_and_hashed_location(ride_request_data):
    try:
        payload = {
            "pickup_location": ride_request_data['pickup_location'],
            "dropoff_location": ride_request_data['dropoff_location'],
            "ride_type": ride_request_data['ride_type'],
        }
        url = settings.GEOES_NODE_API_URL
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            res = response.json()
            print('res is res is res is res is res',res)
            return res
        else:
            raise Exception(f"Node.js API error: {response.status_code}, {response.text}")
    except:
        # raise Exception(f"Node.js API error: {response.status_code}, {response.text}")
        raise NodeAPIError(f"Error communicating with Node.js API: {e}")
