from pathlib import Path

import pytest

from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType

from checkov.common.util.consts import START_LINE, END_LINE
from checkov.terraform.graph_manager import TerraformGraphManager
from checkov.terraform_json.parser import parse

EXAMPLES_DIR = Path(__file__).parent / "examples"


@pytest.mark.parametrize(
    "graph_connector",
    [
        NetworkxConnector,
        IgraphConnector,
    ],
)
def test_build_graph_from_definitions(graph_connector):
    # given
    test_file = EXAMPLES_DIR / "cdk.tf.json"
    graph_manager = TerraformGraphManager(db_connector=graph_connector(), source="Terraform")
    template, _ = parse(file_path=test_file)

    # when
    local_graph = graph_manager.build_graph_from_definitions(
        definitions={str(test_file): template}, render_variables=True
    )

    # then
    assert len(local_graph.vertices) == 5

    bucket_idx = local_graph.vertices_block_name_map["resource"]["aws_s3_bucket.bucket"][0]
    bucket = local_graph.vertices[bucket_idx]

    assert bucket.block_type == BlockType.RESOURCE
    assert bucket.id == "aws_s3_bucket.bucket"
    assert bucket.source == "Terraform"
    assert bucket.attributes[CustomAttributes.RESOURCE_TYPE] == ["aws_s3_bucket"]
    assert bucket.attributes[START_LINE] == 34
    assert bucket.attributes[END_LINE] == 53
    assert bucket.config == {
        "aws_s3_bucket": {
            "bucket": {
                "//": {
                    "checkov": {
                        "skip": [
                            {
                                "comment": "Access logging not needed",
                                "id": "CKV_AWS_18",
                                "__startline__": 38,
                                "__endline__": 41,
                            }
                        ],
                        "__startline__": 36,
                        "__endline__": 43,
                    },
                    "metadata": {
                        "path": "AppStack/bucket",
                        "uniqueId": "bucket",
                        "__startline__": 44,
                        "__endline__": 47,
                    },
                    "__startline__": 35,
                    "__endline__": 48,
                },
                "tags": [
                    {
                        "Name": "example",
                        "Private": "true",
                        "__startline__": 49,
                        "__endline__": 52,
                    }
                ],
                "__startline__": 34,
                "__endline__": 53,
                "__address__": "aws_s3_bucket.bucket",
            }
        }
    }
