from networkx import DiGraph

from checkov.bicep.image_referencer.manager import BicepImageReferencerManager
from checkov.common.images.image_referencer import Image


def test_extract_images_from_resources():
    # given
    resource = {
        "file_path_": "/batch.bicep",
        "__end_line__": 26,
        "__start_line__": 1,
        "properties": {
            "virtualMachineConfiguration": {
                "containerConfiguration": {
                    "containerImageNames": ["python:3.9-alpine"],
                    "containerRegistries": {
                        "password": "myPassword",
                        "registryServer": "myContainerRegistry.azurecr.io",
                        "username": "myUserName",
                    },
                    "type": "DockerCompatible",
                },
            }
        },
        "resource_type": "Microsoft.Batch/batchAccounts/pools",
    }
    graph = DiGraph()
    graph.add_node(1, **resource)

    # when
    images = BicepImageReferencerManager(graph_connector=graph).extract_images_from_resources()

    # then
    assert images == [
        Image(
            file_path="/batch.bicep",
            name="python:3.9-alpine",
            start_line=1,
            end_line=26,
            related_resource_id="/batch.bicep:None",
        ),
    ]
