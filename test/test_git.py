from nose.tools import assert_equal, assert_raises

from blackbelt.git import get_remote_repo_info


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
