import mock
from mock import patch
from nose.tools import assert_equals, assert_raises

import blackbelt
from blackbelt.messages import post_message
from blackbelt.deployment import deploy_production

# http://stackoverflow.com/questions/25692440/mocking-a-subprocess-call-in-python

deploy_production_patcher = mock.patch.object(
    blackbelt.messages, 'post_message',
    mock.Mock(wraps=post_message)
)

class TestDeployment(object):

  def setUp(self):
      self.mocked_deploy_production = deploy_production_patcher.start()

  def tearDown(self):
      deploy_production_patcher.stop()

  def test_deploy_production(self):
      deploy_production()
      assert_equals(mocked_deploy_production.call_args, '1')
