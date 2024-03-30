import base64
import requests


def image_url_to_base64(image_url):
    # Fetch the image from the URL
    response = requests.get(image_url)
    # Check if the request was successful
    if response.status_code == 200:
        # Encode the image content as base64
        encoded_string = base64.b64encode(response.content).decode('utf-8')
        return encoded_string
    else:
        # If the request fails, return None
        return None