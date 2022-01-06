from checkov.github.schemas.base_schema import GithubConfSchema


class OrgSecuritySchema(GithubConfSchema):
    def __init__(self):
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
                                    "type": "string"
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
                                    "type": "object",
                                    "properties": {
                                        "ssoUrl": {
                                            "type": "string"
                                        }
                                    }

                                }
                            }
                        }
                    }
                }
            }
        }
        super().__init__(schema=schema)


schema = OrgSecuritySchema()
