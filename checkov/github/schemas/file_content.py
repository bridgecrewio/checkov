from checkov.common.vcs.vcs_schema import VCSSchema


class FileContentSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "title": "Content Tree",
            "description": "Content Tree",
            "type": "object",
            "properties": {
                "type": {
                    "type": "string"
                },
                "size": {
                    "type": "integer"
                },
                "name": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "sha": {
                    "type": "string"
                },
                "url": {
                    "type": "string",
                    "format": "uri"
                },
                "git_url": {
                    "type": [
                        "string",
                        "null"
                    ],
                    "format": "uri"
                },
                "html_url": {
                    "type": [
                        "string",
                        "null"
                    ],
                    "format": "uri"
                },
                "download_url": {
                    "type": [
                        "string",
                        "null"
                    ],
                    "format": "uri"
                },
                "entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string"
                            },
                            "size": {
                                "type": "integer"
                            },
                            "name": {
                                "type": "string"
                            },
                            "path": {
                                "type": "string"
                            },
                            "content": {
                                "type": "string"
                            },
                            "sha": {
                                "type": "string"
                            },
                            "url": {
                                "type": "string",
                                "format": "uri"
                            },
                            "git_url": {
                                "type": [
                                    "string",
                                    "null"
                                ],
                                "format": "uri"
                            },
                            "html_url": {
                                "type": [
                                    "string",
                                    "null"
                                ],
                                "format": "uri"
                            },
                            "download_url": {
                                "type": [
                                    "string",
                                    "null"
                                ],
                                "format": "uri"
                            },
                            "_links": {
                                "type": "object",
                                "properties": {
                                    "git": {
                                        "type": [
                                            "string",
                                            "null"
                                        ],
                                        "format": "uri"
                                    },
                                    "html": {
                                        "type": [
                                            "string",
                                            "null"
                                        ],
                                        "format": "uri"
                                    },
                                    "self": {
                                        "type": "string",
                                        "format": "uri"
                                    }
                                },
                                "required": [
                                    "git",
                                    "html",
                                    "self"
                                ]
                            }
                        },
                        "required": [
                            "_links",
                            "git_url",
                            "html_url",
                            "download_url",
                            "name",
                            "path",
                            "sha",
                            "size",
                            "type",
                            "url"
                        ]
                    }
                },
                "_links": {
                    "type": "object",
                    "properties": {
                        "git": {
                            "type": [
                                "string",
                                "null"
                            ],
                            "format": "uri"
                        },
                        "html": {
                            "type": [
                                "string",
                                "null"
                            ],
                            "format": "uri"
                        },
                        "self": {
                            "type": "string",
                            "format": "uri"
                        }
                    },
                    "required": [
                        "git",
                        "html",
                        "self"
                    ]
                }
            },
            "required": [
                "_links",
                "git_url",
                "html_url",
                "download_url",
                "name",
                "path",
                "sha",
                "size",
                "type",
                "url",
                "content",
                "encoding"
            ]
        }
        super().__init__(schema=schema)


schema = FileContentSchema()
