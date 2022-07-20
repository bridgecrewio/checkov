from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from checkov.common.bridgecrew.run_metadata.abstract_run_metadata_extractor import RunMetaDataExtractor


class RunMetadataExtractorsRegistry:
    def __init__(self) -> None:
        self.extractors: set[RunMetaDataExtractor] = set()

    def register(self, extractor: RunMetaDataExtractor) -> None:
        self.extractors.add(extractor)

    def get_extractor(self) -> RunMetaDataExtractor:
        for extractor in self.extractors:
            if extractor.is_current_ci():
                return extractor
        for extractor in self.extractors:
            if extractor.__class__.__name__ == "DefaultRunMetadataExtractor":
                return extractor

        # should never be reached
        from checkov.common.bridgecrew.run_metadata.extractors.default_extractor import DefaultRunMetadataExtractor
        return DefaultRunMetadataExtractor()


registry = RunMetadataExtractorsRegistry()
