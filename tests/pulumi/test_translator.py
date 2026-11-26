from __future__ import annotations

from typing import Any

import pytest

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.pulumi.mappings import camel_to_snake, get_resource_mapping
from checkov.pulumi.translator import PulumiResource, translate_resources

STACK = "urn:pulumi:dev::project::"
UNKNOWN = "04da6b54-80e4-46f7-96ec-b56ff0331ba9"
# Pulumi secrets, with '--show-secrets' and without
SECRET = {"4dabf18193072939515e22adb298388d": "1b47061264138c4ac30d75fd1eb44270", "plaintext": '"s3cr3t"'}
ENCRYPTED_SECRET = {"4dabf18193072939515e22adb298388d": "1b47061264138c4ac30d75fd1eb44270", "ciphertext": "AAABA..."}
SECRET_OUTPUT = {"4dabf18193072939515e22adb298388d": "d0e6a833031e9bbcd3f4e8bde6ca49a4", "value": "s3cr3t", "secret": True}


def resource(resource_type: str, name: str, inputs: dict[str, Any], **kwargs: Any) -> PulumiResource:
    return PulumiResource(urn=f"{STACK}{resource_type}::{name}", type=resource_type, inputs=inputs, **kwargs)


def translate_single(res: PulumiResource) -> tuple[str, str, dict[str, Any]]:
    definition = translate_resources([res])
    assert len(definition["resource"]) == 1
    tf_type, block = next(iter(definition["resource"][0].items()))
    name, conf = next(iter(block.items()))
    return tf_type, name, conf


@pytest.mark.parametrize(
    "name,expected",
    [
        ("bucket", "bucket"),
        ("blockPublicAcls", "block_public_acls"),
        ("ipv6CidrBlocks", "ipv6_cidr_blocks"),
        ("kmsKeyId", "kms_key_id"),
        ("s3BucketName", "s3_bucket_name"),
    ],
)
def test_camel_to_snake(name: str, expected: str) -> None:
    assert camel_to_snake(name) == expected


@pytest.mark.parametrize(
    "token,tf_type",
    [
        ("aws:s3/bucket:Bucket", "aws_s3_bucket"),
        ("aws:s3/bucketV2:BucketV2", "aws_s3_bucket"),  # alias of an older major version
        ("gcp:storage/bucket:Bucket", "google_storage_bucket"),
        ("azure:storage/account:Account", "azurerm_storage_account"),
    ],
)
def test_resource_mapping(token: str, tf_type: str) -> None:
    mapping = get_resource_mapping(token)

    assert mapping and mapping["type"] == tf_type


@pytest.mark.parametrize(
    "token",
    [
        "pulumi:pulumi:Stack",
        "random:index/randomPet:RandomPet",
        "azure-native:storage:StorageAccount",
        "kubernetes:apps/v1:Deployment",
        "aws:not/existing:Resource",
    ],
)
def test_unsupported_resources_are_skipped(token: str) -> None:
    definition = translate_resources([resource(token, "test", {"name": "test"})])

    assert definition["resource"] == []


def test_keys_are_converted() -> None:
    tf_type, name, conf = translate_single(
        resource(
            "aws:s3/bucketPublicAccessBlock:BucketPublicAccessBlock",
            "pab",
            {"__defaults": [], "bucket": "my-bucket", "blockPublicAcls": True, "restrictPublicBuckets": False},
        )
    )

    assert tf_type == "aws_s3_bucket_public_access_block"
    assert name == "pab"
    assert conf["bucket"] == ["my-bucket"]
    assert conf["block_public_acls"] == [True]
    assert conf["restrict_public_buckets"] == [False]
    assert "__defaults" not in conf
    assert conf[CustomAttributes.TF_RESOURCE_ADDRESS] == "aws_s3_bucket_public_access_block.pab"


def test_plural_and_renamed_fields() -> None:
    _, _, conf = translate_single(
        resource(
            "aws:lambda/function:Function",
            "fn",
            {
                "name": "my-function",
                "code": {"4dabf18193072939515e22adb298388d": "0def7320c3a5731c473e5ecbe6d01bc7", "path": "./app"},
                "layers": ["arn:aws:lambda:us-east-1:123456789012:layer:layer:1"],
            },
        )
    )

    assert conf["function_name"] == ["my-function"]
    assert conf["filename"] == ["./app"]
    assert conf["layers"] == [["arn:aws:lambda:us-east-1:123456789012:layer:layer:1"]]

    _, _, conf = translate_single(
        resource(
            "aws:ec2/securityGroup:SecurityGroup",
            "sg",
            {"ingress": [{"__defaults": [], "fromPort": 22, "toPort": 22, "cidrBlocks": ["0.0.0.0/0"]}]},
        )
    )

    ingress = conf["ingress"][0]
    assert ingress["from_port"] == [22]
    assert ingress["cidr_blocks"] == [["0.0.0.0/0"]]
    assert "__defaults" not in ingress


def test_max_items_one_fields_become_lists() -> None:
    _, _, conf = translate_single(
        resource(
            "aws:ec2/instance:Instance",
            "vm",
            {"metadataOptions": {"httpTokens": "optional"}, "rootBlockDevice": {"encrypted": False}},
        )
    )

    assert conf["metadata_options"] == [{"http_tokens": ["optional"]}]
    assert conf["root_block_device"] == [{"encrypted": [False]}]


def test_maps_keep_their_keys() -> None:
    _, _, conf = translate_single(
        resource(
            "aws:s3/bucket:Bucket",
            "bucket",
            {"tags": {"Environment": "dev", "CostCenter": "42"}, "tagsAll": {"Environment": "dev"}},
        )
    )

    assert conf["tags"] == [{"Environment": "dev", "CostCenter": "42"}]
    # same as in a Terraform plan, only "tags" values are not wrapped
    assert conf["tags_all"] == [{"Environment": ["dev"]}]


