from typing import List

from IPublisher import IPublisher, Publishers
from FacebookPublisher import FacebookPublisher
from InstagramPublisher import InstagramPublisher
from TwitterPublisher import TwitterPublisher
from YoutubePublisher import YoutubePublisher

class PublisherFactory:
    @staticmethod
    def create_publisher(publisher_type: List[Publishers]):
        if publisher_type == Publishers.FACEBOOK:
            return FacebookPublisher()
        elif publisher_type == Publishers.INSTAGRAM:
            return InstagramPublisher()
        elif publisher_type == Publishers.TWITTER:
            return TwitterPublisher()
        elif publisher_type == Publishers.YOUTUBE:
            return YoutubePublisher()
        else:
            raise ValueError("Invalid publisher type")
