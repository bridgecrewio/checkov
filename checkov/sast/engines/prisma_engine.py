import ctypes
import subprocess  # nosec
import sys
from datetime import datetime
import json
import logging
import os
import platform
import re
import stat
from pathlib import Path
from typing import Optional, List, Set, Union, Dict, Any, Tuple, cast

from cachetools import cached, TTLCache
from pydantic import ValidationError

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as policy_metadata_integration
from checkov.common.bridgecrew.platform_key import bridgecrew_dir
from checkov.common.bridgecrew.severities import get_severity, Severity, Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.common.output.report import Report
from checkov.common.sast.consts import CDKLanguages, SastLanguages
from checkov.common.sca.reachability.sast_contract.data_fetcher_sast_lib import SastReachabilityDataFetcher
from checkov.common.typing import _CheckResult
from checkov.common.util.http_utils import request_wrapper
from checkov.sast.checks_infra.base_registry import Registry
from checkov.sast.common import get_code_block_from_start
from checkov.sast.engines.base_engine import SastEngine
from checkov.sast.prisma_models.library_input import LibraryInput
from checkov.sast.prisma_models.policies_list import SastPolicies
from checkov.common.sast.consts import CDK_FRAMEWORK_PREFIX
from checkov.common.sast.report_types import PrismaReport, RuleMatch, create_empty_report
from checkov.sast.record import SastRecord
from checkov.sast.report import SastReport
from checkov.cdk.report import CDKReport
from checkov.sast.engines.files_filter_manager import FilesFilterManager

logger = logging.getLogger(__name__)

REPORT_PARSING_ERRORS = "report_parsing_errors"
FILE_NAME_PATTERN = re.compile(r"(\d+_\d+_\d+)_library\.(so|dll|dylib)")
SAST_CORE_FILENAME_PATTERN = re.compile(rf"{FILE_NAME_PATTERN.pattern}$")
SAST_CORE_URL_PATTERN = re.compile(rf".*/(?P<name>v?{FILE_NAME_PATTERN.pattern})\?.*")


