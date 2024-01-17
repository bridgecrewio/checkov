import os
import unittest

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.code_categories import CodeCategoryType, CodeCategoryMapping
from checkov.common.bridgecrew.integration_features.features.licensing_integration import LicensingIntegration
from checkov.common.bridgecrew.licensing import CustomerSubscription, SubscriptionCategoryMapping, \
    CategoryToSubscriptionMapping, open_source_categories
from checkov.common.bridgecrew.platform_errors import ModuleNotEnabledError
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.runner_filter import RunnerFilter

from checkov.bitbucket.runner import Runner as bitbucket_configuration_runner
from checkov.sca_package_2.runner import Runner as sca_package_runner_2
from checkov.secrets.runner import Runner as secrets_runner
from checkov.terraform.runner import Runner as tf_graph_runner

# limited set for shorter testing
DEFAULT_RUNNERS = (
    tf_graph_runner(),
    secrets_runner(),
    bitbucket_configuration_runner(),
    sca_package_runner_2()
)

checkov_runners = [value for attr, value in CheckType.__dict__.items() if not attr.startswith("__")]

# pycharm gives false positive "unresolved reference" - ignore https://youtrack.jetbrains.com/issue/PY-36205
module_keys = [e.value for e in CustomerSubscription]

runner_to_subscription_map = {runner: CategoryToSubscriptionMapping.get(CodeCategoryMapping[runner]) for runner in checkov_runners if 'sca_' not in runner}
runner_to_subscription_map['sca_package'] = CustomerSubscription.SCA
runner_to_subscription_map['sca_image'] = CustomerSubscription.SCA
subscription_to_runner_map = {CustomerSubscription(sub): [runner for runner in checkov_runners if runner_to_subscription_map.get(runner) == CustomerSubscription(sub)] for sub in module_keys}


