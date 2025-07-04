import itertools, json, re, requests, os
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import tiktoken

from exceptions import ConfigurationException, CustomException

'''
Note: This file contains utility functions that are used by other files in the project
Also, the functions are in alphabetical order of their names. Please keep it that way.
'''

MULTISPACE = r'[^\S\n]+' # Regex to match multiple spaces

def batched(iterable, n) -> iter:
    """Batch data into tuples of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while (batch := tuple(itertools.islice(it, n))):
        yield batch

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(client: OpenAI, **kwargs):
    return client.chat.completions.create(**kwargs)

def chunked_tokens(text, encoding_name, chunk_length):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    chunks_iterator = batched(tokens, chunk_length)
    yield from chunks_iterator

def make_api_request(url, data, headers=None, max_retries=3, current_retry=0):
    try:
        # Set 'key' as api_key in the data
        data['key'] = None  # Placeholder, will be updated after reading the API key

        # Read the API key file path from the environment variable
        api_key_file = os.getenv("STABLEDIFFUSION_API_KEY_FILE")
        if not api_key_file:
            raise ConfigurationException(
                "API key file path not set", 
                config_key="STABLEDIFFUSION_API_KEY_FILE"
            )

        # Determine the key to read based on the current retry number
        api_key_label = f"STABLEDIFFUSION_API_KEY_{current_retry + 1}"

        # Read the API key from the specified file
        try:
            with open(api_key_file, 'r') as file:
                keys = dict(line.strip().split('=', 1) for line in file if '=' in line)
                api_key = keys.get(api_key_label)
                if not api_key:
                    raise ConfigurationException(
                        f"API key '{api_key_label}' not found in the configuration file", 
                        config_key=api_key_label,
                        details={"file_path": api_key_file}
                    )
                data['key'] = api_key  # Update the data with the API key
        except FileNotFoundError:
            raise ConfigurationException(
                f"API key file not found", 
                config_key="STABLEDIFFUSION_API_KEY_FILE",
                details={"file_path": api_key_file}
            )
        except Exception as e:
            raise ConfigurationException(
                "Failed to read API key file", 
                config_key="STABLEDIFFUSION_API_KEY_FILE",
                details={"file_path": api_key_file, "error": str(e)}
            )

        response = requests.post(url=url, data=json.dumps(data), headers=headers)
        response.raise_for_status()

        # Check for specific error conditions
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("status") == "error" and re.search("limit exceeded", response_json.get("message", "")):
                if current_retry < max_retries:
                    print(f"Retrying with a new API key. Attempt {current_retry + 1} of {max_retries}.")
                    return make_api_request(url, data, headers, max_retries, current_retry + 1)
                else:
                    raise CustomException("Max retries reached for API request.")

        return response

    except requests.exceptions.RequestException as e:
        error_details = {
            "url": url,
            "status_code": response.status_code if 'response' in locals() else None,
            "response_text": response.text if 'response' in locals() else None,
            "error": str(e)
        }
        raise CustomException("API request failed", details=error_details)

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def urlify(s: str) -> str:
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)

    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '', s)

    return s

def ascii_safe_filename(s: str) -> str:
    """Create an ASCII-safe filename from any string, including non-ASCII characters."""
    import unicodedata
    
    # First try to normalize and convert to ASCII
    try:
        # Normalize unicode characters
        s = unicodedata.normalize('NFD', s)
        # Remove non-ASCII characters
        s = s.encode('ascii', 'ignore').decode('ascii')
        # Remove punctuation and special characters, keep only alphanumeric
        s = re.sub(r'[^a-zA-Z0-9\s]', '', s)
        # Replace spaces with underscores and remove extra whitespace
        s = re.sub(r'\s+', '_', s.strip())
        # If the result is empty or too short, use a fallback
        if len(s) < 2:
            return "story_file"
        return s
    except Exception:
        # Fallback to a generic name
        return "story_file"

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
