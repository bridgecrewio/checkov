from checkov.terraform_json.parser import hclify


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
