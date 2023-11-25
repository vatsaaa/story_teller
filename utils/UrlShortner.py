from os import getenv
import requests

class UrlShortner:
    def __init__(self, url: str) -> None:
        self.url = url
        self.short_url = None
    
    def shorten(long_url: str, access_token: str) -> str:
        api_url = getenv("SHORTENER_URL_1")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "long_url": long_url
        }
        
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        return response.json()["link"]