from __future__ import annotations

from typing import Any, TYPE_CHECKING

from policy_sentry.analysis.expand import expand

from checkov.common.graph.checks_infra.extensions.base_extension import BaseGraphCheckExtension
from checkov.common.graph.graph_builder.graph_components.attribute_names import CustomAttributes
from checkov.common.models.enums import GraphCheckExtension
from checkov.common.util.data_structures_utils import pickle_deepcopy
from checkov.common.util.type_forcers import force_list

if TYPE_CHECKING:
    from typing_extensions import Self

SUPPORTED_IAM_BLOCKS = {
    "aws_iam_group_policy",
    "aws_iam_policy",
    "aws_iam_role_policy",
    "aws_iam_user_policy",
    "aws_ssoadmin_permission_set_inline_policy",
    "data.aws_iam_policy_document",
}
IAM_POLICY_BLOCKS = {
    "aws_iam_group_policy",
    "aws_iam_policy",
    "aws_iam_role_policy",
    "aws_iam_user_policy",
}


class IamActionExpansion(BaseGraphCheckExtension):
    _instance = None  # noqa: CCE003  # singleton

    name = GraphCheckExtension.IAM_ACTION_EXPANSION  # noqa: CCE003  # a static attribute
    iam_expanded_actions_cache: dict[str, dict[str, Any]] = {}  # noqa: CCE003  # global cache

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def extend(self, vertex_data: dict[str, Any]) -> dict[str, Any]:
        if not vertex_data[CustomAttributes.RESOURCE_TYPE] in SUPPORTED_IAM_BLOCKS:
            return vertex_data

        cache_key = f"{vertex_data[CustomAttributes.FILE_PATH]}:{vertex_data[CustomAttributes.RESOURCE_TYPE]}:{vertex_data[CustomAttributes.BLOCK_NAME]}"
        if cache_key in IamActionExpansion.iam_expanded_actions_cache:
            return IamActionExpansion.iam_expanded_actions_cache[cache_key]

        expanded_actions = self._expand_iam_actions(vertex_data=vertex_data)
        IamActionExpansion.iam_expanded_actions_cache[cache_key] = expanded_actions
        return expanded_actions

    def _expand_iam_actions(self, vertex_data: dict[str, Any]) -> dict[str, Any]:
        """Returns resource data with the expanded actions of an IAM statement

        Info: Only AWS Terraform resources are supported for now
        """

        vertex_data = pickle_deepcopy(vertex_data)
        resource_type = vertex_data[CustomAttributes.RESOURCE_TYPE]
        if resource_type == "data.aws_iam_policy_document":
            self._adjust_action_value(policy=vertex_data, statement_key="statement", action_key="actions")
        elif resource_type in IAM_POLICY_BLOCKS:
            policy = vertex_data.get("policy")
            if isinstance(policy, dict):
                self._adjust_action_value(policy=policy, statement_key="Statement", action_key="Action")
        elif resource_type == "aws_ssoadmin_permission_set_inline_policy":
            policy = vertex_data.get("inline_policy")
            if isinstance(policy, dict):
                self._adjust_action_value(policy=policy, statement_key="Statement", action_key="Action")

        return vertex_data

    def _adjust_action_value(self, policy: dict[str, Any], statement_key: str, action_key: str) -> None:
        for statement in force_list(policy.get(statement_key, [])):
            if action_key in statement:
                original_actions = statement[action_key]
                expanded_actions = expand(action=original_actions)
                if isinstance(original_actions, list):
                    statement[action_key].extend(expanded_actions)
                else:
                    expanded_actions = list(expanded_actions)  # fix in policy_sentry to be a list not a set
                    expanded_actions.append(original_actions)
                    statement[action_key] = expanded_actions
