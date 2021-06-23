import logging
import os
import re
from typing import Optional
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets import SecretsCollection
from checkov.common.runners.base_runner import ignored_directories
from detect_secrets.settings import transient_settings
from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.models.consts import SUPPORTED_FILE_EXTENSIONS
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner, filter_ignored_directories
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.runner_filter import RunnerFilter
import linecache

SECRET_TYPE_TO_ID = {
    'Artifactory Credentials': 'CKV_SECRET_1',
    'AWS Access Key': 'CKV_SECRET_2',
    'Azure Storage Account access key': 'CKV_SECRET_3',
    'Basic Auth Credentials': 'CKV_SECRET_4',
    'Cloudant Credentials': 'CKV_SECRET_5',
    # 'Base64 High Entropy String': 'CKV_SECRET_6',
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
    # 'Hex High Entropy String': 'CKV_SECRET_19'
}
CHECK_ID_TO_SECRET_TYPE = {v: k for k, v in SECRET_TYPE_TO_ID.items()}

PROHIBITED_FILES = ['Pipfile.lock', 'yarn.lock', 'package-lock.json', 'requirements.txt']


class Runner(BaseRunner):
    check_type = 'secrets'

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(),
            collect_skip_comments=True) -> Report:
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
            ]
        }):
            report = Report(self.check_type)
            # Implement non IaC files (including .terraform dir)
            files_to_scan = files or []
            excluded_paths = (runner_filter.excluded_paths or []) + ignored_directories + [DEFAULT_EXTERNAL_MODULES_DIR]
            if root_folder:
                for root, d_names, f_names in os.walk(root_folder):
                    filter_ignored_directories(d_names, excluded_paths)
                    for file in f_names:
                        if file not in PROHIBITED_FILES and f".{file.split('.')[-1]}" in SUPPORTED_FILE_EXTENSIONS:
                            files_to_scan.append(os.path.join(root, file))
            logging.info(f'Secrets scanning will scan {len(files_to_scan)} files')
            for file in files_to_scan:
                logging.info(f'Scanning file {file} for secrets')
                try:
                    secrets.scan_file(file)
                except Exception as e:
                    logging.warning(f"Secret scanning:could not process file {file}, {e}")
                    continue

            for _, secret in iter(secrets):
                check_id = SECRET_TYPE_TO_ID.get(secret.type)
                if not check_id:
                    continue
                result = {'result': CheckResult.FAILED}
                line_text = linecache.getline(os.path.join(root_folder, secret.filename), secret.line_number)
                if line_text != "" and line_text.split()[0] == 'git_commit':
                    continue
                result = self.search_for_suppression(check_id, root_folder, secret, runner_filter.skip_checks,
                                                     CHECK_ID_TO_SECRET_TYPE) or result
                report.add_record(Record(
                    check_id=check_id,
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
    def search_for_suppression(check_id: str, root_folder: str, secret: PotentialSecret, skipped_checks: list,
                               CHECK_ID_TO_SECRET_TYPE: dict) -> Optional[dict]:
        if skipped_checks:
            for skipped_check in skipped_checks:
                if skipped_check == check_id and skipped_check in CHECK_ID_TO_SECRET_TYPE:
                    return {'result': CheckResult.SKIPPED,
                            'suppress_comment': f"Secret scan {skipped_check} is skipped"}
        # Check for suppression comment in the line before, the line of, and the line after the secret
        for line_number in [secret.line_number, secret.line_number - 1, secret.line_number + 1]:
            lt = linecache.getline(os.path.join(root_folder, secret.filename), line_number)
            skip_search = re.search(COMMENT_REGEX, lt)
            if skip_search:
                return {'result': CheckResult.SKIPPED, 'suppress_comment': skip_search[1]}
        return None
