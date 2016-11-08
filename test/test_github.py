from nose.tools import assert_equals, assert_raises
from mock import patch, MagicMock
import requests
import json

from blackbelt.handle_github import (
    get_pr_info,
    verify_merge,
    get_pr_ticket_id,
    verify_pr_state,
    verify_pr_required_checks,
    verify_branch_required_checks,
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
        assert_raises(ValueError, lambda: get_pr_ticket_id("""
        Related to [naming fixes](https://trello.com/c/yx2SNE3J/1910-naming-fixes)
        """))

class TestMergeVerificationRetries(object):
    pr_url = 'https://github.com/apiaryio/apiary-test/pull/123'

    headers = {}

    @patch.object(requests, 'get')
    def test_timeout(self, get_method):
        get_method.return_value = fake_response = MagicMock()
        fake_response.status_code = 404

        assert_raises(ValueError, lambda: verify_merge(
            self.pr_url,
            self.headers,
            max_waiting_time=0.01,
            retry_time=0.001
        ))

class TestStatusVerifications(object):
    pr_url = 'https://github.com/apiaryio/apiary-test/pull/123'
    branch_name = 'user/local-branch'

    def setUp(self):
        with open('./test/gh-mock-response/pr-details-success.json') as json_data:
            self.pr_details_open = json.load(json_data)
        with open('./test/gh-mock-response/pr-details-failure.json') as json_data:
            self.pr_details_closed = json.load(json_data)

    def init_mock(self, json_data_file):
        fake_response = MagicMock()
        fake_response.status_code = 200
        with open(json_data_file) as json_data:
            response_data = json.load(json_data)
            fake_response.json.return_value = response_data
        return fake_response

    @patch.object(requests, 'get')
    def test_verify_branch_required_checks_success(self, get_method):
        get_method.return_value = self.init_mock(json_data_file='./test/gh-mock-response/ref-status-success.json')
        message = verify_branch_required_checks(self.branch_name)
        assert_equals('Branch required checks (2): success', message)

    @patch.object(requests, 'get')
    def test_verify_branch_required_checks_failure(self, get_method):
        get_method.return_value = self.init_mock(json_data_file='./test/gh-mock-response/ref-status-failure.json')
        assert_raises(ValueError, lambda: verify_branch_required_checks(self.branch_name))

    @patch.object(requests, 'get')
    def test_verify_pr_status_success(self, get_method):
        get_method.return_value = self.init_mock(json_data_file='./test/gh-mock-response/pr-details-success.json')
        message = verify_pr_state(self.pr_details_open)
        assert_equals('PR state: open', message)

    @patch.object(requests, 'get')
    def test_verify_pr_status_failure(self, get_method):
        get_method.return_value = self.init_mock(json_data_file='./test/gh-mock-response/pr-details-failure.json')
        assert_raises(ValueError, lambda: verify_pr_state(self.pr_details_closed))

    @patch.object(requests, 'get')
    def test_verify_pr_required_checks_success(self, get_method):
        get_method.return_value = self.init_mock(json_data_file='./test/gh-mock-response/ref-status-success.json')
        message = verify_pr_required_checks(self.pr_details_open)
        assert_equals('PR required checks (2): success', message)

    @patch.object(requests, 'get')
    def test_verify_pr_required_checks_failure(self, get_method):
        get_method.return_value = self.init_mock(json_data_file='./test/gh-mock-response/ref-status-failure.json')
        assert_raises(ValueError, lambda: verify_pr_required_checks(self.pr_details_closed))


class TestGitHubPullRequestResponseData(object):

    def test_github_details_response_data(self):
        with open('./test/gh-mock-response/pr-details-success.json') as json_data:
            pr_details = json.load(json_data)

        assert_equals('octocat/Hello-World', pr_details['base']['repo']['full_name'])
        assert_equals('new-topic', pr_details['head']['ref'])
        assert_equals('git:github.com/octocat/Hello-World.git', pr_details['base']['repo']['git_url'])
        assert_equals('git@github.com:octocat/Hello-World.git', pr_details['base']['repo']['ssh_url'])
        assert_equals('https://github.com/octocat/Hello-World.git', pr_details['base']['repo']['clone_url'])
        assert_equals('6dcb09b5b57875f334f61aebed695e2e4193db5e', pr_details['head']['sha'])
        assert_equals('new-topic', pr_details['head']['ref'])
        assert_equals(1347, pr_details['number'])
        assert_equals('new-feature', pr_details['title'])
        assert_equals(10, pr_details['comments'])
        assert_equals(3, pr_details['commits'])
        assert_equals('octocat', pr_details['base']['repo']['owner']['login'])
        assert_equals('Hello-World', pr_details['base']['repo']['name'])
        assert_equals('Please pull these awesome changes', pr_details['body'])
        assert_equals('https://github.com/octocat/Hello-World/pull/1347', pr_details['html_url'])
        assert_equals('open', pr_details['state'])
