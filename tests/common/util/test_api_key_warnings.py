"""
Unit tests for API key warning utilities
"""
import unittest
from unittest.mock import Mock, patch
from checkov.common.util.api_key_warnings import (
    check_for_api_key_usage_warnings,
    check_for_severity_filtering_without_api_key,
    warn_about_missing_metadata_without_api_key,
    SEVERITY_CODES
)


class MockConfig:
    """Mock configuration object for testing"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestApiKeyWarnings(unittest.TestCase):
    
    @patch('checkov.common.util.api_key_warnings.logger')
    def test_severity_filtering_with_check_parameter(self, mock_logger):
        """Test warning when using --check with severity codes"""
        config = MockConfig(check=['HIGH', 'CKV_AWS_1'], skip_check=None, hard_fail_on=None, soft_fail_on=None)
        result = check_for_severity_filtering_without_api_key(config, has_api_key=False)
        
        self.assertTrue(result)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn('--check HIGH', warning_message)
        self.assertIn('estimated defaults', warning_message)
    
    @patch('checkov.common.util.api_key_warnings.logger')
    def test_severity_filtering_with_skip_check_parameter(self, mock_logger):
        """Test warning when using --skip-check with severity codes"""
        config = MockConfig(check=None, skip_check=['LOW', 'MEDIUM'], hard_fail_on=None, soft_fail_on=None)
        result = check_for_severity_filtering_without_api_key(config, has_api_key=False)
        
        self.assertTrue(result)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn('--skip-check LOW', warning_message)
        self.assertIn('--skip-check MEDIUM', warning_message)
    
    @patch('checkov.common.util.api_key_warnings.logger')
    def test_severity_filtering_with_hard_fail_on(self, mock_logger):
        """Test warning when using --hard-fail-on with severity codes"""
        config = MockConfig(check=None, skip_check=None, hard_fail_on=['CRITICAL'], soft_fail_on=None)
        result = check_for_severity_filtering_without_api_key(config, has_api_key=False)
        
        self.assertTrue(result)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn('--hard-fail-on CRITICAL', warning_message)
    
    @patch('checkov.common.util.api_key_warnings.logger')
    def test_no_warning_with_api_key(self, mock_logger):
        """Test no warning when API key is present"""
        config = MockConfig(check=['HIGH'], skip_check=None, hard_fail_on=None, soft_fail_on=None)
        result = check_for_severity_filtering_without_api_key(config, has_api_key=True)
        
        self.assertFalse(result)
        mock_logger.warning.assert_not_called()
    
    @patch('checkov.common.util.api_key_warnings.logger')
    def test_no_warning_without_severity_codes(self, mock_logger):
        """Test no warning when using check IDs without severity codes"""
        config = MockConfig(check=['CKV_AWS_1', 'CKV_AWS_2'], skip_check=None, hard_fail_on=None, soft_fail_on=None)
        result = check_for_severity_filtering_without_api_key(config, has_api_key=False)
        
        self.assertFalse(result)
        mock_logger.warning.assert_not_called()
    
    @patch('checkov.common.util.api_key_warnings.logger')
    def test_multiple_severity_parameters(self, mock_logger):
        """Test warning with multiple severity parameters"""
        config = MockConfig(
            check=['HIGH'],
            skip_check=['LOW'],
            hard_fail_on=['CRITICAL'],
            soft_fail_on=['MEDIUM']
        )
        result = check_for_severity_filtering_without_api_key(config, has_api_key=False)
        
        self.assertTrue(result)
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn('--check HIGH', warning_message)
        self.assertIn('--skip-check LOW', warning_message)
        self.assertIn('--hard-fail-on CRITICAL', warning_message)
        self.assertIn('--soft-fail-on MEDIUM', warning_message)
    
    @patch('checkov.common.util.api_key_warnings.logger')
    def test_policy_metadata_filter_warning(self, mock_logger):
        """Test warning when using --policy-metadata-filter without API key"""
        config = MockConfig(
            policy_metadata_filter='policy.label=test',
            check=None,
            skip_check=None,
            hard_fail_on=None,
            soft_fail_on=None
        )
        check_for_api_key_usage_warnings(config, has_api_key=False)
        
        self.assertTrue(mock_logger.warning.called)
        warning_message = str(mock_logger.warning.call_args_list)
        self.assertIn('policy-metadata-filter', warning_message)
    
    @patch('checkov.common.util.api_key_warnings.logger')
    def test_use_enforcement_rules_warning(self, mock_logger):
        """Test warning when using --use-enforcement-rules without API key"""
        config = MockConfig(
            use_enforcement_rules=True,
            check=None,
            skip_check=None,
            hard_fail_on=None,
            soft_fail_on=None
        )
        check_for_api_key_usage_warnings(config, has_api_key=False)
        
        self.assertTrue(mock_logger.warning.called)
        warning_message = str(mock_logger.warning.call_args_list)
        self.assertIn('use-enforcement-rules', warning_message)
    
    def test_severity_codes_are_defined(self):
        """Test that all expected severity codes are defined"""
        expected_codes = {'CRITICAL', 'HIGH', 'MEDIUM', 'MODERATE', 'LOW', 'INFO', 'NONE'}
        self.assertEqual(SEVERITY_CODES, expected_codes)


if __name__ == '__main__':
    unittest.main()
