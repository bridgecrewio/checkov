import json
import logging
from abc import abstractmethod

OUTPUT_CHOICES = ['cli', 'json', 'junitxml', 'github_failed_only']

## Visualization PoC Imports. 
## TODO: Move to own class in bridgecrew>platformintegration.
from os import environ, path
from colorama import init, Fore, Style
from termcolor import colored
from git import Repo
import re
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration

class RunnerRegistry(object):
    runners = []
    scan_reports = []
    banner = ""

    def __init__(self, banner, runner_filter, *runners):
        self.logger = logging.getLogger(__name__)
        self.runner_filter = runner_filter
        self.runners = runners
        self.banner = banner
        self.scan_reports = []
        self.filter_runner_framework()

    @abstractmethod
    def extract_entity_details(self, entity):
        raise NotImplementedError()

    def run(self, root_folder=None, external_checks_dir=None, files=None, guidelines={}):
        for runner in self.runners:
            scan_report = runner.run(root_folder, external_checks_dir=external_checks_dir, files=files,
                                     runner_filter=self.runner_filter)
            RunnerRegistry.enrich_report_with_guidelines(scan_report, guidelines)
            self.scan_reports.append(scan_report)
        return self.scan_reports

    def print_reports(self, scan_reports, args):
        if args.output not in OUTPUT_CHOICES:
            print(f"{self.banner}\n")
        exit_codes = []
        report_jsons = []
        for report in scan_reports:
            if not report.is_empty():
                if args.output == "json":
                    report_jsons.append(report.get_dict())
                elif args.output == "junitxml":
                    report.print_junit_xml()
                elif args.output == 'github_failed_only':
                    report.print_failed_github_md()
                else:
                    report.print_console(is_quiet=args.quiet)
            exit_codes.append(report.get_exit_code(args.soft_fail))
        if args.output == "json":
            if len(report_jsons) == 1:
                print(json.dumps(report_jsons[0], indent=4))
            else:
                print(json.dumps(report_jsons, indent=4))
        ## Visualization PoC Entrypoint with checks (not CI, only interactive CLI, not quiet etc.) 
        ## TODO: Move to own class in bridgecrew>platformintegration.
        if args.output == "cli":
            if args.poc:
                if environ.get('CI') is None:
                    #print("Poc enabled")
                    print(Style.BRIGHT + colored("Visualize and collaborate on these issues with Bridgecrew! \n", 'blue', attrs=['bold']) + colored("Bridgecrew's dashboard for Checkov allows automation of future checks, Pull Request scanning and auto-comments, automatic remidiation PR's and more! Plus it's free for 100 Terraform objects and a great way to visualize and collaborate on these Checkov results. To instantly see this scan in the platform, Press y! \n ", 'yellow') + Style.RESET_ALL)
                    reply = str(input('Visualize results? (y/n): ')).lower().strip()
                    if reply[:1] == 'y':
                        print(Style.BRIGHT + colored("\nEmail Address? \n", 'blue', attrs=['bold']) + colored("Last prompt, promise, well automate the rest, and redirect you to your visualizations! ", 'yellow') + Style.RESET_ALL)
                        reply = str(input('E-Mail:')).lower().strip()
                        #Ignoring the e-mail for now, we have a dummy account
                        # TODO: Integrate with lambda for user creation
                        bc_poc_api_token="be9a013d-7879-56b7-a33d-3a9d24b11c98"
                        if args.file:
                            #Work out git repo name for BC --repo-id from dir at path of --file (files var)
                            #TODO: DIR happy path first
                            print("todo. Files not supported")
                        if args.directory:
                            valid_repos = 0
                            #Work out git repo name for BC --repo-id from root_folder
                            for dir in args.directory:
                                #TODO: The multi-directory (multiple -d's permitted) of Checkov doesn't really tie with the platform logic of needing a --repo-id. 
                                # We could either check that args.directory contains one and otherwise not show this upload/signup PoC
                                # Or, we could support "visualization only" uploads in the platform which arent linked to a specific repo?
                                # NOT AN ISSUE. Multiple -d's has been depreciated in Checkov as it was messing up formatting outputs.
                                try:
                                    repo = Repo(dir)
                                    git_remote_uri = repo.remotes.origin.url
                                    #regex_repo_id = re.compile(r'^(https|git)(:\/\/|@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git$')
                                    git_repo_dict = re.match(r'(https|git)(:\/\/|@)([^\/:]+)[\/:]([^\/:]+)\/(.+).git', git_remote_uri).group(4,5)
                                    repo_id = git_repo_dict[0] + "/" + git_repo_dict[1]
                                    valid_repos +=1
                                except:
                                    pass
                            if valid_repos == 0:
                                #No pushed repo (so no org/repo path)
                                repo_id = "bridgecrewuserrepo/" + path.basename(args.directory[0])
                                print(repo_id)
                        bc_integration = BcPlatformIntegration()
                        bc_integration.setup_bridgecrew_credentials(bc_api_key=bc_poc_api_token, repo_id=repo_id)
                        if bc_integration.is_integration_configured():
                            print(Style.BRIGHT + colored("Sucessfully configured Bridgecrew.cloud...", 'green', attrs=['bold']) + Style.RESET_ALL)
                            bc_integration.persist_repository(args.directory[0])
                            print(Style.BRIGHT + colored("Metadata upload complete", 'green', attrs=['bold']) + Style.RESET_ALL)
                            bc_integration.persist_scan_results(scan_reports)
                            print(Style.BRIGHT + colored("Checkov report upload complete", 'green', attrs=['bold']) + Style.RESET_ALL)
                            bc_integration.commit_repository(args.branch)

    

        exit_code = 1 if 1 in exit_codes else 0
        exit(exit_code)

    def filter_runner_framework(self):
        if not self.runner_filter:
            return
        if self.runner_filter.framework == 'all':
            return
        for runner in self.runners:
            if runner.check_type == self.runner_filter.framework:
                self.runners = [runner]
                return

    @staticmethod
    def enrich_report_with_guidelines(scan_report, guidelines):
        for record in scan_report.failed_checks + scan_report.passed_checks + scan_report.skipped_checks:
            if record.check_id in guidelines:
                record.set_guideline(guidelines[record.check_id])
