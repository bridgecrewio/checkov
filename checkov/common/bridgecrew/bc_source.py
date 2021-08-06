from dataclasses import dataclass


class SourceType:
    def __init__(self, name: str, upload_results: bool):
        self.name = name
        self.upload_results = upload_results


@dataclass
class BCSourceType:
    VSCODE = 'vscode'
    CLI = 'cli'
    KUBERNETES_WORKLOADS = 'kubernetesWorkloads'
    DISABLED = 'disabled'  # use this as a placeholder for generic no-upload logic


SourceTypes = {
    BCSourceType.VSCODE: SourceType(BCSourceType.VSCODE, False),
    BCSourceType.CLI: SourceType(BCSourceType.CLI, True),
    BCSourceType.KUBERNETES_WORKLOADS: SourceType(BCSourceType.KUBERNETES_WORKLOADS, True),
    BCSourceType.DISABLED: SourceType(BCSourceType.VSCODE, False)
}


def get_source_type(source: str):
    # helper method to get the source type with a default - using dict.get is ugly; you have to do:
    # SourceTypes.get(xyz, SourceTypes[BCSourceType.Disabled])
    if source in SourceTypes:
        return SourceTypes[source]
    else:
        return SourceTypes[BCSourceType.DISABLED]
