from pathlib import Path

from checkov.terraform_json.parser import hclify, loads, prepare_definition


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


def test_prepare_definition_terraform_required_version():
    """CDKTF-generated cdk.tf.json files can have terraform.required_version as a string.

    See https://github.com/bridgecrewio/checkov/issues/7454
    """
    cdk_definition = {
        "terraform": {
            "backend": {
                "local": {
                    "path": "terraform.minimal-stack.tfstate"
                }
            },
            "required_providers": {
                "aws": {
                    "source": "aws",
                    "version": "6.25.0"
                }
            },
            "required_version": ">= 1.5.0"
        }
    }

    # when
    tf_definition = prepare_definition(cdk_definition)

    # then
    assert "terraform" in tf_definition
    terraform_blocks = tf_definition["terraform"]

    # required_version should be stored as a list-wrapped simple value
    required_version_block = next(
        (b for b in terraform_blocks if "required_version" in b), None
    )
    assert required_version_block is not None
    assert required_version_block["required_version"] == [">= 1.5.0"]

    # backend and required_providers should still be handled as dicts
    backend_block = next(
        (b for b in terraform_blocks if "backend" in b), None
    )
    assert backend_block is not None

    required_providers_block = next(
        (b for b in terraform_blocks if "required_providers" in b), None
    )
    assert required_providers_block is not None


def test_loads_cdktf_with_required_version():
    """End-to-end test: loads() should not crash on CDKTF JSON with required_version."""
    file_path = Path(__file__).parent / "examples" / "cdk_with_required_version.tf.json"
    template, file_lines = loads(file_path=file_path)

    assert template is not None
    assert file_lines is not None
    assert "terraform" in template
    assert "resource" in template


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
