import ctypes
import json
import logging
import os
import platform
import re
import stat
from pathlib import Path
from typing import Optional, List, Set

from cachetools import cached, TTLCache

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.platform_key import bridgecrew_dir
from checkov.common.bridgecrew.severities import get_severity
from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.typing import _CheckResult
from checkov.common.util.http_utils import request_wrapper
from checkov.sast.checks_infra.base_registry import Registry
from checkov.sast.common import get_code_block
from checkov.sast.consts import SastLanguages
from checkov.sast.engines.base_engine import SastEngine
from checkov.sast.prisma_models.report import PrismaReport
from checkov.sast.record import SastRecord

logger = logging.getLogger(__name__)


class PrismaEngine(SastEngine):
    def __init__(self) -> None:
        self.lib_path = ""
        self.check_type = CheckType.SAST
        self.prisma_sast_dir_path = Path(bridgecrew_dir) / "sast"
        self.sast_platform_base_path = "api/v1/sast"

    def get_reports(self, targets: List[str], registry: Registry, languages: Set[SastLanguages]) -> List[Report]:
        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run Sast prisma scanning")
            return []

        self.setup_sast_artifact()
        prisma_lib_path = self.get_sast_artifact()
        if not prisma_lib_path:
            return []

        self.lib_path = str(prisma_lib_path)

        prisma_result = self.run_go_library(languages, source_codes=targets, policies=registry.checks_dirs_path)

        return prisma_result

    def setup_sast_artifact(self) -> bool:
        current_version = ""
        if not self.prisma_sast_dir_path.exists():
            try:
                os.makedirs(self.prisma_sast_dir_path, exist_ok=True)
            except FileExistsError:
                pass
        else:
            is_file_exists = [f for f in os.listdir(self.prisma_sast_dir_path) if
                              (self.prisma_sast_dir_path / f).is_file() and "library" in f]
            if len(is_file_exists) > 0:
                match = re.match(r"(\d+_\d+_\d+)_library\.(so|dll|dylib)", is_file_exists[0])
                if match:
                    current_version = match.groups()[0]

        if os.getenv("SAST_ARTIFACT_PATH"):
            return True
        status: bool = self.download_sast_artifacts(current_version)

        return status

    @cached(TTLCache(maxsize=1, ttl=300))
    def download_sast_artifacts(self, current_version: str) -> bool:
        try:
            machine = get_machine()
            os_type = platform.system().lower()
            headers = bc_integration.get_default_headers("GET")
            headers["X-Client-Sast-Version"] = current_version
            headers["X-Required-Sast-Version"] = "latest"  # or ant version seperated with _
            response = request_wrapper("GET",
                                       f"{bc_integration.api_url}/{self.sast_platform_base_path}/{os_type}/{machine}/artifacts",
                                       headers=headers,
                                       should_call_raise_for_status=True)

            if response.status_code == 304:
                return True

            match = re.match(r'.*\/(?P<name>\d+_\d+_\d+_library\.(so|dll|dylib))\?.*', response.url)
            if match:
                new_name = match.group('name')
                cli_file_name_path = self.prisma_sast_dir_path / new_name
                self._cleanup_scan()
                cli_file_name_path.touch(exist_ok=True)
                cli_file_name_path.write_bytes(response.content)
                cli_file_name_path.chmod(cli_file_name_path.stat().st_mode | stat.S_IEXEC | stat.S_IREAD)
                logging.debug("sast artifacts downloaded")
            return True
        except Exception:
            logging.debug(
                "Unexpected failure happened during downloading sast artifact. details are below.\n"
                "scanning is terminating. please try again. if it is repeated, please report.\n", exc_info=True)
            return False

    def _cleanup_scan(self) -> None:
        if self.prisma_sast_dir_path.exists():
            for file in os.scandir(self.prisma_sast_dir_path):
                os.unlink(file.path)
            # shutil.rmtree(self.prisma_sast_dir_path)
            logging.info('sast dir is clear')
        else:
            self.prisma_sast_dir_path.mkdir(exist_ok=True)

    def get_sast_artifact(self) -> Optional[Path]:
        env_variable_path = os.getenv("SAST_ARTIFACT_PATH")
        if env_variable_path and os.path.isfile(env_variable_path):
            return Path(env_variable_path)

        files = [(self.prisma_sast_dir_path / f) for f in os.listdir(self.prisma_sast_dir_path) if
                 (self.prisma_sast_dir_path / f).is_file() and "library" in f]

        if len(files) == 0:
            return None

        return files[0]

    def run_go_library(self, languages: Set[SastLanguages],
                       source_codes: List[str],
                       policies: List[str]) -> List[Report]:

        validate_params(languages, source_codes, policies)

        if bc_integration.bc_source:
            name = bc_integration.bc_source.name
        else:
            name = "unknown"

        document = {
            "scan_code_params": {
                "source_codes": source_codes,
                "policies": policies,
                "languages": [a.value for a in languages],
            },
            "auth": {
                "api_key": bc_integration.bc_api_key,
                "platform_url": bc_integration.api_url,
                "client_name": name,
                "version": bc_integration.bc_source_version
            }
        }

        library = ctypes.cdll.LoadLibrary(self.lib_path)
        analyze_code = library.analyzeCode
        analyze_code.restype = ctypes.c_void_p

        # send the document as a byte array of json format
        analyze_code_output = analyze_code(json.dumps(document).encode('utf-8'))

        # we dereference the pointer to a byte array
        analyze_code_bytes = ctypes.string_at(analyze_code_output)

        # convert our byte array to a string
        analyze_code_string = analyze_code_bytes.decode('utf-8')
        d = json.loads(analyze_code_string)
        result = PrismaReport(**d)
        # result: Dict[str, Any] = json.loads(analyze_code_string)
        return self.create_report(result)

    def create_report(self, prisma_report: PrismaReport) -> List[Report]:
        logging.debug("Printing Prisma-SAST profiling data")
        logging.debug(prisma_report.profiler)
        reports: List[Report] = []
        for lang, checks in prisma_report.rule_match.items():
            report = Report(f'{self.check_type.upper()} - {lang.value.title()}')
            for check_id, match_rule in checks.items():
                check_name = match_rule.check_name
                check_cwe = match_rule.check_cwe
                check_owasp = "TBD"  # match.metadata.get('owasp')
                check_result = _CheckResult(result=CheckResult.FAILED)
                severity = get_severity(match_rule.severity)

                for match in match_rule.matches:
                    location = match.location
                    file_abs_path = location.path
                    file_path = file_abs_path.split('/')[-1]
                    file_line_range = [location.start.row, location.end.row]
                    code_block = get_code_block(location.code_block.split('\n'), location.start.row)

                    record = SastRecord(check_id=check_id, check_name=check_name, resource="", evaluations={},
                                        check_class="", check_result=check_result, code_block=code_block,
                                        file_path=file_path, file_line_range=file_line_range,
                                        file_abs_path=file_abs_path, severity=severity, cwe=check_cwe,
                                        owasp=check_owasp, show_severity=True)
                    report.add_record(record)

            reports.append(report)

        return reports


def validate_params(languages: Set[SastLanguages],
                    source_codes: List[str],
                    policies: List[str]) -> None:
    if len(source_codes) == 0:
        raise Exception('must provide source code file or dir for sast runner')

    if len(policies) == 0:
        raise Exception('must provide policy file or dir for sast runner')

    if len(languages) == 0:
        raise Exception('must provide a language for sast runner')


def get_machine() -> str:
    machine = platform.machine().lower()
    if machine in ['amd64', 'x86', 'x86_64', 'x64']:
        return "amd64"

    if machine in ['arm', 'arm64', 'armv8', 'aarch64', 'arm64-v8a']:
        return 'arm64'

    return ''
