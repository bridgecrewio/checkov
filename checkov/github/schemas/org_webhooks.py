from checkov.common.vcs.vcs_schema import VCSSchema


class OrgWebhooksSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "title": "Org Hook",
                "description": "Org Hook",
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "examples": [
                            1
                        ]
                    },
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "examples": [
                            "https://api.github.com/orgs/octocat/hooks/1"
                        ]
                    },
                    "ping_url": {
                        "type": "string",
                        "format": "uri",
                        "examples": [
                            "https://api.github.com/orgs/octocat/hooks/1/pings"
                        ]
                    },
                    "deliveries_url": {
                        "type": "string",
                        "format": "uri",
                        "examples": [
                            "https://api.github.com/orgs/octocat/hooks/1/deliveries"
                        ]
                    },
                    "name": {
                        "type": "string",
                        "examples": [
                            "web"
                        ]
                    },
                    "events": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "examples": [
                            "push",
                            "pull_request"
                        ]
                    },
                    "active": {
                        "type": "boolean",
                        "examples": [
                            True
                        ]
                    },
                    "config": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "examples": [
                                    "\"http://example.com/2\""
                                ]
                            },
                            "insecure_ssl": {
                                "type": "string",
                                "examples": [
                                    "\"0\""
                                ]
                            },
                            "content_type": {
                                "type": "string",
                                "examples": [
                                    "\"form\""
                                ]
                            },
                            "secret": {
                                "type": "string",
                                "examples": [
                                    "\"********\""
                                ]
                            }
                        }
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "examples": [
                            "2011-09-06T20:39:23Z"
                        ]
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "examples": [
                            "2011-09-06T17:26:27Z"
                        ]
                    },
                    "type": {
                        "type": "string",
                        "const": "Organization"
                    }
                },
                "required": [
                    "id",
                    "url",
                    "type",
                    "name",
                    "active",
                    "events",
                    "config",
                    "ping_url",
                    "created_at",
                    "updated_at"
                ]
            }
        }
        super().__init__(schema=schema)


schema = OrgWebhooksSchema()