class PrismaEngine(SastEngine):
    def __init__(self) -> None:
        self.lib_path = ""
        self.winmode = sys.platform.startswith('win')
        self.check_type = CheckType.SAST
        self.prisma_sast_dir_path = Path(bridgecrew_dir) / "sast"
        self.sast_platform_base_path = "api/v1/sast"
        self.enable_inline_suppressions = os.getenv("ENABLE_SAST_INLINE_SUPPRESSIONS", False)

    def get_check_thresholds(self, registry: Registry) -> Tuple[Severity, Severity]:
        """
        Returns a tuple of check threshold and skip check threshold..

        If a severity was specified in --check and / or --skip-check, then return a tuple of those values (these override enforcement rules).
        Else if enforcement rules are enabled, return a tuple of the enforcement rule's SAST soft fail threshold and NONE.
        Else return a tuple of NONE, NONE
        """
        none = Severities[BcSeverities.NONE]

        check_threshold: Optional[Severity] = registry.runner_filter.check_threshold  # type:ignore[union-attr] # not null
        skip_check_threshold: Optional[Severity] = registry.runner_filter.skip_check_threshold  # type:ignore[union-attr] # not null
        enforcement_threshold: Optional[Severity] = cast(Severity, registry.runner_filter.enforcement_rule_configs[self.check_type]) if registry.runner_filter.use_enforcement_rules else None  # type:ignore[union-attr] # not null

        return (check_threshold or none, skip_check_threshold or none) if (check_threshold or skip_check_threshold) else \
            (enforcement_threshold, none) if enforcement_threshold else \
            (none, none)

    def get_reports(self, targets: List[str], registry: Registry, languages: Set[SastLanguages], cdk_languages: List[CDKLanguages]) -> List[Report]:
        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run SAST Prisma Cloud scanning")
            return []

        status = self.setup_sast_artifact()
        if not status:
            return []

        prisma_lib_path = self.get_sast_artifact()
        if not prisma_lib_path:
            return []

        self.lib_path = str(prisma_lib_path)

        check_threshold, skip_check_threshold = self.get_check_thresholds(registry)

        skip_paths = registry.runner_filter.excluded_paths if registry.runner_filter else []

        files_filter_manager = FilesFilterManager(targets, languages)
        skip_paths += files_filter_manager.get_files_to_filter()

        library_input: LibraryInput = {
            'languages': languages,
            'source_codes': targets,
            'policies': registry.checks_dirs_path,
            'checks': registry.runner_filter.checks if registry.runner_filter else [],
            'skip_checks': registry.runner_filter.skip_checks if registry.runner_filter else [],
            'check_threshold': check_threshold,
            'skip_check_threshold': skip_check_threshold,
            'platform_check_metadata': policy_metadata_integration.sast_check_metadata or {},
            'skip_path': skip_paths,
            'report_imports': registry.runner_filter.report_sast_imports if registry.runner_filter else False,
            'remove_default_policies': registry.runner_filter.remove_default_sast_policies if registry.runner_filter else False,
            'report_reachability': registry.runner_filter.report_sast_reachability if registry.runner_filter else False,
            'cdk_languages': cdk_languages
        }
        prisma_result = self.run_go_library(**library_input)

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
                latest_file = os.path.join(self.prisma_sast_dir_path, is_file_exists[0])
                creation_time = os.path.getmtime(latest_file)
                now = datetime.now().timestamp()
                diff = datetime.fromtimestamp(now) - datetime.fromtimestamp(creation_time)
                if diff.days < 1:
                    match = re.search(SAST_CORE_FILENAME_PATTERN, latest_file)
                    if match:
                        current_version = match.groups()[0]

        if os.getenv("SAST_ARTIFACT_PATH"):
            logging.debug(f'using local artifact in path {os.getenv("SAST_ARTIFACT_PATH")}')
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

            # don't use the 'should_call_raise_for_status' parameter for now, because it logs errors messages
            response = request_wrapper(
                method="GET",
                url=f"{bc_integration.api_url}/{self.sast_platform_base_path}/{os_type}/{machine}/artifacts",
                headers=headers,
            )
            response.raise_for_status()

            if response.status_code == 304:
                return True

            match = re.match(SAST_CORE_URL_PATTERN, response.url)
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
                       policies: List[str],
                       checks: List[str],
                       skip_checks: List[str],
                       skip_path: List[str],
                       check_threshold: Severity,
                       skip_check_threshold: Severity,
                       platform_check_metadata: Dict[str, Any],
                       cdk_languages: List[CDKLanguages],
                       list_policies: bool = False,
                       report_imports: bool = True,
                       report_reachability: bool = False,
                       remove_default_policies: bool = False) -> Union[List[Report], SastPolicies]:

        validate_params(languages, source_codes, list_policies)

        if bc_integration.bc_source:
            name = bc_integration.bc_source.name
        else:
            name = "unknown"

        reachability_data = None
        if report_reachability or report_imports:
            # TODO - run sast-core per src
            for source_code in source_codes:
                reachability_data = get_reachability_data(source_code)

        document = {
            "scan_code_params": {
                "source_codes": source_codes,
                "policies": policies,
                "languages": [a.value for a in languages],
                "checks": checks,
                "skip_checks": skip_checks,
                "skip_path": skip_path,
                "check_threshold": str(check_threshold),
                "skip_check_threshold": str(skip_check_threshold),
                "platform_check_metadata": platform_check_metadata,
                "list_policies": list_policies,
                "report_imports": report_imports,
                "remove_default_policies": remove_default_policies,
                "report_reachability": report_reachability,
                "reachability_data": reachability_data,
                "cdk_languages": [a.value for a in cdk_languages]
            },
            "auth": {
                "api_key": bc_integration.get_auth_token(),
                "platform_url": bc_integration.api_url,
                "client_name": name,
                "version": bc_integration.bc_source_version
            }
        }

        if list_policies:
            return self.run_go_library_list_policies(document)

        if self.winmode:
            sast_report = self._windows_sast_scan(document)
        else:
            sast_report = self._sast_default_scan(document)
        try:
            result = self.create_prisma_report(sast_report)
        except ValidationError as e:
            result = create_empty_report(list(languages))
            result.errors = {REPORT_PARSING_ERRORS: [str(err) for err in e.errors()]}
        return self.create_report(result)

    def _sast_default_scan(self, sast_input: Dict[str, Any]) -> Dict[str, Any]:
        library = ctypes.cdll.LoadLibrary(self.lib_path)
        analyze_code = library.analyzeCode
        analyze_code.restype = ctypes.c_void_p
        # send the document as a byte array of json format
        analyze_code_output = analyze_code(json.dumps(sast_input).encode('utf-8'))
        # we dereference the pointer to a byte array
        analyze_code_bytes = ctypes.string_at(analyze_code_output)
        # convert our byte array to a string
        analyze_code_string = analyze_code_bytes.decode('utf-8')
        return json.loads(analyze_code_string)  # type: ignore

    def _windows_sast_scan(self, sast_input: Dict[str, Any]) -> Dict[str, Any]:
        lib_dir_path = f"{os.path.dirname(self.lib_path)}"
        checkov_input_path = os.path.join(lib_dir_path, "checkov_input.json")
        sast_output_path = os.path.join(lib_dir_path, "sast_output.json")
        with open(checkov_input_path, 'w') as f:
            f.write(json.dumps(sast_input))
        log_level_str = "set LOG_LEVEL=" + os.getenv("LOG_LEVEL", "INFO")
        callargs = [log_level_str, "&", self.lib_path, checkov_input_path, sast_output_path]
        subprocess.run(callargs, shell=True)  # nosec B404, B603, B602

        with open(sast_output_path, 'r', encoding='utf-8') as f:
            report = f.read()
        parsed_report = json.loads(report)
        # cleanup
        os.remove(checkov_input_path)
        os.remove(sast_output_path)
        return parsed_report  # type: ignore

    def create_prisma_report(self, data: Dict[str, Any]) -> PrismaReport:
        if not data.get("imports"):
            data["imports"] = {}
        if not data.get("reachability_report"):
            data["reachability_report"] = {}
        return PrismaReport(**data)

    def run_go_library_list_policies(self, document: Dict[str, Any]) -> SastPolicies:
        try:
            library = ctypes.cdll.LoadLibrary(self.lib_path)
            list_policies = library.listPolicies
            list_policies.restype = ctypes.c_void_p

            # send the document as a byte array of json format
            list_policies_output = list_policies(json.dumps(document).encode('utf-8'))

            # we dereference the pointer to a byte array
            list_policies_bytes = ctypes.string_at(list_policies_output)

            # convert our byte array to a string
            list_policies_string = list_policies_bytes.decode('utf-8')

            d = json.loads(list_policies_string)
        except Exception as e:
            logging.error(e)
            return {}

        try:
            return SastPolicies(**d)
        except ValidationError:
            if d.get('errors'):
                logging.error(d.get('errors'))
            return {}

    def create_report(self, prisma_report: PrismaReport) -> List[Union[SastReport, CDKReport]]:
        logging.debug("Printing Prisma-SAST profiling data")
        logging.debug(prisma_report.profiler)
        reports: List[SastReport] = []
        for lang, checks in prisma_report.rule_match.items():
            sast_report = PrismaReport(rule_match={lang: checks}, errors=prisma_report.errors, profiler=prisma_report.profiler,
                                       run_metadata=prisma_report.run_metadata, imports={}, reachability_report={},
                                       skipped_checks_by_file=prisma_report.skipped_checks_by_file)
            report = SastReport(f'{self.check_type.lower()}_{lang.value}', prisma_report.run_metadata, lang, sast_report)
            for check_id, match_rule in checks.items():
                check_name = match_rule.check_name
                check_cwe = match_rule.check_cwe
                check_owasp = match_rule.check_owasp
                severity = get_severity(match_rule.severity)

                for match in match_rule.matches:
                    location = match.location
                    file_abs_path = location.path
                    file_path = file_abs_path.split('/')[-1]
                    file_line_range = [location.start.row, location.end.row]
                    split_code_block = [line + '\n' for line in location.code_block.split('\n')]
                    code_block = get_code_block_from_start(split_code_block, location.start.row)
                    metadata = match.metadata

                    if self.enable_inline_suppressions and any(skipped_check.check_id == match_rule.check_id for skipped_check in prisma_report.skipped_checks_by_file.get(file_abs_path, [])):
                        check_result = _CheckResult(
                            result=CheckResult.SKIPPED,
                            suppress_comment=next(skipped_check.suppress_comment for skipped_check in prisma_report.skipped_checks_by_file.get(file_abs_path, []) if skipped_check.check_id == match_rule.check_id))
                    else:
                        check_result = _CheckResult(result=CheckResult.FAILED)
                    record = SastRecord(check_id=check_id, check_name=check_name, resource="", evaluations={},
                                        check_class="", check_result=check_result, code_block=code_block,
                                        file_path=file_path, file_line_range=file_line_range, metadata=metadata,
                                        file_abs_path=file_abs_path, severity=severity, cwe=check_cwe,
                                        owasp=check_owasp, show_severity=True)
                    report.add_record(record)
            report_parsing_errors = prisma_report.errors.get(REPORT_PARSING_ERRORS)
            if report_parsing_errors:
                report.add_parsing_errors(report_parsing_errors)
            reports.append(report)

        for lang in prisma_report.imports:
            for report in reports:
                if report.language == lang:
                    report.sast_imports = prisma_report.imports[lang]
                    break
            else:
                sast_report = PrismaReport(rule_match={lang: {}}, errors=prisma_report.errors, profiler=prisma_report.profiler,
                                           run_metadata=prisma_report.run_metadata, imports={}, reachability_report={},
                                           skipped_checks_by_file={})
                report = SastReport(f'{self.check_type.lower()}_{lang.value}', prisma_report.run_metadata, lang, sast_report)
                report.sast_imports = prisma_report.imports[lang]
                reports.append(report)

        for lang in prisma_report.reachability_report:
            for report in reports:
                if report.language == lang:
                    report.sast_reachability = prisma_report.reachability_report[lang]
                    break
            else:
                sast_report = PrismaReport(rule_match={lang: {}}, errors=prisma_report.errors, profiler=prisma_report.profiler,
                                           run_metadata=prisma_report.run_metadata, imports={}, reachability_report={},
                                           skipped_checks_by_file={})
                report = SastReport(f'{self.check_type.lower()}_{lang.value}', prisma_report.run_metadata, lang, sast_report)
                report.sast_reachability = prisma_report.reachability_report[lang]
                reports.append(report)

        all_report = self._split_sast_cdk_reports(reports)
        return all_report

    def _split_sast_cdk_reports(self, sast_reports: List[SastReport]) -> List[Union[SastReport, CDKReport]]:
        cdk_reports: List[CDKReport] = []
        for report in sast_reports:
            for lang, rule_matches in report.sast_report.rule_match.items():
                sast_rule_matches: Dict[str, RuleMatch] = {}
                for policy_id, rule_match in rule_matches.items():
                    if rule_match.metadata.framework != CDK_FRAMEWORK_PREFIX:  # type: ignore
                        sast_rule_matches[policy_id] = rule_match
                        continue
                    self._update_cdk_report(lang, cdk_reports, report, policy_id, rule_match)

                if sast_rule_matches:
                    report.sast_report.rule_match[lang] = sast_rule_matches
                else:
                    report.sast_report.rule_match = {}
                self._update_sast_report_checks(report, cdk_reports)

        return self._get_all_reports(sast_reports, cdk_reports)

    @staticmethod
    def _update_cdk_report(lang: SastLanguages, cdk_reports: List[CDKReport], sast_report: SastReport, policy_id: str, rule_match: RuleMatch) -> None:
        if lang not in [c.language for c in cdk_reports]:
            new_cdk_report = PrismaReport(rule_match={lang: {}}, errors=sast_report.sast_report.errors,
                                          profiler=sast_report.sast_report.profiler,
                                          run_metadata=sast_report.sast_report.run_metadata,
                                          imports={}, reachability_report={}, skipped_checks_by_file={})
            new_report = CDKReport(f'{CDK_FRAMEWORK_PREFIX}_{lang.value}', sast_report.sast_report.run_metadata, lang, new_cdk_report)
            cdk_reports.append(new_report)
        for cdk_report in cdk_reports:
            if cdk_report.language == lang:
                cdk_report.cdk_report.rule_match[lang][policy_id] = rule_match
                for failed_check in sast_report.failed_checks:
                    if failed_check.check_id == policy_id:
                        cdk_report.failed_checks.append(failed_check)

                for skiped_check in sast_report.skipped_checks:
                    if skiped_check.check_id == policy_id:
                        cdk_report.skipped_checks.append(skiped_check)
                break

    def _update_sast_report_checks(self, report: SastReport, cdk_reports: List[CDKReport]) -> None:
        sast_failed_checks = []
        sast_skiped_checks = []

        if report.language not in [c.language for c in cdk_reports]:
            report.failed_checks = report.failed_checks
            report.skipped_checks = report.skipped_checks
            return

        for cdk_report in cdk_reports:
            fail_check = self._get_sast_check(report, cdk_report, report.failed_checks)
            if fail_check:
                sast_failed_checks.append(fail_check)
            skip_check = self._get_sast_check(report, cdk_report, report.skipped_checks)
            if skip_check:
                sast_skiped_checks.append(skip_check)

        report.failed_checks = sast_failed_checks
        report.skipped_checks = sast_skiped_checks

    @staticmethod
    def _get_sast_check(sast_report: SastReport, cdk_report: CDKReport, sast_report_checks: List[Any]) -> Any:
        for check in sast_report_checks:
            if sast_report.language == cdk_report.language and check.check_id not in [s.check_id for s in cdk_report.skipped_checks]:
                return check
        return None

    def _get_all_reports(self, sast_reports: List[SastReport], cdk_reports: List[CDKReport]) -> List[Union[SastReport, CDKReport]]:
        all_reports = []
        for report in sast_reports + cdk_reports:
            if report.check_type.startswith('cdk'):
                if report.cdk_report.rule_match:  # type: ignore
                    all_reports.append(report)
                    continue
            if report.check_type.startswith('sast'):
                if report.sast_report.rule_match or report.sast_reachability or report.sast_imports:  # type: ignore
                    all_reports.append(report)
                    continue
        return all_reports

    def get_policies(self, languages: Set[SastLanguages]) -> SastPolicies:
        if not bc_integration.bc_api_key:
            logging.info("The --bc-api-key flag needs to be set to run Sast prisma scanning")
            return []

        self.setup_sast_artifact()
        prisma_lib_path = self.get_sast_artifact()
        if not prisma_lib_path:
            return []

        self.lib_path = str(prisma_lib_path)

        library_input: LibraryInput = {
            'languages': languages,
            'list_policies': True,
            'source_codes': [],
            'policies': [],
            'checks': [],
            'skip_checks': [],
            'check_threshold': Severities[BcSeverities.NONE],
            'skip_check_threshold': Severities[BcSeverities.NONE],
            'platform_check_metadata': policy_metadata_integration.sast_check_metadata,
            'skip_path': [],
            'report_imports': False,
            'report_reachability': False,
            'cdk_languages': []
        }
        prisma_result = self.run_go_library(**library_input)
        return prisma_result


