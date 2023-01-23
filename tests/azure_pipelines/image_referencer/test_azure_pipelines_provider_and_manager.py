from checkov.common.images.image_referencer import Image
from checkov.azure_pipelines.image_referencer.provider import AzurePipelinesProvider
from checkov.azure_pipelines.image_referencer.manager import AzurePipelinesImageReferencerManager


def test_provider_extract_images_from_workflow():
    file_path = 'tests/azure_pipelines/image_referencer/resources/azure-pipelines.yaml'
    workflow_config = {
    "trigger":
    [
        "master"
    ],
    "resources":
    {
        "repositories":
        [
            {
                "repository": "AzureDevOps",
                "type": "git",
                "endpoint": "AzureDevOps",
                "name": "AzureDevOps/AzureDevOps",
                "__startline__": 6,
                "__endline__": 11
            }
        ],
        "__startline__": 5,
        "__endline__": 11
    },
    "stages":
    [
        {
            "stage": "Example",
            "jobs":
            [
                {
                    "job": "FailNoTag",
                    "displayName": "FailNoTagDisplayName",
                    "pool":
                    {
                        "vmImage": "ubuntu-18.04",
                        "__startline__": 17,
                        "__endline__": 18
                    },
                    "steps":
                    [
                        {
                            "task": "Docker@2",
                            "inputs":
                            {
                                "container": "postgres:14.2",
                                "__startline__": 21,
                                "__endline__": 23
                            },
                            "__startline__": 19,
                            "__endline__": 23
                        }
                    ],
                    "__startline__": 14,
                    "__endline__": 23
                },
                {
                    "job": "PassDigest",
                    "pool":
                    {
                        "vmImage": "ubuntu-18.04",
                        "__startline__": 25,
                        "__endline__": 27
                    },
                    "container": "nginx:1.17",
                    "steps":
                    [
                        {
                            "script": "printenv",
                            "__startline__": 30,
                            "__endline__": 32
                        }
                    ],
                    "__startline__": 23,
                    "__endline__": 32
                }
            ],
            "__startline__": 12,
            "__endline__": 32
        }
    ],
    "jobs":
    [
        {
            "job": "MyJob",
            "container": "ruby:2.6",
            "pool":
            {
                "vmImage": "windows-latest",
                "__startline__": 36,
                "__endline__": 37
            },
            "steps":
            [
                {
                    "script": "echo \"Running in a container based on myorg/mycontainer:1.0\"",
                    "__startline__": 38,
                    "__endline__": 39
                }
            ],
            "__startline__": 33,
            "__endline__": 39
        },
        {
            "job": "MyJob2",
            "container":
            {
                "image": "ruby:2.6",
                "__startline__": 41,
                "__endline__": 42
            },
            "pool":
            {
                "vmImage": "ubuntu-latest",
                "__startline__": 43,
                "__endline__": 44
            },
            "steps":
            [
                {
                    "script": "echo \"Running in a container based on ruby:2.6\"",
                    "__startline__": 45,
                    "__endline__": 45
                }
            ],
            "__startline__": 39,
            "__endline__": 45
        }
    ],
    "__startline__": 1,
    "__endline__": 45
}

    azure_pipelines_provider = AzurePipelinesProvider(workflow_config=workflow_config, file_path=file_path)
    images = azure_pipelines_provider.extract_images_from_workflow()

    assert set(images) == {
        Image(
            end_line=23,
            start_line=21,
            file_path=file_path,
            name='postgres:14.2',
            related_resource_id='stages[0](Example).jobs[0](FailNoTagDisplayName).steps[0].inputs'
        ),
        Image(
            end_line=32,
            start_line=23,
            file_path=file_path,
            name='nginx:1.17',
            related_resource_id='stages[0](Example).jobs[1](PassDigest)'
        ),
        Image(
            end_line=39,
            start_line=33,
            file_path=file_path,
            name='ruby:2.6',
            related_resource_id='jobs[0](MyJob)'
        ),
        Image(
            end_line=45,
            start_line=39,
            file_path=file_path,
            name='ruby:2.6',
            related_resource_id='jobs[1](MyJob2)'
        )
    }

