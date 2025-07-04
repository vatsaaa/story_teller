from dotenv import load_dotenv
from os import getenv

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class TwitterPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials)
        
    def login(self) -> None:
        """Login to Twitter with credential validation."""
        access_token = self.credentials.get('access_token')
        if not access_token:
            raise ConfigurationException(
                "Twitter Access Token is not set",
                config_key="TWITTER_ACCESS_TOKEN",
                details={"solution": "Add TWITTER_ACCESS_TOKEN to your .env file with your Twitter access token"}
            )
        
        api_key = self.credentials.get('api_key')
        if not api_key:
            raise ConfigurationException(
                "Twitter API Key is not set",
                config_key="TWITTER_API_KEY",
                details={"solution": "Add TWITTER_API_KEY to your .env file with your Twitter API key"}
            )
        
        api_secret = self.credentials.get('api_secret')
        if not api_secret:
            raise ConfigurationException(
                "Twitter API Secret is not set",
                config_key="TWITTER_API_SECRET",
                details={"solution": "Add TWITTER_API_SECRET to your .env file with your Twitter API secret"}
            )
        
        access_token_secret = self.credentials.get('access_token_secret')
        if not access_token_secret:
            raise ConfigurationException(
                "Twitter Access Token Secret is not set",
                config_key="TWITTER_ACCESS_TOKEN_SECRET",
                details={"solution": "Add TWITTER_ACCESS_TOKEN_SECRET to your .env file with your Twitter access token secret"}
            )
    
    def publish(self, content: dict) -> None:
        """Publish content to Twitter."""
        try:
            # Extract text content for tweet
            text_content = content.get("text", {})
            hindi_text = text_content.get("hindi", "")
            english_text = text_content.get("english", "")
            title = text_content.get("title", "Story")
            
            # Use English text for tweet, fallback to Hindi if English not available
            message_text = english_text if english_text else hindi_text
            
            if not message_text:
                print("Warning: No text content available for Twitter publishing")
                return
            
            # Build tweet message with title
            tweet_message = f"{title}: {message_text}"
            
            # Twitter character limit is 280, so truncate if necessary
            if len(tweet_message) > 280:
                tweet_message = tweet_message[:277] + "..."
            
            # Get image if available
            images = content.get("images", [])
            first_image = images[0] if images else None
            
            # Publish tweet
            if first_image:
                self._tweet_with_image(tweet_message, first_image)
            else:
                self._tweet(tweet_message)
                
            print("Twitter publishing completed successfully")
            
        except Exception as e:
            print(f"Twitter publishing failed: {str(e)}")
            raise

    def _tweet(self, message: str) -> None:
        """Mock tweet function - in real implementation would use Twitter API."""
        print(f"Tweeting: {message}")

    def _tweet_with_image(self, message: str, image: str) -> None:
        """Mock tweet with image function - in real implementation would use Twitter API."""
        print(f"Tweeting with image: {message}, Image: {image}")
    
    def logout(self) -> None:
        """Logout from Twitter."""
        print("Logged out from Twitter Publisher.")