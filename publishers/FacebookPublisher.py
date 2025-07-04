from dotenv import load_dotenv
from os import getenv
import requests
import json

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class FacebookPublisher(IPublisher):
    def __init__(self, page_id: str) -> None:
        super().__init__()
        self.page_id = page_id
        self.mock_mode = getenv('FACEBOOK_MOCK_MODE', 'false').lower() == 'true'
        self.access_token = None
        
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
        
        self.base_url = base_url + base_ver
    
    def login(self) -> None:
        """Login to Facebook with credential validation."""
        if self.mock_mode:
            print("[MOCK MODE] Skipping Facebook authentication")
            return
            
        access_token = getenv('FBIG_ACCESS_TOKEN')
        if not access_token:
            raise ConfigurationException(
                "Facebook Access Token is not set",
                config_key="FBIG_ACCESS_TOKEN",
                details={"solution": "Create an API key from Facebook and set it in your .env file as FBIG_ACCESS_TOKEN"}
            )
        
        self.access_token = access_token
        
        # Test the credentials
        try:
            url = f"{self.base_url}{self.page_id}"
            params = {'access_token': access_token}
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"API returned status code {response.status_code}: {response.text}")
                
        except Exception as e:
            raise ConfigurationException(
                f"Failed to authenticate with Facebook: {str(e)}",
                config_key="FACEBOOK_CREDENTIALS",
                details={"solution": "Check your Facebook API credentials and ensure they are valid"}
            )
    
    def publish(self, content: dict) -> None:
        """Publish content to Facebook."""
        try:
            # Extract text content for Facebook post
            text_content = content.get("text", {})
            hindi_text = text_content.get("hindi", "")
            english_text = text_content.get("english", "")
            title = text_content.get("title", "Story")
            
            # Use English text for post, fallback to Hindi if English not available
            message_text = english_text if english_text else hindi_text
            
            if not message_text:
                print("Warning: No text content available for Facebook publishing")
                return
            
            # Create Facebook post message with title
            post_message = f"{title}\n\n{message_text}"
            
            # Get media if available
            images = content.get("images", [])
            videos = content.get("videos", [])
            audios = content.get("audios", [])
            
            # Publish to Facebook
            if videos:
                self._post_video(post_message, videos[0])
            elif images:
                self._post_image(post_message, images[0])
            else:
                self._post_text(post_message)
                
            print("Facebook publishing completed successfully")
            
        except Exception as e:
            print(f"Facebook publishing failed: {str(e)}")
            raise

    def _post_text(self, message: str) -> None:
        """Post text to Facebook using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Posting to Facebook:")
            print(f"[MOCK MODE] Message: {message}")
            return
            
        try:
            url = f"{self.base_url}{self.page_id}/feed"
            params = {
                'message': message,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=params)
            response_data = response.json()
            
            if 'id' in response_data:
                print(f"Facebook text post published successfully. Post ID: {response_data['id']}")
            else:
                raise Exception(f"Failed to publish text post: {response_data}")
                
        except Exception as e:
            print(f"Failed to post text to Facebook: {str(e)}")
            raise

    def _post_image(self, message: str, image: str) -> None:
        """Post image to Facebook using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Posting to Facebook with image:")
            print(f"[MOCK MODE] Message: {message}")
            print(f"[MOCK MODE] Image: {image}")
            return
            
        try:
            url = f"{self.base_url}{self.page_id}/photos"
            params = {
                'url': image,  # Note: This requires a publicly accessible URL
                'caption': message,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=params)
            response_data = response.json()
            
            if 'id' in response_data:
                print(f"Facebook image post published successfully. Post ID: {response_data['id']}")
            else:
                raise Exception(f"Failed to publish image post: {response_data}")
                
        except Exception as e:
            print(f"Failed to post image to Facebook: {str(e)}")
            print("Note: Facebook API requires publicly accessible image URLs")
            raise

    def _post_video(self, message: str, video: str) -> None:
        """Post video to Facebook using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Posting to Facebook with video:")
            print(f"[MOCK MODE] Message: {message}")
            print(f"[MOCK MODE] Video: {video}")
            return
            
        try:
            url = f"{self.base_url}{self.page_id}/videos"
            params = {
                'file_url': video,  # Note: This requires a publicly accessible URL
                'description': message,
                'access_token': self.access_token
            }
            
            response = requests.post(url, data=params)
            response_data = response.json()
            
            if 'id' in response_data:
                print(f"Facebook video post published successfully. Post ID: {response_data['id']}")
            else:
                raise Exception(f"Failed to publish video post: {response_data}")
                
        except Exception as e:
            print(f"Failed to post video to Facebook: {str(e)}")
            print("Note: Facebook API requires publicly accessible video URLs")
            raise

    def logout(self) -> None:
        """Logout from Facebook."""
        self.access_token = None
        print("Logged out from Facebook Publisher.")