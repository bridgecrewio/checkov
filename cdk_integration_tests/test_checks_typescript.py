from typing import Dict, Any, List

import pytest

from cdk_integration_tests.utils import run_check, load_failed_checks_from_file

LANGUAGE = 'typescript'


@pytest.fixture(scope="session", autouse=True)
def failed_checks() -> Dict[str, List[Dict[str, Any]]]:
    report_failed_checks = load_failed_checks_from_file(LANGUAGE)
    yield report_failed_checks


@pytest.mark.skip(reason="Not supported yet")
def test_ALBDropHttpHeaders():
    run_check(check_results=failed_checks, check_id="CKV_AWS_131", policy_name="ALBDropHttpHeaders", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_ALBListenerHTTPS():
    run_check(check_results=failed_checks, check_id="CKV_AWS_2", policy_name="ALBListenerHTTPS", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_APIGatewayAccessLogging():
    run_check(check_results=failed_checks, check_id="CKV_AWS_76", policy_name="APIGatewayAccessLogging", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_APIGatewayCacheEnable():
    run_check(check_results=failed_checks, check_id="CKV_AWS_120", policy_name="APIGatewayCacheEnable", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_APIGatewayV2AccessLogging():
    run_check(check_results=failed_checks, check_id="CKV_AWS_95", policy_name="APIGatewayV2AccessLogging", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_APIGatewayXray():
    run_check(check_results=failed_checks, check_id="CKV_AWS_73", policy_name="APIGatewayXray", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_AmazonMQBrokerPublicAccess():
    run_check(check_results=failed_checks, check_id="CKV_AWS_131", policy_name="AmazonMQBrokerPublicAccess", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_AuroraEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_96", policy_name="ALBDropHttpHeaders", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_BackupVaultEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_166", policy_name="BackupVaultEncrypted", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CloudTrailLogValidation():
    run_check(check_results=failed_checks, check_id="CKV_AWS_36", policy_name="CloudTrailLogValidation", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_S3PublicACLRead():
    run_check(check_results=failed_checks, check_id="CKV_AWS_20", policy_name="S3PublicACLRead", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_S3RestrictPublicBuckets():
    run_check(check_results=failed_checks, check_id="CKV_AWS_56", policy_name="S3RestrictPublicBuckets", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_SecretManagerSecretEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_149", policy_name="S3RestrictPublicBuckets", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_SecurityGroupRuleDescription():
    run_check(check_results=failed_checks, check_id="CKV_AWS_23", policy_name="SecurityGroupRuleDescription", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_SNSTopicEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_26", policy_name="SNSTopicEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_SQSQueueEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_27", policy_name="SQSQueueEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_TransferServerIsPublic():
    run_check(check_results=failed_checks, check_id="CKV_AWS_164", policy_name="TransferServerIsPublic", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_VPCEndpointAcceptanceConfigured():
    run_check(check_results=failed_checks, check_id="CKV_AWS_123", policy_name="VPCEndpointAcceptanceConfigured", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_WAFEnabled():
    run_check(check_results=failed_checks, check_id="CKV_AWS_68", policy_name="WAFEnabled", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_WorkspaceRootVolumeEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_156", policy_name="WorkspaceRootVolumeEncrypted", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_WorkspaceUserVolumeEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_155", policy_name="WorkspaceUserVolumeEncrypted", language="typescript")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_88_EC2PublicIP():
    run_check(lang="typescript", check_name="EC2PublicIP")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_163_ECRImageScanning():
    run_check(lang="typescript", check_name="ECRImageScanning")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_51_ECRImmutableTags():
    run_check(lang="typescript", check_name="ECRImmutableTags")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_136_ECRRepositoryEncrypted():
    run_check(lang="typescript", check_name="ECRRepositoryEncrypted")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_65_ECSClusterContainerInsights():
    run_check(lang="typescript", check_name="ECSClusterContainerInsights")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_97_ECSTaskDefinitionEFSVolumeEncryption():
    run_check(lang="typescript", check_name="ECSClusterContainerInsights")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_42_EFSEncryptionEnabled():
    run_check(lang="typescript", check_name="EFSEncryptionEnabled")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_58_EKSSecretsEncryption():
    run_check(lang="typescript", check_name="EKSSecretsEncryption")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_29_ElasticacheReplicationGroupEncryptionAtRest():
    run_check(lang="typescript", check_name="ElasticacheReplicationGroupEncryptionAtRest")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_30_ElasticacheReplicationGroupEncryptionAtTransit():
    run_check(lang="typescript", check_name="ElasticacheReplicationGroupEncryptionAtTransit")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_31_ElasticacheReplicationGroupEncryptionAtTransitAuthToken():
    run_check(lang="typescript", check_name="ElasticacheReplicationGroupEncryptionAtTransitAuthToken")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_83_ElasticsearchDomainEnforceHTTPS():
    run_check(lang="typescript", check_name="ElasticsearchDomainEnforceHTTPS")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_84_ElasticsearchDomainLogging():
    run_check(lang="typescript", check_name="ElasticsearchDomainLogging")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_91_ELBAccessLogs():
    run_check(lang="typescript", check_name="ELBAccessLogs")

@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_92_ELBv2AccessLogs():
    run_check(lang="typescript", check_name="ELBv2AccessLogs")