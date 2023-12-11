from typing import Dict, Any, List

import pytest

from cdk_integration_tests.utils import run_check, load_failed_checks_from_file

LANGUAGE = 'python'


@pytest.fixture(scope="session", autouse=True)
def failed_checks() -> Dict[str, List[Dict[str, Any]]]:
    report_failed_checks = load_failed_checks_from_file(LANGUAGE)
    yield report_failed_checks


def test_CKV_AWS_18_S3BucketLogging(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_18", policy_name="S3BucketLogging", language="python")


def test_CKV_AWS_19_S3BucketEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_19", policy_name="S3BucketEncryption", language="python")


def test_CKV_AWS_21_S3BucketVersioning(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_21", policy_name="S3BucketVersioning", language="python")


def test_CKV_AWS_145_S3BucketKMSEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_145", policy_name="S3BucketKMSEncryption", language="python")


def test_CKV2_AWS_6_S3BucketPublicAccessBlock(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV2_AWS_6", policy_name="S3BucketPublicAccessBlock", language="python")


def test_CKV_AWS_54_S3BlockPublicPolicy(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_54", policy_name="S3BlockPublicPolicy", language="python")


def test_CKV_AWS_26_SNSTopicEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_26", policy_name="SNSTopicEncryption", language="python")


def test_CKV_AWS_20_S3PublicACLRead(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_20", policy_name="S3PublicACLRead", language="python")


def test_CKV_AWS_55_S3IgnorePublicACLs(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_55", policy_name="S3IgnorePublicACLs", language="python")


def test_CKV_AWS_56_S3RestrictPublicBuckets(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_56", policy_name="S3RestrictPublicBuckets", language="python")


def test_CKV_AWS_53_S3BlockPublicACLs(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_53", policy_name="S3BlockPublicACLs", language="python")


def test_CKV_AWS_57_S3PublicACLWrite(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_57", policy_name="S3PublicACLWrite", language="python")


def test_CKV_AWS_115_LambdaFunctionLevelConcurrentExecutionLimit(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_115", policy_name="LambdaFunctionLevelConcurrentExecutionLimit", language="python")


def test_CKV_AWS_116_LambdaDLQConfigured(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_116", policy_name="LambdaDLQConfigured", language="python")


def test_CKV_AWS_28_DynamodbRecovery(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_28", policy_name="DynamodbRecovery", language="python")


def test_CKV_AWS_158_CloudWatchLogGroupKMSKey(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_158", policy_name="CloudWatchLogGroupKMSKey", language="python")


def test_CKV_AWS_3_EBSEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_3", policy_name="EBSEncryption", language="python")


def test_CKV_AWS_120_APIGatewayCacheEnable(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_120", policy_name="APIGatewayCacheEnable", language="python")


def test_CKV_AWS_163_ECRImageScanning(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_163", policy_name="ECRImageScanning", language="python")


def test_CKV_AWS_51_ECRImmutableTags(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_51", policy_name="ECRImmutableTags", language="python")


def test_CKV_AWS_44_NeptuneClusterStorageEncrypted(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_44", policy_name="NeptuneClusterStorageEncrypted", language="python")


def test_CKV_AWS_166_BackupVaultEncrypted(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_166", policy_name="BackupVaultEncrypted", language="python")


def test_CKV_AWS_74_DocDBEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_74", policy_name="DocDBEncryption", language="python")


def test_CKV_AWS_47_DAXEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_47", policy_name="DAXEncryption", language="python")


def test_CKV_AWS_156_WorkspaceRootVolumeEncrypted(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_156", policy_name="WorkspaceRootVolumeEncrypted", language="python")


def test_CKV_AWS_155_WorkspaceUserVolumeEncrypted(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_155", policy_name="WorkspaceUserVolumeEncrypted", language="python")


def test_CKV_AWS_165_DynamodbGlobalTableRecovery(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_165", policy_name="DynamodbGlobalTableRecovery", language="python")


def test_CKV_AWS_27_SQSQueueEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_27", policy_name="SQSQueueEncryption", language="python")


def test_CKV_AWS_195_GlueSecurityConfigurationEnabled(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_195", policy_name="GlueSecurityConfigurationEnabled", language="python")


def test_CKV_AWS_30_ElasticacheReplicationGroupEncryptionAtTransit(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_30", policy_name="ElasticacheReplicationGroupEncryptionAtTransit", language="python")


def test_CKV_AWS_29_ElasticacheReplicationGroupEncryptionAtRest(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_29", policy_name="ElasticacheReplicationGroupEncryptionAtRest", language="python")


def test_CKV_AWS_43_KinesisStreamEncryptionType(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_43", policy_name="KinesisStreamEncryptionType", language="python")


def test_CKV_AWS_42_EFSEncryptionEnabled(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_42", policy_name="EFSEncryptionEnabled", language="python")


# def test_CKV_AWS_193_AppSyncLogging(failed_checks):
#    run_check(check_results=failed_checks, check_id="CKV_AWS_193", policy_name="AppSyncLogging", language="python")


# def test_CKV_AWS_194_AppSyncFieldLevelLogs(failed_checks):
#    run_check(check_results=failed_checks, check_id="CKV_AWS_194", policy_name="AppSyncFieldLevelLogs", language="python")


def test_CKV_AWS_104_DocDBAuditLogs(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_104", policy_name="DocDBAuditLogs", language="python")


def test_CKV_AWS_82_AthenaWorkgroupConfiguration(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_82", policy_name="AthenaWorkgroupConfiguration", language="python")


def test_CKV_AWS_17_RDSPubliclyAccessible(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_17", policy_name="RDSPubliclyAccessible", language="python")


def test_CKV_AWS_87_RedshiftClusterPubliclyAccessible(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_87", policy_name="RedshiftClusterPubliclyAccessible", language="python")


def test_CKV_AWS_69_AmazonMQBrokerPublicAccess(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_69", policy_name="AmazonMQBrokerPublicAccess", language="python")


def test_CKV_AWS_118_RDSEnhancedMonitorEnabled(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_118", policy_name="RDSEnhancedMonitorEnabled", language="python")


def test_CKV_AWS_40_IAMPolicyAttachedToGroupOrRoles(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_40", policy_name="IAMPolicyAttachedToGroupOrRoles", language="python")


def test_CKV_AWS_36_CloudTrailLogValidation(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_36", policy_name="CloudTrailLogValidation", language="python")


def test_CKV_AWS_83_ElasticsearchDomainEnforceHTTPS(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_83", policy_name="ElasticsearchDomainEnforceHTTPS", language="python")


# def test_CKV_AWS_76_APIGatewayAccessLogging(failed_checks):
#    run_check(check_results=failed_checks, check_id="CKV_AWS_76", policy_name="APIGatewayAccessLogging", language="python")


def test_CKV_AWS_117_LambdaInVPC(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_117", policy_name="LambdaInVPC", language="python")


def test_CKV_AWS_68_WAFEnabled(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_68", policy_name="WAFEnabled", language="python")


def test_CKV_AWS_64_RedshiftClusterEncryption(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_64", policy_name="RedshiftClusterEncryption", language="python")
