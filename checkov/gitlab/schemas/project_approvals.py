from checkov.common.vcs.vcs_schema import VCSSchema


class ProjectApprovalsSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "approvals_before_merge": {
                    "type": "integer"
                },
                "reset_approvals_on_push": {
                    "type": "boolean"
                },
                "disable_overriding_approvers_per_merge_request": {
                    "type": "boolean"
                },
                "merge_requests_author_approval": {
                    "type": "boolean"
                },
                "merge_requests_disable_committers_approval": {
                    "type": "boolean"
                },
                "require_password_to_approve": {
                    "type": "boolean"
                }
            },
            "required": [
                "approvals_before_merge",
                "reset_approvals_on_push",
                "disable_overriding_approvers_per_merge_request",
                "merge_requests_author_approval",
                "merge_requests_disable_committers_approval",
                "require_password_to_approve"
            ]
        }
        super().__init__(schema=schema)


schema = ProjectApprovalsSchema()
