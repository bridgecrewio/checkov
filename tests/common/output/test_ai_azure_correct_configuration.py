from textwrap import dedent

from checkov.common.output.ai import OpenAi 

import os
import unittest

class TestOpenAi_CorrectConfig(unittest.TestCase):
    @unittest.mock.patch.dict(os.environ, {'CKV_AZURE_OPENAI_API_ENDPOINT': "https://eastus.api.cognitive.microsoft.com/", "CKV_AZURE_OPENAI_API_VERSION": "2023-05-15", "CKV_AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4"})
    def setUp(self):
        self.openai = OpenAi(api_key='not_a_real_key', api_type='azure')
        print(os.environ)

    def tearDown(self):
        self.openai = None

    def test_azure_openai_type_is_set_correctly(self):
        assert self.openai._api_type == 'azure'

    def test_azure_openai_correct_configuration(self):
        assert self.openai._should_run == True