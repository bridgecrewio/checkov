from cdk_integration_tests.utils import run_check
import pytest


@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_18_S3BucketLogging():
    run_check(lang="typescript", check_name="S3BucketLogging")


@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_19_S3BucketEncryption():
    run_check(lang="typescript", check_name="S3BucketEncryption")


@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_21_S3BucketVersioning():
    run_check(lang="typescript", check_name="S3BucketVersioning")


@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV_AWS_145_S3BucketKMSEncryption():
    run_check(lang="typescript", check_name="S3BucketKMSEncryption")


@pytest.mark.skip(reason="Typescript not supported yet")
def test_CKV2_AWS_6_S3BucketPublicAccessBlock():
    run_check(lang="typescript", check_name="S3BucketPublicAccessBlock")

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