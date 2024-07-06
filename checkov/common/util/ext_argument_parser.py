from __future__ import annotations

from io import StringIO
from typing import Any, TYPE_CHECKING, cast, List

import configargparse

from checkov.common.bridgecrew.check_type import checkov_runners
from checkov.common.runners.runner_registry import OUTPUT_CHOICES, SUMMARY_POSITIONS
from checkov.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from checkov.common.util.type_forcers import convert_str_to_bool
from checkov.version import version

if TYPE_CHECKING:
    import argparse


def flatten_csv(list_to_flatten: List[List[str]]) -> List[str]:
    """
    Flattens a list of list of strings into a list of strings, while also splitting out comma-separated values
    Duplicates will be removed.
    [['terraform', 'arm'], ['bicep,cloudformation,arm']] -> ['terraform', 'arm', 'bicep', 'cloudformation']
    (Order is not guaranteed)
    """
    if not list_to_flatten:
        return []
    return list({s for sublist in list_to_flatten for val in sublist for s in val.split(',')})


class ExtArgumentParser(configargparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields_to_sanitize: set[Any] = set()

    def add(self, *args: Any, **kwargs: Any) -> None:
        if kwargs.pop("sanitize", False):
            self.fields_to_sanitize.add(args[0])
        super().add(*args, **kwargs)

    def format_values(self, sanitize: bool = False) -> str:
        if not sanitize:
            return cast(str, super().format_values())

        source_key_to_display_value_map = {
            configargparse._COMMAND_LINE_SOURCE_KEY: "Command Line Args: ",
            configargparse._ENV_VAR_SOURCE_KEY: "Environment Variables:\n",
            configargparse._CONFIG_FILE_SOURCE_KEY: "Config File (%s):\n",
            configargparse._DEFAULTS_SOURCE_KEY: "Defaults:\n",
        }

        r = StringIO()
        for source, settings in self._source_to_settings.items():
            source = source.split("|")
            source = source_key_to_display_value_map[source[0]] % tuple(source[1:])
            r.write(source)
            for key, (action, value) in settings.items():
                if key:
                    if key in self.fields_to_sanitize or action.option_strings[0] in self.fields_to_sanitize:
                        value = "****"
                    r.write("  {:<19}{}\n".format(key + ":", value))
                else:
                    if isinstance(value, str):
                        r.write("  %s\n" % value)
                    elif isinstance(value, list):
                        value = list(value)  # copy
                        if source == "Command Line Args: ":
                            index = 0
                            while index < len(value):
                                if value[index] in self.fields_to_sanitize:
                                    index += 1
                                    value[index] = "****"
                                index += 1
                        r.write("  %s\n" % " ".join(value))

        return r.getvalue()

    def write_config_file(
            self, parsed_namespace: argparse.Namespace, output_file_paths: list[str], exit_after: bool = False
    ) -> None:
        """
        Write the given settings to output files. Overrides write_config_file from the class ArgumentParser for
        correcting types of some attributes (example: check, skip_check)

        :param parsed_namespace: namespace object created within parse_known_args()
        :param output_file_paths: any number of file paths to write the config to
        :param exit_after: whether to exit the program after writing the config files
        """
        for output_file_path in output_file_paths:
            # validate the output file path
            try:
                with self._config_file_open_func(output_file_path, "w") as output_file:
                    pass
            except IOError as e:
                raise ValueError(f"Couldn't open {output_file_path} for writing") from e
        if output_file_paths:
            # generate the config file contents
            config_items = self.get_items_for_config_file_output(self._source_to_settings, parsed_namespace)
            # convert check, skip_check, soft_fail_on and hard_fail_on to list
            if "check" in config_items.keys():
                config_items["check"] = config_items["check"][0].split(",")
            if "skip-check" in config_items.keys():
                config_items["skip-check"] = config_items["skip-check"][0].split(",")
            if "soft-fail-on" in config_items.keys():
                config_items["soft-fail-on"] = config_items["soft-fail-on"][0].split(",")
            if "hard-fail-on" in config_items.keys():
                config_items["hard-fail-on"] = config_items["hard-fail-on"][0].split(",")
            # convert strings to booleans
            for k in config_items.keys():
                config_items[k] = convert_str_to_bool(config_items[k])

            file_contents = self._config_file_parser.serialize(config_items)
            for output_file_path in output_file_paths:
                with self._config_file_open_func(output_file_path, "w") as output_file:
                    output_file.write(file_contents)
            message = "Wrote config file to " + ", ".join(output_file_paths)
            if exit_after:
                self.exit(0, message)
            else:
                print(message)

    def add_parser_args(self) -> None:
        self.add(
            "-v",
            "--version",
            help="version",
            action="version",
            version=version,
        )
        self.add(
            "--support",
            action="store_true",
            help="Enable debug logs and upload the logs to the server. Requires a Bridgecrew or Prisma Cloud API key.",
            default=None
        )
        self.add(
            "-d",
            "--directory",
            action="append",
            help="IaC root directory (can not be used together with --file).",
        )
        self.add(
            "--add-check",
            action="store_true",
            help="Generate a new check via CLI prompt",
        )
        self.add(
            "-f",
            "--file",
            action="append",
            help="File to scan (can not be used together with --directory). With this option, Checkov will attempt "
                 'to filter the runners based on the file type. For example, if you specify a ".tf" file, only the '
                 "terraform and secrets frameworks will be included. You can further limit this (e.g., skip secrets) "
                 "by using the --skip-framework argument.",
            nargs="+",
        )
        self.add(
            "--skip-path",
            action="append",
            help="Path (file or directory) to skip, using regular expression logic, relative to current "
                 'working directory. Word boundaries are not implicit; i.e., specifying "dir1" will skip any '
                 'directory or subdirectory named "dir1". Ignored with -f. Can be specified multiple times.',
        )
        self.add(
            "--external-checks-dir",
            action="append",
            help="Directory for custom checks to be loaded. Can be repeated. Note that this will run Python code "
                 'from the specified directory, so only use this option with trusted directories.',
        )
        self.add(
            "--external-checks-git",
            action="append",
            help="GitHub url of external checks to be added. You can specify a subdirectory after a double-slash //."
                 "It is ossible to use ?ref=tags/tagName or ?ref=heads/branchName or ?ref=commit_id and "
                 "cannot be used together with --external-checks-dir. Note that this will run Python code "
                 "from the specified directory, so only use this option with trusted repositories.",
        )
        self.add(
            "-l",
            "--list",
            help="List checks",
            action="store_true",
        )
        self.add(
            "-o",
            "--output",
            action="append",
            choices=OUTPUT_CHOICES,
            default=None,
            help="Report output format. Add multiple outputs by using the flag multiple times (-o sarif -o cli)",
        )
        self.add(
            "--output-file-path",
            default=None,
            help="Name of the output folder to save the chosen output formats. "
                 "Advanced usage: "
                 "By using -o cli -o junitxml --output-file-path console,results.xml the CLI output will be printed "
                 "to the console and the JunitXML output to the file results.xml.",
        )
        self.add(
            "--output-bc-ids",
            action="store_true",
            help="Print Bridgecrew platform IDs (BC...) instead of Checkov IDs (CKV...), if the check exists in the platform",
        )
        self.add(
            "--include-all-checkov-policies",
            action="store_true",
            help="When running with an API key, Checkov will omit any policies that do not exist in Prisma Cloud platform, "
                 "except for local custom policies loaded with the --external-check flags. Use this key to include policies "
                 "that only exist in Checkov in the scan. Note that this will make the local CLI results different from the "
                 "results you see in the platform. Has no effect if you are not using an API key. Use the --check option to "
                 "explicitly include checks by ID even if they are not in the platform, without using this flag.",
        )
        self.add(
            "--quiet",
            action="store_true",
            default=False,
            help="in case of CLI output, display only failed checks. Also disables progress bars",
        )
        self.add(
            "--compact",
            action="store_true",
            default=False,
            help="in case of CLI output, do not display code blocks",
        )
        self.add(
            "--framework",
            help="Filter scan to run only on specific infrastructure as code frameworks. Defaults to all frameworks. If you "
                 "explicitly include 'all' as a value, then all other values are ignored. Enter as a "
                 "comma-separated list or repeat the flag multiple times. For example, --framework terraform,sca_package "
                 f"or --framework terraform --framework sca_package. Possible values: {', '.join(['all'] + checkov_runners)}",
            env_var="CKV_FRAMEWORK",
            action='append',
            nargs='+'  # we will still allow the old way (eg: --framework terraform arm cloudformation), just not prefer it
            # intentionally no default value - we will set it explicitly during normalization (it messes up the list of lists)
        )
        self.add(
            "--skip-framework",
            help="Filter scan to skip specific infrastructure as code frameworks. "
                 "This will be included automatically for some frameworks if system dependencies "
                 "are missing. Enter as a comma-separated list or repeat the flag multiple times. For example, "
                 "--skip-framework terraform,sca_package or --skip-framework terraform --skip-framework sca_package. "
                 "Cannot include values that are also included in --framework. "
                 f"Possible values: {', '.join(checkov_runners)}",
            default=None,
            action='append',
            nargs='+'
        )
        self.add(
            "-c",
            "--check",
            help="Checks to run; any other checks will be skipped. Enter one or more items separated by commas. "
                 "Each item may be either a Checkov check ID (CKV_AWS_123), a BC check ID (BC_AWS_GENERAL_123), or "
                 "a severity (LOW, MEDIUM, HIGH, CRITICAL). If you use a severity, then all checks equal to or "
                 "above the lowest severity in the list will be included. This option can be combined with "
                 "--skip-check. If it is, then the logic is to first take all checks that match this list, and then "
                 "remove all checks that match the skip list. For example, if you use --check CKV_123 and "
                 "--skip-check LOW, then CKV_123 will not run if it is a LOW severity. Similarly, if you use "
                 "--check CKV_789 --skip-check MEDIUM, then CKV_789 will run if it is a HIGH severity. If you use a "
                 "check ID here along with an API key, and the check is not part of the BC / PC platform, then the "
                 "check will still be run (see --include-all-checkov-policies for more info).",
            action="append",
            default=None,
            env_var="CKV_CHECK",
        )
        self.add(
            "--skip-check",
            help="Checks to skip; any other checks will not be run. Enter one or more items separated by commas. "
                 "Each item may be either a Checkov check ID (CKV_AWS_123), a BC check ID (BC_AWS_GENERAL_123), or "
                 "a severity (LOW, MEDIUM, HIGH, CRITICAL). If you use a severity, then all checks equal to or "
                 "below the highest severity in the list will be skipped. This option can be combined with --check. "
                 "If it is, priority is given to checks explicitly listed by ID or wildcard over checks listed by "
                 "severity. For example, if you use --skip-check CKV_123 and --check HIGH, then CKV_123 will be "
                 "skipped even if it is a HIGH severity. In the case of a tie (e.g., --check MEDIUM and "
                 "--skip-check HIGH for a medium severity check), then the check will be skipped.",
            action="append",
            default=None,
            env_var="CKV_SKIP_CHECK",
        )
        self.add(
            "--run-all-external-checks",
            action="store_true",
            help="Run all external checks (loaded via --external-checks options) even if the checks are not present "
                 "in the --check list. This allows you to always ensure that new checks present in the external "
                 "source are used. If an external check is included in --skip-check, it will still be skipped.",
        )
        self.add(
            "-s",
            "--soft-fail",
            help="Runs checks but always returns a 0 exit code. Using either --soft-fail-on and / or --hard-fail-on "
                 "overrides this option, except for the case when a result does not match either of the soft fail "
                 "or hard fail criteria, in which case this flag determines the result.",
            action="store_true",
        )
        self.add(
            "--soft-fail-on",
            help="Exits with a 0 exit code if only the specified items fail. Enter one or more items "
                 "separated by commas. Each item may be either a Checkov check ID (CKV_AWS_123), a BC "
                 "check ID (BC_AWS_GENERAL_123), or a severity (LOW, MEDIUM, HIGH, CRITICAL). If you use "
                 "a severity, then any severity equal to or less than the highest severity in the list "
                 "will result in a soft fail. This option may be used with --hard-fail-on, using the same "
                 "priority logic described in --check and --skip-check options above, with --hard-fail-on "
                 "taking precedence in a tie. If a given result does not meet the --soft-fail-on nor "
                 "the --hard-fail-on criteria, then the default is to hard fail",
            action="append",
            default=None,
        )
        self.add(
            "--hard-fail-on",
            help="Exits with a non-zero exit code for specified checks. Enter one or more items "
                 "separated by commas. Each item may be either a Checkov check ID (CKV_AWS_123), a BC "
                 "check ID (BC_AWS_GENERAL_123), or a severity (LOW, MEDIUM, HIGH, CRITICAL). If you use a "
                 "severity, then any severity equal to or greater than the lowest severity in the list will "
                 "result in a hard fail. This option can be used with --soft-fail-on, using the same "
                 "priority logic described in --check and --skip-check options above, with --hard-fail-on "
                 "taking precedence in a tie.",
            action="append",
            default=None,
        )
        self.add(
            "--bc-api-key",
            env_var="BC_API_KEY",
            sanitize=True,
            help="Bridgecrew API key or Prisma Cloud Access Key (see --prisma-api-url)",
        )
        self.add(
            "--prisma-api-url",
            env_var="PRISMA_API_URL",
            default=None,
            help="The Prisma Cloud API URL (see: https://prisma.pan.dev/api/cloud/api-urls). "
                 "Requires --bc-api-key to be a Prisma Cloud Access Key in the following format: <access_key_id>::<secret_key>",
        )
        self.add(
            "--skip-results-upload",
            action='store_true',
            help="Do not upload scan results to the platform to view in the console. Results are only available locally. "
                 "If you use the --support flag, logs will still get uploaded.",
        )
        self.add(
            "--docker-image",
            "--image",
            help="Scan docker images by name or ID. Only works with --bc-api-key flag",
        )
        self.add(
            "--dockerfile-path",
            help="Path to the Dockerfile of the scanned docker image",
        )
        self.add(
            "--repo-id",
            help="Identity string of the repository, with form <repo_owner>/<repo_name>. Required when using the platform integration (API key).",
        )
        self.add(
            "-b",
            "--branch",
            help="Selected branch of the persisted repository. Only has effect when using the --bc-api-key flag",
            default="master",
        )
        self.add(
            "--skip-download",
            help="Do not download any data from Prisma Cloud. This will omit doc links, severities, etc., as well as "
                 "custom policies and suppressions if using an API token. Note: it will prevent BC platform IDs from "
                 "being available in Checkov.",
            action="store_true",
        )
        self.add(
            "--use-enforcement-rules",
            action="store_true",
            help="Use the Enforcement rules configured in the platform for hard / soft fail logic. With this option, "
                 "the enforcement rule matching this repo, or the default rule if there is no match, will determine "
                 "this behavior: any check with a severity below the selected rule's soft-fail threshold will be "
                 "skipped; any check with a severity equal to or greater than the rule's hard-fail threshold will "
                 "be part of the hard-fail list, and any check in between will be part of the soft-fail list. For "
                 "example, if the given enforcement rule has a hard-fail value of HIGH and a soft-fail value of MEDIUM,"
                 "this is the equivalent of using the flags `--skip-check LOW --hard-fail-on HIGH`. You can use --check, "
                 "--skip-check, --soft-fail, --soft-fail-on, or --hard-fail-on to override portions of an enforcement rule. "
                 "Note, however, that the logic of applying the --check list and then the --skip-check list (as described "
                 "above under --check) still applies here. Requires a BC or PC platform API key.",
        )
        self.add(
            "--download-external-modules",
            help="download external terraform modules from public git repositories and terraform registry",
            default=False,
            env_var="DOWNLOAD_EXTERNAL_MODULES",
        )
        self.add(
            "--var-file",
            action="append",
            help="Variable files to load in addition to the default files (see "
                 "https://www.terraform.io/docs/language/values/variables.html#variable-definitions-tfvars-files)."
                 "Currently only supported for source Terraform (.tf file), and Helm chart scans."
                 "Requires using --directory, not --file.",
            env_var="CKV_VAR_FILE",
        )
        self.add(
            "--external-modules-download-path",
            help="set the path for the download external terraform modules",
            default=DEFAULT_EXTERNAL_MODULES_DIR,
            env_var="EXTERNAL_MODULES_DIR",
        )
        self.add(
            "--evaluate-variables",
            help="evaluate the values of variables and locals",
            env_var="CKV_EVAL_VARS",
            default=True,
        )
        self.add(
            "-ca", "--ca-certificate", help="Custom CA certificate (bundle) file", default=None, env_var="BC_CA_BUNDLE"
        )
        self.add(
            "--no-cert-verify",
            action="store_true",
            help="Skip SSL certificate verification. Use this to bypass errors related to SSL certificates. Warning: "
                 "this should only be used for testing purposes. Skipping certificate verification is dangerous as "
                 "invalid and falsified certificates cannot be detected."
        )
        self.add(
            "--repo-root-for-plan-enrichment",
            help="Directory containing the hcl code used to generate a given plan file. Use with -f.",
            dest="repo_root_for_plan_enrichment",
            action="append",
        )
        self.add(
            "--config-file",
            help="path to the Checkov configuration YAML file",
            is_config_file=True,
            default=None,
        )
        self.add(
            "--create-config",
            help="takes the current command line args and writes them out to a config file at " "the given path",
            is_write_out_config_file_arg=True,
            default=None,
        )
        self.add(
            "--show-config",
            help="prints all args and config settings and where they came from "
                 "(eg. commandline, config file, environment variable or default)",
            action="store_true",
            default=None,
        )
        self.add(
            "--create-baseline",
            help="Alongside outputting the findings, save all results to .checkov.baseline file"
                 " so future runs will not re-flag the same noise. Works only with `--directory` flag",
            action="store_true",
            default=False,
        )
        self.add(
            "--baseline",
            help="Use a .checkov.baseline file to compare current results with a known baseline. "
                 "Report will include only failed checks that are new with respect to the provided baseline",
            default=None,
        )
        self.add(
            "--output-baseline-as-skipped",
            help="output checks that are skipped due to baseline file presence",
            action="store_true",
            default=False,
        )
        self.add(
            "--skip-cve-package",
            help="filter scan to run on all packages but a specific package identifier (denylist), You can "
                 "specify this argument multiple times to skip multiple packages",
            action="append",
            default=None,
        )
        self.add(
            "--policy-metadata-filter",
            help="comma separated key:value string to filter policies based on Prisma Cloud policy metadata. "
                 "When used with --policy-metadata-filter-exception, the exceptions override any policies selected as"
                 "a result of the --policy-metadata-filter flag."
                 "See https://prisma.pan.dev/api/cloud/cspm/policy#operation/get-policy-filters-and-options for "
                 "information on allowed filters. Format: policy.label=test,cloud.type=aws ",
            default=None,
        )
        self.add(
            "--policy-metadata-filter-exception",
            help="comma separated key:value string to exclude filtered policies based on Prisma Cloud policy metadata. "
                 "When used with --policy-metadata-filter, the exceptions override any policies selected as"
                 "a result of the --policy-metadata-filter flag."
                 "See https://prisma.pan.dev/api/cloud/cspm/policy#operation/get-policy-filters-and-options for "
                 "information on allowed filters. Format: policy.label=test,cloud.type=aws ",
            default=None,
        )
        self.add(
            "--secrets-scan-file-type",
            default=[],
            env_var="CKV_SECRETS_SCAN_FILE_TYPE",
            action="append",
            help="not in use",
        )
        self.add(
            "--enable-secret-scan-all-files",
            default=False,
            env_var="CKV_SECRETS_SCAN_ENABLE_ALL",
            action="store_true",
            help="enable secret scan for all files",
        )
        self.add(
            "--block-list-secret-scan",
            default=[],
            env_var="CKV_SECRETS_SCAN_BLOCK_LIST",
            action="append",
            help="List of files to filter out from the secret scanner",
        )
        self.add(
            "--summary-position",
            default="top",
            choices=SUMMARY_POSITIONS,
            help="Chose whether the summary will be appended on top (before the checks results) or on bottom "
                 "(after check results), default is on top.",
        )
        self.add(
            "--skip-resources-without-violations",
            help="exclude extra resources (resources without violations) from report output",
            action="store_true",
            env_var="CKV_SKIP_RESOURCES_WITHOUT_VIOLATIONS",
        )
        self.add(
            "--deep-analysis",
            default=False,
            action="store_true",
            help="Combine the TF Plan and TF graphs to make connections not available in either",
        )
        self.add(
            "--no-fail-on-crash",
            default=False,
            env_var="CKV_NO_FAIL_ON_CRASH",
            action="store_true",
            help="Return exit code 0 instead of 2",
        )
        self.add(
            "--mask",
            action="append",
            default=[],
            help="List of <resource_type>:<variable> OR <variable> only. Each entry in the list will be used for"
                 "masking the desired attribute for resource (or for all resources, if no resource given)."
                 "Notice: one entry can contain several variables, seperated with a comma. For example:"
                 "<resource_type>:<variable1>,<variable2> OR <variable1>,<variable2>"
        )
        self.add(
            "--scan-secrets-history",
            action="store_true",
            default=False,
            help="will scan the history of commits for secrets"
        )
        self.add(
            "--secrets-history-timeout",
            action="store",
            default='12h',
            help="maximum time to stop the scan "
        )
        self.add(
            "--openai-api-key",
            env_var="CKV_OPENAI_API_KEY",
            sanitize=True,
            help="Add an OpenAI API key to enhance finding guidelines by sending violated policies and "
                 "resource code to OpenAI to request remediation guidance. This will use your OpenAI credits. "
                 "Set your number of findings that will receive enhanced guidelines using CKV_OPENAI_MAX_FINDINGS",
        )
