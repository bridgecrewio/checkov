from typing import Dict, Any, List

import pytest

from cdk_integration_tests.utils import run_check, load_failed_checks_from_file

LANGUAGE = 'typescript'


@pytest.fixture(scope="session", autouse=True)
def failed_checks() -> Dict[str, List[Dict[str, Any]]]:
    report_failed_checks = load_failed_checks_from_file(LANGUAGE)
    yield report_failed_checks


def test_ALBDropHttpHeaders():
    run_check(check_results=failed_checks, check_id="CKV_AWS_131", policy_name="ALBDropHttpHeaders", language="typescript")


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
    run_check(check_results=failed_checks, check_id="CKV_AWS_20", policy_name="S3PublicACLRead", language="typescript")


def test_S3RestrictPublicBuckets():
    run_check(check_results=failed_checks, check_id="CKV_AWS_56", policy_name="S3RestrictPublicBuckets", language="typescript")


def test_SecretManagerSecretEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_149", policy_name="S3RestrictPublicBuckets", language="typescript")


def test_SecurityGroupRuleDescription():
    run_check(check_results=failed_checks, check_id="CKV_AWS_23", policy_name="SecurityGroupRuleDescription", language="typescript")


def test_SNSTopicEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_26", policy_name="SNSTopicEncryption", language="typescript")


def test_SQSQueueEncryption():
    run_check(check_results=failed_checks, check_id="CKV_AWS_27", policy_name="SQSQueueEncryption", language="typescript")


def test_TransferServerIsPublic():
    run_check(check_results=failed_checks, check_id="CKV_AWS_164", policy_name="TransferServerIsPublic", language="typescript")


def test_VPCEndpointAcceptanceConfigured():
    run_check(check_results=failed_checks, check_id="CKV_AWS_123", policy_name="VPCEndpointAcceptanceConfigured", language="typescript")
   

def test_WAFEnabled():
    run_check(check_results=failed_checks, check_id="CKV_AWS_68", policy_name="WAFEnabled", language="typescript")


def test_WorkspaceRootVolumeEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_156", policy_name="WorkspaceRootVolumeEncrypted", language="typescript")


def test_WorkspaceUserVolumeEncrypted():
    run_check(check_results=failed_checks, check_id="CKV_AWS_155", policy_name="WorkspaceUserVolumeEncrypted", language="typescript")
