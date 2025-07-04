from dotenv import load_dotenv
from os import getenv

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class FacebookPublisher(IPublisher):
    def __init__(self, page_id: str) -> None:
        super().__init__()
        
        # Check for required environment variables
        base_url = getenv('FBIG_BASE_URL')
        base_ver = getenv('FBIG_BASE_VER')
        
        if not base_url:
            raise ConfigurationException(
                "Facebook Base URL is not set",
                config_key="FBIG_BASE_URL",
                details={"solution": "Add FBIG_BASE_URL to your .env file"}
            )
        
        if not base_ver:
            raise ConfigurationException(
                "Facebook API version is not set",
                config_key="FBIG_BASE_VER", 
                details={"solution": "Add FBIG_BASE_VER to your .env file"}
            )
        
        self.base_url = base_url + base_ver + '{}/photos'
        self.base_url = self.base_url.format(page_id)
    
    def login(self) -> None:
        access_token = getenv('FBIG_ACCESS_TOKEN')
        if not access_token:
            raise ConfigurationException(
                "Facebook Access Token is not set",
                config_key="FBIG_ACCESS_TOKEN",
                details={"solution": "Create an API key from Facebook and set it in your .env file as FBIG_ACCESS_TOKEN"}
            )
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def publish(self, content: dict) -> None:
        print(self.base_url)
        print(f"Publishing content: {content}")  # For debugging

    def logout(self) -> None:
        self.headers = None
        print("Logged out from Facebook Publisher.")