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
import openai
from os import getenv, path
import pyttsx3, re
from string import punctuation
from sys import stderr

from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from PIL import Image


dotenv.load_dotenv()

from utils.introduction import introduction
from utils.conclusion import conclusion
from utils.Constants import SocialMedia, STABLEDIFFUSION_API_KEY, TEXT_TO_IMAGE_URL
from utils.Utils import make_api_request, urlify
from CustomException import CustomException
from utils.publishers.InstagramPublisher import InstagramPublisher
from utils.publishers.TwitterPublisher import TwitterPublisher
from utils.publishers.YoutubePublisher import YoutubePublisher

class Story:
    id_obj = itertools.count(1)

    def __init__(self, progargs: dict) -> None:
        self.fb = progargs.get('fb')
        self.ig = progargs.get('ig')
        self.tw = progargs.get('tw')
        self.yt = progargs.get('yt')

        self.id = next(Story.id_obj)
        self.url = progargs.get('url')
        self.title = {}
        self.text = {}
        self.moral = {}
        self.images = list()
        self.date = datetime.datetime.today().strftime('%Y-%m-%d')

        self.llm = OpenAI(temperature=0.4)

    def get_text(self):
        pattern = re.compile(r':\s$', re.MULTILINE)

        response = requests.get(self.url)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        headings = soup.find_all('h1')
        paragraphs = soup.find_all('p')

        self.title["Hindi"] = [h.get_text() for h in headings][0].split(":")[0]
        self.text["Hindi"] = [re.sub(pattern, '-', p.get_text().replace("दु:खी", "दुखी")) for p in paragraphs][0].split(":")[0]

    def translate(self) -> None:
        if self.text.get("Hindi"):
            # Get the text to be translated
            text_to_translate = self.text.get("Hindi")

            # Set up the translation prompt, grammer (e.g. articles) omitted for brevity
            translation_template = '''
            Following tag <TEXT>, is text of famous kids story in {from_lang} language. Please translate it to {to_lang} language.
            
            Return only the translation in {to_lang} language, not any text in original {from_lang} language.

            Returned text must be suitable for a blog and a podcast higly popular amongst kids of 5 years to 14 years.
            Ensure returned text is highly engaging with elaborated and illustrative scenes.


            <TEXT>
            {text}
            '''

            text_prompt = PromptTemplate(template=translation_template, input_variables=['from_lang', 'to_lang', 'text'])

            chain2 = LLMChain(llm=self.llm,prompt=text_prompt)

            # Extract the translated text from the API response
            input = {'from_lang': "Hindi", 'to_lang': "English", 'text': text_to_translate}
            translated_text = chain2.run(input)

            # Print the translated text
            print("\n\n<TRANSLATION>\n")
            print(translated_text)
            print("\n</TRANSLATION>\n\n")
        else:
            raise CustomException("Please call .translate() after having fetched the Hindi story!")

    def get_moral(self):
        # Having created the English story, we get its moral
        if self.text.get("English"):
            self.moral["English"] = self.text.get("English")

        # Then we translate the English moral to Hindi
        self.moral["Hindi"] = self.moral.get("English")
    
    def get_images(self, width: int = 1024, height: int = 512, count: int = 1) -> list:
        image_title = self.title

        img_data = None
        image_url = None
        output_path = None

        data = {
            'key': STABLEDIFFUSION_API_KEY,
            'width': width,
            'height': height,
            'prompt': self.text,
            "enhance_prompt": "no",
            "safety_checker": "no",
            "samples": str(count)
        }

        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }

        for i in range(count):
            response = make_api_request(TEXT_TO_IMAGE_URL, data, headers)
            self.images = response.json().get('output', [])[0]
            img_data = requests.get(image_url).content if image_url else None

            if img_data:
                output_path = path.join('./images/', urlify(image_title) + '.png')
                with open(output_path, 'wb') as handler:
                    handler.write(img_data)

    def get_audio(self, lib: str):
        final_text = introduction.get("Hindi") + "\n\n" + self.text.get("Hindi") + "\n\n" + conclusion.get("Hindi") + "\n\n"
        if lib.lower() == 'gtts':
            gttsLang = 'hi'

            replyObj = gTTS(text=final_text, lang=gttsLang, slow=True, pre_processor_funcs=[abbreviations, end_of_line])
            self.audio_name = self.title.get("Hindi").replace(" ", '').translate(str.maketrans('', '', punctuation)) + ".mp3"

            replyObj.save(self.audio_name)
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
        song = MP3(self.audio_name)
        audio_length = round(song.info.length)
        
        image_list = list()
        for image_name in self.images:
            image = Image.open(image_name).resize((800, 800), Image.ANTIALIAS)
            image_list.append(image)
    
    def _publish_facebook(self):
        if not self.fb:
            return
        

    def _publish_instagram(self):
        if not self.ig:
            return

    def _publish_twitter(self, tweet_text: str):
        if not self.tw:
            return
        
        instagrammer = InstagramPublisher(
            getenv('INSTAGRAM_USERNAME'),
            getenv('INSTAGRAM_PASSWORD')
        )
        instagrammer.publish(self.text.get("Hindi"))

        tweeter = TwitterPublisher(
            getenv('TWITTER_CONSUMER_KEY'),
            getenv('TWITTER_CONSUMER_SECRET'),
            getenv('TWITTER_ACCESS_TOKEN'),
            getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        tweeter.tweet(self.text.get("Hindi"))

    def _publish_youtube(self):
        if not self.yt:
            return
        
        youtuber = YoutubePublisher(
            getenv('YOUTUBE_CLIENT_ID'),
            getenv('YOUTUBE_CLIENT_SECRET'),
            getenv('YOUTUBE_REFRESH_TOKEN'),
            getenv('YOUTUBE_ACCESS_TOKEN')
        )
        youtuber.publish(self.text.get("Hindi"))

    def publish(self):
        self._publish_facebook()

        self._publish_instagram()
        
        self._publish_twitter()
        
        self._publish_youtube()
