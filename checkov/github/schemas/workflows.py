from checkov.common.vcs.vcs_schema import VCSSchema


class WorkflowsSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "type": "object",
            "required": [
                "total_count",
                "workflows"
            ],
            "properties": {
                "total_count": {
                    "type": "integer"
                },
                "workflows": {
                    "type": "array",
                    "items": {
                        "title": "Workflow",
                        "description": "A GitHub Actions workflow",
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "examples": [
                                    5
                                ]
                            },
                            "node_id": {
                                "type": "string",
                                "examples": [
                                    "MDg6V29ya2Zsb3cxMg=="
                                ]
                            },
                            "name": {
                                "type": "string",
                                "examples": [
                                    "CI"
                                ]
                            },
                            "path": {
                                "type": "string",
                                "examples": [
                                    "ruby.yaml"
                                ]
                            },
                            "state": {
                                "type": "string",
                                "enum": [
                                    "active",
                                    "deleted",
                                    "disabled_fork",
                                    "disabled_inactivity",
                                    "disabled_manually"
                                ],
                                "examples": [
                                    "active"
                                ]
                            },
                            "created_at": {
                                "type": "string",
                                "format": "date-time",
                                "examples": [
                                    "2019-12-06T14:20:20.000Z"
                                ]
                            },
                            "updated_at": {
                                "type": "string",
                                "format": "date-time",
                                "examples": [
                                    "2019-12-06T14:20:20.000Z"
                                ]
                            },
                            "url": {
                                "type": "string",
                                "examples": [
                                    "https://api.github.com/repos/actions/setup-ruby/workflows/5"
                                ]
                            },
                            "html_url": {
                                "type": "string",
                                "examples": [
                                    "https://github.com/actions/setup-ruby/blob/master/.github/workflows/ruby.yaml"
                                ]
                            },
                            "badge_url": {
                                "type": "string",
                                "examples": [
                                    "https://github.com/actions/setup-ruby/workflows/CI/badge.svg"
                                ]
                            },
                            "deleted_at": {
                                "type": "string",
                                "format": "date-time",
                                "examples": [
                                    "2019-12-06T14:20:20.000Z"
                                ]
                            }
                        },
                        "required": [
                            "id",
                            "node_id",
                            "name",
                            "path",
                            "state",
                            "url",
                            "html_url",
                            "badge_url",
                            "created_at",
                            "updated_at"
                        ]
                    }
                }
            }
        }
        super().__init__(schema=schema)


schema = WorkflowsSchema()
