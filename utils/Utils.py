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
        
        return response
    except requests.exceptions.RequestException as e:
        raise CustomException("API request failed") from e
    
def usage(exit_code: int) -> None:
    print("Usage: app.py [OPTIONS]")
    print("Options:")
    print("\t-h, --help\t\t\t\tPrint this help message\n\n")
    print("\t- f, --help\t\t\t\tPublish to Facebook")
    print("\t- g, --help\t\t\t\tPublish to Instagram")
    print("\t-i, --image\t\t\t\tNumber of images to generate")
    print("\t-t, --help\t\t\t\tPublish to Twitter (i.e. x.com)")
    print("\t-u, --url\t\t\t\tUrl to get story from")
    print("\t-y, --help\t\t\t\tPublish to YouTube")
    exit(exit_code)

