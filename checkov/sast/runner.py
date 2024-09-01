from __future__ import annotations

import logging
import os
import sys

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner
from checkov.common.sast.consts import SUPPORT_FILE_EXT, FILE_EXT_TO_SAST_LANG, CDKLanguages, CDK_CHECKS_DIR_PATH
from checkov.runner_filter import RunnerFilter
from checkov.sast.checks_infra.base_registry import Registry
from checkov.sast.engines.prisma_engine import PrismaEngine, get_machine

from typing import List, Optional

logger = logging.getLogger(__name__)


class Runner(BaseRunner[None, None, None]):
    check_type = CheckType.SAST  # noqa: CCE003  # a static attribute

    def __init__(self) -> None:
        super().__init__(file_extensions=["." + a for a in FILE_EXT_TO_SAST_LANG.keys()])
        self.registry = Registry()
        self.engine = PrismaEngine()  # noqa: disallow-untyped-calls
        self.cdk_langs: List[CDKLanguages] = []

    def should_scan_file(self, file: str) -> bool:
        for extensions in SUPPORT_FILE_EXT.values():
            for extension in extensions:
                if file.endswith(extension):
                    return True
        return False

    def run(self, root_folder: Optional[str],
            external_checks_dir: Optional[List[str]] = None,
            files: Optional[List[str]] = None,
            runner_filter: Optional[RunnerFilter] = None,
            collect_skip_comments: bool = True) -> List[Report]:

        # We support only windows amd
        if sys.platform.startswith('win') and not get_machine() == "amd64":
            logger.warning('Skip SAST for windows arm')
            # TODO: Enable SAST for windows arm runners.
            return [Report(self.check_type)]
        if not runner_filter:
            logger.warning('no runner filter')
            return [Report(self.check_type)]

        if bc_integration.daemon_process:
            # only happens for 'ParallelizationType.SPAWN'
            bc_integration.setup_http_manager()
            bc_integration.set_s3_client()

        # registry get all the paths
        self.registry.set_runner_filter(runner_filter)
        self.registry.add_external_dirs(external_checks_dir)

        targets = []
        if root_folder:
            if not os.path.isabs(root_folder):
                root_folder = os.path.abspath(root_folder)
            targets.append(root_folder)
        if files:
            targets.extend([a if os.path.isabs(a) else os.path.abspath(a) for a in files])

        if self.cdk_langs:
            self.registry.checks_dirs_path.append(str(CDK_CHECKS_DIR_PATH))

        reports = []
        try:
            reports = self.engine.get_reports(targets, self.registry, runner_filter.sast_languages, self.cdk_langs)
        except BaseException as e:  # noqa: B036
            logger.error(f"got error when try to run prisma sast: {e}")

        return reports
