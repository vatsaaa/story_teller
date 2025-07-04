from os import getenv
from dotenv import load_dotenv

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class InstagramPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials=credentials)
    
    def login(self) -> None:
        """Login to Instagram with credential validation."""
        access_token = self.credentials.get('access_token')
        if not access_token:
            raise ConfigurationException(
                "Instagram Access Token is not set",
                config_key="IG_ACCESS_TOKEN",
                details={"solution": "Add IG_ACCESS_TOKEN to your .env file with your Instagram access token"}
            )
        
        business_account_id = self.credentials.get('business_account_id')
        if not business_account_id:
            raise ConfigurationException(
                "Instagram Business Account ID is not set",
                config_key="IG_BUSINESS_ACCOUNT_ID",
                details={"solution": "Add IG_BUSINESS_ACCOUNT_ID to your .env file with your Instagram Business Account ID"}
            )
        
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.business_account_id = business_account_id
    
    def publish(self, content: dict) -> None:
        """Publish content to Instagram."""
        try:
            # Extract text content for caption
            text_content = content.get("text", {})
            hindi_text = text_content.get("hindi", "")
            english_text = text_content.get("english", "")
            title = text_content.get("title", "Story")
            
            # Use English text for caption, fallback to Hindi if English not available
            message_text = english_text if english_text else hindi_text
            
            if not message_text:
                print("Warning: No text content available for Instagram publishing")
                return
            
            # Create Instagram caption with title
            caption = f"{title}\n\n{message_text}"
            
            # Instagram caption limit is 2200 characters
            if len(caption) > 2200:
                caption = caption[:2197] + "..."
            
            # Get image - Instagram requires at least one image
            images = content.get("images", [])
            if not images:
                print("Warning: No image available for Instagram publishing. Instagram requires at least one image.")
                return
            
            # Get video if available
            videos = content.get("videos", [])
            first_video = videos[0] if videos else None
            
            # Publish to Instagram
            if first_video:
                self._post_video(caption, first_video)
            else:
                self._post_image(caption, images[0])
                
            print("Instagram publishing completed successfully")
            
        except Exception as e:
            print(f"Instagram publishing failed: {str(e)}")
            raise

    def _post_image(self, caption: str, image: str) -> None:
        """Mock Instagram image posting function - in real implementation would use Instagram API."""
        print(f"Posting to Instagram:")
        print(f"Image: {image}")
        print(f"Caption: {caption}")

    def _post_video(self, caption: str, video: str) -> None:
        """Mock Instagram video posting function - in real implementation would use Instagram API."""
        print(f"Posting video to Instagram:")
        print(f"Video: {video}")
        print(f"Caption: {caption}")

    def logout(self) -> None:
        """Logout from Instagram."""
        self.headers = None
        self.business_account_id = None
        print("Logged out from Instagram Publisher.")