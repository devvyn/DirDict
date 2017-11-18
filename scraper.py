import requests


def fetch_from_web(key_path):
    # @todo extract web specific actions out of this class
    # fetch from URL and write to file if not
    response = requests.get(key_path)
    response.raise_for_status()
    return response