def validate_params(languages: Set[SastLanguages],
                    source_codes: List[str],
                    list_policies: bool) -> None:
    if list_policies:
        return

    if len(source_codes) == 0:
        raise Exception('must provide source code file or dir for sast runner')

    if len(languages) == 0:
        raise Exception('must provide a language for sast runner')


def get_machine() -> str:
    machine = platform.machine().lower()
    if machine in ['amd64', 'x86', 'x86_64', 'x64']:
        return "amd64"

    if machine in ['arm', 'arm64', 'armv8', 'aarch64', 'arm64-v8a']:
        return 'arm64'

    return ''


def get_reachability_data(repo_path: str) -> Dict[str, Any]:
    fetcher = SastReachabilityDataFetcher()
    reachability_data = fetcher.fetch(repository_name=repo_path, repository_root_dir=repo_path)
    data: Dict[str, Any] = {}
    if not reachability_data:
        return data
    langs = reachability_data.aliasMapping.get("languages")
    if not langs:
        return {}
    for lang, lang_data in langs.items():
        if lang == "nodejs":
            lang = "javascript"
        data[lang] = {"package_alias": {}}
        for _, files in lang_data.get("repositories", {}).items():
            for _, files_data in files.get("files", {}).items():
                for original_package_name, package_alias in files_data.get("packageAliases", {}).items():
                    aliases = package_alias.get("packageAliases", [])
                    if aliases:
                        data[lang]["package_alias"][original_package_name] = aliases[0]
    return data
