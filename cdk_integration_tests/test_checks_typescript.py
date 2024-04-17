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
