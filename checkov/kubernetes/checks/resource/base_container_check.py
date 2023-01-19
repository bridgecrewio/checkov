import logging
from abc import abstractmethod
from collections.abc import Iterable
from typing import Dict, Any, List, Optional

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.kubernetes.checks.resource.base_spec_check import BaseK8Check
from checkov.kubernetes.checks.resource.registry import registry


class BaseK8sContainerCheck(BaseK8Check):
    TEMPLATE_ENTITIES = (
        "Deployment",
        "DeploymentConfig",
        "DaemonSet",
        "Job",
        "ReplicaSet",
        "ReplicationController",
        "StatefulSet",
    )
    SUPPORTED_ENTITIES = (
        "CronJob",
        "Pod",
        "PodTemplate",
    ) + TEMPLATE_ENTITIES

    def __init__(
        self,
        name: str,
        id: str,
        categories: Optional[List[CheckCategories]] = None,
        supported_entities: Optional["Iterable[str]"] = None,
        supported_container_types: Optional["Iterable[str]"] = None,
        guideline: Optional[str] = None,
    ) -> None:
        categories = categories or [CheckCategories.KUBERNETES]
        supported_entities = supported_entities or BaseK8sContainerCheck.SUPPORTED_ENTITIES

        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            guideline=guideline,
        )
        self.supported_container_types = supported_container_types or ("containers", "initContainers")
        self.evaluated_container_keys: List[str] = []

        registry.register(self)

    def get_resource_id(self, conf: Dict[str, Any]) -> str:  # TODO: remove when implementing graph
        return f"{conf['kind']}.{conf['metadata'].get('namespace', 'default')}.{conf['metadata']['name']}"

    def scan_spec_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if self.entity_type == "Pod":
            evaluated_key_prefix = "spec"
            try:
                spec = conf["spec"]
                metadata = conf.get("metadata", {})
            except KeyError:
                logging.info(f"failed to extract {evaluated_key_prefix} for {self.entity_path}")
                return CheckResult.UNKNOWN
        elif self.entity_type in "PodTemplate":
            evaluated_key_prefix = "template/spec"
            try:
                spec = conf["template"]["spec"]
                metadata = conf["template"].get("metadata", {})
            except KeyError:
                logging.info(f"failed to extract {evaluated_key_prefix} for {self.entity_path}")
                return CheckResult.UNKNOWN
        elif self.entity_type in BaseK8sContainerCheck.TEMPLATE_ENTITIES:
            evaluated_key_prefix = "spec/template/spec"
            try:
                spec = conf["spec"]["template"]["spec"]
                metadata = conf["spec"]["template"].get("metadata", {})
            except (KeyError, TypeError):
                return CheckResult.UNKNOWN
        elif self.entity_type == "CronJob":
            evaluated_key_prefix = "spec/jobTemplate/spec/template/spec"
            try:
                spec = conf["spec"]["jobTemplate"]["spec"]["template"]["spec"]
                metadata = conf["spec"]["jobTemplate"]["spec"]["template"].get("metadata", {})
            except (KeyError, TypeError):
                return CheckResult.UNKNOWN
        else:
            logging.info(f"entity type {self.entity_type} not supported")
            return CheckResult.UNKNOWN

        containers: List[Dict[str, Any]] = (
            spec.get("containers", []) if "containers" in self.supported_container_types and isinstance(spec, dict) else []
        ) or []
        init_containers: List[Dict[str, Any]] = (
            spec.get("initContainers", []) if "initContainers" in self.supported_container_types and isinstance(spec, dict) else []
        ) or []

        results = set()
        result = self._check_containers(
            evaluated_key_prefix=evaluated_key_prefix,
            container_type="containers",
            metadata=metadata,
            containers=containers,
        )
        results.add(result)
        if result == CheckResult.FAILED:
            return CheckResult.FAILED

        result = self._check_containers(
            evaluated_key_prefix=evaluated_key_prefix,
            container_type="initContainers",
            metadata=metadata,
            containers=init_containers,
        )
        results.add(result)
        if result == CheckResult.FAILED:
            return CheckResult.FAILED

        return CheckResult.PASSED if CheckResult.PASSED in results else CheckResult.UNKNOWN

    def _check_containers(
        self, evaluated_key_prefix: str, container_type: str, metadata: Dict[str, Any], containers: List[Dict[str, Any]]
    ) -> CheckResult:
        """Check containers for possible violations."""
        if not isinstance(containers, list):
            return CheckResult.UNKNOWN
        results = set()
        for idx, container in enumerate(containers):
            result = self.scan_container_conf(metadata, container)
            results.add(result)

            # fail with the first occurrence
            if result == CheckResult.FAILED:
                if self.evaluated_container_keys:
                    self.evaluated_keys = [
                        f"{evaluated_key_prefix}/{container_type}/[{idx}]/{key}"
                        for key in self.evaluated_container_keys
                    ]
                else:
                    self.evaluated_keys = [f"{evaluated_key_prefix}/initContainers/[{idx}]"]
                return CheckResult.FAILED

        return CheckResult.PASSED if CheckResult.PASSED in results else CheckResult.UNKNOWN

    @abstractmethod
    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        """Return result of container check."""
        pass
