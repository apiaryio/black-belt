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
        branch_name = 'prefix/branch-name'
        if (version_info[0] == 3):
            check_output_mock.return_value = bytes(branch_name, 'utf-8')
        else:
            check_output_mock.return_value = str(branch_name)

        assert_equal(branch_name, get_current_branch())

    @patch('subprocess.check_output')
    def test_branch_name_parsing_with_trailing_whitespace(self, check_output_mock):
        branch_name = 'prefix/branch-name'
        if (version_info[0] == 3):
            check_output_mock.return_value = bytes(branch_name+'\n', 'utf-8')
        else:
            check_output_mock.return_value = str(branch_name+'\n')

        assert_equal(branch_name, get_current_branch())
