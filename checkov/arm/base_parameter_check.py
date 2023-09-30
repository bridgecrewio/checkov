from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Callable

from checkov.arm.registry import arm_parameter_registry
from checkov.common.checks.base_check import BaseCheck
from checkov.common.multi_signature import multi_signature

if TYPE_CHECKING:
    from checkov.common.models.enums import CheckCategories, CheckResult


class BaseParameterCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_resources: Iterable[str],
        guideline: str | None = None
    ) -> None:
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type="parameter", guideline=guideline)
        self.supported_resources = supported_resources
        arm_parameter_registry.register(self)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:  # type:ignore[override]  # it's ok
        return self.scan_resource_conf(conf, entity_type)  # type:ignore[no-any-return]  # issue with multi_signature annotation

    @multi_signature()
    @abstractmethod
    def scan_resource_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult:
        raise NotImplementedError()

    @classmethod
    @scan_resource_conf.add_signature(args=["self", "conf"])
    def _scan_resource_conf_self_conf(cls, wrapped: Callable[..., CheckResult]) -> Callable[..., CheckResult]:
        def wrapper(self: BaseCheck, conf: dict[str, Any], entity_type: str | None = None) -> CheckResult:
            # keep default argument for entity_type so old code, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
