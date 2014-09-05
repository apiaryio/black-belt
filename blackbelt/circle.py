from datetime import datetime, timedelta
from time import sleep
import sys

import requests

from .config import config

MAX_WAIT_MINUTES = 120


class Client(object):

    def __init__(self, token=None):
        if not token:
            token = config['circleci']['access_token']

        if not token:
            raise ValueError("Can't do things with CircleCI without access token. Run bb init.")

        self.token = token

        self.default_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        self.endpoint = 'https://circleci.com/api/v1'

    def get_url(self, url, **kwargs):
        kwargs['token'] = self.token

        url = self.endpoint + url + '?circle-token={token}'
        return url.format(**kwargs)

    def request(self, method, url, data=None):
        res = getattr(requests, method)(url, headers=self.default_headers)
        if not res.ok:
            raise ValueError("Request to URL %s failed" % url)

        return res.json()

    def get_builds(self, username, project):
        url = self.get_url(
            '/project/{username}/{project}',
            username=username,
            project=project
        )

        return self.request('get', url)

    def get_build(self, username, project, number):
        url = self.get_url(
            '/project/{username}/{project}/{number}',
            username=username,
            project=project,
            number=number
        )

        return self.request('get', url)


def wait_for_tests(sha, owner, name, retry_interval=30):
    client = Client()
    builds = client.get_builds(username=owner, project=name)
    build = None

    for b in builds:
        if b['vcs_revision'] == sha:
            build = b
            break

    if not build:
        raise ValueError("Cannot find build for our revision. TODO: Implement retry")

    start_time = datetime.now()

    while not build.get('stop_time'):
        if datetime.now() < start_time + timedelta(minutes=MAX_WAIT_MINUTES):
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(retry_interval)
        else:
            raise ValueError("Build haven't finished in time")

        build = client.get_build(
            username=owner,
            project=name,
            number=build['build_num']
        )

    # guards to prevent false positives
    assert build['build_time_millis'] > 0

    if build['status'] not in ['success', 'fixed']:
        raise ValueError("Build failed with status %(status)s" % build)

    return build
