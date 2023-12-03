import json
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
        print("Called {url} ".format(url=url))
        response.raise_for_status()
        print(response.json())
        # TODO: If response is 200 but there is an error in the response, raise exception
        return response
    except requests.exceptions.RequestException as e:
        raise CustomException("API request failed") from e
