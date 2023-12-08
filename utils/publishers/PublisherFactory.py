from os import getenv
from typing import List

from utils.publishers.IPublisher import PublisherType
from utils.publishers.FacebookPublisher import FacebookPublisher
from utils.publishers.InstagramPublisher import InstagramPublisher
from utils.publishers.TwitterPublisher import TwitterPublisher
from utils.publishers.YoutubePublisher import YoutubePublisher

class PublisherFactory:
    @staticmethod
    def create_publisher(publisher_type: List[PublisherType]):
        credentials = dict()

        if publisher_type == PublisherType.FACEBOOK:
            credentials['username'] = getenv('FB_USER_NAME', None)
            credentials['password'] = getenv('FB_USER_PASS', None)
            credentials['api_ept'] = getenv('FB_API_EPT', None)
            credentials['api_key'] = getenv('FB_API_KEY', None)
            credentials['consumer_key'] = getenv('FB_CONSUMER_KEY', None)
            credentials['consumer_secret'] = getenv('FB_CONSUMER_SECRET', None)
            credentials['access_token'] = getenv('FB_ACCESS_TOKEN', None)

            return FacebookPublisher(credentials=credentials)
        elif publisher_type == PublisherType.INSTAGRAM:
            credentials['username'] = getenv('IG_USER_NAME', None)
            credentials['password'] = getenv('IG_USER_PASS', None)
            credentials['api_ept'] = getenv('IG_API_EPT', None)
            credentials['api_key'] = getenv('IG_API_KEY', None)
            credentials['consumer_key'] = getenv('IG_CONSUMER_KEY', None)
            credentials['consumer_secret'] = getenv('IG_CONSUMER_SECRET', None)
            credentials['access_token'] = getenv('IG_ACCESS_TOKEN', None)
            credentials['access_token_secret'] = getenv('IG_ACCESS_TOKEN_SECRET', None)
            
            return InstagramPublisher(credentials=credentials)
        elif publisher_type == PublisherType.TWITTER:
            credentials['username'] = getenv('TW_USER_NAME', None)
            credentials['password'] = getenv('TW_USER_PASS', None)
            credentials['api_ept'] = getenv('TW_API_EPT', None)
            credentials['api_key'] = getenv('TW_API_KEY', None)
            credentials['consumer_key'] = getenv('TW_CONSUMER_KEY', None)
            credentials['consumer_secret'] = getenv('TW_CONSUMER_SECRET', None)
            credentials['access_token'] = getenv('TW_ACCESS_TOKEN', None)
            credentials['access_token_secret'] = getenv('TW_ACCESS_TOKEN_SECRET', None)

            return TwitterPublisher(credentials=credentials)
        elif publisher_type == PublisherType.YOUTUBE:
            credentials['username'] = getenv('YT_USER_NAME', None)
            credentials['password'] = getenv('YT_USER_PASS', None)
            credentials['api_ept'] = getenv('YT_API_EPT', None)
            credentials['api_key'] = getenv('YT_API_KEY', None)
            credentials['consumer_key'] = getenv('YT_CONSUMER_KEY', None)
            credentials['consumer_secret'] = getenv('YT_CONSUMER_SECRET', None)
            credentials['access_token'] = getenv('YT_ACCESS_TOKEN', None)
            credentials['access_token_secret'] = getenv('YT_ACCESS_TOKEN_SECRET', None)

            return YoutubePublisher(credentials=credentials)
        else:
            raise ValueError("Invalid publisher type {pt}".format(pt=publisher_type))
