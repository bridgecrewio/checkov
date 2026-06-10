from __future__ import annotations

import fnmatch
import importlib
import importlib.util
import logging
import os
import sys
from abc import abstractmethod
from collections import defaultdict
from itertools import chain
from typing import Generator, Tuple, Dict, List, Optional, Any, TYPE_CHECKING

from checkov.common.external_checks.verification.errors import SignatureVerificationError
from checkov.common.external_checks.verification.sources_registry import (
    get_all_verified_sources,
    get_verified_sources_for_directory,
)
from checkov.common.external_checks.verification.verified_loader import (
    install_finder,
    load_verified_sources_into_module,
    uninstall_finder,
)
from checkov.common.models.enums import CheckResult
from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.typing import _SkippedCheck, _CheckResult
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck


class BaseCheckRegistry:
    # NOTE: Needs to be static to because external check loading may be triggered by a registry to which
    #       checks aren't registered. (This happens with Serverless, for example.)
    __loading_external_checks = False  # noqa: CCE003
    __all_registered_checks: list[BaseCheck] = []  # noqa: CCE003

    def __init__(self, report_type: str) -> None:
        self.logger = logging.getLogger(__name__)
        add_resource_code_filter_to_logger(self.logger)
        # IMPLEMENTATION NOTE: Checks is used to directly access checks based on an specific entity
        self.checks: Dict[str, List[BaseCheck]] = defaultdict(list)
        # IMPLEMENTATION NOTE: When using a wildcard, every pattern needs to be checked. To reduce the
        #                      number of checks checks with the same pattern are grouped, which is the
        #                      reason to use a dict for this too.
        self.wildcard_checks: Dict[str, List[BaseCheck]] = defaultdict(list)
        self.check_id_allowlist: Optional[List[str]] = None
        self.report_type = report_type
        self.definitions_raw: list[tuple[int, str]] | None = None
        self.graph = None

    def register(self, check: BaseCheck) -> None:
        # IMPLEMENTATION NOTE: Checks are registered when the script is loaded
        #                      (see BaseResourceCheck.__init__() for the various frameworks). The only
        #                      difficultly with this process is that external checks need to be specially
        #                      identified for filter handling. That's why you'll see stateful setting of
        #                      RunnerFilters during load_external_checks.
        #                      Built-in checks are registered immediately at script start, before
        #                      external checks.
        if BaseCheckRegistry.__loading_external_checks:
            RunnerFilter.notify_external_check(check.id)

        for entity in check.supported_entities:
            checks = self.wildcard_checks if self._is_wildcard(entity) else self.checks
            if not any(c.id == check.id for c in checks[entity]):
                checks[entity].append(check)

        BaseCheckRegistry.__all_registered_checks.append(check)

    @staticmethod
    def get_all_registered_checks() -> List[BaseCheck]:
        return BaseCheckRegistry.__all_registered_checks

    @staticmethod
    def _is_wildcard(entity: str) -> bool:
        return "*" in entity or "?" in entity or ("[" in entity and "]" in entity)

    def get_check_by_id(self, check_id: str) -> Optional[BaseCheck]:
        return next(
            (check for check in chain(*self.checks.values(), *self.wildcard_checks.values()) if check.id == check_id),
            None,
        )

    def all_checks(self) -> Generator[Tuple[str, BaseCheck], None, None]:
        for entity, checks in self.checks.items():
            for check in checks:
                yield entity, check
        for entity, checks in self.wildcard_checks.items():
            for check in checks:
                yield entity, check

    @property
    def contains_wildcard(self) -> bool:
        return bool(self.wildcard_checks)

    def get_checks(self, entity: str) -> List[BaseCheck]:
        if not self.wildcard_checks:
            # Optimisation: When no wildcards are used, we can use the list in self.checks
            return self.checks.get(entity) or []
        else:
            res = self.checks[entity].copy() if entity in self.checks.keys() else []
            # check wildcards
            for pattern, checks in self.wildcard_checks.items():
                if entity and fnmatch.fnmatchcase(entity, pattern):
                    res += checks
            return res

    def set_checks_allowlist(self, runner_filter: RunnerFilter) -> None:
        if runner_filter.checks:
            self.check_id_allowlist = runner_filter.checks

    @abstractmethod
    def extract_entity_details(self, entity: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        raise NotImplementedError()

    def scan(
        self,
        scanned_file: str,
        entity: Dict[str, Any],
        skipped_checks: List[_SkippedCheck],
        runner_filter: RunnerFilter,
        report_type: Optional[str] = None  # allow runners like TF plan to override the type while using the same registry
    ) -> Dict[BaseCheck, _CheckResult]:
        results: Dict[BaseCheck, _CheckResult] = {}

        try:
            (entity_type, entity_name, entity_configuration) = self.extract_entity_details(entity)
        except Exception:
            logging.debug(f"Error in entity details extraction for file {scanned_file}", exc_info=True)
            return results

        if not isinstance(entity_configuration, dict):
            return results

        checks = self.get_checks(entity_type)
        for check in checks:
            skip_info: _SkippedCheck = {}
            if skipped_checks:
                if check.id in [x["id"] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x["id"] == check.id][0]

            if runner_filter.should_run_check(
                    check,
                    report_type=report_type or self.report_type,
                    file_origin_paths=[scanned_file]
            ):
                result = self.run_check(check, entity_configuration, entity_name, entity_type, scanned_file, skip_info)
                results[check] = result
        return results

    def run_check(
        self,
        check: BaseCheck,
        entity_configuration: Dict[str, List[Any]],
        entity_name: str,
        entity_type: str,
        scanned_file: str,
        skip_info: _SkippedCheck,
    ) -> _CheckResult:
        self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))
        check.graph = self.graph
        try:
            result = check.run(
                scanned_file=scanned_file,
                entity_configuration=entity_configuration,
                entity_name=entity_name,
                entity_type=entity_type,
                skip_info=skip_info,
            )
            return result
        except Exception:
            return _CheckResult(
                result=CheckResult.UNKNOWN, suppress_comment="", evaluated_keys=[],
                results_configuration=entity_configuration, check=check, entity=entity_configuration
            )

    @staticmethod
    def _directory_has_init_py(directory: str) -> bool:
        """ Check if a given directory contains a file named __init__.py.

        __init__.py is needed to ensure the directory is a Python module, thus
        can be imported.
        """
        return os.path.exists(os.path.join(directory, "__init__.py"))

    @staticmethod
    def _file_can_be_imported(entry: "os.DirEntry[str]") -> bool:
        """ Verify if a directory entry is a non-magic Python file."""
        return entry.is_file() and not entry.name.startswith("__") and entry.name.endswith(".py")

    def _resolve_verified_source(
        self,
        verified_sources: Dict[str, bytes],
        check_full_path: str,
    ) -> "bytes | None":
        """Look up ``check_full_path`` in the allowlist using ONLY the realpath-normalised key.

        The registry promises (per ``sources_registry.verify_and_register``)
        that every key is the realpath-normalised path of a verified file.
        """
        canonical_path = os.path.normpath(os.path.realpath(check_full_path))
        return verified_sources.get(canonical_path)

    def load_external_checks(
        self,
        directory: str,
        verified_sources: Optional[Dict[str, bytes]] = None,
    ) -> None:
        """Import ``.py`` files from ``directory`` as external checks.

        Verified opt-in load when ``verified_sources`` or the registry has
        an allowlist; backward-compatible unverified disk-load otherwise
        (the default when ``--external-checks-public-key`` is not set).
        Not thread-safe.
        """
        directory = os.path.expanduser(directory)
        self.logger.debug(f"Loading external checks from {directory}")

        if verified_sources is None:
            verified_sources = get_verified_sources_for_directory(directory)
            if verified_sources is None:
                self._load_external_checks_from_disk(directory)
                return

        # Finder must see the FULL registry, not just this dir's subset,
        # so cross-directory transitive imports are served from verified bytes.
        finder_sources = get_all_verified_sources() or verified_sources
        finder_dirs = sorted({os.path.dirname(p) for p in finder_sources})
        finder = install_finder(finder_sources, finder_dirs)
        previous_dont_write_bytecode = sys.dont_write_bytecode

        previous_sys_path = list(sys.path)
        sys.dont_write_bytecode = True
        try:
            self._load_external_checks_from_verified_sources(directory, verified_sources)
        finally:
            uninstall_finder(finder)
            sys.dont_write_bytecode = previous_dont_write_bytecode
            sys.path[:] = previous_sys_path

    def _walk_external_check_files(
        self, directory: str,
    ) -> "Generator[tuple[str, str], None, None]":
        """Yield ``(check_name, check_full_path)`` for every importable ``.py``.

        Shared walker used by both the unverified and verified load paths.
        Skips directories without ``__init__.py`` (with an INFO log) and
        applies the same ``_file_can_be_imported`` filter the loaders
        depend on (no dotfiles, no ``__init__.py``, only ``.py``). Side-
        effect: prepends each walked dir to ``sys.path`` exactly as the
        old per-loader walks did, so transitive imports inside loaded
        checks resolve identically to pre-refactor behaviour.
        """
        for root, _, _ in os.walk(directory):
            sys.path.insert(1, root)
            with os.scandir(root) as directory_content:
                if not self._directory_has_init_py(root):
                    self.logger.info(f"No __init__.py found in {root}. Cannot load any check here.")
                    continue
                for entry in directory_content:
                    if not self._file_can_be_imported(entry):
                        continue
                    check_name = entry.name.replace(".py", "")
                    yield check_name, entry.path

    def _exec_check_from_disk(self, check_name: str, check_full_path: str) -> None:
        """Compile + exec the on-disk ``.py`` file as a fresh module.

        Unverified path's per-file action. Mirrors the pre-MR behaviour
        byte-for-byte: no signature checks, errors are logged and the
        walk continues so a single broken check doesn't abort the scan.
        """
        spec = importlib.util.spec_from_file_location(check_name, check_full_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
            sys.modules[check_name] = module
            spec.loader.exec_module(module)  # type: ignore[union-attr]
        else:
            self.logger.error(f"Cannot load external check '{check_name}' from {check_full_path}")

    def _load_external_checks_from_disk(self, directory: str) -> None:
        """Unverified disk-exec path.

        Active when ``--external-checks-public-key`` is NOT set. Loads every
        ``.py`` file under ``directory`` exactly as before the verification
        feature was introduced — no signature checks. This is the
        backward-compatible default for operators who haven't opted in to
        trailer-based signing.

        See ``_load_external_checks_from_verified_sources`` for the
        opt-in verified equivalent.
        """
        for check_name, check_full_path in self._walk_external_check_files(directory):
            try:
                BaseCheckRegistry.__loading_external_checks = True
                self.logger.debug(f"Importing external check '{check_name}'")
                self._exec_check_from_disk(check_name, check_full_path)
            except Exception:
                self.logger.error(
                    f"Cannot load external check '{check_name}' from {check_full_path}",
                    exc_info=True,
                )
            finally:
                BaseCheckRegistry.__loading_external_checks = False

    def _load_external_checks_from_verified_sources(
        self,
        directory: str,
        verified_sources: Dict[str, bytes],
    ) -> None:
        """Verified opt-in path: exec ONLY the in-memory bytes for allowlist files.

        Active when ``--external-checks-public-key`` is set AND the chokepoint
        successfully registered the directory via ``verify_and_register``.
        Any ``.py`` file present on disk but absent from ``verified_sources``
        is refused and surfaces as a ``SignatureVerificationError`` after the
        walk (M1/S3 TOCTOU escalation).

        See ``_load_external_checks_from_disk`` for the unverified default
        used when no public key is configured.
        """
        refused_paths: "list[str]" = []
        for check_name, check_full_path in self._walk_external_check_files(directory):
            try:
                BaseCheckRegistry.__loading_external_checks = True
                self.logger.debug(f"Importing external check '{check_name}'")
                source_bytes = self._resolve_verified_source(
                    verified_sources, check_full_path,
                )
                if source_bytes is None:
                    self.logger.error(
                        f"Refusing to load unverified external check "
                        f"'{check_name}' from {check_full_path}"
                    )
                    refused_paths.append(check_full_path)
                    continue
                load_verified_sources_into_module(
                    check_name, check_full_path, source_bytes,
                )
            except Exception:
                self.logger.error(
                    f"Cannot load external check '{check_name}' from {check_full_path}",
                    exc_info=True,
                )
            finally:
                BaseCheckRegistry.__loading_external_checks = False
        if refused_paths:
            bullets = "\n".join(f"  - {p}" for p in refused_paths)
            raise SignatureVerificationError(
                "unverified external check files refused at load time "
                "(disk state diverged from the verified allowlist):\n"
                f"{bullets}"
            )
