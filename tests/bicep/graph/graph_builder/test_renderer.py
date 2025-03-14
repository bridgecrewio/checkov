from pathlib import Path

from checkov.bicep.graph_manager import BicepGraphManager
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector


def test_render_parameter():
    # given
    test_dir = Path(__file__).parent / "examples/parameter"
    graph_manager = BicepGraphManager(db_connector=NetworkxConnector())

    # when
    local_graph, _ = graph_manager.build_graph_from_source_directory(source_dir=str(test_dir), render_variables=True)

    # then
    vertex = local_graph.vertices[local_graph.vertices_by_name["vm"]]

    assert vertex.config["config"] == {
        "name": "example-vm",
        "location": "location",
        "properties": {
            "networkProfile": {
                "networkInterfaces": [{"id": "example-id"}]
            },
            "osProfile": {
                "linuxConfiguration": {
                    "ssh": {
                        "publicKeys": [
                            {"keyData": "key-data-1", "path": "path-1"},
                            {"keyData": "key-data-2", "path": "path-2"},
                            {"keyData": "key-data-3", "path": "path-3"},
                            {"keyData": {
                                "operator": {
                                    "type": "property_accessor",
                                    "operands": {
                                        "operand_1": {"keyData": "key-data-4", "path": {"name": "path-4"}},
                                        "operand_2": "keyData"
                                    }
                                }
                            },
                             "path": {
                                 "operator": {
                                     "type": "property_accessor",
                                     "operands": {
                                         "operand_1": {"keyData": "key-data-4", "path": {"name": "path-4"}},
                                         "operand_2": {
                                             "operator": {
                                                 "type": "property_accessor",
                                                 "operands": {"operand_1": "path", "operand_2": "name"}
                                             }
                                         }
                                     }
                                 }
                             }}
                        ]
                    }
                }
            },
            "storageProfile": {
                "imageReference": {"publisher": "MicrosoftWindowsServer"}
            }
        },
        "tags": {
            "displayName": "Container Registry",
            "'container.registry.name'": "exmaple-acr",
            "'container.registry'": {"name": "exmaple-nested-acr"},
        },
    }


def test_render_variable():
    # given
    test_dir = Path(__file__).parent / "examples/variable"
    graph_manager = BicepGraphManager(db_connector=NetworkxConnector())

    # when
    local_graph, _ = graph_manager.build_graph_from_source_directory(source_dir=str(test_dir), render_variables=True)

    # then
    vertex = local_graph.vertices[local_graph.vertices_by_name["vm"]]

    assert vertex.config["config"] == {
        "name": "example-vm",
        "location": "westeurope",
        "properties": {
            "networkProfile": {
                "networkInterfaces": [
                    {"id": "example-id"}
                ]
            },
            "osProfile": {
                "linuxConfiguration": {
                    "ssh": {
                        "publicKeys": [
                            {"keyData": "key-data-1", "path": "path-1"},
                            {"keyData": "key-data-2", "path": "path-2"},
                            {"keyData": "key-data-3", "path": "path-3"},
                            {
                                "keyData": {
                                    "operator": {
                                        "type": "property_accessor",
                                        "operands": {
                                            "operand_1": {
                                                "keyData": "key-data-4",
                                                "path": {"name": "path-4"}
                                            },
                                            "operand_2": "keyData"
                                        }
                                    }
                                },
                                "path": {
                                    "operator": {
                                        "type": "property_accessor",
                                        "operands": {
                                            "operand_1": {
                                                "keyData": "key-data-4",
                                                "path": {"name": "path-4"}
                                            },
                                            "operand_2": {
                                                "operator": {
                                                    "type": "property_accessor",
                                                    "operands": {
                                                        "operand_1": "path",
                                                        "operand_2": "name"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            "storageProfile": {
                "imageReference": {
                    "publisher": "MicrosoftWindowsServer"
                }
            }
        },
        "tags": {
            "displayName": "Container Registry",
            "'container.registry.name'": "exmaple-acr",
            "'container.registry'": {"name": "exmaple-nested-acr"},
        },
    }


def test_render_mixed():
    # given
    test_dir = Path(__file__).parent / "examples/mixed"
    graph_manager = BicepGraphManager(db_connector=NetworkxConnector())

    # when
    local_graph, _ = graph_manager.build_graph_from_source_directory(source_dir=str(test_dir), render_variables=True)

    # then
    vertex = local_graph.vertices[local_graph.vertices_by_name["vm"]]

    assert vertex.config["config"] == {
        "name": "example-vm",
        "location": "location",
        "properties": {
            "networkProfile": {
                "networkInterfaces": [
                    {"id": "example-id"}
                ]
            },
            "osProfile": {
                "linuxConfiguration": {
                    "ssh": {
                        "publicKeys": [
                            {"keyData": "key-data-1", "path": "path-1"},
                            {"keyData": "key-data-2", "path": "path-2"},
                            {"keyData": "keyData3", "path": "path-3"},
                            {
                                "keyData": {
                                    "operator": {
                                        "type": "property_accessor",
                                        "operands": {
                                            "operand_1": {
                                                "keyData": "key-data-4",
                                                "path": {
                                                    "name": {
                                                        "operator": {
                                                            "type": "property_accessor",
                                                            "operands": {
                                                                "operand_1": {
                                                                    "keyData": "key-data-2",
                                                                    "path": "path-2"
                                                                },
                                                                "operand_2": "path"
                                                            }
                                                        }
                                                    }
                                                }
                                            },
                                            "operand_2": "keyData"
                                        }
                                    }
                                },
                                "path": {
                                    "operator": {
                                        "type": "property_accessor",
                                        "operands": {
                                            "operand_1": {
                                                "keyData": "key-data-4",
                                                "path": {
                                                    "name": {
                                                        "operator": {
                                                            "type": "property_accessor",
                                                            "operands": {
                                                                "operand_1": {
                                                                    "keyData": "key-data-2",
                                                                    "path": "path-2"
                                                                },
                                                                "operand_2": "path"
                                                            }
                                                        }
                                                    }
                                                }
                                            },
                                            "operand_2": {
                                                "operator": {
                                                    "type": "property_accessor",
                                                    "operands": {
                                                        "operand_1": "path",
                                                        "operand_2": "name"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            "storageProfile": {
                "imageReference": {
                    "publisher": "publisher"
                }
            }
        },
        "tags": {
            "displayName": "Container Registry",
            "'container.registry.name'": "acrName",
            "'container.registry'": {"name": "acrNestedName"},
        },
    }
