from nose.tools import assert_equal, assert_raises
from mock import patch
from sys import version_info
from blackbelt.git import get_remote_repo_info, get_current_branch


class TestGithubRepoGitAddressParsing(object):

    github_repo = 'git@github.com:apiaryio/apiary-test.git'

    def setUp(self):
        self.parsed = get_remote_repo_info(self.github_repo)

    def test_repo_owner(self):
        assert_equal('apiaryio', self.parsed['owner'])

    def test_repo_name(self):
        assert_equal('apiary-test', self.parsed['name'])


class TestGithubRepoHttpsAddressParsing(object):

    github_repo = 'https://github.com/apiaryio/apiary-test.git'

    def setUp(self):
        self.parsed = get_remote_repo_info(self.github_repo)

    def test_repo_owner(self):
        assert_equal('apiaryio', self.parsed['owner'])

    def test_repo_name(self):
        assert_equal('apiary-test', self.parsed['name'])


class TestGitBranchOutput(object):

    @patch('subprocess.check_output')
    def test_branch_name_parsing(self, check_output_mock):
        check_output_mock.return_value = b'prefix/branch-name\n'
        assert_equal('prefix/branch-name', get_current_branch())
