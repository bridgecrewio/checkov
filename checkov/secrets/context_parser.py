from __future__ import annotations

import os
import logging
from typing import List, Tuple, Dict, Any
from checkov.common.typing import _SkippedCheck
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration


class ContextParser:
    """
    Context parser for secrets scanning — supports:
    - Metadata suppressions like:
      {
        "Metadata": {
          "checkov": {
            "skip": [
              {"id": "CKV_SECRET_6", "comment": "example reason"}
            ]
          }
        }
      }
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.file_lines: List[Tuple[int, str]] = self._read_file_lines()

    def _read_file_lines(self) -> List[Tuple[int, str]]:
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r", encoding="utf-8") as f:
            return [(i + 1, line.rstrip('\n')) for i, line in enumerate(f.readlines())]

    def collect_skip_comments(
            self,
            resource_config: Dict[str, Any] | List[Dict[str, Any]] | None = None
    ) -> List[_SkippedCheck]:
        """
        Collects suppressions from resource metadata.

        Supports:
        - Metadata under 'checkov' and 'bridgecrew' keys
        - Object-rooted and array-rooted JSON/YAML structures

        Returns a list of suppression dicts
        """
        skipped_checks: List[_SkippedCheck] = []
        bc_id_mapping = metadata_integration.bc_to_ckv_id_mapping

        def extract_skips(metadata_block: Dict[str, Any]) -> None:
            for source in ("checkov", "bridgecrew"):
                for skip in metadata_block.get(source, {}).get("skip", []):
                    skip_id = skip.get("id")
                    skip_comment = skip.get("comment", "No comment provided")
                    if not skip_id:
                        logging.warning("Check suppression is missing key 'id'")
                        continue

                    skipped_check: _SkippedCheck = {
                        "id": skip_id,
                        "suppress_comment": skip_comment,
                    }

                    if bc_id_mapping and skip_id in bc_id_mapping:
                        skipped_check["bc_id"] = skip_id
                        skipped_check["id"] = bc_id_mapping[skip_id]
                    elif metadata_integration.check_metadata:
                        skipped_check["bc_id"] = metadata_integration.get_bc_id(skip_id)

                    skipped_checks.append(skipped_check)

        if isinstance(resource_config, dict):
            metadata = resource_config.get("Metadata", {})
            extract_skips(metadata)

        elif isinstance(resource_config, list):
            for item in resource_config:
                if isinstance(item, dict):
                    metadata = item.get("Metadata", {})
                    extract_skips(metadata)

        return skipped_checks
