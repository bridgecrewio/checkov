#!/usr/bin/env python

import argparse
import logging
import os

from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.banner import banner as checkov_banner
from checkov.common.util.docs_generator import print_checks
from checkov.terraform.runner import Runner as tf_runner
from checkov.version import version
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration

logging.basicConfig(level=logging.INFO)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# tell the handler to use this format
console.setFormatter(formatter)


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
    parser.add_argument('-o', '--output', nargs='?', choices=['cli', 'json', 'junitxml'], default='cli',
                        help='Report output format')
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
    runner_registry = RunnerRegistry(banner, tf_runner(), cfn_runner())
    if args.version:
        print(version)
        return
    if args.bc_api_key:
        if args.repo_id is None:
            parser.error("--repo-id argument is required when using --bc-api-key")
        bc_integration.setup_bridgecrew_credentials(bc_api_key=args.bc_api_key, repo_id=args.repo_id)
    if args.list:
        print_checks()
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
