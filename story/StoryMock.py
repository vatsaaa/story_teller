import copy, cv2, datetime, itertools
from os import path, getcwd
from string import punctuation
from typing import List

from story.IStory import IStory
from story.Text import Text
from story.Audio import Audio
from story.Video import Video
from story.Story import Story # Used in get_images()
from publishers.IPublisher import IPublisher
from utils.mock.inputs import mock_sceneries, mock_text, mock_title
from utils.Utils import urlify

class StoryMock(IStory):
    id_obj = itertools.count(1)

    def __init__(self, progargs: dict=None) -> None:
        super().__init__()

        self.id = next(StoryMock.id_obj)
        self.date = datetime.datetime.today().strftime('%Y-%m-%d')

        self.fb = progargs.get('fb')
        self.ig = progargs.get('ig')
        self.tw = progargs.get('tw')
        self.yt = progargs.get('yt')
        self.story_name = None

        self.url = None
        self.mock = True
        self.texts = {
            "Hindi": Text(language="Hindi", title=mock_title.get("Hindi"), content=mock_text.get("Hindi")),
            "English": Text(language="English", title=mock_title.get("English"), content=mock_text.get("English"))
        }
        self.sceneries = mock_sceneries
        # Don't hardcode audio path - let it be generated when needed
        self.audio = Audio(file_path="./output/audios/", file_name="mock_story" + "_" + str(self.id))
        # self.video = Video()

    def get_text(self):
        self.story_name = self.texts["Hindi"].title.replace(" ", '').translate(str.maketrans('', '', punctuation))

    def translate(self):
        pass

    def get_images(self):
        # Use available images in the output/images directory instead of trying to generate them
        # Only include images that can be successfully opened by PIL
        from PIL import Image as PILImage
        import os
        
        images_dir = path.join(getcwd(), 'output', 'images')
        candidate_images = []
        
        if path.exists(images_dir):
            # Get all files with common image extensions
            image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(image_extensions):
                    candidate_images.append(filename)
        
        # Check both output/images and root images directories
        image_directories = [
            path.join(getcwd(), 'output', 'images')
        ]
        
        # Validate images and keep only the ones that can be opened
        available_images = []
        for img_name in candidate_images:
            img_path = path.join(images_dir, img_name)
            if path.exists(img_path):
                try:
                    # Test if PIL can open the image
                    with PILImage.open(img_path) as test_img:
                        test_img.verify()  # Verify the image is not corrupted
                    available_images.append((img_name, img_path))
                    break  # Found valid image, no need to check other directories
                except Exception:
                    # Skip corrupted or unreadable images
                    continue
        
        # Map our sceneries to available valid images
        scenery_keys = list(self.sceneries.keys())
        
        if not available_images:
            print("Warning: No valid images available for mock sceneries")
            # Create mock image paths even if files don't exist to prevent errors
            for i, key in enumerate(scenery_keys):
                self.sceneries[key]["path"] = path.join(getcwd(), 'output', 'images', f'mock_image_{i}.png')
            return
        
        for i, key in enumerate(scenery_keys):
            if i < len(available_images):
                img_name, img_path = available_images[i]
                self.sceneries[key]["path"] = img_path
            else:
                # If we have more sceneries than images, reuse images
                img_idx = i % len(available_images)
                img_name, img_path = available_images[img_idx]
                self.sceneries[key]["path"] = img_path

        return

    def get_video(self):
        # Check if video already exists and is valid
        if self.video.path and path.exists(self.video.path):
            return self.video.path
            
        # Generate video if it doesn't exist
        try:
            # Ensure we have audio first
            if not self.audio.path or not path.exists(self.audio.path):
                # Generate audio first if it doesn't exist
                self.get_audio('gTTS')
            
            # Ensure we have images
            self.get_images()  # Always call get_images to ensure mapping is done
            
            # Collect available image paths
            image_paths = []
            for key, scenery in self.sceneries.items():
                if scenery.get("path") and path.exists(scenery["path"]):
                    image_paths.append(scenery["path"])
            
            # If no images are available, we can't create a video
            if not image_paths:
                from exceptions import VideoGenerationException
                raise VideoGenerationException(
                    "No images available for video generation",
                    method="mock",
                    details={"sceneries": list(self.sceneries.keys())}
                )
            
            # Use a proper name for the mock video
            video_name = f"{self.name}_{self.id}" if self.name else f"mock_story_{self.id}"
            
            self.video.generate(
                name=video_name,
                audio_path=self.audio.path,
                image_paths=image_paths
            )
            
            return self.video.path
            
        except Exception as e:
            # Import the exception here to avoid circular imports
            from exceptions import VideoGenerationException
            if isinstance(e, VideoGenerationException):
                raise
            else:
                raise VideoGenerationException(
                    f"Failed to generate video for mock story: {str(e)}",
                    method="mock",
                    details={"story_id": self.id, "error": str(e)}
                )

    def get_audio(self, tts_engine: str):
        # Check if audio already exists and is valid
        if self.audio.path and path.exists(self.audio.path):
            return self.audio.path
            
        # Generate audio if it doesn't exist
        try:
            from utils.introduction import introduction
            from utils.conclusion import conclusion
            
            final_text = introduction.get("Hindi") + "\n\n" + self.texts["Hindi"].content + "\n\n" + conclusion.get("Hindi") + "\n\n"
            
            # Use a proper name for the mock story
            audio_name = f"{self.name}_{self.id}" if self.name else f"mock_story_{self.id}"
            
            self.audio.generate(text=final_text, name=audio_name, lib=tts_engine)
            
            return self.audio.path
        except Exception as e:
            # Import the exception here to avoid circular imports
            from exceptions import AudioGenerationException
            raise AudioGenerationException(
                f"Failed to generate audio for mock story: {str(e)}",
                library=tts_engine,
                details={"story_id": self.id, "error": str(e)}
            )
    
    def get_sceneries(self):
        self.sceneries = mock_sceneries

    def publish(self, publishers: List[IPublisher]) -> None:
        # Prepare content for publishing
        content = {
            "text": {
                "hindi": self.texts.get("Hindi").content if self.texts.get("Hindi") else "",
                "english": self.texts.get("English").content if self.texts.get("English") else "",
                "title": self.texts.get("Hindi").title if self.texts.get("Hindi") else "Mock Story"
            },
            "audio": self.audio.path if self.audio.path else None,
            "video": self.video.path if self.video.path else None,
            "images": [s.get("path") for s in self.sceneries.values() if s.get("path")] if hasattr(self, 'sceneries') else []
        }
        
        for publisher in publishers:
            try:
                publisher.login()
                publisher.publish(content)
                publisher.logout()
            except Exception as e:
                print(f"Publishing failed for {type(publisher).__name__}: {e}")
                # Continue with other publishers even if one fails

