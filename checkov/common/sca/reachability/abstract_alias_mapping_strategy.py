from abc import ABC, abstractmethod
from typing import List, Dict, Set, Any, Callable
import logging
import os

from checkov.common.sca.reachability.typing import FileParserOutput
from checkov.common.sca.reachability.commons import add_package_aliases


class AbstractAliasMappingStrategy(ABC):
    @abstractmethod
    def get_language(self) -> str:
        pass

    @abstractmethod
    def get_file_name_to_parser_map(self) -> Dict[str, Callable[[str, Set[str]], FileParserOutput]]:
        pass

    def update_alias_mapping(self, alias_mapping: Dict[str, Any], repository_name: str, root_dir: str, relevant_packages: Set[str]) -> Dict[
        str, List[str]]:
        logging.debug("[AbstractAliasMappingStrategy](create_alias_mapping) - starting")
        file_name_to_parser_map = self.get_file_name_to_parser_map()
        for curr_root, _, f_names in os.walk(root_dir):
            for file_name in f_names:
                if file_name in file_name_to_parser_map:
                    logging.debug(f"[AbstractAliasMappingStrategy](create_alias_mapping) - starting parsing ${file_name}")
                    file_absolute_path = os.path.join(curr_root, file_name)
                    file_relative_path = os.path.relpath(file_absolute_path, root_dir)
                    with open(file_absolute_path) as f:
                        file_content = f.read()
                        try:
                            output = file_name_to_parser_map[file_name](file_content, relevant_packages)
                            for package_name in output:
                                add_package_aliases(alias_mapping, self.get_language(), repository_name, file_relative_path,
                                                    package_name, output[package_name]["packageAliases"])
                            logging.debug(
                                f"[AbstractAliasMappingStrategy](create_alias_mapping) - done parsing for ${file_name}")
                        except Exception:
                            logging.error(f"[AbstractAliasMappingStrategy](create_alias_mapping) - failure when "
                                          f"parsing the file '${file_name}'. file content:\n{file_content}.\n",
                                          exc_info=True)
        return alias_mapping
