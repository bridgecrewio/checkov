#!/usr/bin/env python

import logging
import argparse

from checkov.terraform.runner import Runner
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
    parser = argparse.ArgumentParser(description='Add some integers.')
    parser.add_argument('-v', '--version',
                        help='Checkov version', action='store_true')
    parser.add_argument('-d', '--directory',
                        help='Terraform root directory (can not be used together with --file). Can be repeated')
    parser.add_argument('-f', '--file', action='append',
                        help='Terraform file(can not be used together with --directory)')
    parser.add_argument('--external-checks-dir', action='append',
                        help='Directory for custom checks to be loaded. Can be repeated')
    parser.add_argument('-l', '--list', help='List checks', action='store_true')
    parser.add_argument('-o', '--output', nargs='?', choices=['cli', 'json', 'junitxml'], default='cli',
                        help='Report output format')
    args = parser.parse_args()
    if args.version:
        print(version)
        return
    if args.list:
        # pylint: disable=unused-import
        import checkov.terraform.util.docs_generator
        return
    else:
        root_folder = args.directory
        file = args.file
        report = Runner().run(root_folder, external_checks_dir=args.external_checks_dir, files=file)
        if args.output == "json":
            report.print_json()
        elif args.output == "junitxml":
            report.print_junit_xml()
        else:
            report.print_console()

        exit(report.get_exit_code())


if __name__ == '__main__':
    run()
