from nose.tools import assert_equals, assert_raises

from blackbelt.handle_trello import infer_branch_name

class TestInferringBranch(object):

    def test_simple_url(self):
        assert_equals('bb-t-next', infer_branch_name('https://trello.com/c/7b4Z3V8o/1803-bb-t-next'))
