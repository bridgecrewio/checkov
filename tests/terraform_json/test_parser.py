from checkov.terraform.plan_parser import _sanitize_count_from_name
from checkov.terraform_json.parser import hclify, prepare_definition


def test_hclify():
    # given
    bucket_version = {
        "//": {
            "metadata": {
                "path": "AppStack/bucket_version",
                "uniqueId": "bucket_version",
            }
        },
        "bucket": "${aws_s3_bucket.bucket.bucket}",
        "versioning_configuration": {
            "status": "Enabled",
        },
    }

    # when
    result = hclify(obj=bucket_version)

    # then
    assert result == {
        "//": {
            "metadata": {
                "path": "AppStack/bucket_version",
                "uniqueId": "bucket_version",
            }
        },
        "bucket": ["${aws_s3_bucket.bucket.bucket}"],
        "versioning_configuration": [
            {
                "status": ["Enabled"],
            }
        ],
    }


def test_prepare_definition_locals():
    cdk_definition = {
        "locals": {
            "bucket_name": "example",
            "http_endpoint": "disabled",
            "__startline__": 1,
            "__endline__": 2,
        }
    }

    # when
    tf_definition = prepare_definition(cdk_definition)

    # then
    assert tf_definition == {
        "locals": [
            {
                "bucket_name": ["example"],
                "http_endpoint": ["disabled"],
                "__startline__": 1,
                "__endline__": 2,
            }
        ]
    }


def test__sanitize_count_from_name_with_count():
    # given
    name = "aws_s3_bucket.bucket[0]"

    # when
    result = _sanitize_count_from_name(name)

    # then
    assert result == "aws_s3_bucket.bucket"


def test__sanitize_count_from_name_with_no_count():
    # given
    name = "aws_s3_bucket.bucket"

    # when
    result = _sanitize_count_from_name(name)

    # then
    assert result == "aws_s3_bucket.bucket"
