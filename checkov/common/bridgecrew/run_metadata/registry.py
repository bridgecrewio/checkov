

class RunMetadataExtractorsRegistry():
    def __init__(self):
        self.extractors = set()

    def register(self, extractor) -> None:
        self.extractors.add(extractor)

    def get_extractor(self):
        for extractor in self.extractors:
            if extractor.is_current_ci():
                return extractor
        for extractor in self.extractors:
            if extractor.__class__.__name__ == 'DefaultRunMetadataExtractor':
                return extractor

registry = RunMetadataExtractorsRegistry()
