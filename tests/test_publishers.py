import unittest
from unittest.mock import Mock, patch
from publishers.FacebookPublisher import FacebookPublisher
from publishers.InstagramPublisher import InstagramPublisher
from publishers.TwitterPublisher import TwitterPublisher
from publishers.YoutubePublisher import YoutubePublisher
from publishers.PublisherFactory import PublisherFactory
from publishers.IPublisher import IPublisher, PublisherType

class TestPublishers(unittest.TestCase):

    @patch.dict('os.environ', {'FBIG_BASE_URL': 'https://graph.facebook.com/', 'FBIG_BASE_VER': 'v12.0/'})
    def test_facebook_publisher(self):
        fb_publisher = FacebookPublisher(page_id="test_page_id")
        fb_publisher.login = Mock()
        fb_publisher.publish = Mock()
        fb_publisher.logout = Mock()

        fb_publisher.login()
        fb_publisher.publish("Test content")
        fb_publisher.logout()

        fb_publisher.login.assert_called_once()
        fb_publisher.publish.assert_called_once_with("Test content")
        fb_publisher.logout.assert_called_once()

    def test_instagram_publisher(self):
        ig_publisher = InstagramPublisher(credentials={"username": "test_user", "password": "test_pass"})
        ig_publisher.login = Mock()
        ig_publisher.publish = Mock()
        ig_publisher.logout = Mock()

        ig_publisher.login()
        ig_publisher.publish("Test content")
        ig_publisher.logout()

        ig_publisher.login.assert_called_once()
        ig_publisher.publish.assert_called_once_with("Test content")
        ig_publisher.logout.assert_called_once()

    def test_twitter_publisher(self):
        tw_publisher = TwitterPublisher(credentials={"username": "test_user", "password": "test_pass"})
        tw_publisher.login = Mock()
        tw_publisher.publish = Mock()
        tw_publisher.logout = Mock()

        tw_publisher.login()
        tw_publisher.publish("Test content")
        tw_publisher.logout()

        tw_publisher.login.assert_called_once()
        tw_publisher.publish.assert_called_once_with("Test content")
        tw_publisher.logout.assert_called_once()

    @patch('googleapiclient.discovery.build', return_value=Mock(videos=Mock(return_value=Mock(insert=Mock(return_value=Mock(next_chunk=Mock(return_value=(None, {'id': 'test_video_id'}))))))))
    @patch('google_auth_oauthlib.flow.InstalledAppFlow.run_local_server', return_value=Mock())
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"installed": {"client_id": "test_client_id", "project_id": "test_project", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_secret": "test_client_secret"}}')
    @patch('os.path.exists', return_value=True)
    def test_youtube_publisher(self, mock_exists, mock_open, mock_run_local_server, mock_build):
        yt_publisher = YoutubePublisher(credentials={"username": "test_user", "password": "test_pass"})
        yt_publisher.login = Mock()
        yt_publisher.publish = Mock()
        yt_publisher.logout = Mock()

        yt_publisher.login()
        yt_publisher.publish("Test content")
        yt_publisher.logout()

        yt_publisher.login.assert_called_once()
        yt_publisher.publish.assert_called_once_with("Test content")
        yt_publisher.logout.assert_called_once()

    def test_publisher_factory(self):
        factory = PublisherFactory()
        with patch.dict('os.environ', {'FBIG_BASE_URL': 'https://graph.facebook.com/', 'FBIG_BASE_VER': 'v12.0/'}):
            fb_publisher = factory.create_publisher(PublisherType.FACEBOOK, page_id="test_page_id")
            self.assertIsInstance(fb_publisher, FacebookPublisher)

        ig_publisher = factory.create_publisher(PublisherType.INSTAGRAM, credentials={"username": "test_user", "password": "test_pass"})
        self.assertIsInstance(ig_publisher, InstagramPublisher)

        tw_publisher = factory.create_publisher(PublisherType.TWITTER, credentials={"username": "test_user", "password": "test_pass"})
        self.assertIsInstance(tw_publisher, TwitterPublisher)

        with patch('googleapiclient.discovery.build', return_value=Mock(videos=Mock(return_value=Mock(insert=Mock(return_value=Mock(next_chunk=Mock(return_value=(None, {'id': 'test_video_id'})))))))):
            with patch('google_auth_oauthlib.flow.InstalledAppFlow.run_local_server', return_value=Mock()):
                with patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"installed": {"client_id": "test_client_id", "project_id": "test_project", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_secret": "test_client_secret"}}'):
                    yt_publisher = factory.create_publisher(PublisherType.YOUTUBE, credentials={"username": "test_user", "password": "test_pass"})
                    self.assertIsInstance(yt_publisher, YoutubePublisher)

    def test_ipublisher_interface(self):
        with self.assertRaises(TypeError):
            IPublisher()

if __name__ == "__main__":
    unittest.main()