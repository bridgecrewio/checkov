import os
from checkov.common.sca.reachability.package_alias_mapping.alias_mapping_creator import AliasMappingCreator
from checkov.common.sca.reachability.package_alias_mapping.nodejs.utils import load_json_with_comments

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

def test_load_json_with_no_comments():
    json_data_with_comments = """
    {
      "compilerOptions": {
        "paths": {
          "@modules/*": ["src/modules/*"],
          "@shared/*": ["src/shared/*"]
        },
        "declaration": true,
        "target": "es2021",
        "strict": true /* Enable all strict type-checking options. */,
        "noUnusedLocals": false, // off for convenience, enable to enforce cleaner code
        "noUnusedParameters": false, // off for convenience, enable to enforce cleaner code
        "noImplicitAny": false,  // off for convenience, recommended value is true to enforce types and reduce bugs
        "forceConsistentCasingInFileNames": true /* Disallow inconsistently-cased references to the same file. */,
        "resolveJsonModule": true
      },
      "exclude": ["node_modules", "dist"]
    }
    """
    clean_json = load_json_with_comments(json_data_with_comments)
    assert clean_json == {
        "compilerOptions": {
            "paths": {
                "@modules/*": ["src/modules/*"],
                "@shared/*": ["src/shared/*"]
            },
            "declaration": True,
            "target": "es2021",
            "strict": True,
            "noUnusedLocals": False,
            "noUnusedParameters": False,
            "noImplicitAny": False,
            "forceConsistentCasingInFileNames": True,
            "resolveJsonModule": True
        },
        "exclude": ["node_modules", "dist"]
    }