import unittest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.code_categories import CodeCategoryType, CodeCategoryMapping
from checkov.common.bridgecrew.integration_features.features.licensing_integration import LicensingIntegration
from checkov.common.bridgecrew.licensing import CustomerLicense, CustomerSubscription, SubscriptionCategoryMapping, \
    CategoryToSubscriptionMapping
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration

checkov_runners = [value for attr, value in CheckType.__dict__.items() if not attr.startswith("__")]
module_keys = [e.value for e in CustomerSubscription]

runner_to_subscription_map = {runner: CategoryToSubscriptionMapping.get(CodeCategoryMapping[runner]) for runner in checkov_runners}
subscription_to_runner_map = {CustomerSubscription(sub): [runner for runner in checkov_runners if runner_to_subscription_map.get(runner) == CustomerSubscription(sub)] for sub in module_keys}


class TestLicensingIntegration(unittest.TestCase):

    def test_constants(self):
        # these tests ensure that these lists get maintained if the runners and categories change
        self.assertEqual(set(module_keys), {'IAC', 'SECRETS', 'SCA'})

        self.assertEqual(set(checkov_runners), {
            'bitbucket_pipelines', 'circleci_pipelines', 'argo_workflows', 'arm', 'azure_pipelines', 'bicep',
            'cloudformation', 'dockerfile', 'github_configuration', 'github_actions', 'gitlab_configuration',
            'gitlab_ci', 'bitbucket_configuration', 'helm', 'json', 'yaml', 'kubernetes', 'kustomize', 'openapi',
            'sca_package', 'sca_image', 'secrets', 'serverless', 'terraform', 'terraform_plan'
        })

        self.assertEqual(SubscriptionCategoryMapping.get(CustomerSubscription.IAC), [CodeCategoryType.IAC, CodeCategoryType.SUPPLY_CHAIN])
        self.assertEqual(SubscriptionCategoryMapping.get(CustomerSubscription.SCA), [CodeCategoryType.OPEN_SOURCE, CodeCategoryType.IMAGES])
        self.assertEqual(SubscriptionCategoryMapping.get(CustomerSubscription.SECRETS), [CodeCategoryType.SECRETS])

        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.IAC], CustomerSubscription.IAC)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.SUPPLY_CHAIN], CustomerSubscription.IAC)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.OPEN_SOURCE], CustomerSubscription.SCA)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.IMAGES], CustomerSubscription.SCA)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.SECRETS], CustomerSubscription.SECRETS)

        self.assertEqual(CodeCategoryMapping.get(CheckType.BITBUCKET_PIPELINES), CodeCategoryType.SUPPLY_CHAIN)
        self.assertEqual(CodeCategoryMapping.get(CheckType.CIRCLECI_PIPELINES), CodeCategoryType.SUPPLY_CHAIN)
        self.assertEqual(CodeCategoryMapping.get(CheckType.ARM), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.AZURE_PIPELINES), CodeCategoryType.SUPPLY_CHAIN)
        self.assertEqual(CodeCategoryMapping.get(CheckType.BICEP), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.CLOUDFORMATION), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.DOCKERFILE), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.GITHUB_CONFIGURATION), CodeCategoryType.SUPPLY_CHAIN)
        self.assertEqual(CodeCategoryMapping.get(CheckType.GITHUB_ACTIONS), CodeCategoryType.SUPPLY_CHAIN)
        self.assertEqual(CodeCategoryMapping.get(CheckType.GITLAB_CONFIGURATION), CodeCategoryType.SUPPLY_CHAIN)
        self.assertEqual(CodeCategoryMapping.get(CheckType.GITLAB_CI), CodeCategoryType.SUPPLY_CHAIN)
        self.assertEqual(CodeCategoryMapping.get(CheckType.BITBUCKET_CONFIGURATION), CodeCategoryType.SUPPLY_CHAIN)
        self.assertEqual(CodeCategoryMapping.get(CheckType.HELM), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.JSON), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.YAML), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.KUBERNETES), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.KUSTOMIZE), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.OPENAPI), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.SCA_PACKAGE), CodeCategoryType.OPEN_SOURCE)
        self.assertEqual(CodeCategoryMapping.get(CheckType.SCA_IMAGE), CodeCategoryType.IMAGES)
        self.assertEqual(CodeCategoryMapping.get(CheckType.SECRETS), CodeCategoryType.SECRETS)
        self.assertEqual(CodeCategoryMapping.get(CheckType.SERVERLESS), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.TERRAFORM), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.TERRAFORM_PLAN), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.ARGO_WORKFLOWS), CodeCategoryType.SUPPLY_CHAIN)

    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.skip_download = False
        instance.platform_integration_configured = True

        # it is always valid, because it always makes a determination for which runners run
        licensing_integration = LicensingIntegration(instance)

        self.assertTrue(licensing_integration.is_valid())

        instance.skip_download = True
        self.assertTrue(licensing_integration.is_valid())

        instance.platform_integration_configured = False
        self.assertTrue(licensing_integration.is_valid())

        instance.skip_download = False
        self.assertTrue(licensing_integration.is_valid())

        licensing_integration.integration_feature_failures = True
        self.assertTrue(licensing_integration.is_valid())

    def test_oss_mode(self):
        instance = BcPlatformIntegration()

        licensing_integration = LicensingIntegration(instance)

        licensing_integration.pre_scan()
        self.assertTrue(licensing_integration.open_source_only)  # no API key

        instance.bc_api_key = '1234'
        licensing_integration.pre_scan()
        self.assertTrue(licensing_integration.open_source_only)  # no customer run config

        # IAC and secrets are valid, SCA is not
        for runner in checkov_runners:
            self.assertEqual(licensing_integration.is_runner_valid(runner), runner_to_subscription_map[runner] != CustomerSubscription.SCA)

        # value does not matter for this test, just checking if it's set
        instance.customer_run_config_response = {
            'license': {
                'modules': {m: True for m in module_keys},
                'git_clone_enabled': True
            }
        }

        licensing_integration.pre_scan()
        self.assertFalse(licensing_integration.open_source_only)

    def test_resource_mode(self):
        # tests for return values that can occur when the user is in resource pricing

        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'

        licensing_integration = LicensingIntegration(instance)

        instance.customer_run_config_response = {
            'license': {
                'modules': {m: True for m in module_keys},
                'git_clone_enabled': True
            }
        }

        licensing_integration.pre_scan()

        for runner in checkov_runners:
            self.assertTrue(licensing_integration.is_runner_valid(runner))
        self.assertTrue(licensing_integration.should_run_image_referencer())
        self.assertTrue(licensing_integration.include_old_secrets())
        self.assertTrue(licensing_integration.include_new_secrets())

        instance.customer_run_config_response = {
            'license': {
                'modules': {m: True for m in module_keys},
                'git_clone_enabled': False
            }
        }

        licensing_integration.pre_scan()

        for runner in checkov_runners:
            self.assertTrue(licensing_integration.is_runner_valid(runner))
        self.assertTrue(licensing_integration.should_run_image_referencer())
        self.assertTrue(licensing_integration.include_old_secrets())
        self.assertFalse(licensing_integration.include_new_secrets())

    def test_developer_mode(self):
        # tests for return values that can occur when the user is in dev pricing
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'

        licensing_integration = LicensingIntegration(instance)

        # test all enabled
        instance.customer_run_config_response = {
            'license': {
                'modules': {key: True for key in module_keys},
                'git_clone_enabled': True
            }
        }

        licensing_integration.pre_scan()

        for runner in checkov_runners:
            self.assertTrue(licensing_integration.is_runner_valid(runner))
        self.assertTrue(licensing_integration.should_run_image_referencer())
        self.assertTrue(licensing_integration.include_old_secrets())
        self.assertTrue(licensing_integration.include_new_secrets())

        instance.customer_run_config_response = {
            'license': {
                'modules': {key: False for key in module_keys},
                'git_clone_enabled': False
            }
        }

        licensing_integration.pre_scan()

        # test all disabled
        for runner in checkov_runners:
            self.assertFalse(licensing_integration.is_runner_valid(runner))
        self.assertFalse(licensing_integration.should_run_image_referencer())
        self.assertFalse(licensing_integration.include_old_secrets())
        self.assertFalse(licensing_integration.include_new_secrets())

        # test one module at a time
        for module in module_keys:
            instance.customer_run_config_response = {
                'license': {
                    'modules': {key: key == module for key in module_keys},
                    'git_clone_enabled': module == 'SECRETS'
                }
            }
            licensing_integration.pre_scan()
            for runner in checkov_runners:
                self.assertEqual(licensing_integration.is_runner_valid(runner), runner in subscription_to_runner_map[CustomerSubscription(module)])
            self.assertEqual(licensing_integration.should_run_image_referencer(), module == 'SCA')
            self.assertEqual(licensing_integration.include_old_secrets(), module == 'SECRETS')
            self.assertEqual(licensing_integration.include_new_secrets(), module == 'SECRETS')

    def test_include_secrets(self):
        licensing_integration = LicensingIntegration(None)

        # starts in OSS mode
        self.assertFalse(licensing_integration.include_new_secrets())
        self.assertTrue(licensing_integration.include_old_secrets())

        # could be resource or dev pricing mode
        licensing_integration.open_source_only = False
        licensing_integration.git_clone_enabled = True
        licensing_integration.enabled_modules = [CustomerSubscription.SECRETS]
        self.assertTrue(licensing_integration.include_new_secrets())
        self.assertTrue(licensing_integration.include_old_secrets())

        # resource mode without git clone
        licensing_integration.git_clone_enabled = False
        self.assertFalse(licensing_integration.include_new_secrets())
        self.assertTrue(licensing_integration.include_old_secrets())

        # dev mode with secrets disabled
        licensing_integration.enabled_modules = []
        self.assertFalse(licensing_integration.include_new_secrets())
        self.assertFalse(licensing_integration.include_old_secrets())

    def test_run_image_referencer(self):
        licensing_integration = LicensingIntegration(None)

        # starts in OSS mode
        self.assertFalse(licensing_integration.should_run_image_referencer())

        # dev or resource mode, doesn't matter
        licensing_integration.open_source_only = False
        licensing_integration.enabled_modules = [CustomerSubscription.SCA]
        self.assertTrue(licensing_integration.should_run_image_referencer())

        # dev mode with SCA disabled
        licensing_integration.enabled_modules = []
        self.assertFalse(licensing_integration.should_run_image_referencer())


if __name__ == '__main__':
    unittest.main()
