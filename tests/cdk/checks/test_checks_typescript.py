from tests.cdk.checks.utils import run_check


def run(check_name: str) -> None:
    run_check(check_name=check_name, lang="typescript")


def test_CKV_AWS_18_S3BucketLogging():
    run(check_name="S3BucketLogging")


def test_CKV_AWS_19_S3BucketEncryption():
    run(check_name="S3BucketEncryption")


def test_CKV_AWS_21_S3BucketVersioning():
    run(check_name="S3BucketVersioning")


def test_CKV_AWS_145_S3BucketKMSEncryption():
    run(check_name="S3BucketKMSEncryption")


def test_CKV2_AWS_6_S3BucketPublicAccessBlock():
    run(check_name="S3BucketPublicAccessBlock")
