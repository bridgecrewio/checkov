#!/usr/bin/env python

import argparse
import logging

from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.common.util.docs_generator import print_checks
from checkov.terraform.runner import Runner as tf_runner
from checkov.version import version

logging.basicConfig(level=logging.INFO)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# tell the handler to use this format
console.setFormatter(formatter)


def run():
    parser = argparse.ArgumentParser(description='Infrastructure as code static analysis')
    parser.add_argument('-v', '--version',
                        help='Checkov version', action='store_true')
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
    args = parser.parse_args()
    runner_registry = RunnerRegistry(tf_runner(), cfn_runner())
    if args.version:
        print(version)
        return
    elif args.list:
        print_checks()
        return
    elif args.directory:
        for root_folder in args.directory:
            file = args.file
            scan_reports = runner_registry.run(root_folder, external_checks_dir=args.external_checks_dir, files=file)
            runner_registry.print_reports(scan_reports, args)
        return
    elif args.file:
        scan_reports = runner_registry.run(None, external_checks_dir=args.external_checks_dir, files=args.file)
        runner_registry.print_reports(scan_reports, args)
    else:
        print("No argument given. Try `checkov --help` for further information")


if __name__ == '__main__':
    run()
