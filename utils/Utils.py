import getopt, json
import re, requests

from CustomException import CustomException

def urlify(s: str):

    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '-', s)

    return s

def make_api_request(url, data, headers):
    try:
        response = requests.post(url=url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise CustomException("API request failed") from e
