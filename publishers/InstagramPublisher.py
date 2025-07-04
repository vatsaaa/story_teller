from os import getenv
from dotenv import load_dotenv
import requests
import json

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class InstagramPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials=credentials)
        self.mock_mode = getenv('INSTAGRAM_MOCK_MODE', 'false').lower() == 'true'
        self.access_token = None
        self.business_account_id = None
    
    def login(self) -> None:
        """Login to Instagram with credential validation."""
        if self.mock_mode:
            print("[MOCK MODE] Skipping Instagram authentication")
            return
            
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
        
        self.access_token = access_token
        self.business_account_id = business_account_id
        
        # Test the credentials
        try:
            url = f"https://graph.facebook.com/v18.0/{business_account_id}"
            params = {'access_token': access_token}
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"API returned status code {response.status_code}: {response.text}")
                
        except Exception as e:
            raise ConfigurationException(
                f"Failed to authenticate with Instagram: {str(e)}",
                config_key="INSTAGRAM_CREDENTIALS",
                details={"solution": "Check your Instagram API credentials and ensure they are valid"}
            )
    
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
        """Post image to Instagram using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Posting to Instagram:")
            print(f"[MOCK MODE] Image: {image}")
            print(f"[MOCK MODE] Caption: {caption}")
            return
            
        try:
            # Step 1: Create media object
            create_url = f"https://graph.facebook.com/v18.0/{self.business_account_id}/media"
            create_params = {
                'image_url': image,  # Note: This requires a publicly accessible URL
                'caption': caption,
                'access_token': self.access_token
            }
            
            create_response = requests.post(create_url, data=create_params)
            create_data = create_response.json()
            
            if 'id' not in create_data:
                raise Exception(f"Failed to create media object: {create_data}")
            
            media_id = create_data['id']
            
            # Step 2: Publish the media
            publish_url = f"https://graph.facebook.com/v18.0/{self.business_account_id}/media_publish"
            publish_params = {
                'creation_id': media_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            publish_data = publish_response.json()
            
            if 'id' in publish_data:
                print(f"Instagram image posted successfully. Post ID: {publish_data['id']}")
            else:
                raise Exception(f"Failed to publish media: {publish_data}")
                
        except Exception as e:
            print(f"Failed to post image to Instagram: {str(e)}")
            print("Note: Instagram API requires publicly accessible image URLs")
            raise

    def _post_video(self, caption: str, video: str) -> None:
        """Post video to Instagram using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Posting video to Instagram:")
            print(f"[MOCK MODE] Video: {video}")
            print(f"[MOCK MODE] Caption: {caption}")
            return
            
        try:
            # Step 1: Create video media object
            create_url = f"https://graph.facebook.com/v18.0/{self.business_account_id}/media"
            create_params = {
                'video_url': video,  # Note: This requires a publicly accessible URL
                'caption': caption,
                'media_type': 'VIDEO',
                'access_token': self.access_token
            }
            
            create_response = requests.post(create_url, data=create_params)
            create_data = create_response.json()
            
            if 'id' not in create_data:
                raise Exception(f"Failed to create video media object: {create_data}")
            
            media_id = create_data['id']
            
            # Step 2: Publish the video
            publish_url = f"https://graph.facebook.com/v18.0/{self.business_account_id}/media_publish"
            publish_params = {
                'creation_id': media_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            publish_data = publish_response.json()
            
            if 'id' in publish_data:
                print(f"Instagram video posted successfully. Post ID: {publish_data['id']}")
            else:
                raise Exception(f"Failed to publish video: {publish_data}")
                
        except Exception as e:
            print(f"Failed to post video to Instagram: {str(e)}")
            print("Note: Instagram API requires publicly accessible video URLs")
            raise

    def logout(self) -> None:
        """Logout from Instagram."""
        self.access_token = None
        self.business_account_id = None
        print("Logged out from Instagram Publisher.")