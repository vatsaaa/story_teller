import unittest
from utils.Utils import batched, completion_with_backoff, chunked_tokens, make_api_request, num_tokens_from_string, urlify
from exceptions.CustomException import CustomException
from unittest.mock import patch, Mock
import requests

class TestUtils(unittest.TestCase):

    def test_batched(self):
        data = list(range(10))
        result = list(batched(data, 3))
        self.assertEqual(result, [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)])

        with self.assertRaises(ValueError):
            list(batched(data, 0))

    @patch('utils.Utils.OpenAI')
    def test_completion_with_backoff(self, MockOpenAI):
        mock_client = MockOpenAI()
        mock_client.chat.completions.create.return_value = {'response': 'success'}
        result = completion_with_backoff(mock_client, param='value')
        self.assertEqual(result, {'response': 'success'})

    def test_chunked_tokens(self):
        with patch('utils.Utils.tiktoken.get_encoding') as mock_encoding:
            mock_encoding.return_value.encode.return_value = list(range(10))
            result = list(chunked_tokens("test text", "test_encoding", 3))
            self.assertEqual(result, [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)])

    @patch('utils.Utils.requests.post')
    def test_make_api_request(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = make_api_request("http://example.com", {"data": "value"}, {"header": "value"})
        self.assertEqual(result.json(), {"key": "value"})

        mock_post.side_effect = requests.exceptions.RequestException("Error")
        with self.assertRaises(CustomException):
            make_api_request("http://example.com", {"data": "value"}, {"header": "value"})

    def test_num_tokens_from_string(self):
        with patch('utils.Utils.tiktoken.encoding_for_model') as mock_encoding:
            mock_encoding.return_value.encode.return_value = list(range(5))
            result = num_tokens_from_string("test text", "test_encoding")
            self.assertEqual(result, 5)

    def test_urlify(self):
        self.assertEqual(urlify("Hello World!"), "HelloWorld")
        self.assertEqual(urlify("Multiple   Spaces"), "MultipleSpaces")
        self.assertEqual(urlify("Special@#Characters"), "SpecialCharacters")

if __name__ == "__main__":
    unittest.main()