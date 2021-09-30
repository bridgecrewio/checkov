import linecache
import logging
import os
import re
import time
from typing import Optional, List

from detect_secrets import SecretsCollection
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.settings import transient_settings
from typing_extensions import TypedDict

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.graph.graph_builder.utils import run_function_multithreaded
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_paths
from checkov.common.runners.base_runner import ignored_directories
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


class _CheckResult(TypedDict, total=False):
    result: CheckResult
    suppress_comment: str


class Runner(BaseRunner):
    check_type = 'secrets'

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

            def _scan_file(file_paths: List[str]) -> None:
                for file_path in file_paths:
                    start = time.time()
                    try:
                        secrets.scan_file(file_path)
                    except Exception as err:
                        logging.warning(f"Secret scanning:could not process file {file_path}, {err}")
                        continue
                    end = time.time()
                    scan_time = end - start
                    if scan_time > 10:
                        logging.info(f'Scanned {file_path}, took {scan_time} seconds')

            run_function_multithreaded(_scan_file, files_to_scan, 1, num_of_workers=os.cpu_count())

            for _, secret in iter(secrets):
                check_id = SECRET_TYPE_TO_ID.get(secret.type)
                bc_check_id = bc_integration.ckv_to_bc_id_mapping.get(check_id) if bc_integration.ckv_to_bc_id_mapping else None
                if not check_id:
                    continue
                if runner_filter.checks and not runner_filter.should_run_check(check_id, bc_check_id):
                    continue
                result: _CheckResult = {'result': CheckResult.FAILED}
                line_text = linecache.getline(secret.filename, secret.line_number)
                if line_text != "" and len(line_text.split()) > 0 and line_text.split()[0] == 'git_commit':
                    continue
                result = self.search_for_suppression(
                    check_id=check_id,
                    bc_check_id=bc_check_id,
                    secret=secret,
                    runner_filter=runner_filter,
                ) or result
                report.add_resource(f'{secret.filename}:{secret.secret_hash}')
                report.add_record(Record(
                    check_id=check_id,
                    bc_check_id=bc_check_id,
                    check_name=secret.type,
                    check_result=result,
                    code_block=[(secret.line_number, line_text)],
                    file_path=f'/{os.path.relpath(secret.filename, root_folder)}',
                    file_line_range=[secret.line_number, secret.line_number + 1],
                    resource=secret.secret_hash,
                    check_class=None,
                    evaluations=None,
                    file_abs_path=os.path.abspath(secret.filename)
                ))

            return report

    @staticmethod
    def search_for_suppression(
        check_id: str,
        bc_check_id: str,
        secret: PotentialSecret,
        runner_filter: RunnerFilter
    ) -> Optional[_CheckResult]:
        if not runner_filter.should_run_check(check_id, bc_check_id) and check_id in CHECK_ID_TO_SECRET_TYPE.keys():
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
