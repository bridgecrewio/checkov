import asyncio
import logging
from typing import Set, Dict, Any, Union
from pydantic import ValidationError
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.sca.reachability.package_alias_mapping.alias_mapping_creator import AliasMappingCreator
from .models import ReachabilityRunConfig, ReachabilityData


class SastReachabilityDataFetcher:
    def __init__(self) -> None:
        self.alias_mapping_creator = AliasMappingCreator()
        self.reachability_run_config_raw: Union[Dict[str, Any], None] = None
        self.reachability_run_config: Union[ReachabilityRunConfig, None] = None

    def fetch(self, repository_name: str, repository_root_dir: str) -> Union[ReachabilityData, None]:
        self.reachability_run_config_raw = bc_integration.get_reachability_run_config()

        if not self.reachability_run_config_raw:
            logging.error('reachability_run_config is null, unable to proceed', exc_info=True)
            return None

        try:
            self.reachability_run_config = ReachabilityRunConfig(
                packageNamesForMapping=self.reachability_run_config_raw.get('packageNamesForMapping', []))
        except ValidationError:
            logging.error('Unable to serialize reachability run_config', exc_info=True)
            return None

        try:
            result = ReachabilityData(
                aliasMapping=self._fetch_alias_mapping(repository_name=repository_name,
                                                       repository_root_dir=repository_root_dir,
                                                       relevant_packages=self.reachability_run_config.packageNamesForMapping)
            )
        except ValidationError:
            logging.error('Unable to serialize reachability data', exc_info=True)
            return None

        return result

    def _fetch_alias_mapping(self, repository_name: str, repository_root_dir: str, relevant_packages: Set[str]) -> Dict[str, Any]:
        self.alias_mapping_creator.update_alias_mapping_for_repository(
            repository_name=repository_name,
            repository_root_dir=repository_root_dir,
            relevant_packages=relevant_packages
        )
        res: Dict[str, Any] = self.alias_mapping_creator.get_alias_mapping()
        asyncio.run(bc_integration.persist_reachability_alias_mapping(res))
        return res
