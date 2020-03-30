#!/usr/bin/env python

import logging
import argparse
from checkov.common.util.docs_generator import print_checks
from checkov.cloudformation.runner import Runner as cfn_runner
from checkov.terraform.runner import Runner as tf_runner
from checkov.common.runners.runner_registry import RunnerRegistry
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
    if args.version:
        print(version)
        return
    if args.list:
        print_checks()
        return

    runner_registry = RunnerRegistry(tf_runner(), cfn_runner())
    for root_folder in args.directory:
        file = args.file
        scan_reports = runner_registry.run(root_folder, external_checks_dir=args.external_checks_dir, files=file)
        runner_registry.print_reports(scan_reports, args)


if __name__ == '__main__':
    run()
