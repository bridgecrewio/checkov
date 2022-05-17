import datetime
import linecache
import logging
import os
import re
from typing import Optional, List

from detect_secrets import SecretsCollection
from detect_secrets.core import scan
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.settings import transient_settings

from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.severities import Severity
from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.parallelizer.parallel_runner import parallel_runner
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report, CheckType
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.runners.base_runner import ignored_directories
from checkov.common.typing import _CheckResult
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.runner_filter import RunnerFilter

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
    # 'Secret Keyword': 'CKV_SECRET_10',
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

ENTROPY_KEYWORD_LIMIT = 3
PROHIBITED_FILES = ['Pipfile.lock', 'yarn.lock', 'package-lock.json', 'requirements.txt']
MAX_FILE_SIZE = int(os.getenv('CHECKOV_MAX_FILE_SIZE', '5000000'))  # 5 MB is default limit


class Runner(BaseRunner):
    check_type = CheckType.SECRETS

    def run(
        self,
        root_folder: str,
        external_checks_dir: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
        runner_filter: RunnerFilter = RunnerFilter(),
        collect_skip_comments: bool = True
    ) -> Report:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        secrets = SecretsCollection()
        with transient_settings({
            # Only run scans with only these plugins.
            'plugins_used': [
                {
                    'name': 'AWSKeyDetector'
                },
                {
                    'name': 'ArtifactoryDetector'
                },
                {
                    'name': 'AzureStorageKeyDetector'
                },
                {
                    'name': 'BasicAuthDetector'
                },
                {
                    'name': 'CloudantDetector'
                },
                {
                    'name': 'IbmCloudIamDetector'
                },
                {
                    'name': 'MailchimpDetector'
                },
                {
                    'name': 'PrivateKeyDetector'
                },
                {
                    'name': 'SlackDetector'
                },
                {
                    'name': 'SoftlayerDetector'
                },
                {
                    'name': 'SquareOAuthDetector'
                },
                {
                    'name': 'StripeDetector'
                },
                {
                    'name': 'TwilioKeyDetector'
                },
                {
                    'name': 'EntropyKeywordCombinator',
                    'path': f'file://{current_dir}/plugins/entropy_keyword_combinator.py',
                    'limit': ENTROPY_KEYWORD_LIMIT
                }
            ]
        }) as settings:
            report = Report(self.check_type)
            # Implement non IaC files (including .terraform dir)
            files_to_scan = files or []
            excluded_paths = (runner_filter.excluded_paths or []) + ignored_directories + [DEFAULT_EXTERNAL_MODULES_DIR]
            if root_folder:
                for root, d_names, f_names in os.walk(root_folder):
                    filter_ignored_paths(root, d_names, excluded_paths)
                    filter_ignored_paths(root, f_names, excluded_paths)
                    for file in f_names:
                        if file not in PROHIBITED_FILES and f".{file.split('.')[-1]}" in SUPPORTED_FILE_EXTENSIONS:
                            files_to_scan.append(os.path.join(root, file))
            logging.info(f'Secrets scanning will scan {len(files_to_scan)} files')

            settings.disable_filters(*['detect_secrets.filters.heuristic.is_indirect_reference'])

            Runner._scan_files(files_to_scan, secrets)

            for _, secret in iter(secrets):
                check_id = SECRET_TYPE_TO_ID.get(secret.type)
                if not check_id:
                    continue
                bc_check_id = metadata_integration.get_bc_id(check_id)
                severity = metadata_integration.get_severity(check_id)
                if runner_filter.checks and not runner_filter.should_run_check(check_id=check_id, bc_check_id=bc_check_id, severity=severity):
                    continue
                result: _CheckResult = {'result': CheckResult.FAILED}
                line_text = linecache.getline(secret.filename, secret.line_number)
                if line_text != "" and len(line_text.split()) > 0 and line_text.split()[0] == 'git_commit':
                    continue
                result = self.search_for_suppression(
                    check_id=check_id,
                    bc_check_id=bc_check_id,
                    severity=severity,
                    secret=secret,
                    runner_filter=runner_filter,
                ) or result
                report.add_resource(f'{secret.filename}:{secret.secret_hash}')
                report.add_record(Record(
                    check_id=check_id,
                    bc_check_id=bc_check_id,
                    severity=severity,
                    check_name=secret.type,
                    check_result=result,
                    code_block=[(secret.line_number, line_text)],
                    file_path=f'/{os.path.relpath(secret.filename, root_folder)}',
                    file_line_range=[secret.line_number, secret.line_number + 1],
                    resource=secret.secret_hash,
                    check_class=None,
                    evaluations=None,
                    file_abs_path=os.path.abspath(secret.filename),
                ))

            return report

    @staticmethod
    def _scan_files(files_to_scan, secrets):
        # implemented the scan function like secrets.scan_files
        def _safe_scan(f):
            full_file_path = os.path.join(secrets.root, f)
            file_size = os.path.getsize(full_file_path)
            if file_size > MAX_FILE_SIZE > 0:
                logging.info(f'Skipping secret scanning on {full_file_path} due to file size. To scan this file for '
                             f'secrets, run this command again with the environment variable "CHECKOV_MAX_FILE_SIZE" '
                             f'to 0 or {file_size + 1}')
                return list()
            try:
                start_time = datetime.datetime.now()
                file_results = list(scan.scan_file(full_file_path))
                end_time = datetime.datetime.now()
                run_time = end_time - start_time
                if run_time > datetime.timedelta(seconds=10):
                    logging.info(f'Secret scanning for {full_file_path} took {run_time} seconds')
                return file_results
            except Exception:
                logging.warning(f"Secret scanning:could not process file {f}")
                logging.debug("Complete trace:", exc_info=True)
                return list()

        results = parallel_runner.run_function(
            func=lambda f: list(_safe_scan(f)), items=files_to_scan,
            run_multiprocess=os.getenv("RUN_SECRETS_MULTIPROCESS", "").lower() == "true")
        for secrets_results in results:
            for secret in secrets_results:
                secrets[os.path.relpath(secret.filename, secrets.root)].add(secret)

    @staticmethod
    def search_for_suppression(
        check_id: str,
        bc_check_id: str,
        severity: Severity,
        secret: PotentialSecret,
        runner_filter: RunnerFilter
    ) -> Optional[_CheckResult]:
        if not runner_filter.should_run_check(check_id=check_id, bc_check_id=bc_check_id, severity=severity) and check_id in CHECK_ID_TO_SECRET_TYPE.keys():
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
