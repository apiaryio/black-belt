from nose.tools import assert_equals, assert_raises
from mock import patch, MagicMock

import requests

from blackbelt.handle_github import (
    get_pr_info,
    verify_merge,
    get_pr_ticket_id
)


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


    def test_trello_id_extracted(self):
        link = get_pr_ticket_id("""
        # This is edited and a long pull requests
        Hoever, I'd like to warn you...

        Pull request for [Naming fixes](https://trello.com/c/yx2SNE3J/1910-naming-fixes).
        """)

        assert_equals('yx2SNE3J', link)

    def test_error_on_bad_phrase(self):
        assert_raises(ValueError, lambda:get_pr_ticket_id("""
        Related to [naming fixes](https://trello.com/c/yx2SNE3J/1910-naming-fixes)
        """))



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
