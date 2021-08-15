import requests


def create_request(method, params):
    result = requests.get(f'https://api.vk.com/method/{method}', params=params)
    return result.json()
