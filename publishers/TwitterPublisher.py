from dotenv import load_dotenv
from os import getenv
import tweepy

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class TwitterPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials)
        self.twitter_client = None
        self.mock_mode = getenv('TWITTER_MOCK_MODE', 'false').lower() == 'true'
        
    def login(self) -> None:
        """Login to Twitter with credential validation."""
        if self.mock_mode:
            print("[MOCK MODE] Skipping Twitter authentication")
            return
            
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
        
        try:
            # Initialize Twitter API client
            self.twitter_client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Test the connection
            self.twitter_client.get_me()
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to authenticate with Twitter: {str(e)}",
                config_key="TWITTER_CREDENTIALS",
                details={"solution": "Check your Twitter API credentials and ensure they are valid"}
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
        """Post tweet to Twitter using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Tweeting: {message}")
            return
            
        try:
            if not self.twitter_client:
                raise Exception("Twitter client not initialized. Call login() first.")
            
            response = self.twitter_client.create_tweet(text=message)
            print(f"Tweet posted successfully. Tweet ID: {response.data['id']}")
            
        except Exception as e:
            print(f"Failed to post tweet: {str(e)}")
            raise

    def _tweet_with_image(self, message: str, image: str) -> None:
        """Post tweet with image to Twitter using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Tweeting with image: {message}, Image: {image}")
            return
            
        try:
            if not self.twitter_client:
                raise Exception("Twitter client not initialized. Call login() first.")
            
            # Note: For image upload, we need to use the v1.1 API
            # This is a simplified implementation - in production you'd handle image upload properly
            print(f"Image posting not fully implemented yet. Posting text only.")
            print(f"Image: {image}")
            
            # For now, just post the text
            response = self.twitter_client.create_tweet(text=message)
            print(f"Tweet with image reference posted successfully. Tweet ID: {response.data['id']}")
            
        except Exception as e:
            print(f"Failed to post tweet with image: {str(e)}")
            raise
    
    def logout(self) -> None:
        """Logout from Twitter."""
        self.twitter_client = None
        print("Logged out from Twitter Publisher.")