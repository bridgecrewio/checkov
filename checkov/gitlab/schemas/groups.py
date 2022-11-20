from checkov.common.vcs.vcs_schema import VCSSchema


class GroupsSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "array",
            "items": [
                {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer"
                        },
                        "web_url": {
                            "type": "string"
                        },
                        "name": {
                            "type": "string"
                        },
                        "path": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "visibility": {
                            "type": "string"
                        },
                        "share_with_group_lock": {
                            "type": "boolean"
                        },
                        "require_two_factor_authentication": {
                            "type": "boolean"
                        },
                        "two_factor_grace_period": {
                            "type": "integer"
                        },
                        "project_creation_level": {
                            "type": "string"
                        },
                        "auto_devops_enabled": {
                            "type": "null"
                        },
                        "subgroup_creation_level": {
                            "type": "string"
                        },
                        "emails_disabled": {
                            "oneOf": [
                                {"type": "boolean"},
                                {"type": "null"}
                            ]
                        },
                        "mentions_disabled": {
                            "oneOf": [
                                {"type": "boolean"},
                                {"type": "null"}
                            ]
                        },
                        "lfs_enabled": {
                            "oneOf": [
                                {"type": "boolean"},
                                {"type": "null"}
                            ]
                        },
                        "default_branch_protection": {
                            "type": "integer"
                        },
                        "avatar_url": {
                            "oneOf": [
                                {"type": "string"},
                                {"type": "null"}
                            ]
                        },
                        "request_access_enabled": {
                            "type": "boolean"
                        },
                        "full_name": {
                            "type": "string"
                        },
                        "full_path": {
                            "type": "string"
                        },
                        "created_at": {
                            "type": "string"
                        },
                        "parent_id": {
                            "type": "null"
                        },
                        "ldap_cn": {
                            "type": "null"
                        },
                        "ldap_access": {
                            "type": "null"
                        }
                    },
                    "required": [
                        "id",
                        "web_url",
                        "name",
                        "path",
                        "description",
                        "visibility",
                        "share_with_group_lock",
                        "require_two_factor_authentication",
                        "two_factor_grace_period",
                        "project_creation_level",
                        "auto_devops_enabled",
                        "subgroup_creation_level",
                        "emails_disabled",
                        "mentions_disabled",
                        "lfs_enabled",
                        "default_branch_protection",
                        "avatar_url",
                        "request_access_enabled",
                        "full_name",
                        "full_path",
                        "created_at",
                        "parent_id",
                        "ldap_cn",
                        "ldap_access"
                    ]
                }
            ]
        }
        super().__init__(schema=schema)


schema = GroupsSchema()