def test_unknown_and_secret_values() -> None:
    _, _, conf = translate_single(
        resource(
            "aws:rds/instance:Instance",
            "db",
            {
                "identifier": UNKNOWN,
                "password": SECRET,
                "username": "[secret]",
                "kmsKeyId": ENCRYPTED_SECRET,
                "masterUserSecretKmsKeyId": SECRET_OUTPUT,
                "engine": "mysql",
            },
        )
    )

    assert "identifier" not in conf
    # secrets are set, but their values are not part of the results
    assert conf["password"] == ["[secret]"]
    assert conf["username"] == ["[secret]"]
    assert conf["kms_key_id"] == ["[secret]"]
    assert conf["master_user_secret_kms_key_id"] == ["[secret]"]
    assert conf["engine"] == ["mysql"]


def test_names_are_sanitized_and_unique() -> None:
    definition = translate_resources(
        [
            resource("aws:s3/bucket:Bucket", "my.bucket/1", {}),
            PulumiResource(
                urn=f"{STACK}my:component$aws:s3/bucket:Bucket::my.bucket/1", type="aws:s3/bucket:Bucket", inputs={}
            ),
        ]
    )

    addresses = [next(iter(r["aws_s3_bucket"].values()))[CustomAttributes.TF_RESOURCE_ADDRESS] for r in definition["resource"]]
    assert addresses == ["aws_s3_bucket.my_bucket_1", "aws_s3_bucket.my_bucket_1_2"]


def test_property_dependencies_become_references() -> None:
    bucket = resource("aws:s3/bucket:Bucket", "bucket", {"bucket": "my-bucket"})
    pab = resource(
        "aws:s3/bucketPublicAccessBlock:BucketPublicAccessBlock",
        "pab",
        # unknown during the creation, known for existing resources
        {"bucket": UNKNOWN, "blockPublicAcls": True},
        property_dependencies={"bucket": [bucket.urn], "blockPublicAcls": []},
    )
    existing_pab = resource(
        "aws:s3/bucketPublicAccessBlock:BucketPublicAccessBlock",
        "existing",
        {"bucket": "my-bucket"},
        property_dependencies={"bucket": [bucket.urn]},
    )

    definition = translate_resources([bucket, pab, existing_pab])

    new_conf, existing_conf = (next(iter(e["aws_s3_bucket_public_access_block"].values())) for e in definition["resource"][1:])
    # unknown values are replaced by the reference, known values are kept
    assert new_conf["bucket"] == ["aws_s3_bucket.bucket.id"]
    assert existing_conf["bucket"] == ["my-bucket"]
    for conf in (new_conf, existing_conf):
        assert conf[CustomAttributes.REFERENCES] == [["aws_s3_bucket.bucket.id", "aws_s3_bucket.bucket"]]


def test_known_values_with_dependencies_are_checked() -> None:
    bucket = resource("aws:s3/bucket:Bucket", "bucket", {"bucket": "my-bucket"})
    policy = resource(
        "aws:iam/policy:Policy",
        "policy",
        {"policy": '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}'},
        property_dependencies={"policy": [bucket.urn]},
    )

    definition = translate_resources([bucket, policy])

    conf = definition["resource"][1]["aws_iam_policy"]["policy"]
    assert conf["policy"] == [{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}]


def test_null_and_name_edge_cases() -> None:
    _, name, conf = translate_single(
        PulumiResource(
            urn=f"{STACK}aws:s3/bucket:Bucket::my::bucket", type="aws:s3/bucket:Bucket", inputs={"logging": None}
        )
    )

    assert name == "my__bucket"
    # same as a null value in a Terraform plan
    assert conf["logging"] == [None]


def test_policy_objects_become_json() -> None:
    _, _, conf = translate_single(
        resource("aws:iam/role:Role", "role", {"assumeRolePolicy": {"Version": "2012-10-17", "Statement": []}})
    )

    assert conf["assume_role_policy"] == [{"Version": "2012-10-17", "Statement": []}]


def test_providers() -> None:
    definition = translate_resources(
        [
            PulumiResource(
                urn="urn:pulumi:::pulumi:providers:aws::default",
                type="pulumi:providers:aws",
                inputs={"region": "us-east-1", "accessKey": "AKIA" + "IOSFODNN7EXAMPLE", "skipMetadataApiCheck": "true"},
                start_line=2,
                end_line=6,
            ),
            resource("pulumi:providers:gcp", "west", {"project": "my-project", "version": "9.0.0"}),
            resource("pulumi:providers:random", "default_4_0_0", {}),
            resource("pulumi:providers:aws", "default-west", {"region": "us-west-2"}),
        ]
    )

    aws, gcp, aws_west = definition["provider"]
    # explicit providers, which start with 'default' are not the default provider
    assert aws_west["aws"][CustomAttributes.TF_RESOURCE_ADDRESS] == "aws.default-west"
    assert aws["aws"]["region"] == ["us-east-1"]
    assert aws["aws"]["access_key"] == ["AKIA" + "IOSFODNN7EXAMPLE"]
    assert aws["aws"]["skip_metadata_api_check"] == [True]
    assert aws["aws"]["alias"] == ["default"]
    assert aws["aws"][CustomAttributes.TF_RESOURCE_ADDRESS] == "aws.default"
    assert aws["aws"]["start_line"] == [2]
    assert gcp["google"]["project"] == ["my-project"]
    assert "version" not in gcp["google"]
    assert gcp["google"][CustomAttributes.TF_RESOURCE_ADDRESS] == "google.west"
