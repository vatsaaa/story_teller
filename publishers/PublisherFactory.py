from os import getenv
from typing import List

from exceptions import PublishingException, ConfigurationException
from publishers.IPublisher import PublisherType
from publishers.TwitterPublisher import TwitterPublisher
from publishers.InstagramPublisher import InstagramPublisher
from publishers.ThreadsPublisher import ThreadsPublisher
from publishers.FacebookPublisher import FacebookPublisher
from publishers.YoutubePublisher import YoutubePublisher

class PublisherFactory:
    @staticmethod
    def create_publisher(publisher_type: PublisherType, **kwargs):
        if publisher_type == PublisherType.TWITTER:
            credentials = kwargs.get('credentials', None)
            if not credentials:
                raise ConfigurationException(
                    "credentials are required for TwitterPublisher",
                    config_key="credentials",
                    details={"platform": "Twitter"}
                )
            return TwitterPublisher(credentials=credentials)
        elif publisher_type == PublisherType.INSTAGRAM:
            credentials = kwargs.get('credentials', None)
            if not credentials:
                raise ConfigurationException(
                    "credentials are required for InstagramPublisher",
                    config_key="credentials",
                    details={"platform": "Instagram"}
                )
            return InstagramPublisher(credentials=credentials)
        elif publisher_type == PublisherType.THREADS:
            credentials = kwargs.get('credentials', None)
            if not credentials:
                raise ConfigurationException(
                    "credentials are required for ThreadsPublisher",
                    config_key="credentials",
                    details={"platform": "Threads"}
                )
            return ThreadsPublisher(credentials=credentials)
        elif publisher_type == PublisherType.FACEBOOK:
            page_id = kwargs.get('page_id', None)
            if not page_id:
                raise ConfigurationException(
                    "page_id is required for FacebookPublisher",
                    config_key="page_id",
                    details={"platform": "Facebook"}
                )
            return FacebookPublisher(page_id=page_id)
        elif publisher_type == PublisherType.YOUTUBE:
            credentials = kwargs.get('credentials', None)
            if not credentials:
                raise ConfigurationException(
                    "credentials are required for YoutubePublisher",
                    config_key="credentials",
                    details={"platform": "YouTube"}
                )
            return YoutubePublisher(credentials=credentials)
        else:
            raise PublishingException(
                f"Invalid publisher type: {publisher_type}",
                details={"provided_type": str(publisher_type), "valid_types": list(PublisherType)}
            )