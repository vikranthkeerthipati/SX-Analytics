import requests

class Eventbrite:
    def __init__(self, config):
        self.api_url = 'https://www.eventbriteapi.com/v3'
        self.api_key = config['api_key']

    def request(self, endpoint):
        url=f'{self.api_url}{endpoint}'
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }

        return requests.get(url, headers=headers).json()
