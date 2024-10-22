from checkov.common.vcs.vcs_schema import VCSSchema


class BranchRestrictionsSchema(VCSSchema):
    def __init__(self) -> None:
        schema = \
            {
                "$schema": "http://json-schema.org/draft-04/schema#",
                "type": "object",
                "properties": {
                    "pagelen": {
                        "type": "integer"
                    },
                    "values": {
                        "type": "array",
                        "items": [
                            {
                                "type": "object",
                                "properties": {
                                    "kind": {
                                        "type": "string"
                                    },
                                    "users": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "links": {
                                        "type": "object",
                                        "properties": {
                                            "self": {
                                                "type": "object",
                                                "properties": {
                                                    "href": {
                                                        "type": "string"
                                                    }
                                                },
                                                "required": [
                                                    "href"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "self"
                                        ]
                                    },
                                    "pattern": {
                                        "type": "string"
                                    },

                                    "branch_match_kind": {
                                        "type": "string"
                                    },
                                    "groups": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "integer"
                                    }
                                },
                                "required": [
                                    "kind",
                                    "users",
                                    "links",
                                    "pattern",
                                    "branch_match_kind",
                                    "groups",
                                    "type",
                                    "id"
                                ]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "kind": {
                                        "type": "string"
                                    },
                                    "users": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "links": {
                                        "type": "object",
                                        "properties": {
                                            "self": {
                                                "type": "object",
                                                "properties": {
                                                    "href": {
                                                        "type": "string"
                                                    }
                                                },
                                                "required": [
                                                    "href"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "self"
                                        ]
                                    },
                                    "pattern": {
                                        "type": "string"
                                    },

                                    "branch_match_kind": {
                                        "type": "string"
                                    },
                                    "groups": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "integer"
                                    }
                                },
                                "required": [
                                    "kind",
                                    "users",
                                    "links",
                                    "pattern",
                                    "branch_match_kind",
                                    "groups",
                                    "type",
                                    "id"
                                ]
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "kind": {
                                        "type": "string"
                                    },
                                    "users": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "links": {
                                        "type": "object",
                                        "properties": {
                                            "self": {
                                                "type": "object",
                                                "properties": {
                                                    "href": {
                                                        "type": "string"
                                                    }
                                                },
                                                "required": [
                                                    "href"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "self"
                                        ]
                                    },
                                    "pattern": {
                                        "type": "string"
                                    },

                                    "branch_match_kind": {
                                        "type": "string"
                                    },
                                    "groups": {
                                        "type": "array",
                                        "items": {}
                                    },
                                    "type": {
                                        "type": "string"
                                    },
                                    "id": {
                                        "type": "integer"
                                    }
                                },
                                "required": [
                                    "kind",
                                    "users",
                                    "links",
                                    "pattern",
                                    "branch_match_kind",
                                    "groups",
                                    "type",
                                    "id"
                                ]
                            }
                        ]
                    },
                    "page": {
                        "type": "integer"
                    },
                    "size": {
                        "type": "integer"
                    }
                },
                "required": [
                    "pagelen",
                    "values",
                    "page",
                    "size"
                ]
            }
        super().__init__(schema=schema)


schema = BranchRestrictionsSchema()
