from dataclasses import dataclass


class SourceType:
    __slots__ = ("name", "upload_results", "report_contributor_metrics")

    def __init__(self, name: str, upload_results: bool, report_contributor_metrics: bool = False):
        self.name = name
        self.upload_results = upload_results
        self.report_contributor_metrics = report_contributor_metrics


@dataclass
class BCSourceType:
    VSCODE = 'vscode'
    JETBRAINS = 'jetbrains'
    CLI = 'cli'
    KUBERNETES_WORKLOADS = 'kubernetesWorkloads'
    GITHUB_ACTIONS = 'githubActions'
    CODEBUILD = 'codebuild'
    JENKINS = 'jenkins'
    ADMISSION_CONTROLLER = 'admissionController'
    CIRCLECI = 'circleci'
    DISABLED = 'disabled'  # use this as a placeholder for generic no-upload logic


SourceTypes = {
    BCSourceType.VSCODE: SourceType(BCSourceType.VSCODE, False),
    BCSourceType.JETBRAINS: SourceType(BCSourceType.JETBRAINS, False),
    BCSourceType.CLI: SourceType(BCSourceType.CLI, True),
    BCSourceType.KUBERNETES_WORKLOADS: SourceType(BCSourceType.KUBERNETES_WORKLOADS, True),
    BCSourceType.DISABLED: SourceType(BCSourceType.VSCODE, False),
    BCSourceType.GITHUB_ACTIONS: SourceType(BCSourceType.GITHUB_ACTIONS, True, report_contributor_metrics=True),
    BCSourceType.CODEBUILD: SourceType(BCSourceType.CODEBUILD, True, report_contributor_metrics=True),
    BCSourceType.JENKINS: SourceType(BCSourceType.JENKINS, True, report_contributor_metrics=True),
    BCSourceType.CIRCLECI: SourceType(BCSourceType.CIRCLECI, True, report_contributor_metrics=True),
    BCSourceType.ADMISSION_CONTROLLER: SourceType(BCSourceType.ADMISSION_CONTROLLER, False)
}


def get_source_type(source: str) -> SourceType:
    # helper method to get the source type with a default - using dict.get is ugly; you have to do:
    # SourceTypes.get(xyz, SourceTypes[BCSourceType.Disabled])
    if source in SourceTypes:
        return SourceTypes[source]
    else:
        return SourceTypes[BCSourceType.CLI]
