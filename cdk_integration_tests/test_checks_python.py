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
