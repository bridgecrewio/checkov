from textwrap import dedent

from checkov.common.output.ai import OpenAi 

import os
import unittest

class TestOpenAi_MissingConfig(unittest.TestCase):
    @unittest.mock.patch.dict(os.environ, {}) 
    def setUp(self):
        # Set up any necessary test-specific state
        self.openai = OpenAi(api_key='not_a_real_key', api_type='azure')

    def tearDown(self):
        # Clean up any resources or state after each test
        self.openai = None

    def test_azure_openai_missing_configuration(self):
        assert self.openai._should_run == False
