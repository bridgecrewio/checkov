from pathlib import Path

from checkov.terraform_json.parser import handle_block_type, hclify, parse, prepare_definition

EXAMPLES_DIR = Path(__file__).parent / "examples"


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


def test_handle_block_type_provider_single_dict_config():
    """Provider config as a single dict (not wrapped in a list) should be handled without crashing.

    When a provider has a single configuration in .tf.json, the HCL JSON spec allows it
    as a plain dict. The parser must normalize it to a list before iterating, otherwise
    iterating a dict yields its keys (strings) and hclify() crashes with
    'Exception: this method receives only dicts'.
    """
    # given — provider name maps to a dict (not a list)
    blocks = {"artifactory": {"url": "https://example.com", "access_token": "token123"}}

    # when / then — should NOT crash, should return valid parsed result
    result = handle_block_type(block_type="provider", blocks=blocks)

    assert isinstance(result, list)
    assert len(result) == 1
    assert "artifactory" in result[0]
    # The inner dict should be hclified (values wrapped in lists)
    assert result[0]["artifactory"] == {
        "url": ["https://example.com"],
        "access_token": ["token123"],
    }


def test_handle_block_type_provider_list_config():
    """Provider config as a list of dicts (the existing working case).

    This should continue to work — it's the format the current code already handles.
    """
    # given — provider name maps to a list of dicts
    blocks = {"aws": [{"region": "us-east-1"}, {"alias": "west", "region": "us-west-2"}]}

    # when
    result = handle_block_type(block_type="provider", blocks=blocks)

    # then
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {"aws": {"region": ["us-east-1"]}}
    assert result[1] == {"aws": {"alias": ["west"], "region": ["us-west-2"]}}


def test_parse_provider_single_dict_config_file():
    """End-to-end parse of a .tf.json file where a provider config is a plain dict.

    This exercises the full parse → loads → prepare_definition → handle_block_type pipeline
    with the single-dict provider crash scenario.
    """
    # given
    fixture = EXAMPLES_DIR / "provider_single_dict.tf.json"

    # when
    template, file_lines = parse(file_path=fixture)

    # then — should not crash and should return a valid template
    assert template is not None
    assert file_lines is not None

    # Provider block should be parsed correctly
    assert "provider" in template
    provider_blocks = template["provider"]
    assert isinstance(provider_blocks, list)
    assert len(provider_blocks) == 1
    assert "artifactory" in provider_blocks[0]
    assert provider_blocks[0]["artifactory"]["url"] == ["https://example.com"]
    assert provider_blocks[0]["artifactory"]["access_token"] == ["token123"]

    # Resource block should also be parsed correctly
    assert "resource" in template
    resource_blocks = template["resource"]
    assert isinstance(resource_blocks, list)
    assert len(resource_blocks) == 1
    assert "aws_instance" in resource_blocks[0]


def test_parse_provider_array_of_objects_file():
    """End-to-end parse of a .tf.json file where provider is a top-level array of objects.

    The HCL JSON spec also allows:
      "provider": [{"aws": {"region": "us-east-1"}}, {"aws": {...}}]
    This is a different format from the dict-of-lists format and exercises another code path.
    """
    # given
    fixture = EXAMPLES_DIR / "provider_top_level_array.tf.json"

    # when
    template, file_lines = parse(file_path=fixture)

    # then — should not crash and should return a valid template
    assert template is not None
    assert file_lines is not None

    # Provider block should be parsed correctly
    assert "provider" in template
    provider_blocks = template["provider"]
    assert isinstance(provider_blocks, list)
    assert len(provider_blocks) == 2
    assert "aws" in provider_blocks[0]
    assert provider_blocks[0]["aws"]["region"] == ["us-east-1"]
    assert "aws" in provider_blocks[1]
    assert provider_blocks[1]["aws"]["region"] == ["us-west-2"]
    assert provider_blocks[1]["aws"]["alias"] == ["west"]


def test_parse_provider_array_with_null_values():
    """End-to-end parse of a .tf.json file where provider is a top-level array with null values.

    The HCL JSON spec allows null values in provider configurations:
      "provider": [{"aws": {"region": "us-west-2", "profile": null}}]
    The parser must preserve null as [None] after hclification.
    """
    # given
    fixture = EXAMPLES_DIR / "provider_array_with_null.tf.json"

    # when
    template, file_lines = parse(file_path=fixture)

    # then — should not crash and should return a valid template
    assert template is not None
    assert file_lines is not None

    # Provider block should be parsed correctly
    assert "provider" in template
    provider_blocks = template["provider"]
    assert isinstance(provider_blocks, list)
    assert len(provider_blocks) == 1
    assert "aws" in provider_blocks[0]
    assert provider_blocks[0]["aws"]["region"] == ["us-west-2"]
    assert provider_blocks[0]["aws"]["profile"] == [None]

    # Resource block should also be parsed correctly
    assert "resource" in template
    resource_blocks = template["resource"]
    assert isinstance(resource_blocks, list)
    assert len(resource_blocks) == 1
    assert "aws_instance" in resource_blocks[0]
