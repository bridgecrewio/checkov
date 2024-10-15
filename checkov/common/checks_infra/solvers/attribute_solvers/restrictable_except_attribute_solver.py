from typing import Any, List, Optional, Union, Dict
from checkov.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver
from checkov.common.graph.checks_infra.enums import Operators
from cloudsplaining.scan.policy_document import PolicyDocument


class RestrictableExceptAttributeSolver(BaseAttributeSolver):
    operator = Operators.RESTRICTABLE_EXCEPT  # noqa: CCE003  # a static attribute

    def __init__(
            self, resource_types: List[str], attribute: Optional[str], value: Union[Any, List[Any]],
            is_jsonpath_check: bool = False
    ) -> None:
        super().__init__(resource_types, attribute, value, is_jsonpath_check)
        self.exclusions = set(self.value if isinstance(self.value, list) else [self.value])

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        policy = vertex["policy"]

        policy_doc = PolicyDocument(policy).all_allowed_unrestricted_actions


        #vertex.entity_type == "aws_ssoadmin_permission_set_inline_policy":
        #    return "inline_policy" in conf

        #return "policy" in conf

        # Get all allowed unrestricted actions
        #unrestricted_actions = policy.all_allowed_unrestricted_actions

        #for resource_type in self.resource_types:
        #    if resource_type in conf:
        #        policy_document = conf[resource_type]
        #        policy = PolicyDocument(policy_document)
        #        restricted_actions = self._get_operation(policy)
        #        if restricted_actions:
        #            return True

        # Filter out actions that are in the exclusions list
        #restricted_actions = [
        #    action for action in unrestricted_actions if action not in self.exclusions
        #]

        return False
