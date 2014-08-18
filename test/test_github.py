from nose.tools import assert_equals, assert_raises
from mock import patch, MagicMock

import requests

from blackbelt.handle_github import (
    get_remote_repo_info,
    get_pr_info,
    verify_merge
)


class TestGithubRepoParsing(object):

    github_repo = 'git@github.com:apiaryio/apiary-test.git'

    def setUp(self):
        self.parsed = get_remote_repo_info(self.github_repo)

    def test_repo_owner(self):
        assert_equals('apiaryio', self.parsed['owner'])

    def test_repo_name(self):
        assert_equals('apiary-test', self.parsed['name'])


class TestGithubPullRequestParsing(object):

    github_pr = 'https://github.com/apiaryio/apiary-test/pull/123'

    def setUp(self):
        self.parsed = get_pr_info(self.github_pr)

    def test_repo_owner(self):
        assert_equals('apiaryio', self.parsed['owner'])

    def test_repo_name(self):
        assert_equals('apiary-test', self.parsed['name'])

    def test_pr_number(self):
        assert_equals('123', self.parsed['number'])

    def test_files_link(self):
        parsed = get_pr_info(self.github_pr + '/files')
        assert_equals('123', parsed['number'])


class TestMergeVerificationRetries(object):
    pr_info = {
        'owner': 'apiaryio',
        'name': 'apiary-test',
        'number': '666'
    }

    headers = {}

    @patch.object(requests, 'get')
    def test_timeout(self, get_method):
        get_method.return_value = fake_response = MagicMock()
        fake_response.status_code = 404

        assert_raises(ValueError, lambda: verify_merge(
            self.pr_info,
            self.headers,
            max_waiting_time=0.01,
            retry_time=0.001
        ))
