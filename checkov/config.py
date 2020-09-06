import argparse

from typing import FrozenSet, Optional, Iterable


class CheckovConfig:

    def __init__(self, source: str, *, directory: Optional[Iterable[str]] = None, file: Optional[Iterable[str]] = None,
                 external_checks_dir: Optional[Iterable[str]] = None,
                 external_checks_git: Optional[Iterable[str]] = None, output: Optional[str] = None,
                 no_guide: Optional[bool] = None, quiet: Optional[bool] = None, framework: Optional[str] = None,
                 check: Optional[str] = None, skip_check: Optional[str] = None, soft_fail: Optional[bool] = None,
                 repo_id: Optional[str] = None, branch: Optional[str] = None):
        self.source = source
        self.directory: FrozenSet = frozenset(directory or {})
        self.file: FrozenSet = frozenset(file or {})
        self.external_checks_dir: FrozenSet = frozenset(external_checks_dir or {})
        self.external_checks_git: FrozenSet = frozenset(external_checks_git or {})
        self._output = output
        self._no_guide = no_guide
        self._quiet = quiet
        self._framework = framework
        self.check = check
        self.skip_check = skip_check
        self._soft_fail = soft_fail
        self.repo_id = repo_id
        self._branch = branch

    @staticmethod
    def from_args(args: argparse.Namespace):
        # TODO there should be a way to clear this from a parent
        # Currently if a parent set this, there is no way for the cli to override that in a way, that every check
        # runs
        return CheckovConfig(
            source='args',
            directory=args.directory,
            file=args.file,
            external_checks_dir=args.external_checks_dir,
            external_checks_git=args.external_checks_git,
            output=args.output,
            no_guide=args.no_guide,
            quiet=args.quiet,
            framework=args.framework,
            check=args.check,
            skip_check=args.skip_check,
            soft_fail=args.soft_fail,
            repo_id=args.repo_id,
            branch=args.branch,
        )

    def _init_from_file(self, file):
        self.source = 'file'
        # self.directory = args.directory
        # self.file = args.file
        # self.external_checks_dir = args.external_checks_dir
        # self.external_checks_git = args.external_checks_git
        # self._output = args.output
        # self._no_guide = args.no_guide
        # self._quiet = args.quiet
        # self.framework = args.framework
        # self.check = args.check
        # self.skip_check = args.skip_check
        # self._soft_fail = args.soft_fail
        # self.repo_id = args.repo_id
        # self._branch = args.branch
        pass

    @property
    def output(self) -> str:
        return self._output or 'cli'

    @property
    def no_guide(self) -> bool:
        return self._no_guide if self._no_guide is not None else False

    @property
    def quiet(self) -> bool:
        return self._quiet if self._quiet is not None else False

    @property
    def framework(self) -> str:
        return self._framework or 'all'

    @property
    def soft_fail(self) -> bool:
        return self._soft_fail if self._soft_fail is not None else False

    @property
    def branch(self):
        return self._branch or 'master'

    def extend(self, parent: 'CheckovConfig'):
        self.directory = self.directory.union(parent.directory)
        self.file = self.file.union(parent.file)
        self.external_checks_dir = self.external_checks_dir.union(parent.external_checks_dir)
        self.external_checks_git = self.external_checks_git.union(parent.external_checks_git)
        # _output is never ''
        self._output = self._output or parent._output
        if self._no_guide is None:
            self._no_guide = parent._no_guide
        if self._quiet is None:
            self._quiet = parent._quiet
        # _framework is never ''
        self._framework = self._framework or parent._framework
        if self._soft_fail is None:
            self._soft_fail = parent._soft_fail
        # repo_id is never ''
        self.repo_id = self.repo_id or parent.repo_id
        # repo_id is never ''
        self._branch = self._branch or parent._branch

        if not self.check and not self.skip_check:
            # if nothing is set, copy from parent
            self.check = parent.check
            self.skip_check = parent.skip_check
        else:
            # At least one is set. Update the once, that are set. If it are both, it was invalid and will be invalid.
            if self.check and parent.check:
                # parent.check is a string but not an empty one
                self.check = f'{self.check},{parent.check}'
            if self.skip_check and parent.skip_check:
                # parent.skip_check is a string but not an empty one
                self.skip_check = f'{self.skip_check},{parent.skip_check}'
