import unittest

from checkov.common.models.enums import CheckResult
from checkov.common.output.secrets_record import SecretsRecord
from checkov.secrets.runner import Runner, ENTROPY_CHECK_IDS, GENERIC_PRIVATE_KEY_CHECK_IDS


class TestPrioritiseSecrets(unittest.TestCase):
    def setUp(self):
        self.secret_records = {
            'key1': SecretsRecord(check_id='CKV_SECRET_6', check_name='foo',
                                  check_result={"result": CheckResult.FAILED}, code_block=[(1, 'baz')],
                                  file_path='qux', file_line_range=[1, 2], resource='resource', evaluations=None,
                                  check_class='CheckClass', file_abs_path='abs_path'),
            'key2': SecretsRecord(check_id='CKV_SECRET_10', check_name='foo',
                                  check_result={"result": CheckResult.FAILED},
                                  code_block=[(1, 'baz')], file_path='qux', file_line_range=[1, 2], resource='resource',
                                  evaluations=None, check_class='CheckClass', file_abs_path='abs_path'),
            'key3': SecretsRecord(check_id='CKV_SECRET_18', check_name='foo',
                                  check_result={"result": CheckResult.FAILED}, code_block=[(1, 'baz')],
                                  file_path='qux', file_line_range=[1, 2], resource='resource', evaluations=None,
                                  check_class='CheckClass', file_abs_path='abs_path'),
        }
        self.ENTROPY_CHECK_IDS = ENTROPY_CHECK_IDS
        self.GENERIC_PRIVATE_KEY_CHECK_IDS = GENERIC_PRIVATE_KEY_CHECK_IDS

    def test_entropy_check_id_removed(self):
        result = Runner._prioritise_secrets(self.secret_records, 'key1', 'CKV_SECRET_18')
        self.assertTrue(result)
        self.assertNotIn('key1', self.secret_records)

    def test_generic_private_key_check_id_removed(self):
        result = Runner._prioritise_secrets(self.secret_records, 'key2', 'CKV_SECRET_18')
        self.assertTrue(result)
        self.assertNotIn('key2', self.secret_records)

    def test_no_removal_entropy_check_id(self):
        result = Runner._prioritise_secrets(self.secret_records, 'key1', 'CKV_SECRET_6')
        self.assertFalse(result)
        self.assertIn('key1', self.secret_records)

    def test_no_removal_generic_private_key_check_id(self):
        result = Runner._prioritise_secrets(self.secret_records, 'key2', 'CKV_SECRET_10')
        self.assertFalse(result)
        self.assertIn('key2', self.secret_records)

    def test_no_removal_other_check_id(self):
        result = Runner._prioritise_secrets(self.secret_records, 'key3', 'CKV_SECRET_1000')
        self.assertFalse(result)
        self.assertIn('key3', self.secret_records)


if __name__ == '__main__':
    unittest.main()
