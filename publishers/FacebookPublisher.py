from dotenv import load_dotenv
from os import getenv

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class FacebookPublisher(IPublisher):
    def __init__(self, page_id: str) -> None:
        super().__init__()
        self.page_id = page_id
        
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
        self.access_token = access_token
    
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
        """Mock Facebook text posting function - in real implementation would use Facebook API."""
        print(f"Posting to Facebook:")
        print(f"Message: {message}")

    def _post_image(self, message: str, image: str) -> None:
        """Mock Facebook image posting function - in real implementation would use Facebook API."""
        print(f"Posting to Facebook with image:")
        print(f"Message: {message}")
        print(f"Image: {image}")

    def _post_video(self, message: str, video: str) -> None:
        """Mock Facebook video posting function - in real implementation would use Facebook API."""
        print(f"Posting to Facebook with video:")
        print(f"Message: {message}")
        print(f"Video: {video}")

    def logout(self) -> None:
        """Logout from Facebook."""
        self.headers = None
        self.access_token = None
        print("Logged out from Facebook Publisher.")