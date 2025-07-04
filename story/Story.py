import ast, datetime, dotenv, itertools, requests

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from moviepy import editor
from mutagen.mp3 import MP3

from os import getenv, path

from PIL import Image

from string import punctuation
from sys import stderr
from typing import List

# Project imports
from exceptions import (
    ConfigurationException, 
    ImageGenerationException, 
    TranslationException, 
    StoryProcessingException,
    VideoGenerationException
)
from publishers.IPublisher import IPublisher

from story.IStory import IStory
from story.Audio import Audio
from story.Image import Image
from story.Text import Text
from story.Video import Video

from utils.conclusion import conclusion
from utils.introduction import introduction
from utils.Utils import make_api_request, urlify

dotenv.load_dotenv()

class Story(IStory):
    id_obj = itertools.count(1)

    def __init__(self, progargs: dict = None) -> None:
        from langchain_community.chat_models import ChatOpenAI

        super().__init__()

        self.id = next(Story.id_obj)
        self.date = datetime.datetime.today().strftime('%Y-%m-%d')

        self.fb = progargs.get('fb', None)
        self.ig = progargs.get('ig', None)
        self.tw = progargs.get('tw', None)
        self.yt = progargs.get('yt', None)

        self.url = progargs.get('url', None)
        self.mock = False

        self.texts = {
            "Hindi": Text(language="Hindi"),
            "English": Text(language="English")
        }
        
        self.audio = None
        self.video = None
        self.sceneries = {}  # Initialize sceneries dictionary
        self.llm = ChatOpenAI(
            temperature=0.4, 
            api_key=getenv('OPENROUTER_API_KEY'), 
            base_url="https://openrouter.ai/api/v1",
            model=getenv('MODEL', "google/gemma-3-27b-it:free"),
            default_headers={
                "HTTP-Referer": "https://localhost:8501",
                "X-Title": "Story Teller App"
            }
        )
        self.images: List[Image] = []  # Initialize as an empty list to store Image objects

    def get_text(self, language: str = "Hindi") -> None:
        self.texts[language].get(self.url)
        self.name = self.texts[language].title.replace(" ", '').translate(str.maketrans('', '', punctuation))

    def translate(self):
        print("Translating story to English...")
        if self.texts["Hindi"].content and self.texts["Hindi"].title:
            self.texts["English"].content = self.texts["Hindi"].translate(to_language="English", llm=self.llm)
            # There is no need to copy or translate the title 
        else:
            raise TranslationException(
                "Hindi story text is missing. Please fetch the story first.",
                source_lang="Hindi",
                target_lang="English"
            )

    def get_sceneries(self):
        print("Getting description for sceneries...")

        template_prompt = '''Act as a highly creative visual illustrator. Based on the story within <STORY> and </STORY> tags, extract scenery descriptions as a Python dictionary.
        Each key: meaningful scene name written in CamelCase, starting with a capital letter but no spaces or special characters
        Each value: nested dictionary containing:
        A short, vivid description of the scene with living entities e.g., animals, birds, insects, humans and natural elements, season, time, weather, colors and more.
        and
        A list of adjectives and sentiments from the scene.
        Descriptions must be rich but concise.
        <STORY>{story}</STORY>
        '''

        sceneries_prompt = PromptTemplate(template=template_prompt, input_variables=['story'])

        chain2 = LLMChain(llm=self.llm, prompt=sceneries_prompt)
        input = {'story': self.texts["English"].content}

        try:
            sceneries_output = chain2.run(input)
            
            # Clean the output if it's wrapped in markdown code blocks
            if isinstance(sceneries_output, str):
                # Remove markdown code blocks if present
                sceneries_output = sceneries_output.strip()
                if sceneries_output.startswith('```python'):
                    sceneries_output = sceneries_output[9:]
                if sceneries_output.startswith('```'):
                    sceneries_output = sceneries_output[3:]
                if sceneries_output.endswith('```'):
                    sceneries_output = sceneries_output[:-3]
                sceneries_output = sceneries_output.strip()
            
            self.sceneries = ast.literal_eval(sceneries_output) if isinstance(sceneries_output, str) else sceneries_output
            
            # Validate that sceneries were extracted
            if not self.sceneries or not isinstance(self.sceneries, dict):
                raise StoryProcessingException(
                    "No valid sceneries extracted from the story",
                    processing_step="scenery_validation",
                    details={"sceneries_output": str(sceneries_output)[:200]}
                )
            
            print(f"Sceneries extracted: {self.sceneries}")

            # Create Image objects and append to images array
            for key, value in self.sceneries.items():
                print(f"Creating image for scenery: {key}")
                print(f"Description: {value.get('description', '')}")
                print(f"Sentiments: {value.get('adjectives', [])}")

                image = Image(title=key, path="./output/images/", description=value.get("description", ""), sentiments=value.get("adjectives", []))
                image.width = 512
                image.height = 512
                self.images.append(image)
        except Exception as e:
            raise StoryProcessingException(
                "Failed to get sceneries", 
                processing_step="scenery_extraction",
                details={"error": str(e), "story_length": len(self.texts["English"].content) if self.texts["English"].content else 0}
            )

    def get_images(self, count: int = 1) -> None:
        try:
            for image in self.images:
                image.create()
        except (ConfigurationException, ImageGenerationException) as e:
            if "TEXT_TO_IMAGE_URL is not set" in str(e):
                raise ConfigurationException(
                    "Image generation is not configured. Please set TEXT_TO_IMAGE_URL in your .env file to use Stable Diffusion for image generation.",
                    config_key="TEXT_TO_IMAGE_URL",
                    details={
                        "solution": "Add TEXT_TO_IMAGE_URL=your_stable_diffusion_url to .env file"
                    }
                )
            else:
                # Re-raise other specific exceptions as-is
                raise e
        except Exception as e:
            raise ImageGenerationException(
                "Failed to generate images", 
                details={"error": str(e), "image_count": len(self.images)}
            )
            
    def get_audio(self, lib: str) -> str:
        print("Beginning to process audio...")
        final_text = introduction.get("Hindi") + "\n\n" + self.texts["Hindi"].content + "\n\n" + conclusion.get("Hindi") + "\n\n"
        self.audio.generate(text=final_text, name=self.name, lib=lib)
        return self.audio.path

    def get_video(self) -> str:
        print("Beginning to process video...")
        # Use the CamelCase scenery titles directly for image paths, but only if files exist
        image_paths = []
        for key in self.sceneries.keys():
            image_path = f"./output/images/{key}.png"
            if path.exists(image_path):
                image_paths.append(image_path)
        
        if not image_paths:
            raise VideoGenerationException(
                "No images found for video generation",
                details={"expected_images": list(self.sceneries.keys())}
            )
        
        self.video.generate(name=self.name, audio_path=self.audio.path, image_paths=image_paths)
        return self.video.path
    
    def publish(self, publishers: List[IPublisher]) -> None:
        # Prepare content for publishing
        content = {
            "text": {
                "hindi": self.texts.get("Hindi", Text("Hindi")).content if hasattr(self, 'texts') else "",
                "english": self.texts.get("English", Text("English")).content if hasattr(self, 'texts') else "",
                "title": self.texts.get("Hindi", Text("Hindi")).title if hasattr(self, 'texts') else "Story"
            },
            "audios": [self.audio.path] if hasattr(self, 'audio') and self.audio.path else [],
            "videos": [self.video.path] if hasattr(self, 'video') and self.video.path else [],
            "images": [img.path for img in getattr(self, 'images', []) if hasattr(img, 'path') and img.path] if hasattr(self, 'images') else []
        }
        
        for publisher in publishers:
            try:
                publisher.login()
                publisher.publish(content)
                publisher.logout()
            except Exception as e:
                print(f"Publishing failed for {type(publisher).__name__}: {e}")
                # Continue with other publishers even if one fails