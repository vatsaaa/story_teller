import cv2, datetime, itertools
from os import path, getcwd
from string import punctuation

from IStory import IStory
from utils.mock.inputs import mock_sceneries, mock_text, mock_title
from utils.Utils import urlify

class StoryMock(IStory):
    id_obj = itertools.count(1)

    def __init__(self, progargs: dict) -> None:
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
        self.text = mock_text
        self.title = mock_title
        self.sceneries = mock_sceneries
        self.llm = None

    def get_text(self):
        self.text = mock_text
        self.story_name = self.title.get("Hindi").replace(" ", '').translate(str.maketrans('', '', punctuation))

    def translate(self):
        pass

    def get_images(self):
        img_data = None
        output_path = None

        for key in self.sceneries:
            scenery_title = key

            img_data = cv2.imread('./images', cv2.IMREAD_UNCHANGED)

            # Load images from disk
            try:
                img_name = path.join(getcwd(), 'images', urlify(scenery_title) + '.png')
                img_data = cv2.imread(img_name, cv2.IMREAD_UNCHANGED)
                if img_data is None:
                    self.sceneries[key]["path"] = None
                else:
                    self.sceneries[key]["path"] = img_name
            except Exception as e:
                print(e)

        return

    def get_video(self):
        return path.join(getcwd(), 'videos', self.story_name + '.mp4')

    def get_audio(self, tts_engine: str):
        return path.join(getcwd(), 'audios', self.story_name + '.mp3')
    
    def get_sceneries(self):
        self.sceneries = mock_sceneries


