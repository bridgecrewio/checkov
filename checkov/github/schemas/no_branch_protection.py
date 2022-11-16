from checkov.common.vcs.vcs_schema import VCSSchema


class NoBranchProtectionSchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "message": {
                    "type": "string"
                },
                "documentation_url": {
                    "type": "string"
                }
            },
            "required": [
                "message",
                "documentation_url"
            ]
        }
        super().__init__(schema=schema)


schema = NoBranchProtectionSchema()
