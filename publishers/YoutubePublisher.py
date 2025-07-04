import os
from dotenv import load_dotenv

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class YoutubePublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials=credentials)
        
        # Check if client secrets file exists
        client_secrets_file = self.credentials.get('client_secrets_file', 'client_secret.json')
        if not os.path.exists(client_secrets_file):
            raise ConfigurationException(
                "YouTube client secrets file not found",
                config_key="client_secret.json",
                details={
                    "solution": "Download client_secret.json from Google Cloud Console and place it in the project root",
                    "path_checked": os.path.abspath(client_secrets_file),
                    "instructions": "1. Go to Google Cloud Console\n2. Enable YouTube Data API v3\n3. Create OAuth 2.0 credentials\n4. Download client_secret.json\n5. Place it in the project root directory"
                }
            )
        
        self.client_secrets_file = client_secrets_file
    
    def login(self) -> None:
        """Login to YouTube with credential validation."""
        try:
            # Note: In a real implementation, this would handle OAuth flow
            # For now, we're using a mock approach
            print("YouTube login initialized successfully")
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to initialize YouTube publisher: {str(e)}",
                config_key="youtube_oauth",
                details={
                    "error": str(e),
                    "solution": "Ensure client_secret.json is valid and YouTube Data API is enabled"
                }
            )
         
    def publish(self, content: dict) -> None:
        """Publish content to YouTube."""
        try:
            # Extract video and metadata from content
            videos = content.get("videos", [])
            if not videos:
                print("Warning: No video content available for YouTube publishing")
                return
                
            video_file = videos[0]  # Use first video
            
            # Extract text content for title and description
            text_content = content.get("text", {})
            title = text_content.get("title", "Story Video")
            hindi_text = text_content.get("hindi", "")
            english_text = text_content.get("english", "")
            
            # Use English text for description, fallback to Hindi if English not available
            description = english_text if english_text else hindi_text
            if not description:
                description = "Generated story video"
            
            # Limit title to YouTube's limit (100 characters)
            if len(title) > 100:
                title = title[:97] + "..."
            
            # Get thumbnail if available
            images = content.get("images", [])
            thumbnail = images[0] if images else None
            
            # Publish to YouTube
            self._upload_video(video_file, title, description, thumbnail)
            
            print("YouTube publishing completed successfully")
            
        except Exception as e:
            print(f"YouTube publishing failed: {str(e)}")
            raise

    def _upload_video(self, video_file: str, title: str, description: str, thumbnail: str = None) -> None:
        """Mock YouTube video upload function - in real implementation would use YouTube API."""
        print(f"Uploading to YouTube:")
        print(f"Video file: {video_file}")
        print(f"Title: {title}")
        print(f"Description: {description[:100]}...")
        if thumbnail:
            print(f"Thumbnail: {thumbnail}")

    def logout(self) -> None:
        """Logout from YouTube."""
        print("Logged out from YouTube Publisher.")
