from __future__ import annotations

import datetime
import linecache
import logging
import os
import re
from os.path import exists
from pathlib import Path
from typing import TYPE_CHECKING, cast

from detect_secrets import SecretsCollection
from detect_secrets.core import scan
from detect_secrets.settings import transient_settings

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import \
    integration as metadata_integration
from checkov.common.bridgecrew.severities import Severity
from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.runners.base_runner import ignored_directories
from checkov.common.typing import _CheckResult
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.dockerfile import is_docker_file
from checkov.common.util.secrets import omit_secret_value_from_line
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.util.tqdm_utils import ProgressBar
    from detect_secrets.core.potential_secret import PotentialSecret

SOURCE_CODE_EXTENSION = ['.py', '.js', '.properties', '.pem', '.php', '.xml', '.ts', '.env', '.java', '.rb',
                         'go', 'cs', '.txt']
SECRET_TYPE_TO_ID = {
    'Artifactory Credentials': 'CKV_SECRET_1',
    'AWS Access Key': 'CKV_SECRET_2',
    'Azure Storage Account access key': 'CKV_SECRET_3',
    'Basic Auth Credentials': 'CKV_SECRET_4',
    'Cloudant Credentials': 'CKV_SECRET_5',
    'Base64 High Entropy String': 'CKV_SECRET_6',
    'IBM Cloud IAM Key': 'CKV_SECRET_7',
    'IBM COS HMAC Credentials': 'CKV_SECRET_8',
    'JSON Web Token': 'CKV_SECRET_9',
    'Secret Keyword': 'CKV_SECRET_10',
    'Mailchimp Access Key': 'CKV_SECRET_11',
    'NPM tokens': 'CKV_SECRET_12',
    'Private Key': 'CKV_SECRET_13',
    'Slack Token': 'CKV_SECRET_14',
    'SoftLayer Credentials': 'CKV_SECRET_15',
    'Square OAuth Secret': 'CKV_SECRET_16',
    'Stripe Access Key': 'CKV_SECRET_17',
    'Twilio API Key': 'CKV_SECRET_18',
    'Hex High Entropy String': 'CKV_SECRET_19'
}
CHECK_ID_TO_SECRET_TYPE = {v: k for k, v in SECRET_TYPE_TO_ID.items()}

PROHIBITED_FILES = ['Pipfile.lock', 'yarn.lock', 'package-lock.json', 'requirements.txt']

MAX_FILE_SIZE = int(os.getenv('CHECKOV_MAX_FILE_SIZE', '5000000'))  # 5 MB is default limit


