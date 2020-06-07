#!/usr/bin/env python

import argparse
import os

from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner as checkov_banner
from checkov.common.util.docs_generator import print_checks
from checkov.kubernetes.runner import Runner as k8_runner
from checkov.logging_init import init as logging_init
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner as tf_runner
from checkov.version import version

logging_init()

def run(banner=checkov_banner):
    parser = argparse.ArgumentParser(description='Infrastructure as code static analysis')
    parser.add_argument('-v', '--version',
                        help='version', action='store_true')
    parser.add_argument('-d', '--directory', action='append',
                        help='IaC root directory (can not be used together with --file). Can be repeated')
    parser.add_argument('-f', '--file', action='append',
                        help='IaC file(can not be used together with --directory)')
    parser.add_argument('--external-checks-dir', action='append',
                        help='Directory for custom checks to be loaded. Can be repeated')
    parser.add_argument('-l', '--list', help='List checks', action='store_true')
    parser.add_argument('-o', '--output', nargs='?', choices=['cli', 'json', 'junitxml', 'github_failed_only'],
                        default='cli',
                        help='Report output format')
    parser.add_argument('--quiet', action='store_true',
                        default=False,
                        help='in case of CLI output, display only failed checks')
    parser.add_argument('--framework', help='filter scan to run only on a specific infrastructure code frameworks',
                        choices=['cloudformation', 'terraform', 'kubernetes', 'all'], default='all')
    parser.add_argument('-c', '--check',
                        help='filter scan to run only on a specific check identifier(allowlist), You can '
                             'specify multiple checks separated by comma delimiter', default=None)
    parser.add_argument('--skip-check',
                        help='filter scan to run on all check but a specific check identifier(denylist), You can '
                             'specify multiple checks separated by comma delimiter', default=None)
    parser.add_argument('-s', '--soft-fail',
                        help='Runs checks but suppresses error code', action='store_true')
    parser.add_argument('--bc-api-key', help='Bridgecrew API key')
    parser.add_argument('--repo-id',
                        help='Identity string of the repository, with form <repo_owner>/<repo_name>')
    parser.add_argument('-b', '--branch',
                        help="Selected branch of the persisted repository. Only has effect when using the --bc-api-key flag",
                        default='master')
    args = parser.parse_args()
    bc_integration = BcPlatformIntegration()
    runner_filter = RunnerFilter(framework=args.framework, checks=args.check, skip_checks=args.skip_check)
    runner_registry = RunnerRegistry(banner, runner_filter, tf_runner(), cfn_runner(), k8_runner())
    if args.version:
        print(version)
        return
    if args.bc_api_key:
        if args.repo_id is None:
            parser.error("--repo-id argument is required when using --bc-api-key")
            if len(args.repo_id.split('/')) != 2:
                parser.error("--repo-id argument format should be 'organization/repository_name' E.g "
                             "bridgecrewio/checkov")
        bc_integration.setup_bridgecrew_credentials(bc_api_key=args.bc_api_key, repo_id=args.repo_id)
    if args.check and args.skip_check:
        parser.error("--check and --skip-check can not be applied together. please use only one of them")
        return
    if args.list:
        print_checks(framework=args.framework)
        return
    if args.directory:
        for root_folder in args.directory:
            file = args.file
            scan_reports = runner_registry.run(root_folder=root_folder, external_checks_dir=args.external_checks_dir,
                                               files=file)
            if bc_integration.is_integration_configured():
                bc_integration.persist_repository(root_folder)
                bc_integration.persist_scan_results(scan_reports)
                bc_integration.commit_repository(args.branch)
            runner_registry.print_reports(scan_reports, args)
        return
    elif args.file:
        scan_reports = runner_registry.run(external_checks_dir=args.external_checks_dir, files=args.file)
        if bc_integration.is_integration_configured():
            files = [os.path.abspath(file) for file in args.file]
            root_folder = os.path.split(os.path.commonprefix(files))[0]
            bc_integration.persist_repository(root_folder)
            bc_integration.persist_scan_results(scan_reports)
            bc_integration.commit_repository(args.branch)
        runner_registry.print_reports(scan_reports, args)
    else:
        print("No argument given. Try ` --help` for further information")


if __name__ == '__main__':
    run()
