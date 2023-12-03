from bs4 import BeautifulSoup
import datetime, dotenv, itertools, json, requests

from gtts import gTTS
from gtts.tokenizer.pre_processors import abbreviations, end_of_line

from langchain.chains import LLMChain
from langchain.llms.fake import FakeListLLM
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

from moviepy import editor
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4

import openai
from os import getenv, path

import pathlib, pyttsx3, re
from PIL import Image

from string import punctuation
from sys import stderr

from utils.introduction import introduction
from utils.conclusion import conclusion
from utils.Constants import SocialMedia, TEXT_TO_IMAGE_URL
from utils.Utils import make_api_request, urlify
from CustomException import CustomException
from utils.publishers.InstagramPublisher import InstagramPublisher
from utils.publishers.TwitterPublisher import TwitterPublisher
from utils.publishers.YoutubePublisher import YoutubePublisher
from utils.mock.inputs import mock_sceneries, mock_text, mock_title


dotenv.load_dotenv()

class Story:
    id_obj = itertools.count(1)

    def __init__(self, progargs: dict) -> None:
        self.fb = progargs.get('fb')
        self.ig = progargs.get('ig')
        self.tw = progargs.get('tw')
        self.yt = progargs.get('yt')
        self.story_name = None

        self.id = next(Story.id_obj)
        
        if progargs.get('mock'):
            self.url = None
            self.mock = True
            self.text = mock_text
            self.title = mock_title
            self.sceneries = mock_sceneries
            self.llm = None
        else: 
            self.url = progargs.get('url')
            self.mock = False
            self.text = {
                "Hindi": None,
                "English": None
            }
            self.title = {
                "Hindi": None,
                "English": None
            }
            self.sceneries = dict()
            self.llm = ChatOpenAI(temperature=0.4)

        self.moral = dict()
        # self.images = list()
        self.date = datetime.datetime.today().strftime('%Y-%m-%d')


    def get_text(self):
        if self.mock:
            self.text = mock_text
        else:
            pattern = re.compile(r':\s$', re.MULTILINE)

            response = requests.get(self.url)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            headings = soup.find_all('h1')
            paragraphs = soup.find_all('p')

            self.title["Hindi"] = [h.get_text() for h in headings][0].split(":")[0]
            self.text["Hindi"] = [re.sub(pattern, '-', p.get_text().replace("दु:खी", "दुखी")) for p in paragraphs][0].split(":")[0]

        # Set the story name using the title
        self.story_name = self.title.get("Hindi").replace(" ", '').translate(str.maketrans('', '', punctuation))

    def translate(self) -> None:
        if not self.mock and self.text.get("Hindi") and not self.text.get("English"):
            text_to_translate = self.text.get("Hindi")

            # Set up the translation prompt, grammer (e.g. articles) omitted for brevity
            translation_template = '''
            Please act as a highly proficient translator for {from_lang} and {to_lang} languages.
            Between tags <TEXT> and </TEXT>, is the text of a popular story for kids in {from_lang} language. Please translate it to {to_lang} language.
            
            Return only the translation in {to_lang} language, not any text in original {from_lang} language.

            Ensure that returned text is highly engaging and suitable for a youtube channel higly popular amongst kids of 5 years to 14 years.

            <TEXT>{text}</TEXT>
            '''

            text_prompt = PromptTemplate(template=translation_template, input_variables=['from_lang', 'to_lang', 'text'])

            chain2 = LLMChain(llm=self.llm,prompt=text_prompt)

            # Extract the translated text from the API response
            input = {'from_lang': "Hindi", 'to_lang': "English", 'text': text_to_translate}
            translated_text = chain2.run(input)

            # Print the translated text
            self.text["English"] = translated_text
        elif self.mock and self.text.get("Hindi") and self.text.get("English"):
            pass
        else:
            raise CustomException("Please call .translate() after having fetched the Hindi story!")

    def get_moral(self):
        # Having created the English story, we get its moral
        if self.text.get("English"):
            self.moral["English"] = self.text.get("English")

        # Then we translate the English moral to Hindi
        self.moral["Hindi"] = self.moral.get("English")
    
    def get_sceneries(self):
        if not self.mock and self.text.get("English"):
            template_prompt = '''Please act as a highly creative and accomplished "visual illustrator" that extracts sceneries from story text given within <STORY> and </STORY> tags. 
            Detailed explanation of sceneries extracted from the given story text should not have names of the characters, places or other proper nouns. All living beings should should be accompanied by others in the sceneries.
            The sceneries should set in natural surroundings, with humans, trees, flowers, water bodies, birds, mountains, valleys, Sun, Moon, stars, animals and other living beings in them. Indoor scenes should be spared unless explained in the story.
            Where possible, especially when outdoors, the explanation of sceneries should have details about climate, weather, time of the day, season, etc.
            The extracted sceneries should be represented as a Python dictionary where title of the scene is the key and value is a nested python dictionary with the detailed description of the scene as the first element. 
            The second element in the nested dictionary is a list of sentiments that can be used to explain the scenery in the detailed description. 
            Nothing else is required in the output Python dictionary.

            <STORY>{story}</STORY>
            '''

            sceneries_prompt = PromptTemplate(template=template_prompt, input_variables=['story'])

            chain2 = LLMChain(llm=self.llm,prompt=sceneries_prompt)
            input = {'story': self.text.get("English")}
            
            self.sceneries = chain2.run(input)
    
    def get_images(self, width: int = 512, height: int = 512, count: int = 1) -> None:
        for key in self.sceneries:
            scenery_title = key
            scenery_prompt = '''Create a hyper-realistic scene described in these words: {description}. 
                                The lighting is cinematic and the photograph is ultra-detailed, with 8k resolution and sharp focus. 
                                The scene sentiments are explained by words such as {sentiments}.
                            '''.format(description=self.sceneries.get(key).get("description"), 
                                        sentiments=self.sceneries.get(key).get("sentiments"))

            img_data = None
            image_url = None
            output_path = None

            data = {
                'key': getenv('STABLEDIFFUSION_API_KEY_99'),
                'width': width,
                'height': height,
                'prompt': scenery_prompt,
                'negative_prompt': 'multiple images of the same scene',
                "enhance_prompt": "no",
                'guidance_scale': 8,
                "safety_checker": "no",
                'multi_lingual': 'no',
                'panorama': 'no',
                "samples": str(count)
            }

            headers = {
                'Content-type': 'application/json',
                'Accept': 'text/plain'
            }

            response = make_api_request(TEXT_TO_IMAGE_URL, data, headers)
            # print(response.json().get('output'))[0]
            img_data = requests.get(image_url).content if image_url else None

            if img_data:
                output_path = path.join('./images/', urlify(scenery_title) + '.png')
                with open(output_path, 'wb') as handler:
                    handler.write(img_data)
            
            break

    def get_audio(self, lib: str) -> None:
        final_text = introduction.get("Hindi") + "\n\n" + self.text.get("Hindi") + "\n\n" + conclusion.get("Hindi") + "\n\n"
        if lib.lower() == 'gtts':
            gttsLang = 'hi' # Hindi language

            replyObj = gTTS(text=final_text, lang=gttsLang, slow=True, pre_processor_funcs=[abbreviations, end_of_line])

            replyObj.save(path.join('./audios/', self.story_name + ".mp3"))
        elif lib.lower() == 'pyttsx3':
            engine = pyttsx3.init()
            voices = filter(lambda v: v.gender == 'VoiceGenderFemale', engine.getProperty('voices'))
            for voice in enumerate(voices):
                print(voice[0], "Voice ID: ", voice[1].id, voice[1].languages[0])
                engine.setProperty('voice', voice[1].id)
                engine.say(final_text)
                engine.runAndWait()
        else:
            raise CustomException("Please use a valid speech processing library. {lib} is not valid!".format(lib=lib))

    def get_video(self):
        video_name = self.story_name + ".mp4"
        audio_name = self.story_name + ".mp3"

        video_path = path.join('./videos', video_name)
        audio_path = path.join('./audios', audio_name)

        # Read the story audio mp3 file and set its length
        story_audio = MP3(audio_path)
        audio_length = round(story_audio.info.length) + 1
        
        # Glob the images and stitch them to get the gif
        path_images = pathlib.Path('./images/')
        # print("Path images: ", path_images.absolute())
        images = list(path_images.absolute().glob('*.png'))
        image_list = list()
        
        for image_name in images:
            image = Image.open(image_name).resize((800, 800), Image.Resampling.LANCZOS)
            image_list.append(image)
        
        print("Number of images: ", len(image_list)
                , "\nAudio length: ", audio_length)
        duration = int(audio_length / len(image_list)) * 1000

        # Creating the gif
        image_list[0].save(path.join('./videos/',"temp.gif"),save_all=True,append_images=image_list[1:],duration=duration)
        
        # Getting the vieo from the gif
        video = editor.VideoFileClip(path.join('./videos/', "temp.gif"))

        # Add audio to the video
        audio = editor.AudioFileClip(audio_path)
        video = video.set_audio(audio).set_fps(60)
        video.write_videofile(video_path)        
    
    def _publish_facebook(self) -> None:
        if not self.fb:
            return
        

    def _publish_instagram(self) -> None:
        if not self.ig:
            return

        content = dict()
        if self.ig and not self.mock: 
            # TODO: Below line assumes gif file is present
            # adopt defensive programming here to prevent errors
            content["image"] = path.join('./videos/', self.story_name + ".gif")

            # Get caption from the story text in English
            text_to_get_caption_from = self.text.get("English")

            # Set up the translation prompt, grammer (e.g. articles) omitted for brevity
            caption_template = '''
            Create a highly engaging summary from the given text between tags <TEXT> and </TEXT>, for publishing as caption on a Instagram post.

            Return only the summary, not the original text. Character Vikram should not be summary.

            <TEXT>{text}</TEXT>
            '''

            caption_prompt = PromptTemplate(template=caption_template, input_variables=['text'])

            chain2 = LLMChain(llm=self.llm,prompt=caption_prompt)

            # Extract the translated text from the API response
            input = {'text': text_to_get_caption_from}
            content["caption"] = chain2.run(input)

        instagrammer = InstagramPublisher(
            getenv('INSTAGRAM_USERNAME'),
            getenv('INSTAGRAM_PASSWORD')
        )
        
        if self.ig and self.mock:
            content["image"] = path.join('./videos/', self.story_name + ".gif")
            content["caption"] = "This is a mock caption for the story"

        instagrammer.login()
        instagrammer.publish(content)

    def _publish_twitter(self, tweet_text: str) -> None:
        if not self.tw:
            return
        
        tweeter = TwitterPublisher(
            getenv('TWITTER_CONSUMER_KEY'),
            getenv('TWITTER_CONSUMER_SECRET'),
            getenv('TWITTER_ACCESS_TOKEN'),
            getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        tweeter.tweet(self.text.get("Hindi"))

    def _publish_youtube(self) -> None:
        if not self.yt:
            return
        
        youtuber = YoutubePublisher(
            getenv('YOUTUBE_CLIENT_ID'),
            getenv('YOUTUBE_CLIENT_SECRET'),
            getenv('YOUTUBE_REFRESH_TOKEN'),
            getenv('YOUTUBE_ACCESS_TOKEN')
        )
        youtuber.publish(self.text.get("Hindi"))

    def publish(self) -> None:
        self._publish_facebook() if self.fb else None

        self._publish_instagram() if self.ig else None
        
        self._publish_twitter() if self.tw else None
        
        self._publish_youtube() if self.yt else None
