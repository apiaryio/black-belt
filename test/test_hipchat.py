from nose.plugins.skip import SkipTest

import os

from blackbelt.apis.hipchat import HipChat

"""
Integration exploratory playground for CircleCI.
Don't really treat it as a test, but it may still be useful for you.
"""


class TestBuildInfoRetrieval(object):

    def setUp(self):
        try:
            self.client = HipChat()
        except ValueError:
            raise SkipTest()

        if os.environ.get('FORCE_DISCOVERY') != '1':
            raise SkipTest()

    def test_posting_message(self):
        self.client.post_message("Testing HipChat Messages in Black Belt Exploratory Test Suite")
