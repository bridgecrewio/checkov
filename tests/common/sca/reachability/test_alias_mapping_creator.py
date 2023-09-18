import os
import pytest
import sys
from checkov.common.sca.reachability.alias_mapping_creator import AliasMappingCreator

current_dir = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Python 3.7 isn't supporting TypedDict")
def test_alias_mapping_creator():
    alias_mapping_creator = AliasMappingCreator()
    alias_mapping_creator.update_alias_mapping_for_repository("example_repo", os.path.join(current_dir, "example_repo"), {'axios'})
    alias_mapping = alias_mapping_creator.get_alias_mapping()
    assert alias_mapping == {
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
