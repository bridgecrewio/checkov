from cdk_integration_tests.utils import run_check
import pytest

def test_ALBDropHttpHeaders():
    run_check(lang="typescript", check_name="ALBDropHttpHeaders")

@pytest.mark.skip(reason="Not supported yet")
def test_S3BucketEncryption():
    run_check(lang="typescript", check_name="S3BucketEncryption")

@pytest.mark.skip(reason="Not supported yet")
def test_S3BucketKMSEncryption():
    run_check(lang="typescript", check_name="S3BucketKMSEncryption")

@pytest.mark.skip(reason="Not supported yet")
def test_S3BucketLogging():
    run_check(lang="typescript", check_name="S3BucketLogging")

@pytest.mark.skip(reason="Not supported yet")
def test_S3BucketPublicAccessBlock():
    run_check(lang="typescript", check_name="S3BucketPublicAccessBlock")

@pytest.mark.skip(reason="Not supported yet")
def test_S3BucketVersioning():
    run_check(lang="typescript", check_name="S3BucketVersioning")

def test_S3PublicACLRead():
    run_check(lang="typescript", check_name="S3PublicACLRead")

def test_S3RestrictPublicBuckets():
    run_check(lang="typescript", check_name="S3RestrictPublicBuckets")

def test_SecretManagerSecretEncrypted():
    run_check(lang="typescript", check_name="SecretManagerSecretEncrypted")

def test_SecurityGroupRuleDescription():
    run_check(lang="typescript", check_name="SecurityGroupRuleDescription")

def test_SNSTopicEncryption():
    run_check(lang="typescript", check_name="SNSTopicEncryption")

def test_SQSQueueEncryption():
    run_check(lang="typescript", check_name="SQSQueueEncryption")

def test_TransferServerIsPublic():
    run_check(lang="typescript", check_name="TransferServerIsPublic")

def test_VPCEndpointAcceptanceConfigured():
    run_check(lang="typescript", check_name="VPCEndpointAcceptanceConfigured")
   
def test_WAFEnabled():
    run_check(lang="typescript", check_name="WAFEnabled")

def test_WorkspaceRootVolumeEncrypted():
    run_check(lang="typescript", check_name="WorkspaceRootVolumeEncrypted")

def test_WorkspaceUserVolumeEncrypted():
    run_check(lang="typescript", check_name="WorkspaceUserVolumeEncrypted")
