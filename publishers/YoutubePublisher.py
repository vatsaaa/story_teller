import os
from dotenv import load_dotenv
import httplib2
import random
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle

# Project imports
from publishers.IPublisher import IPublisher
from exceptions.ConfigurationException import ConfigurationException

load_dotenv()

# YouTube API settings
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

# Retry settings
MAX_RETRIES = 3
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

class YoutubePublisher(IPublisher):
    def __init__(self, credentials: dict) -> None:
        super().__init__(credentials=credentials)
        self.mock_mode = os.getenv('YOUTUBE_MOCK_MODE', 'false').lower() == 'true'
        self.youtube_service = None
        
        # Check if client secrets file exists
        client_secrets_file = self.credentials.get('client_secrets_file', 'client_secret.json')
        if not self.mock_mode and not os.path.exists(client_secrets_file):
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
        if self.mock_mode:
            print("[MOCK MODE] Skipping YouTube authentication")
            return
            
        try:
            creds = None
            token_file = 'youtube_token.pickle'
            
            # Load existing credentials from file
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials are available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build the YouTube service
            self.youtube_service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
            
            # Test the connection
            channels_response = self.youtube_service.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            if not channels_response.get('items'):
                raise Exception("No YouTube channel found for the authenticated user")
                
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
        """Upload video to YouTube using the API or mock mode."""
        if self.mock_mode:
            print(f"[MOCK MODE] Uploading to YouTube:")
            print(f"[MOCK MODE] Video file: {video_file}")
            print(f"[MOCK MODE] Title: {title}")
            print(f"[MOCK MODE] Description: {description[:100]}...")
            if thumbnail:
                print(f"[MOCK MODE] Thumbnail: {thumbnail}")
            return
            
        try:
            if not self.youtube_service:
                raise Exception("YouTube service not initialized. Call login() first.")
            
            # Check if video file exists
            if not os.path.exists(video_file):
                raise Exception(f"Video file not found: {video_file}")
            
            # Prepare video metadata
            tags = ["story", "generated", "content"]
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': '22'  # People & Blogs category
                },
                'status': {
                    'privacyStatus': 'public'  # Can be 'private', 'public', or 'unlisted'
                }
            }
            
            # Create media upload object
            media = MediaFileUpload(
                video_file,
                chunksize=-1,
                resumable=True,
                mimetype='video/*'
            )
            
            # Call the API's videos.insert method to create and upload the video
            insert_request = self.youtube_service.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute the upload with retry logic
            video_id = self._resumable_upload(insert_request)
            
            if video_id:
                print(f"Video uploaded successfully. Video ID: {video_id}")
                print(f"Video URL: https://www.youtube.com/watch?v={video_id}")
                
                # Upload thumbnail if provided
                if thumbnail and os.path.exists(thumbnail):
                    self._upload_thumbnail(video_id, thumbnail)
            else:
                raise Exception("Failed to upload video")
                
        except Exception as e:
            print(f"Failed to upload video to YouTube: {str(e)}")
            raise

    def _resumable_upload(self, insert_request):
        """Execute the upload with resumable upload and retry logic."""
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                print('Uploading video...')
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        return response['id']
                    else:
                        raise Exception(f'Upload failed with unexpected response: {response}')
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f'A retriable HTTP error {e.resp.status} occurred:\n{e.content}'
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = f'A retriable error occurred: {e}'
            
            if error is not None:
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    raise Exception('No longer attempting to retry.')
                
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f'Sleeping {sleep_seconds} seconds and then retrying...')
                time.sleep(sleep_seconds)

    def _upload_thumbnail(self, video_id: str, thumbnail_file: str) -> None:
        """Upload thumbnail for the video."""
        try:
            self.youtube_service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_file)
            ).execute()
            print(f"Thumbnail uploaded successfully for video {video_id}")
        except Exception as e:
            print(f"Failed to upload thumbnail: {str(e)}")

    def logout(self) -> None:
        """Logout from YouTube."""
        self.youtube_service = None
        print("Logged out from YouTube Publisher.")
