from checkov.common.vcs.vcs_schema import VCSSchema


class BranchProtectionSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "url": {
                    "type": "string"
                },
                "required_signatures": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string"
                        },
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "url",
                        "enabled"
                    ]
                },
                "enforce_admins": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string"
                        },
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "url",
                        "enabled"
                    ]
                },
                "required_linear_history": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "enabled"
                    ]
                },
                "allow_force_pushes": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "enabled"
                    ]
                },
                "allow_deletions": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "enabled"
                    ]
                },
                "required_conversation_resolution": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "enabled"
                    ]
                }
            },
            "required": [
                "url",
                "enforce_admins",
                "required_linear_history",
                "allow_force_pushes",
                "allow_deletions",
            ]
        }
        super().__init__(schema=schema)


schema = BranchProtectionSchema()
