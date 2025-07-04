from os import getenv
from dotenv import load_dotenv
import requests
import json

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

class ThreadsPublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials)
        self.mock_mode = getenv('THREADS_MOCK_MODE', 'false').lower() == 'true'
        self.access_token = None
        self.user_id = None
        
    def login(self) -> None:
        """Login to Threads with credential validation."""
        if self.mock_mode:
            print("[MOCK MODE] Skipping Threads authentication")
            return
            
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
        
        self.access_token = access_token
        self.user_id = user_id
        
        # Test the credentials
        try:
            url = f"https://graph.threads.net/v1.0/{user_id}"
            params = {'access_token': access_token}
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"API returned status code {response.status_code}: {response.text}")
                
        except Exception as e:
            raise ConfigurationException(
                f"Failed to authenticate with Threads: {str(e)}",
                config_key="THREADS_CREDENTIALS",
                details={"solution": "Check your Threads API credentials and ensure they are valid"}
            )

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
        """Post thread to Threads using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Posting to Threads: {message}")
            return
            
        try:
            # Step 1: Create thread post
            create_url = f"https://graph.threads.net/v1.0/{self.user_id}/threads"
            create_params = {
                'media_type': 'TEXT',
                'text': message,
                'access_token': self.access_token
            }
            
            create_response = requests.post(create_url, data=create_params)
            create_data = create_response.json()
            
            if 'id' not in create_data:
                raise Exception(f"Failed to create thread: {create_data}")
            
            thread_id = create_data['id']
            
            # Step 2: Publish the thread
            publish_url = f"https://graph.threads.net/v1.0/{self.user_id}/threads_publish"
            publish_params = {
                'creation_id': thread_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            publish_data = publish_response.json()
            
            if 'id' in publish_data:
                print(f"Thread posted successfully. Thread ID: {publish_data['id']}")
            else:
                raise Exception(f"Failed to publish thread: {publish_data}")
                
        except Exception as e:
            print(f"Failed to post thread: {str(e)}")
            raise

    def _post_thread_with_image(self, message: str, image: str) -> None:
        """Post thread with image to Threads using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Posting to Threads with image: {message}, Image: {image}")
            return
            
        try:
            # Step 1: Create thread post with image
            create_url = f"https://graph.threads.net/v1.0/{self.user_id}/threads"
            create_params = {
                'media_type': 'IMAGE',
                'image_url': image,  # Note: This requires a publicly accessible URL
                'text': message,
                'access_token': self.access_token
            }
            
            create_response = requests.post(create_url, data=create_params)
            create_data = create_response.json()
            
            if 'id' not in create_data:
                raise Exception(f"Failed to create thread with image: {create_data}")
            
            thread_id = create_data['id']
            
            # Step 2: Publish the thread
            publish_url = f"https://graph.threads.net/v1.0/{self.user_id}/threads_publish"
            publish_params = {
                'creation_id': thread_id,
                'access_token': self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            publish_data = publish_response.json()
            
            if 'id' in publish_data:
                print(f"Thread with image posted successfully. Thread ID: {publish_data['id']}")
            else:
                raise Exception(f"Failed to publish thread with image: {publish_data}")
                
        except Exception as e:
            print(f"Failed to post thread with image: {str(e)}")
            print("Note: Threads API requires publicly accessible image URLs")
            raise
    
    def logout(self) -> None:
        """Logout from Threads."""
        self.access_token = None
        self.user_id = None
        print("Logged out from Threads Publisher.")
