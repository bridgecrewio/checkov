from enum import Enum

from checkov.common.bridgecrew.code_categories import CodeCategoryType


class CustomerSubscription(str, Enum):
    IAC = "IAC"
    SCA = "SCA"
    SECRETS = "SECRETS"


class BillingPlan(str, Enum):
    DEVELOPER_BASED = "DEVELOPER_BASED"
    RESOURCE_BASED = "RESOURCE_BASED"


SubscriptionCategoryMapping = {
    CustomerSubscription.IAC: (CodeCategoryType.IAC, CodeCategoryType.BUILD_INTEGRITY),
    CustomerSubscription.SCA: (CodeCategoryType.LICENSES, CodeCategoryType.VULNERABILITIES),
    CustomerSubscription.SECRETS: (CodeCategoryType.SECRETS,)
}

CategoryToSubscriptionMapping = {}
for sub, cats in SubscriptionCategoryMapping.items():
    for cat in cats:
        CategoryToSubscriptionMapping[cat] = sub


open_source_categories = [CodeCategoryType.IAC, CodeCategoryType.SECRETS, CodeCategoryType.BUILD_INTEGRITY]
