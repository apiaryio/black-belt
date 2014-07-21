from nose.tools import assert_equals

from blackbelt.handle_github import get_remote_repo_info

class TestGithubParsing(object):

	github_repo = 'git@github.com:apiaryio/apiary.git'

	def setUp(self):
		self.parsed = get_remote_repo_info(self.github_repo)

	def test_repo_owner(self):
		assert_equals('apiaryio', self.parsed['owner'])

	def test_repo_name(self):
		assert_equals('apiary', self.parsed['name'])
