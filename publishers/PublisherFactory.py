from os import getenv
from typing import List

from publishers.IPublisher import PublisherType
from publishers.FacebookPublisher import FacebookPublisher
from publishers.InstagramPublisher import InstagramPublisher
from publishers.TwitterPublisher import TwitterPublisher
from publishers.YoutubePublisher import YoutubePublisher

class PublisherFactory:
    @staticmethod
    def create_publisher(publisher_type: PublisherType, **kwargs):
        if publisher_type == PublisherType.FACEBOOK:
            page_id = kwargs.get('page_id', None)
            if not page_id:
                raise ValueError("page_id is required for FacebookPublisher")
            return FacebookPublisher(page_id=page_id)
        elif publisher_type == PublisherType.INSTAGRAM:
            credentials = kwargs.get('credentials', None)
            if not credentials:
                raise ValueError("credentials are required for InstagramPublisher")
            return InstagramPublisher(credentials=credentials)
        elif publisher_type == PublisherType.TWITTER:
            credentials = kwargs.get('credentials', None)
            if not credentials:
                raise ValueError("credentials are required for TwitterPublisher")
            return TwitterPublisher(credentials=credentials)
        elif publisher_type == PublisherType.YOUTUBE:
            credentials = kwargs.get('credentials', None)
            if not credentials:
                raise ValueError("credentials are required for YoutubePublisher")
            return YoutubePublisher(credentials=credentials)
        else:
            raise ValueError("Invalid publisher type {pt}".format(pt=publisher_type))
