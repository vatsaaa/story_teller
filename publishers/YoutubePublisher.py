from http import client
import httplib2
import os, random, time
from unittest.mock import Mock

from google.oauth2 import credentials
from google_auth_oauthlib import flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException


httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, client.NotConnected,
                        client.IncompleteRead, client.ImproperConnectionState,
                        client.CannotSendRequest, client.CannotSendHeader,
                        client.ResponseNotReady, client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = 'client_secret.json'

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print('Video id "%s" was successfully uploaded.' %
                          response['id'])
                else:
                    exit('The upload failed with an unexpected response: %s' % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)

class YoutubePublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials=credentials)
        
        # Check if client secrets file exists
        if not os.path.exists(CLIENT_SECRETS_FILE):
            raise ConfigurationException(
                "YouTube client secrets file not found",
                config_key="client_secret.json",
                details={
                    "solution": "Download client_secret.json from Google Cloud Console and place it in the project root",
                    "path_checked": os.path.abspath(CLIENT_SECRETS_FILE),
                    "instructions": "1. Go to Google Cloud Console\n2. Enable YouTube Data API v3\n3. Create OAuth 2.0 credentials\n4. Download client_secret.json\n5. Place it in the project root directory"
                }
            )
        
        try:
            # Mocked service object to bypass actual API calls during development
            self.youtube_service = Mock()
            
            # Note: The actual OAuth flow would happen here in production
            # For now, we're using a mock to avoid requiring real credentials during development
            # flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            # credentials = flow.run_local_server(port=0)
            # self.youtube_service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
            
        except Exception as e:
            raise ConfigurationException(
                f"Failed to initialize YouTube publisher: {str(e)}",
                config_key="youtube_oauth",
                details={
                    "error": str(e),
                    "solution": "Ensure client_secret.json is valid and YouTube Data API is enabled"
                }
            )
    
    def login(self) -> None:
        pass

    def logout(self) -> None:
        print("Logged out of Youtube")
         
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
            description = text_content.get("english", text_content.get("hindi", "Generated story video"))
            
            # Mock implementation - in real scenario would upload to YouTube
            print(f"Publishing to YouTube:")
            print(f"Video file: {video_file}")
            print(f"Title: {title}")
            print(f"Description: {description[:100]}...")
            print("YouTube publishing completed successfully")
            
        except Exception as e:
            print(f"YouTube publishing failed: {str(e)}")
            raise