class TestLicensingIntegration(unittest.TestCase):

    def test_constants(self):
        # these tests ensure that these lists get maintained if the runners and categories change
        self.assertEqual(set(module_keys), {'IAC', 'SECRETS', 'SCA', 'SAST'})

        self.assertEqual(set(checkov_runners), {
            'ansible',
            'argo_workflows',
            'arm',
            'azure_pipelines',
            'bicep',
            'bitbucket_configuration',
            'bitbucket_pipelines',
            'cdk',
            'circleci_pipelines',
            'cloudformation',
            'dockerfile',
            'github_configuration',
            'github_actions',
            'gitlab_configuration',
            'gitlab_ci',
            'helm',
            'json',
            'kubernetes',
            'kustomize',
            'openapi',
            'sca_package',
            'sca_image',
            'secrets',
            'serverless',
            'terraform',
            'terraform_json',
            'terraform_plan',
            'yaml',
            'sast',
            'sast_python',
            'sast_java',
            'sast_javascript',
            '3d_policy'
        })

        self.assertEqual(SubscriptionCategoryMapping.get(CustomerSubscription.IAC), (CodeCategoryType.IAC, CodeCategoryType.BUILD_INTEGRITY))
        self.assertEqual(SubscriptionCategoryMapping.get(CustomerSubscription.SCA), (CodeCategoryType.LICENSES, CodeCategoryType.VULNERABILITIES))
        self.assertEqual(SubscriptionCategoryMapping.get(CustomerSubscription.SECRETS), (CodeCategoryType.SECRETS,))
        self.assertEqual(SubscriptionCategoryMapping.get(CustomerSubscription.SAST), (CodeCategoryType.WEAKNESSES,))

        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.IAC], CustomerSubscription.IAC)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.BUILD_INTEGRITY], CustomerSubscription.IAC)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.LICENSES], CustomerSubscription.SCA)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.VULNERABILITIES], CustomerSubscription.SCA)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.SECRETS], CustomerSubscription.SECRETS)
        self.assertEqual(CategoryToSubscriptionMapping[CodeCategoryType.WEAKNESSES], CustomerSubscription.SAST)

        self.assertEqual(CodeCategoryMapping.get(CheckType.BITBUCKET_PIPELINES), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.CIRCLECI_PIPELINES), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.ANSIBLE), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.ARM), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.AZURE_PIPELINES), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.BICEP), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.CDK), CodeCategoryType.WEAKNESSES)
        self.assertEqual(CodeCategoryMapping.get(CheckType.CLOUDFORMATION), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.DOCKERFILE), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.GITHUB_CONFIGURATION), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.GITHUB_ACTIONS), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.GITLAB_CONFIGURATION), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.GITLAB_CI), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.BITBUCKET_CONFIGURATION), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.HELM), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.JSON), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.YAML), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.KUBERNETES), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.KUSTOMIZE), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.OPENAPI), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.SCA_PACKAGE), [CodeCategoryType.LICENSES, CodeCategoryType.VULNERABILITIES])
        self.assertEqual(CodeCategoryMapping.get(CheckType.SCA_IMAGE), [CodeCategoryType.LICENSES, CodeCategoryType.VULNERABILITIES])
        self.assertEqual(CodeCategoryMapping.get(CheckType.SECRETS), CodeCategoryType.SECRETS)
        self.assertEqual(CodeCategoryMapping.get(CheckType.SERVERLESS), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.TERRAFORM), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.TERRAFORM_PLAN), CodeCategoryType.IAC)
        self.assertEqual(CodeCategoryMapping.get(CheckType.ARGO_WORKFLOWS), CodeCategoryType.BUILD_INTEGRITY)
        self.assertEqual(CodeCategoryMapping.get(CheckType.SAST), CodeCategoryType.WEAKNESSES)

        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.BITBUCKET_PIPELINES), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.CIRCLECI_PIPELINES), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.ANSIBLE), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.ARM), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.AZURE_PIPELINES), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.BICEP), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.CDK), CustomerSubscription.SAST)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.CLOUDFORMATION), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.DOCKERFILE), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.GITHUB_CONFIGURATION), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.GITHUB_ACTIONS), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.GITLAB_CONFIGURATION), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.GITLAB_CI), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.BITBUCKET_CONFIGURATION), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.HELM), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.JSON), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.YAML), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.KUBERNETES), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.KUSTOMIZE), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.OPENAPI), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.SCA_PACKAGE), CustomerSubscription.SCA)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.SCA_IMAGE), CustomerSubscription.SCA)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.SECRETS), CustomerSubscription.SECRETS)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.SERVERLESS), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.TERRAFORM), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.TERRAFORM_PLAN), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.ARGO_WORKFLOWS), CustomerSubscription.IAC)
        self.assertEqual(LicensingIntegration.get_subscription_for_runner(CheckType.SAST), CustomerSubscription.SAST)

        self.assertEqual(open_source_categories, [CodeCategoryType.IAC, CodeCategoryType.SECRETS, CodeCategoryType.BUILD_INTEGRITY])

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

    def test_oss_mode_enabled(self):
        instance = BcPlatformIntegration()

        licensing_integration = LicensingIntegration(instance)

        licensing_integration.pre_scan()
        self.assertTrue(licensing_integration.open_source_only)  # no API key

        instance.bc_api_key = '1234'
        licensing_integration.pre_scan()
        self.assertTrue(licensing_integration.open_source_only)  # no customer run config

        # IAC and secrets are valid, SCA is not
        for runner_check_type in checkov_runners:
            self.assertEqual(
                licensing_integration.is_runner_valid(runner_check_type),
                runner_to_subscription_map[runner_check_type] not in (CustomerSubscription.SCA, CustomerSubscription.SAST),
            )

    def test_oss_mode_resource_plan(self):
        instance = BcPlatformIntegration()
        licensing_integration = LicensingIntegration(instance)
        instance.bc_api_key = '1234'
        licensing_integration.pre_scan()

        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {m: True for m in module_keys},
            }
        }
        licensing_integration.pre_scan()
        self.assertFalse(licensing_integration.open_source_only)

    def test_oss_mode_dev_plan(self):
        instance = BcPlatformIntegration()
        licensing_integration = LicensingIntegration(instance)
        instance.bc_api_key = '1234'
        licensing_integration.pre_scan()

        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {m: True for m in module_keys},
            }
        }
        licensing_integration.pre_scan()
        self.assertFalse(licensing_integration.open_source_only)

    def test_resource_mode(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'

        licensing_integration = LicensingIntegration(instance)

        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {m: True for m in module_keys},
            }
        }

        licensing_integration.pre_scan()

        for runner_check_type in checkov_runners:
            self.assertTrue(licensing_integration.is_runner_valid(runner_check_type))
        self.assertTrue(licensing_integration.should_run_image_referencer())

    def test_developer_mode_all_enabled(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'

        licensing_integration = LicensingIntegration(instance)

        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {key: True for key in module_keys},
            }
        }

        licensing_integration.pre_scan()

        for runner_check_type in checkov_runners:
            if runner_check_type.startswith("sast"):  # todo: remove when sast will be active
                continue
            self.assertTrue(licensing_integration.is_runner_valid(runner_check_type))
        self.assertTrue(licensing_integration.should_run_image_referencer())

    def test_developer_mode_all_disabled(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'

        licensing_integration = LicensingIntegration(instance)

        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {key: False for key in module_keys},
            }
        }

        licensing_integration.pre_scan()

        for runner_check_type in checkov_runners:
            if runner_check_type.startswith(("cdk", "sast")):  # todo: remove when sast will be active
                continue
            self.assertFalse(licensing_integration.is_runner_valid(runner_check_type))
        self.assertFalse(licensing_integration.should_run_image_referencer())

    def test_developer_mode_each_enabled(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'

        licensing_integration = LicensingIntegration(instance)

        # test one module at a time
        for module in module_keys:
            instance.customer_run_config_response = {
                'platformLicense': {
                    'modules': {key: key == module for key in module_keys},
                }
            }
            licensing_integration.pre_scan()
            for runner_check_type in checkov_runners:
                if runner_check_type.startswith(("cdk", "sast")):  # todo: remove when sast will be active
                    continue
                self.assertEqual(licensing_integration.is_runner_valid(runner_check_type), runner_check_type in subscription_to_runner_map[CustomerSubscription(module)])
            self.assertEqual(licensing_integration.should_run_image_referencer(), module == 'SCA')

    def test_runner_registry_single_runner(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'
        licensing_integration = LicensingIntegration(instance)
        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {m: True for m in module_keys},
            }
        }

        licensing_integration.pre_scan()

        scan_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

        runner_filter = RunnerFilter(framework=['terraform'], runners=checkov_runners)
        runner_registry = RunnerRegistry('', runner_filter, *DEFAULT_RUNNERS)
        runner_registry.licensing_integration = licensing_integration
        reports = runner_registry.run(root_folder=scan_dir)
        self.assertEqual(len(reports), 1)
        self.assertIsNotNone(reports[0])

    def test_runner_registry_single_runner_hard_fail(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'
        licensing_integration = LicensingIntegration(instance)
        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {m: False for m in module_keys},
            }
        }

        licensing_integration.pre_scan()

        scan_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

        runner_filter = RunnerFilter(framework=['terraform'], runners=checkov_runners)
        runner_registry = RunnerRegistry('', runner_filter, *DEFAULT_RUNNERS)
        runner_registry.licensing_integration = licensing_integration
        try:
            runner_registry.run(root_folder=scan_dir)
            raise AssertionError('Runner registry should hard fail because a single framework was used')
        except Exception as e:
            self.assertIsInstance(e, ModuleNotEnabledError)

    def test_runner_registry_multiple_runners_with_framework(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'
        licensing_integration = LicensingIntegration(instance)
        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {
                    'IAC': True,
                    'SECRETS': False,
                    'SCA': False
                },
            }
        }

        licensing_integration.pre_scan()

        scan_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

        runner_filter = RunnerFilter(framework=['terraform', 'bitbucket_configuration', 'sca_package', 'secrets'], runners=checkov_runners)
        runner_registry = RunnerRegistry('', runner_filter, *DEFAULT_RUNNERS)
        runner_registry.licensing_integration = licensing_integration
        with self.assertLogs(level='INFO') as log:
            reports = runner_registry.run(root_folder=scan_dir)
            self.assertEqual(len(reports), 2)  # terraform and bitbucket
            # we are specifically verifying the log level here
            self.assertIn('WARNING:root:The framework "secrets" is part of the "SECRETS" module, which is not enabled in the platform', log.output)
            self.assertIn('WARNING:root:The framework "secrets" is part of the "SECRETS" module, which is not enabled in the platform', log.output)

    def test_runner_registry_multiple_runners_without_framework(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'
        licensing_integration = LicensingIntegration(instance)
        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {
                    'IAC': True,
                    'SECRETS': False,
                    'SCA': False
                },
            }
        }

        licensing_integration.pre_scan()

        scan_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

        runner_filter = RunnerFilter(runners=checkov_runners)
        runner_registry = RunnerRegistry('', runner_filter, *DEFAULT_RUNNERS)
        runner_registry.licensing_integration = licensing_integration
        with self.assertLogs(level='INFO') as log:
            reports = runner_registry.run(root_folder=scan_dir)
            self.assertEqual(len(reports), 2)  # terraform and bitbucket
            # we are specifically verifying the log level here
            self.assertIn('INFO:root:The framework "secrets" is part of the "SECRETS" module, which is not enabled in the platform', log.output)
            self.assertIn('INFO:root:The framework "secrets" is part of the "SECRETS" module, which is not enabled in the platform', log.output)

    def test_runner_registry_multiple_runners_all_disabled(self):
        instance = BcPlatformIntegration()
        instance.bc_api_key = '1234'
        licensing_integration = LicensingIntegration(instance)
        instance.customer_run_config_response = {
            'platformLicense': {
                'modules': {
                    'IAC': False,
                    'SECRETS': False,
                    'SCA': False
                }
            }
        }

        licensing_integration.pre_scan()

        scan_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

        runner_filter = RunnerFilter(framework=['terraform', 'bitbucket_configuration', 'sca_package', 'secrets'], runners=checkov_runners)
        runner_registry = RunnerRegistry('', runner_filter, *DEFAULT_RUNNERS)
        runner_registry.licensing_integration = licensing_integration
        try:
            runner_registry.run(root_folder=scan_dir)
            raise AssertionError('Runner registry should hard fail because a single framework was used')
        except Exception as e:
            self.assertIsInstance(e, ModuleNotEnabledError)


if __name__ == '__main__':
    unittest.main()
