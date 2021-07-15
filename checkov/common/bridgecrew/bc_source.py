from typing import Optional

# Helper methods for determining behavior based on different BC_SOURCE values. Python enums are limiting here, and
# using a class is overkill


def should_upload_results(source: Optional[str]) -> bool:
    """Whether scan results should be uploaded to the platform. Default for unknown sources is False."""
    if source == 'vscode':
        return False
    elif source == 'cli':
        return True
    else:
        return False