def test_provider_extract_images_from_workflow_no_images():
    file_path = 'tests/azure_pipelines/image_referencer/resources/azure-pipelines.yaml'
    workflow_config = {
    "trigger":
    [
        "master"
    ],
    "resources":
    {
        "repositories":
        [
            {
                "repository": "AzureDevOps",
                "type": "git",
                "endpoint": "AzureDevOps",
                "name": "AzureDevOps/AzureDevOps",
                "__startline__": 6,
                "__endline__": 11
            }
        ],
        "__startline__": 5,
        "__endline__": 11
    },
    "stages":
    [
        {
            "stage": "Example",
            "jobs":
            [
                {
                    "job": "FailNoTag",
                    "displayName": "FailNoTagDisplayName",
                    "pool":
                    {
                        "vmImage": "ubuntu-18.04",
                        "__startline__": 17,
                        "__endline__": 19
                    },
                    "__startline__": 14,
                    "__endline__": 19
                },
                {
                    "job": "PassDigest",
                    "pool":
                    {
                        "vmImage": "ubuntu-18.04",
                        "__startline__": 21,
                        "__endline__": 23
                    },
                    "steps":
                    [
                        {
                            "script": "printenv",
                            "__startline__": 24,
                            "__endline__": 26
                        }
                    ],
                    "__startline__": 19,
                    "__endline__": 26
                }
            ],
            "__startline__": 12,
            "__endline__": 26
        }
    ],
    "jobs":
    [
        {
            "job": "MyJob",
            "pool":
            {
                "vmImage": "windows-latest",
                "__startline__": 29,
                "__endline__": 30
            },
            "steps":
            [
                {
                    "script": "echo \"Running in a container based on myorg/mycontainer:1.0\"",
                    "__startline__": 31,
                    "__endline__": 31
                }
            ],
            "__startline__": 27,
            "__endline__": 31
        }
    ],
    "__startline__": 1,
    "__endline__": 31
}

    azure_pipelines_provider = AzurePipelinesProvider(workflow_config=workflow_config, file_path=file_path)
    images = azure_pipelines_provider.extract_images_from_workflow()

    assert not images

