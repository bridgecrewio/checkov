import os
from checkov.common.sca.reachability.package_alias_mapping.alias_mapping_creator import AliasMappingCreator

current_dir = os.path.dirname(os.path.realpath(__file__))


def test_alias_mapping_creator():
    alias_mapping_creator = AliasMappingCreator()
    alias_mapping_creator.update_alias_mapping_for_repository("example_repo", os.path.join(current_dir, "example_repo"), {'axios'})
    alias_mapping = alias_mapping_creator.get_alias_mapping()
    assert alias_mapping == {
        "languages": {
            "nodejs": {
                "repositories": {
                    "example_repo": {
                        "files": {
                            "tsconfig.json": {
                                "packageAliases": {
                                    "axios": {
                                        "packageAliases":["ax"]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
