import json
import re
import requests
from urllib import quote, quote_plus

from blackbelt.config import config
from blackbelt.errors import ConfigurationError

class Papertrail(object):
    """
    I represent a authenticated connection to Papertrail API.
    Dispatch all requests to it through my methods.

    My actions are named from the BlackBelt's POW; I don't aim to be a full,
    usable client.
    """

    URL_PREFIX = "https://papertrailapp.com/api/v1"

    def __init__(self, access_token=None):
        self._access_token = access_token
        if not self._access_token and config.get('papertrail') and config['papertrail'].get('access_token'):
            self._access_token = config['papertrail']['access_token']

    
    ### Infra
    def do_request(self, url, method='get', data=None):
        if not self._access_token:
            raise ConfigurationError("Trying to talk to Papertrail without having access token")

        url = self.URL_PREFIX + url
        response = getattr(requests, method)(
            url,
            headers={
                'X-Papertrail-Token': self._access_token
            },
            data=data
        )
        # try:
        #     print response.text
        # except Exception:
        #     print 'Cannot print'
        response.raise_for_status()
        return json.loads(response.content)


    def get_search(self, search_id):
        pass