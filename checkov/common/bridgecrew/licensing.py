from collections import ChainMap
from dataclasses import dataclass

from checkov.common.bridgecrew.code_categories import CodeCategoryType


@dataclass
class CustomerLicense:
    RESOURCES = "resources"
    DEVELOPER = "developer"


@dataclass
class CustomerSubscription:
    IAC = "IaC"
    SCA = "SCA"
    SECRETS = "Secrets"


SubscriptionCategoryMapping = {
    CustomerSubscription.IAC: [CodeCategoryType.IAC, CodeCategoryType.SUPPLY_CHAIN],
    CustomerSubscription.SCA: [CodeCategoryType.OPEN_SOURCE, CodeCategoryType.IMAGES],
    CustomerSubscription.SECRETS: [CodeCategoryType.SECRETS]
}

CategoryToSubscriptionMapping = {}
for sub, cats in SubscriptionCategoryMapping.items():
    for cat in cats:
        CategoryToSubscriptionMapping[cat] = sub