class Runner(BaseRunner[None]):
    check_type = CheckType.SECRETS  # noqa: CCE003  # a static attribute

    def run(
            self,
            root_folder: str | None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True
    ) -> Report:
        runner_filter = runner_filter or RunnerFilter()
        current_dir = Path(__file__).parent
        secrets = SecretsCollection()
        plugins_used = [
            {'name': 'AWSKeyDetector'},
            {'name': 'ArtifactoryDetector'},
            {'name': 'AzureStorageKeyDetector'},
            {'name': 'BasicAuthDetector'},
            {'name': 'CloudantDetector'},
            {'name': 'IbmCloudIamDetector'},
            {'name': 'MailchimpDetector'},
            {'name': 'PrivateKeyDetector'},
            {'name': 'SlackDetector'},
            {'name': 'SoftlayerDetector'},
            {'name': 'SquareOAuthDetector'},
            {'name': 'StripeDetector'},
            {'name': 'TwilioKeyDetector'},
            {'name': 'EntropyKeywordCombinator', 'path': f'file://{current_dir}/plugins/entropy_keyword_combinator.py'}
        ]
        custom_plugins = os.getenv("CHECKOV_CUSTOM_DETECTOR_PLUGINS_PATH")
        logging.info(f"Custom detector flag set to {custom_plugins}")
        if custom_plugins:
            detector_path = f"{custom_plugins}/custom_regex_detector.py"
            if exists(detector_path):
                logging.info(f"Custom detector found at {detector_path}. Loading...")
                plugins_used.append({
                    'name': 'CustomRegexDetector',
                    'path': f'file://{detector_path}'
                })
            else:
                logging.info(f"Custom detector not found at path {detector_path}. Skipping...")
        with transient_settings({
            # Only run scans with only these plugins.
            'plugins_used': plugins_used
        }) as settings:
            report = Report(self.check_type)
            if not runner_filter.show_progress_bar:
                self.pbar.turn_off_progress_bar()

            # Implement non IaC files (including .terraform dir)
            files_to_scan = files or []
            excluded_paths = (runner_filter.excluded_paths or []) + ignored_directories + [DEFAULT_EXTERNAL_MODULES_DIR]
            if root_folder:
                enable_secret_scan_all_files = runner_filter.enable_secret_scan_all_files
                block_list_secret_scan = runner_filter.block_list_secret_scan or []
                block_list_secret_scan_lower = [file_type.lower() for file_type in block_list_secret_scan]
                for root, d_names, f_names in os.walk(root_folder):
                    filter_ignored_paths(root, d_names, excluded_paths)
                    filter_ignored_paths(root, f_names, excluded_paths)
                    for file in f_names:
                        if enable_secret_scan_all_files:
                            if is_docker_file(file):
                                if 'dockerfile' not in block_list_secret_scan_lower:
                                    files_to_scan.append(os.path.join(root, file))
                            elif f".{file.split('.')[-1]}" not in block_list_secret_scan_lower:
                                files_to_scan.append(os.path.join(root, file))
                        elif file not in PROHIBITED_FILES and f".{file.split('.')[-1]}" in SUPPORTED_FILE_EXTENSIONS or is_docker_file(file):
                            files_to_scan.append(os.path.join(root, file))
            logging.info(f'Secrets scanning will scan {len(files_to_scan)} files')

            settings.disable_filters(*['detect_secrets.filters.heuristic.is_indirect_reference'])

            self.pbar.initiate(len(files_to_scan))
            self._scan_files(files_to_scan, secrets, self.pbar)
            self.pbar.close()
            secrets_duplication: dict[str, bool] = {}
            for _, secret in secrets:
                check_id = getattr(secret, "check_id", SECRET_TYPE_TO_ID.get(secret.type))
                if not check_id:
                    continue
                secret_key = f'{secret.filename}_{secret.line_number}_{secret.secret_hash}'
                if secret_key in secrets_duplication:
                    continue
                else:
                    secrets_duplication[secret_key] = True
                bc_check_id = metadata_integration.get_bc_id(check_id)
                severity = metadata_integration.get_severity(check_id)
                if not runner_filter.should_run_check(check_id=check_id, bc_check_id=bc_check_id, severity=severity, report_type=CheckType.SECRETS):
                    continue
                result: _CheckResult = {'result': CheckResult.FAILED}
                try:
                    line_text = linecache.getline(secret.filename, secret.line_number)
                except SyntaxError as e:
                    # If encoding is a problem, this is probably not human-readable source code
                    # hence there's no need in flagging this secret
                    logging.info(f'Failed to log secret {secret.type} for file {secret.filename} because of {e}')
                    continue
                if line_text and line_text.startswith('git_commit'):
                    continue
                result = self.search_for_suppression(
                    check_id=check_id,
                    bc_check_id=bc_check_id,
                    severity=severity,
                    secret=secret,
                    runner_filter=runner_filter,
                ) or result
                report.add_resource(f'{secret.filename}:{secret.secret_hash}')
                # 'secret.secret_value' can actually be 'None', but only when 'PotentialSecret' was created
                # via 'load_secret_from_dict'
                line_text_censored = omit_secret_value_from_line(cast(str, secret.secret_value), line_text)
                report.add_record(Record(
                    check_id=check_id,
                    bc_check_id=bc_check_id,
                    severity=severity,
                    check_name=secret.type,
                    check_result=result,
                    code_block=[(secret.line_number, line_text_censored)],
                    file_path=f'/{os.path.relpath(secret.filename, root_folder)}',
                    file_line_range=[secret.line_number, secret.line_number + 1],
                    resource=secret.secret_hash,
                    check_class="",
                    evaluations=None,
                    file_abs_path=os.path.abspath(secret.filename),
                ))
            return report

    @staticmethod
    def _scan_files(files_to_scan: list[str], secrets: SecretsCollection, pbar: ProgressBar) -> None:
        # implemented the scan function like secrets.scan_files
        base_path = secrets.root
        results = parallel_runner.run_function(
            func=lambda f: Runner._safe_scan(f, base_path),
            items=files_to_scan,
            run_multiprocess=os.getenv("RUN_SECRETS_MULTIPROCESS", "").lower() == "true"
        )

        for filename, secrets_results in results:
            pbar.set_additional_data({'Current File Scanned': str(filename)})
            for secret in secrets_results:
                secrets[os.path.relpath(secret.filename, base_path)].add(secret)
            pbar.update()

    @staticmethod
    def _safe_scan(file_path: str, base_path: str) -> tuple[str, list[PotentialSecret]]:
        full_file_path = os.path.join(base_path, file_path)
        file_size = os.path.getsize(full_file_path)
        if file_size > MAX_FILE_SIZE > 0:
            logging.info(
                f'Skipping secret scanning on {full_file_path} due to file size. To scan this file for '
                'secrets, run this command again with the environment variable "CHECKOV_MAX_FILE_SIZE" '
                f'to 0 or {file_size + 1}'
            )
            return file_path, []
        try:
            start_time = datetime.datetime.now()
            file_results = [*scan.scan_file(full_file_path)]
            logging.info(f'file {full_file_path} results {file_results}')
            end_time = datetime.datetime.now()
            run_time = end_time - start_time
            if run_time > datetime.timedelta(seconds=10):
                logging.info(f'Secret scanning for {full_file_path} took {run_time} seconds')
            return file_path, file_results
        except Exception:
            logging.warning(f"Secret scanning:could not process file {full_file_path}")
            logging.debug("Complete trace:", exc_info=True)
            return file_path, []

    @staticmethod
    def search_for_suppression(
            check_id: str,
            bc_check_id: str,
            severity: Severity | None,
            secret: PotentialSecret,
            runner_filter: RunnerFilter
    ) -> _CheckResult | None:
        if not runner_filter.should_run_check(check_id=check_id, bc_check_id=bc_check_id, severity=severity, report_type=CheckType.SECRETS) and check_id in CHECK_ID_TO_SECRET_TYPE.keys():
            return {
                "result": CheckResult.SKIPPED,
                "suppress_comment": f"Secret scan {check_id} is skipped"
            }
        # Check for suppression comment in the line before, the line of, and the line after the secret
        for line_number in [secret.line_number, secret.line_number - 1, secret.line_number + 1]:
            lt = linecache.getline(secret.filename, line_number)
            skip_search = re.search(COMMENT_REGEX, lt)
            if skip_search and (skip_search.group(2) == check_id or skip_search.group(2) == bc_check_id):
                return {
                    "result": CheckResult.SKIPPED,
                    "suppress_comment": skip_search.group(3)[1:] if skip_search.group(3) else "No comment provided"
                }
        return None
