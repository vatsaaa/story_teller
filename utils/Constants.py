from enum import Enum
from os import getenv

TEXT_TO_IMAGE_URL = getenv('TEXT_TO_IMAGE_URL')

class SocialMedia(Enum):
    FACEBOOK = 1
    INSTAGRAM = 2
    TWITTER = 3
    YOUTUBE = 4
