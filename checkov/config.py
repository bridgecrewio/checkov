from typing import FrozenSet, Optional


class CheckovConfig:

    def __init__(self, *, args=None, file=None):
        if (args is None) == (file is None):
            raise ValueError(f'You have to specify either args or file.')

        if args:
            self.type = 'args'
            self.directory: FrozenSet = frozenset(args.directory or {})
            self.file: FrozenSet = frozenset(args.file or {})
            self.external_checks_dir: FrozenSet = frozenset(args.external_checks_dir or {})
            self.external_checks_git: FrozenSet = frozenset(args.external_checks_git or {})
            self._output: Optional[str] = args.output
            self._no_guide: Optional[bool] = args.no_guide
            self._quiet: Optional[bool] = args.quiet
            self._framework: Optional[str] = args.framework
            # TODO there should be a way to clear this from a parent
            # Currently if a parent set this, there is no way for the cli to override that in a way, that every check
            # runs
            self.check: Optional[str] = args.check
            self.skip_check: Optional[str] = args.skip_check
            self._soft_fail: Optional[bool] = args.soft_fail
            self.repo_id: Optional[str] = args.repo_id
            self._branch: Optional[str] = args.branch
        else:
            self._init_from_file(file)

    def _init_from_file(self, file):
        self.type = 'file'
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
