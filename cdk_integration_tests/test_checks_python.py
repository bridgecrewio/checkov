from cdk_integration_tests.utils import run_check


def test_CKV_AWS_18_S3BucketLogging():
    run_check(lang='python', check_name="S3BucketLogging")


def test_CKV_AWS_19_S3BucketEncryption():
    run_check(lang='python', check_name="S3BucketEncryption")


def test_CKV_AWS_21_S3BucketVersioning():
    run_check(lang='python', check_name="S3BucketVersioning")


def test_CKV_AWS_145_S3BucketKMSEncryption():
    run_check(lang='python', check_name="S3BucketKMSEncryption")


def test_CKV2_AWS_6_S3BucketPublicAccessBlock():
    run_check(lang='python', check_name="S3BucketPublicAccessBlock")


def test_CKV_AWS_54_S3BlockPublicPolicy():
    run_check(lang='python', check_name="S3BlockPublicPolicy")


def test_CKV_AWS_26_SNSTopicEncryption():
    run_check(lang='python', check_name="SNSTopicEncryption")


def test_CKV_AWS_20_S3PublicACLRead():
    run_check(lang='python', check_name="S3PublicACLRead")


def test_CKV_AWS_55_S3IgnorePublicACLs():
    run_check(lang='python', check_name="S3IgnorePublicACLs")


def test_CKV_AWS_56_S3RestrictPublicBuckets():
    run_check(lang='python', check_name="S3RestrictPublicBuckets")


def test_CKV_AWS_53_S3BlockPublicACLs():
    run_check(lang='python', check_name="S3BlockPublicACLs")


def test_CKV_AWS_57_S3PublicACLWrite():
    run_check(lang='python', check_name="S3PublicACLWrite")


def test_CKV_AWS_115_LambdaFunctionLevelConcurrentExecutionLimit():
    run_check(lang='python', check_name="LambdaFunctionLevelConcurrentExecutionLimit")


def test_CKV_AWS_116_LambdaDLQConfigured():
    run_check(lang='python', check_name="LambdaDLQConfigured")


def test_CKV_AWS_28_DynamodbRecovery():
    run_check(lang='python', check_name="DynamodbRecovery")


def test_CKV_AWS_158_CloudWatchLogGroupKMSKey():
    run_check(lang='python', check_name="CloudWatchLogGroupKMSKey")


def test_CKV_AWS_3_EBSEncryption():
    run_check(lang='python', check_name="EBSEncryption")


def test_CKV_AWS_120_APIGatewayCacheEnable():
    run_check(lang='python', check_name="APIGatewayCacheEnable")


def test_CKV_AWS_163_ECRImageScanning():
    run_check(lang='python', check_name="ECRImageScanning")


def test_CKV_AWS_51_ECRImmutableTags():
    run_check(lang='python', check_name="ECRImmutableTags")


def test_CKV_AWS_44_NeptuneClusterStorageEncrypted():
    run_check(lang='python', check_name="NeptuneClusterStorageEncrypted")


def test_CKV_AWS_166_BackupVaultEncrypted():
    run_check(lang='python', check_name="BackupVaultEncrypted")


def test_CKV_AWS_74_DocDBEncryption():
    run_check(lang='python', check_name="DocDBEncryption")


def test_CKV_AWS_47_DAXEncryption():
    run_check(lang='python', check_name="DAXEncryption")


def test_CKV_AWS_156_WorkspaceRootVolumeEncrypted():
    run_check(lang='python', check_name="WorkspaceRootVolumeEncrypted")


def test_CKV_AWS_155_WorkspaceUserVolumeEncrypted():
    run_check(lang='python', check_name="WorkspaceUserVolumeEncrypted")


def test_CKV_AWS_165_DynamodbGlobalTableRecovery():
    run_check(lang='python', check_name="DynamodbGlobalTableRecovery")


def test_CKV_AWS_27_SQSQueueEncryption():
    run_check(lang='python', check_name="SQSQueueEncryption")


def test_CKV_AWS_195_GlueSecurityConfigurationEnabled():
    run_check(lang='python', check_name="GlueSecurityConfigurationEnabled")


def test_CKV_AWS_30_ElasticacheReplicationGroupEncryptionAtTransit():
    run_check(lang='python', check_name="ElasticacheReplicationGroupEncryptionAtTransit")


def test_CKV_AWS_68_WAFEnabled():
    run_check(lang='python', check_name="WAFEnabled")


def test_CKV_AWS_64_RedshiftClusterEncryption():
    run_check(lang='python', check_name="RedshiftClusterEncryption")
