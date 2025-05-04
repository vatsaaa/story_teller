import unittest
from unittest.mock import patch, Mock
from story.StoryMock import StoryMock
from publishers.IPublisher import IPublisher
from utils.mock.inputs import mock_sceneries, mock_text, mock_title
import os
from string import punctuation

class TestStoryMock(unittest.TestCase):

    def setUp(self):
        self.progargs = {'fb': True, 'ig': True, 'tw': True, 'yt': True}
        self.story_mock = StoryMock(self.progargs)

    def test_get_text(self):
        self.story_mock.get_text()
        self.assertEqual(self.story_mock.text, mock_text)
        expected_story_name = mock_title.get("Hindi").replace(" ", '').translate(str.maketrans('', '', punctuation))
        self.assertEqual(self.story_mock.story_name, expected_story_name)

    @patch('cv2.imread', return_value=None)
    def test_get_images_no_image(self, mock_imread):
        self.story_mock.get_images()
        for key in mock_sceneries:
            self.assertIsNone(self.story_mock.sceneries[key]["path"])

    @patch('cv2.imread', return_value='image_data')
    def test_get_images_with_image(self, mock_imread):
        with patch('os.getcwd', return_value='/mock/path'):
            self.story_mock.get_images()
            for key in mock_sceneries:
                self.assertTrue(self.story_mock.sceneries[key]["path"].endswith('.png'))

    def test_get_video(self):
        self.story_mock.story_name = 'test_story'
        video_path = self.story_mock.get_video()
        expected_path = os.path.join(os.getcwd(), 'videos', 'test_story.mp4')
        self.assertEqual(video_path, expected_path)

    def test_get_audio(self):
        self.story_mock.story_name = 'test_story'
        audio_path = self.story_mock.get_audio('test_engine')
        expected_path = os.path.join(os.getcwd(), 'audios', 'test_story.mp3')
        self.assertEqual(audio_path, expected_path)

    def test_publish(self):
        mock_publisher = Mock(spec=IPublisher)
        self.story_mock.publish([mock_publisher])
        mock_publisher.login.assert_called_once()
        mock_publisher.publish.assert_called_once()
        mock_publisher.logout.assert_called_once()

if __name__ == "__main__":
    unittest.main()