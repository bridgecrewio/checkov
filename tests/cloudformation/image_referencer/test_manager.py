from networkx import DiGraph

from checkov.cloudformation.image_referencer.manager import CloudFormationImageReferencerManager
from checkov.common.images.image_referencer import Image


def test_extract_images_from_resources():
    # given
    aws_resource = {
        "file_path_": "/ecs.yaml",
        "__endline__": 37,
        "__startline__": 5,
        "ContainerDefinitions": [
            {
                "Name": "my-app",
                "Image": "amazon/amazon-ecs-sample",
                "Cpu": 256,
                "EntryPoint": ["/usr/sbin/apache2", "-D", "FOREGROUND"],
                "Memory": 512,
                "Essential": True,
                "__startline__": 10,
                "__endline__": 22,
            },
        ],
        "resource_type": "AWS::ECS::TaskDefinition",
    }
    graph = DiGraph()
    graph.add_node(1, **aws_resource)

    # when
    images = CloudFormationImageReferencerManager(graph_connector=graph).extract_images_from_resources()

    # then
    assert images == [
        Image(file_path="/ecs.yaml", name="amazon/amazon-ecs-sample", start_line=5, end_line=37, related_resource_id="/ecs.yaml:None"),
    ]
