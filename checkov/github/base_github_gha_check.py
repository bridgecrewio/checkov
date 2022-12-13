from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.github_actions.common.artifact_build import buildcmds
from checkov.json_doc.enums import BlockType


class BaseGHACheck(BaseGithubCheck):
    def __init__(self, id: str, name: str) -> None:
        categories = (CheckCategories.SUPPLY_CHAIN,)
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=("*",),
            block_type=BlockType.DOCUMENT,
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        pass

    @staticmethod
    def is_gha_enabled(ckv_metadata: dict[str, Any]) -> bool:
        return bool(
            ckv_metadata['repo_complementary_metadata'].get('gha', {}).get('enabled') and
            ckv_metadata['repo_complementary_metadata'].get('gha', {}).get('total_count')
        )

    @staticmethod
    def is_build_workflow(workflow_name: str) -> bool:
        return 'build' in workflow_name

    @staticmethod
    def workflow_contain_build(workflow_content: list[dict[str, Any]]) -> bool:
        for content in workflow_content:
            for _, job_data in content.get('jobs', {}).items():
                if not isinstance(job_data, dict):
                    continue
                for step in job_data.get('steps', []):
                    if isinstance(step, dict):
                        shell_script = step.get('run', '')
                        if shell_script and isinstance(shell_script, str):
                            shell_commands = shell_script.splitlines()
                            for command in shell_commands:
                                if any(build_cmd in command for build_cmd in buildcmds):
                                    return True
        return False
