from os import getenv
from dotenv import load_dotenv

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class ThreadsPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials)
        
    def login(self) -> None:
        """Login to Threads with credential validation."""
        access_token = self.credentials.get('access_token')
        if not access_token:
            raise ConfigurationException(
                "Threads Access Token is not set",
                config_key="THREADS_ACCESS_TOKEN",
                details={"solution": "Add THREADS_ACCESS_TOKEN to your .env file with your Threads access token"}
            )
        
        user_id = self.credentials.get('user_id')
        if not user_id:
            raise ConfigurationException(
                "Threads User ID is not set",
                config_key="THREADS_USER_ID",
                details={"solution": "Add THREADS_USER_ID to your .env file with your Threads user ID"}
            )
        
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.user_id = user_id

    def publish(self, content: dict) -> None:
        """Publish content to Threads."""
        try:
            # Extract text content for thread
            text_content = content.get("text", {})
            hindi_text = text_content.get("hindi", "")
            english_text = text_content.get("english", "")
            title = text_content.get("title", "Story")
            
            # Use English text for thread, fallback to Hindi if English not available
            message_text = english_text if english_text else hindi_text
            
            if not message_text:
                print("Warning: No text content available for Threads publishing")
                return
            
            # Create thread message with title
            thread_message = f"{title}\n\n{message_text}"
            
            # Limit message to appropriate length (Threads has character limits)
            if len(thread_message) > 500:
                thread_message = thread_message[:497] + "..."
            
            # Get image if available
            images = content.get("images", [])
            first_image = images[0] if images else None
            
            # Publish to Threads
            if first_image:
                self._post_thread_with_image(thread_message, first_image)
            else:
                self._post_thread(thread_message)
                
            print("Threads publishing completed successfully")
            
        except Exception as e:
            print(f"Threads publishing failed: {str(e)}")
            raise

    def _post_thread(self, message: str) -> None:
        """Mock thread posting function - in real implementation would use Threads API."""
        print(f"Posting to Threads: {message}")

    def _post_thread_with_image(self, message: str, image: str) -> None:
        """Mock thread with image posting function - in real implementation would use Threads API."""
        print(f"Posting to Threads with image: {message}, Image: {image}")
    
    def logout(self) -> None:
        """Logout from Threads."""
        self.headers = None
        self.user_id = None
        print("Logged out from Threads Publisher.")
