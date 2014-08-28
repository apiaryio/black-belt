from datetime import datetime, timedelta
import json
from time import sleep
import sys
from urllib import quote

import requests

from .config import config


class Client(object):
    endpoint = 'https://api.hipchat.com/v2'

    def __init__(self, token=None):
        if not token:
            token = config['hipchat']['access_token']

        if not token:
            raise ValueError("Can't do things with CircleCI without access token. Run bb init.")

        self.token = token

    def get_url(self, url, **kwargs):
        kwargs['token'] = self.token

        url = self.endpoint + url + '?auth_token={token}'
        return url.format(**kwargs)

    def request(self, method, url, data=None):
        if data:
            data = json.dumps(data)
        res = getattr(requests, method)(url, data=data, headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        if not res.ok:
            raise ValueError("Request to URL %s failed" % url)

        if res.text:
            return res.json()

    def post_message(self, message, room='Engine Room'):
        url = self.get_url(
            '/room/{room}/notification',
            room=quote(room)
        )

        return self.request('post', url, data={
            'color': 'purple',
            'message': message,
            'message_format': 'text'
        })



def post_message(message):
    client = Client()
    client.post_message(message)