def test_manager_extract_images_from_workflow():
    file_path = 'tests/azure_pipelines/image_referencer/resources/azure-pipelines.yaml'
    workflow_config = {
    "trigger":
    [
        "master"
    ],
    "resources":
    {
        "repositories":
        [
            {
                "repository": "AzureDevOps",
                "type": "git",
                "endpoint": "AzureDevOps",
                "name": "AzureDevOps/AzureDevOps",
                "__startline__": 6,
                "__endline__": 11
            }
        ],
        "__startline__": 5,
        "__endline__": 11
    },
    "stages":
    [
        {
            "stage": "Example",
            "jobs":
            [
                {
                    "job": "FailNoTag",
                    "displayName": "FailNoTagDisplayName",
                    "pool":
                    {
                        "vmImage": "ubuntu-18.04",
                        "__startline__": 17,
                        "__endline__": 18
                    },
                    "steps":
                    [
                        {
                            "task": "Docker@2",
                            "inputs":
                            {
                                "container": "postgres:14.2",
                                "__startline__": 21,
                                "__endline__": 23
                            },
                            "__startline__": 19,
                            "__endline__": 23
                        }
                    ],
                    "__startline__": 14,
                    "__endline__": 23
                },
                {
                    "job": "PassDigest",
                    "pool":
                    {
                        "vmImage": "ubuntu-18.04",
                        "__startline__": 25,
                        "__endline__": 27
                    },
                    "container": "nginx:1.17",
                    "steps":
                    [
                        {
                            "script": "printenv",
                            "__startline__": 30,
                            "__endline__": 32
                        }
                    ],
                    "__startline__": 23,
                    "__endline__": 32
                }
            ],
            "__startline__": 12,
            "__endline__": 32
        }
    ],
    "jobs":
    [
        {
            "job": "MyJob",
            "container": "ruby:2.6",
            "pool":
            {
                "vmImage": "windows-latest",
                "__startline__": 36,
                "__endline__": 37
            },
            "steps":
            [
                {
                    "script": "echo \"Running in a container based on myorg/mycontainer:1.0\"",
                    "__startline__": 38,
                    "__endline__": 39
                }
            ],
            "__startline__": 33,
            "__endline__": 39
        },
        {
            "job": "MyJob2",
            "container":
            {
                "image": "ruby:2.6",
                "__startline__": 41,
                "__endline__": 42
            },
            "pool":
            {
                "vmImage": "ubuntu-latest",
                "__startline__": 43,
                "__endline__": 44
            },
            "steps":
            [
                {
                    "script": "echo \"Running in a container based on ruby:2.6\"",
                    "__startline__": 45,
                    "__endline__": 45
                }
            ],
            "__startline__": 39,
            "__endline__": 45
        }
    ],
    "__startline__": 1,
    "__endline__": 45
}

    manager = AzurePipelinesImageReferencerManager(workflow_config=workflow_config, file_path=file_path)
    images = manager.extract_images_from_workflow()

    assert set(images) == {
        Image(
            end_line=23,
            start_line=21,
            file_path=file_path,
            name='postgres:14.2',
            related_resource_id='stages[0](Example).jobs[0](FailNoTagDisplayName).steps[0].inputs'
        ),
        Image(
            end_line=32,
            start_line=23,
            file_path=file_path,
            name='nginx:1.17',
            related_resource_id='stages[0](Example).jobs[1](PassDigest)'
        ),
        Image(
            end_line=39,
            start_line=33,
            file_path=file_path,
            name='ruby:2.6',
            related_resource_id='jobs[0](MyJob)'
        ),
        Image(
            end_line=45,
            start_line=39,
            file_path=file_path,
            name='ruby:2.6',
            related_resource_id='jobs[1](MyJob2)'
        )
    }

def test_manager_extract_images_from_workflow_no_images():
    file_path = 'tests/azure_pipelines/image_referencer/resources/azure-pipelines.yaml'
    workflow_config = {
    "trigger":
    [
        "master"
    ],
    "resources":
    {
        "repositories":
        [
            {
                "repository": "AzureDevOps",
                "type": "git",
                "endpoint": "AzureDevOps",
                "name": "AzureDevOps/AzureDevOps",
                "__startline__": 6,
                "__endline__": 11
            }
        ],
        "__startline__": 5,
        "__endline__": 11
    },
    "stages":
    [
        {
            "stage": "Example",
            "jobs":
            [
                {
                    "job": "FailNoTag",
                    "displayName": "FailNoTagDisplayName",
                    "pool":
                    {
                        "vmImage": "ubuntu-18.04",
                        "__startline__": 17,
                        "__endline__": 19
                    },
                    "__startline__": 14,
                    "__endline__": 19
                },
                {
                    "job": "PassDigest",
                    "pool":
                    {
                        "vmImage": "ubuntu-18.04",
                        "__startline__": 21,
                        "__endline__": 23
                    },
                    "steps":
                    [
                        {
                            "script": "printenv",
                            "__startline__": 24,
                            "__endline__": 26
                        }
                    ],
                    "__startline__": 19,
                    "__endline__": 26
                }
            ],
            "__startline__": 12,
            "__endline__": 26
        }
    ],
    "jobs":
    [
        {
            "job": "MyJob",
            "pool":
            {
                "vmImage": "windows-latest",
                "__startline__": 29,
                "__endline__": 30
            },
            "steps":
            [
                {
                    "script": "echo \"Running in a container based on myorg/mycontainer:1.0\"",
                    "__startline__": 31,
                    "__endline__": 31
                }
            ],
            "__startline__": 27,
            "__endline__": 31
        }
    ],
    "__startline__": 1,
    "__endline__": 31
}

    manager = AzurePipelinesImageReferencerManager(workflow_config=workflow_config, file_path=file_path)
    images = manager.extract_images_from_workflow()

    assert not images
