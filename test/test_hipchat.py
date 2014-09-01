from nose.tools import assert_equals, assert_raises
from nose.plugins.skip import SkipTest

import requests

from blackbelt.config import config

from blackbelt.hipchat import Client

"""
Integration exploratory playground for CircleCI.
Don't really treat it as a test, but it may still be useful for you.
"""


class TestBuildInfoRetrieval(object):

    def setUp(self):
        try:
            self.client = Client()
        except ValueError:
            raise SkipTest()

    def test_posting_message(self):
        self.client.post_message("Testing HipChat Messages in Black Belt Exploratory Test Suite")
