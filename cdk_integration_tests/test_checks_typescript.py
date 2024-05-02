from typing import Dict, Any, List

import pytest

from cdk_integration_tests.utils import run_check, load_failed_checks_from_file

LANGUAGE = 'typescript'


@pytest.fixture(scope="session", autouse=True)
def failed_checks() -> Dict[str, List[Dict[str, Any]]]:
    report_failed_checks = load_failed_checks_from_file(LANGUAGE)
    yield report_failed_checks


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_131_ALBDropHttpHeaders():
    run_check(check_results=failed_checks, check_id="CKV_AWS_131", policy_name="ALBDropHttpHeaders", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_2_ALBListenerHTTPS():
    run_check(check_results=failed_checks, check_id="CKV_AWS_2", policy_name="ALBListenerHTTPS", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_59_APIGatewayAuthorization(failed_checks):
    run_check(check_results=failed_checks, check_id="CKV_AWS_59", policy_name="APIGatewayAuthorization", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_76_APIGatewayAccessLogging():
    run_check(check_results=failed_checks, check_id="CKV_AWS_76", policy_name="APIGatewayAccessLogging", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_120_APIGatewayCacheEnable():
    run_check(check_results=failed_checks, check_id="CKV_AWS_120", policy_name="APIGatewayCacheEnable", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_95_APIGatewayV2AccessLogging():
    run_check(check_results=failed_checks, check_id="CKV_AWS_95", policy_name="APIGatewayV2AccessLogging", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_73_APIGatewayXray():
    run_check(check_results=failed_checks, check_id="CKV_AWS_73", policy_name="APIGatewayXray", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_194_AppSyncFieldLevelLogs():
    run_check(check_results=failed_checks, check_id="CKV_AWS_194", policy_name="AppSyncFieldLevelLogs", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_193_AppSyncLogging():
    run_check(check_results=failed_checks, check_id="CKV_AWS_193", policy_name="AppSyncLogging", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_82_AthenaWorkgroupConfiguration():
    # need to wait for variable rendering in TS
    run_check(check_results=failed_checks, check_id="CKV_AWS_82", policy_name="AthenaWorkgroupConfiguration", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_131_AmazonMQBrokerPublicAccess():
    run_check(check_results=failed_checks, check_id="CKV_AWS_131", policy_name="AmazonMQBrokerPublicAccess", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_96_AuroraEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_96", policy_name="ALBDropHttpHeaders", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_166_BackupVaultEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_166", policy_name="BackupVaultEncrypted", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_174_CloudFrontTLS12():
    run_check(check_results=failed_checks, check_id="CKV_AWS_174", policy_name="CloudFrontTLS12", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_36_CloudTrailLogValidation():
    run_check(check_results=failed_checks, check_id="CKV_AWS_36", policy_name="CloudTrailLogValidation", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_20_S3PublicACLRead():
    run_check(check_results=failed_checks, check_id="CKV_AWS_20", policy_name="S3PublicACLRead", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_56_S3RestrictPublicBuckets():
    run_check(check_results=failed_checks, check_id="CKV_AWS_56", policy_name="S3RestrictPublicBuckets", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_149_SecretManagerSecretEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_149", policy_name="S3RestrictPublicBuckets", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_23_SecurityGroupRuleDescription():
    run_check(check_results=failed_checks, check_id="CKV_AWS_23", policy_name="SecurityGroupRuleDescription", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_26_SNSTopicEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_26", policy_name="SNSTopicEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_27_SQSQueueEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_27", policy_name="SQSQueueEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_164_TransferServerIsPublic():
    run_check(check_results=failed_checks, check_id="CKV_AWS_164", policy_name="TransferServerIsPublic", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_123_VPCEndpointAcceptanceConfigured():
    run_check(check_results=failed_checks, check_id="CKV_AWS_123", policy_name="VPCEndpointAcceptanceConfigured", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_68_WAFEnabled():
    run_check(check_results=failed_checks, check_id="CKV_AWS_68", policy_name="WAFEnabled", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_156_WorkspaceRootVolumeEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_156", policy_name="WorkspaceRootVolumeEncrypted", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_155_WorkspaceUserVolumeEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_155", policy_name="WorkspaceUserVolumeEncrypted", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_88_EC2PublicIP():
    run_check(check_results=failed_checks, check_id="CKV_AWS_88", policy_name="EC2PublicIP", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_163_ECRImageScanning():
    run_check(check_results=failed_checks, check_id="CKV_AWS_163", policy_name="ECRImageScanning",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_51_ECRImmutableTags():
    run_check(check_results=failed_checks, check_id="CKV_AWS_51", policy_name="ECRImmutableTags", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_136_ECRRepositoryEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_136", policy_name="ECRRepositoryEncrypted",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_65_ECSClusterContainerInsights():
    run_check(check_results=failed_checks, check_id="CKV_AWS_65", policy_name="ECSClusterContainerInsights",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_97_ECSTaskDefinitionEFSVolumeEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_97", policy_name="ECSClusterContainerInsights",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_42_EFSEncryptionEnabled():
    run_check(check_results=failed_checks, check_id="CKV_AWS_42", policy_name="EFSEncryptionEnabled",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_58_EKSSecretsEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_58", policy_name="EKSSecretsEncryption",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_29_ElasticacheReplicationGroupEncryptionAtRest():
    run_check(check_results=failed_checks, check_id="CKV_AWS_29",
              policy_name="ElasticacheReplicationGroupEncryptionAtRest", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_30_ElasticacheReplicationGroupEncryptionAtTransit():
    run_check(check_results=failed_checks, check_id="CKV_AWS_30",
              policy_name="ElasticacheReplicationGroupEncryptionAtTransit",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_31_ElasticacheReplicationGroupEncryptionAtTransitAuthToken():
    run_check(check_results=failed_checks, check_id="CKV_AWS_31",
              policy_name="ElasticacheReplicationGroupEncryptionAtTransitAuthToken",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_83_ElasticsearchDomainEnforceHTTPS():
    run_check(check_results=failed_checks, check_id="CKV_AWS_83", policy_name="ElasticsearchDomainEnforceHTTPS",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_84_ElasticsearchDomainLogging():
    run_check(check_results=failed_checks, check_id="CKV_AWS_84", policy_name="ElasticsearchDomainLogging",
              language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_91_ELBAccessLogs():
    run_check(check_results=failed_checks, check_id="CKV_AWS_91", policy_name="ELBAccessLogs", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_92_ELBv2AccessLogs():
    run_check(check_results=failed_checks, check_id="CKV_AWS_92", policy_name="ELBv2AccessLogs", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_158_CloudWatchLogGroupKMSKey():
    run_check(check_results=failed_checks, check_id="CKV_AWS_158", policy_name="CloudWatchLogGroupKMSKey", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def test_CKV_AWS_66_CloudWatchLogGroupRetention():
    run_check(check_results=failed_checks, check_id="CKV_AWS_66", policy_name="CloudWatchLogGroupRetention", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_34_CloudfrontDistributionEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_34", policy_name="CloudfrontDistributionEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_86_CloudfrontDistributionLogging():
    run_check(check_results=failed_checks, check_id="CKV_AWS_86", policy_name="CloudfrontDistributionLogging", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_35_CloudtrailEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_35", policy_name="CloudtrailEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_67_CloudtrailMultiRegion():
    run_check(check_results=failed_checks, check_id="CKV_AWS_67", policy_name="CloudtrailMultiRegion", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_78_CodeBuildProjectEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_78", policy_name="CodeBuildProjectEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_47_DAXEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_47", policy_name="DAXEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_89_DMSReplicationInstancePubliclyAccessible():
    run_check(check_results=failed_checks, check_id="CKV_AWS_89", policy_name="DMSReplicationInstancePubliclyAccessible", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_104_DocDBAuditLogs():
    run_check(check_results=failed_checks, check_id="CKV_AWS_104", policy_name="DocDBAuditLogs", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_74_DocDBEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_74", policy_name="DocDBEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_90_DocDBTLS():
    run_check(check_results=failed_checks, check_id="CKV_AWS_90", policy_name="DocDBTLS", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_165_DynamodbGlobalTableRecovery():
    run_check(check_results=failed_checks, check_id="CKV_AWS_165", policy_name="DynamodbGlobalTableRecovery", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_28_DynamodbRecovery():
    run_check(check_results=failed_checks, check_id="CKV_AWS_28", policy_name="DynamodbRecovery", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_3_EBSEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_3", policy_name="EBSEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_5_ElasticsearchEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_5", policy_name="ElasticsearchEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_6_ElasticsearchNodeToNodeEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_6", policy_name="ElasticsearchNodeToNodeEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_94_GlueDataCatalogEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_94", policy_name="GlueDataCatalogEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_99_GlueSecurityConfiguration():
    run_check(check_results=failed_checks, check_id="CKV_AWS_99", policy_name="GlueSecurityConfiguration", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_195_GlueSecurityConfigurationEnabled():
    run_check(check_results=failed_checks, check_id="CKV_AWS_195", policy_name="GlueSecurityConfigurationEnabled", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_40_IAMPolicyAttachedToGroupOrRoles():
    run_check(check_results=failed_checks, check_id="CKV_AWS_40", policy_name="IAMPolicyAttachedToGroupOrRoles", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_43_KinesisStreamEncryptionType():
    run_check(check_results=failed_checks, check_id="CKV_AWS_43", policy_name="KinesisStreamEncryptionType", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_116_LambdaDLQConfigured():
    run_check(check_results=failed_checks, check_id="CKV_AWS_116", policy_name="LambdaDLQConfigured", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_45_LambdaEnvironmentCredentials():
    run_check(check_results=failed_checks, check_id="CKV_AWS_45", policy_name="LambdaEnvironmentCredentials", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_173_LambdaEnvironmentEncryptionSettings():
    run_check(check_results=failed_checks, check_id="CKV_AWS_173", policy_name="LambdaEnvironmentEncryptionSettings", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_115_LambdaFunctionLevelConcurrentExecutionLimit():
    run_check(check_results=failed_checks, check_id="CKV_AWS_115", policy_name="LambdaFunctionLevelConcurrentExecutionLimit", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_117_LambdaInVPC():
    run_check(check_results=failed_checks, check_id="CKV_AWS_117", policy_name="LambdaInVPC", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_8_LaunchConfigurationEBSEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_8", policy_name="LaunchConfigurationEBSEncryption", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_44_NeptuneClusterStorageEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_44", policy_name="NeptuneClusterStorageEncrypted", language="typescript")


@pytest.mark.skip(reason="Not supported yet")
def CKV_AWS_118_RDSEnhancedMonitorEnabled():
    run_check(check_results=failed_checks, check_id="CKV_AWS_118", policy_name="RDSEnhancedMonitorEnabled", language="typescript")
