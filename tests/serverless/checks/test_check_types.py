import os
import unittest

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.serverless.checks.complete.base_complete_check import BaseCompleteCheck
from checkov.serverless.checks.custom.base_custom_check import BaseCustomCheck
from checkov.serverless.checks.function.base_function_check import BaseFunctionCheck
from checkov.serverless.checks.layer.base_layer_check import BaseLayerCheck
from checkov.serverless.checks.package.base_package_check import BasePackageCheck
from checkov.serverless.checks.plugin.base_plugin_check import BasePluginCheck
from checkov.serverless.checks.provider.base_provider_check import BaseProviderCheck
from checkov.serverless.checks.service.base_service_check import BaseServiceCheck
from checkov.serverless.runner import Runner
from checkov.runner_filter import RunnerFilter


CATS = [CheckCategories.APPLICATION_SECURITY]


class TestCheckTypes(unittest.TestCase):
    def helper(self, check):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_CheckTypes"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_complete_check(self):
        check = ATestCompleteCheck()
        self.helper(check)

    def test_custom_check(self):
        check = ATestCustomCheck()
        self.helper(check)

    def test_function_check(self):
        check = ATestFunctionCheck()
        self.helper(check)

    def test_layer_check(self):
        check = ATestLayerCheck()
        self.helper(check)

    def test_package_check(self):
        check = ATestPackageCheck()
        self.helper(check)

    def test_plugin_check(self):
        check = ATestPluginCheck()
        self.helper(check)

    def test_provider_check(self):
        check = ATestProviderCheck()
        self.helper(check)

    def test_service_check(self):
        check = ATestServiceCheck()
        self.helper(check)


class ATestCompleteCheck(BaseCompleteCheck):
    def __init__(self):
        id = "CKV_TCT_0"
        super().__init__(name="test", id=id, categories=CATS, supported_entities=['serverless_aws'])

    def scan_complete_conf(self, conf):
        if isinstance(conf["service"], dict) and conf["service"].get("awsKmsKeyArn") != "arn:aws:kms:us-east-1:XXXXXX:key/some-hash":
            return CheckResult.FAILED
        if conf["provider"]["runtime"] != "nodejs12.x":
            return CheckResult.FAILED
        if conf["plugins"] != ["some-plugin", "some-other-plugin"]:
            return CheckResult.FAILED
        if conf["package"]["artifact"] != "path/to/my-artifact.zip":
            return CheckResult.FAILED
        if conf["custom"]["my_custom_var"] != "sourced-in-value":
            return CheckResult.FAILED
        if conf["layers"]["hello"]["path"] != "yup/that's/my/path":
            return CheckResult.FAILED

        if conf["functions"]["myFunction"]["handler"] != "myfunction.invoke":
            return CheckResult.FAILED
        if conf["functions"]["myFunction"]["environment"]["SOME_PROVIDER_VAR"] != "spv_value":  # enriched
            return CheckResult.FAILED
        if conf["functions"]["myFunction"]["tags"]["MY_TAG"] != "tag_value":                    # enriched
            return CheckResult.FAILED

        return CheckResult.PASSED


class ATestCustomCheck(BaseCustomCheck):
    def __init__(self):
        id = "CKV_TCT_1"
        super().__init__(name="test", id=id, categories=CATS, supported_entities=['serverless_aws'])

    def scan_custom_conf(self, conf):
        if conf.get("my_custom_var") == "sourced-in-value":
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


class ATestFunctionCheck(BaseFunctionCheck):
    def __init__(self):
        id = "CKV_TCT_2"
        super().__init__(name="test", id=id, categories=CATS, supported_entities=['serverless_aws'])

    def scan_function_conf(self, conf):
        if conf.get("handler") != "myfunction.invoke":
            return CheckResult.FAILED

        # Environment should be pulled in ("enriched") from provider block
        if conf["environment"]["SOME_PROVIDER_VAR"] != "spv_value":
            return CheckResult.FAILED

        # Tags should be pulled in ("enriched") from provider block (stackTags)
        if conf["tags"]["MY_TAG"] != "tag_value":
            return CheckResult.FAILED

        return CheckResult.PASSED


class ATestLayerCheck(BaseLayerCheck):
    def __init__(self):
        id = "CKV_TCT_3"
        super().__init__(name="test", id=id, categories=CATS, supported_entities=['serverless_aws'])

    def scan_layer_conf(self, conf):
        if conf.get("path") == "yup/that's/my/path":
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


class ATestPackageCheck(BasePackageCheck):
    def __init__(self):
        id = "CKV_TCT_4"
        super().__init__(name="test", id=id, categories=CATS, supported_entities=['serverless_aws'])

    def scan_package_conf(self, conf):
        if conf.get("artifact") == "path/to/my-artifact.zip":
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


class ATestPluginCheck(BasePluginCheck):
    def __init__(self):
        id = "CKV_TCT_5"
        super().__init__(name="test", id=id, categories=CATS, supported_entities=['serverless_aws'])

    def scan_plugin_list(self, plugin_list):
        if plugin_list == ["some-plugin", "some-other-plugin"]:
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


class ATestProviderCheck(BaseProviderCheck):
    def __init__(self):
        id = "CKV_TCT_6"
        super().__init__(name="test", id=id, categories=CATS, supported_entities=['serverless_aws'])

    def scan_provider_conf(self, conf):
        if conf.get("runtime") == "nodejs12.x":
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


class ATestServiceCheck(BaseServiceCheck):
    def __init__(self):
        id = "CKV_TCT_7"
        super().__init__(name="test", id=id, categories=CATS, supported_entities=['serverless_aws'])

    def scan_service_conf(self, conf):
        if isinstance(conf, dict) and conf.get("awsKmsKeyArn") == "arn:aws:kms:us-east-1:XXXXXX:key/some-hash":
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


if __name__ == '__main__':
    unittest.main()
