from collections import ChainMap
from dataclasses import dataclass
from enum import Enum

from checkov.common.bridgecrew.code_categories import CodeCategoryType


class CustomerLicense(Enum):
    RESOURCE = "resource"
    DEVELOPER = "developer"


class CustomerSubscription(Enum):
    IAC = "IAC"
    SCA = "SCA"
    SECRETS = "SECRETS"


SubscriptionCategoryMapping = {
    CustomerSubscription.IAC: [CodeCategoryType.IAC, CodeCategoryType.SUPPLY_CHAIN],
    CustomerSubscription.SCA: [CodeCategoryType.OPEN_SOURCE, CodeCategoryType.IMAGES],
    CustomerSubscription.SECRETS: [CodeCategoryType.SECRETS]
}

CategoryToSubscriptionMapping = {}
for sub, cats in SubscriptionCategoryMapping.items():
    for cat in cats:
        CategoryToSubscriptionMapping[cat] = sub
