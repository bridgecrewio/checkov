import itertools
import os
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from checkov.runner_filter import RunnerFilter

IGNORED_DIRECTORIES_ENV = os.getenv('CKV_IGNORED_DIRECTORIES', "node_modules,.terraform,.serverless")

ignored_directories = IGNORED_DIRECTORIES_ENV.split(",")


class BaseRunner(ABC):
    check_type = ""
    definitions = None
    context = None
    breadcrumbs = None
    external_registries = None
    graph_manager = None
    graph_registry = None

    @abstractmethod
    def run(self, root_folder, external_checks_dir=None, files=None, runner_filter=RunnerFilter(), collect_skip_comments=True):
        pass

    def set_external_data(self, definitions: Optional[Dict], context: Optional[Dict], breadcrumbs: Optional[Dict]):
        self.definitions = definitions
        self.context = context
        self.breadcrumbs = breadcrumbs

    def load_external_checks(self, external_checks_dir: List[str]):
        pass

    def get_graph_checks_report(self, root_folder, runner_filter: RunnerFilter):
        pass

    def run_graph_checks_results(self, runner_filter):
        checks_results = {}
        for r in itertools.chain(self.external_registries, [self.graph_registry]):
            r.load_checks()
            registry_results = r.run_checks(self.graph_manager.get_reader_endpoint(), runner_filter)
            checks_results = {**checks_results, **registry_results}
        return checks_results


def filter_ignored_paths(root_dir, names, excluded_paths: List[str]):
    # we need to handle legacy logic, where directories to skip could be specified using the env var (default value above)
    # or a directory starting with '.'; these look only at directory basenames, not relative paths.
    #
    # But then any other excluded paths (specified via --skip-path or via the platform repo settings) should look at
    # the path name relative to the root folder. These can be files or directories.
    # Example: take the following dir tree:
    # .
    #   ./dir1
    #      ./dir1/dir33
    #      ./dir1/.terraform
    #   ./dir2
    #      ./dir2/dir33
    #      /.dir2/hello.yaml
    #
    # if excluded_paths = ['dir1/dir33', 'dir2/hello.yaml'], then we would scan dir1, but we would skip its subdirectories. We would scan
    # dir2 and its subdirectory, but we'd skip hello.yaml.

    # first handle the legacy logic - this will also remove files starting with '.' but that's probably fine
    # mostly this will just remove those problematic directories hardcoded above.
    [names.remove(path) for path in list(names) if path in ignored_directories or path.startswith(".")]

    # now apply the new logic
    # TODO this is not going to work well on Windows, because paths specified in the platform will use /, and
    #  paths specified via the CLI argument will presumably use \\
    if excluded_paths:
        compiled = [re.compile(p.replace('.terraform', '\.terraform')) for p in excluded_paths]
        [names.remove(path) for path in list(names) if any(pattern.search(os.path.join(root_dir, path)) for pattern in compiled)]
