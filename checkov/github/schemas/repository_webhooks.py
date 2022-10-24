from checkov.common.vcs.vcs_schema import VCSSchema


class RepositoryWebhookSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "type": "array",
            "items": {
                "title": "Webhook",
                "description": "Webhooks for repositories.",
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "const": "Repository"
                    },
                    "id": {
                        "description": "Unique identifier of the webhook.",
                        "type": "integer",
                        "examples": [
                            42
                        ]
                    },
                    "name": {
                        "description": "The name of a valid service, use 'web' for a webhook.",
                        "type": "string",
                        "examples": [
                            "web"
                        ]
                    },
                    "active": {
                        "description": "Determines whether the hook is actually triggered on pushes.",
                        "type": "boolean",
                        "examples": [
                            True
                        ]
                    },
                    "events": {
                        "description": "Determines what events the hook is triggered for. Default: ['push'].",
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "examples": [
                            "push",
                            "pull_request"
                        ]
                    },
                    "config": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "examples": [
                                    "\"foo@bar.com\""
                                ]
                            },
                            "password": {
                                "type": "string",
                                "examples": [
                                    "\"foo\""
                                ]
                            },
                            "room": {
                                "type": "string",
                                "examples": [
                                    "\"roomer\""
                                ]
                            },
                            "subdomain": {
                                "type": "string",
                                "examples": [
                                    "\"foo\""
                                ]
                            },
                            "url": {
                                "type": "string",
                                "description": "The URL to which the payloads will be delivered.",
                                "format": "uri",
                                "examples": [
                                    "https://example.com/webhook"
                                ]
                            },
                            "insecure_ssl": {
                                "oneOf": [
                                    {
                                        "type": "string",
                                        "description": "Determines whether the SSL certificate of the host for `url` will be verified when delivering payloads. Supported values include `0` (verification is performed) and `1` (verification is not performed). The default is `0`. **We strongly recommend not setting this to `1` as you are subject to man-in-the-middle and other attacks.**",
                                        "examples": [
                                            "\"0\""
                                        ]
                                    },
                                    {
                                        "type": "number"
                                    }
                                ]
                            },
                            "content_type": {
                                "type": "string",
                                "description": "The media type used to serialize the payloads. Supported values include `json` and `form`. The default is `form`.",
                                "examples": [
                                    "\"json\""
                                ]
                            },
                            "digest": {
                                "type": "string",
                                "examples": [
                                    "\"sha256\""
                                ]
                            },
                            "secret": {
                                "type": "string",
                                "description": "If provided, the `secret` will be used as the `key` to generate the HMAC hex digest value for [delivery signature headers](https://docs.github.com/webhooks/event-payloads/#delivery-headers).",
                                "examples": [
                                    "\"********\""
                                ]
                            },
                            "token": {
                                "type": "string",
                                "examples": [
                                    "\"abc\""
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
                    "url": {
                        "type": "string",
                        "format": "uri",
                        "examples": [
                            "https://api.github.com/repos/octocat/Hello-World/hooks/1"
                        ]
                    },
                    "test_url": {
                        "type": "string",
                        "format": "uri",
                        "examples": [
                            "https://api.github.com/repos/octocat/Hello-World/hooks/1/test"
                        ]
                    },
                    "ping_url": {
                        "type": "string",
                        "format": "uri",
                        "examples": [
                            "https://api.github.com/repos/octocat/Hello-World/hooks/1/pings"
                        ]
                    },
                    "deliveries_url": {
                        "type": "string",
                        "format": "uri",
                        "examples": [
                            "https://api.github.com/repos/octocat/Hello-World/hooks/1/deliveries"
                        ]
                    },
                    "last_response": {
                        "title": "Hook Response",
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": [
                                    "integer",
                                    "null"
                                ]
                            },
                            "status": {
                                "type": [
                                    "string",
                                    "null"
                                ]
                            },
                            "message": {
                                "type": [
                                    "string",
                                    "null"
                                ]
                            }
                        },
                        "required": [
                            "code",
                            "status",
                            "message"
                        ]
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
                    "updated_at",
                    "last_response",
                    "test_url"
                ]
            }
        }
        super().__init__(schema=schema)


schema = RepositoryWebhookSchema()
