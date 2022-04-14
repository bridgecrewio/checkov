#
# Example check
# This is checking yaml that looks like this example where
# Our resource is "jobs"
# It is of type ARRAY because there can be more than one that
# needs to be checked
#
# jobs:
#   unsecure-job:
#     name: job2
#     runs-on: ubuntu-latest
#     env:
#       ACTIONS_ALLOW_UNSECURE_COMMANDS: true
#     steps:
#       - name: unsecure-step2
#         run: |
#           echo "goo"
#   secure-job:
#     name: job3
#     runs-on: ubuntu-latest
#     env:
#       ACTIONS_ALLOW_UNSECURE_COMMANDS: false
#     run: |
#       echo "ok"
# 
from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult
# Import your base check
from checkov.example_runner.checks.base_example_runner_job_check import BaseExampleRunnerJobCheck

from checkov.yaml_doc.enums import BlockType


class ExampleCheckTrueFalse(BaseExampleRunnerJobCheck):
    def __init__(self) -> None:
        # Describe the check for the user
        name = "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn't true on environment variables on a job"
        # Give the check a unique id eg. CKV_TLA_24 where 
        #  CKV is standard for python checks
        #  TLA = Three letter acronym for your runner check type: GHA is GitHub Actions
        #  24 is the number in sequence of checks.  Must be unique!
        id = "CKV_GHA_1"
        super().__init__(
            name=name,
            id=id,
            # the block type tells the parse whether you'd expect one resource or many
            # options are ARRAY or OBJECT
            block_type=BlockType.ARRAY,
        )

    def scan_entity_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        # The block type is passed as a data structure.  
        # Add logic to parse the structure for the misconfig
        # Remember to always return a PASSED or FAILED. 
        # It is easy to miss a result in complex logic
        if "env" not in conf:
            return CheckResult.PASSED, conf
        env_variables = conf.get("env", {})
        if env_variables.get("MY_ENV_IS_PASSED", False):
            return CheckResult.FAILED, conf
        return CheckResult.PASSED, conf

# Set this to your check name
check = ExampleCheckTrueFalse()
