from typing import Dict, Any, List

import pytest

from cdk_integration_tests.utils import run_check, load_failed_checks_from_file

LANGUAGE = 'python'


@pytest.fixture(scope="session", autouse=True)
def failed_checks() -> Dict[str, List[Dict[str, Any]]]:
    report_failed_checks = load_failed_checks_from_file(LANGUAGE)
    yield report_failed_checks


def test_CKV_AWS_18_S3BucketLogging(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_18")


def test_CKV_AWS_19_S3BucketEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_19")


def test_CKV_AWS_21_S3BucketVersioning(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_21")


def test_CKV_AWS_145_S3BucketKMSEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_145")


def test_CKV2_AWS_6_S3BucketPublicAccessBlock(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV2_AWS_6")


def test_CKV_AWS_54_S3BlockPublicPolicy(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_54")


def test_CKV_AWS_26_SNSTopicEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_26")


def test_CKV_AWS_20_S3PublicACLRead(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_20")


def test_CKV_AWS_55_S3IgnorePublicACLs(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_55")


def test_CKV_AWS_56_S3RestrictPublicBuckets(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_56")


def test_CKV_AWS_53_S3BlockPublicACLs(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_53")


def test_CKV_AWS_57_S3PublicACLWrite(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_57")


def test_CKV_AWS_115_LambdaFunctionLevelConcurrentExecutionLimit(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_115")


def test_CKV_AWS_116_LambdaDLQConfigured(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_116")


def test_CKV_AWS_28_DynamodbRecovery(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_28")


def test_CKV_AWS_158_CloudWatchLogGroupKMSKey(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_158")


def test_CKV_AWS_3_EBSEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_3")


def test_CKV_AWS_120_APIGatewayCacheEnable(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_120")


def test_CKV_AWS_163_ECRImageScanning(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_163")


def test_CKV_AWS_51_ECRImmutableTags(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_51")


def test_CKV_AWS_44_NeptuneClusterStorageEncrypted(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_44")


def test_CKV_AWS_166_BackupVaultEncrypted(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_166")


def test_CKV_AWS_74_DocDBEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_74")


def test_CKV_AWS_47_DAXEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_47")


def test_CKV_AWS_156_WorkspaceRootVolumeEncrypted(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_156")


def test_CKV_AWS_155_WorkspaceUserVolumeEncrypted(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_155")


def test_CKV_AWS_165_DynamodbGlobalTableRecovery(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_165")


def test_CKV_AWS_27_SQSQueueEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_27")


def test_CKV_AWS_195_GlueSecurityConfigurationEnabled(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_195")


def test_CKV_AWS_30_ElasticacheReplicationGroupEncryptionAtTransit(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_30")


def test_CKV_AWS_68_WAFEnabled(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_68")


def test_CKV_AWS_64_RedshiftClusterEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_64")
