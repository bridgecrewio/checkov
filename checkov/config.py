class CheckovConfig:

    def __init__(self, *, args=None, file=None):
        if (args is None) == (file is None):
            raise ValueError(f'You have to specify either args or file.')

        if args:
            self._init_from_args(args)
        else:
            self._init_from_file(file)

    def _init_from_args(self, args):
        self.type = 'args'
        self.directory = args.directory
        self.file = args.file
        self.external_checks_dir = args.external_checks_dir
        self.external_checks_git = args.external_checks_git
        self._output = args.output
        self._no_guide = args.no_guide
        self._quiet = args.quiet
        self._framework = args.framework
        self.check = args.check
        self.skip_check = args.skip_check
        self._soft_fail = args.soft_fail
        self.repo_id = args.repo_id
        self._branch = args.branch

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
    def output(self):
        return self._output or 'cli'

    @property
    def no_guide(self):
        return self._no_guide if self._no_guide is not None else False

    @property
    def quiet(self):
        return self._quiet if self._quiet is not None else False

    @property
    def framework(self):
        return self._framework or 'all'

    @property
    def soft_fail(self):
        return self._soft_fail if self._soft_fail is not None else False

    @property
    def branch(self):
        return self._branch or 'master'
