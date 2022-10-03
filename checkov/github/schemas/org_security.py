from checkov.common.vcs.vcs_schema import VCSSchema


class OrgSecuritySchema(VCSSchema):
    def __init__(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "organization": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "login": {
                                    "type": "string"
                                },
                                "description": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "null"}
                                    ]
                                },
                                "ipAllowListEnabledSetting": {
                                    "type": "string"
                                },
                                "ipAllowListForInstalledAppsEnabledSetting": {
                                    "type": "string"
                                },
                                "requiresTwoFactorAuthentication": {
                                    "type": "boolean"
                                },
                                "samlIdentityProvider": {
                                    "anyOf": [
                                        {
                                            "type": "object",
                                            "properties": {
                                                "ssoUrl": {
                                                    "type": "string"
                                                }
                                            }
                                        },
                                        {
                                            "type": "null"
                                        }
                                    ]
                                }
                            },
                            "required": [
                                "name",
                                "login",
                                "description",
                                "ipAllowListEnabledSetting",
                                "ipAllowListForInstalledAppsEnabledSetting",
                                "requiresTwoFactorAuthentication"]
                        }
                    },
                    "required": [
                        "organization"
                    ]
                }
            },
            "required": [
                "data"
            ]
        }
        super().__init__(schema=schema)


schema = OrgSecuritySchema()
