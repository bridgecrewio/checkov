import os
import re

from detect_secrets.core.usage import initialize_plugin_settings
from detect_secrets.main import baseline

from checkov.common.comment.enum import COMMENT_REGEX
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.runners.base_runner import BaseRunner
from checkov.runner_filter import RunnerFilter
import linecache

class Runner(BaseRunner):
    check_type = 'secrets'

    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(),
            collect_skip_comments=True):
        report = Report(self.check_type)
        initialize_plugin_settings(None)
        secrets = baseline.create(root_folder, root=root_folder, should_scan_all_files=True)

        for file, secrets in secrets.data.items():
            for secret in secrets:

                line_text = linecache.getline(os.path.join(root_folder, secret.filename), secret.line_number)
                if line_text.split()[0] == 'git_commit':
                    continue
                skip_search = re.search(COMMENT_REGEX, line_text)
                report.add_record(Record(
                    check_id='Mock', # TODO: create check IDs
                    check_name=secret.type,
                    check_result={'result': CheckResult.FAILED},
                    code_block=None,
                    file_path=secret.filename,
                    file_line_range=[secret.line_number, secret.line_number],
                    resource=secret.filename,
                    check_class=None,
                    evaluations=None,
                    file_abs_path=secret.filename
                ))

        return report
