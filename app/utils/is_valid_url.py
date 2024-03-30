import requests

def is_valid_image_url(image_url):
    try:
        response = requests.head(image_url)
        return response.status_code == 200 and response.headers['Content-Type'].startswith('image')
    except requests.RequestException:
        return False