import argparse
import yaml
from typing import FrozenSet, Optional, Iterable, TextIO, Union, Any
from yaml import YAMLError

OUTPUT_CHOICES = ['cli', 'json', 'junitxml', 'github_failed_only']
FRAMEWORK_CHOICES = ['cloudformation', 'terraform', 'kubernetes', 'serverless', 'arm', 'all']


class CheckovConfigError(Exception):
    pass


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
    def from_args(args: argparse.Namespace) -> 'CheckovConfig':
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

    @staticmethod
    def from_file(file: Union[TextIO, str]) -> 'CheckovConfig':
        if isinstance(file, str):
            with open(file, 'r') as stream:
                return CheckovConfig._from_file(stream)
        else:
            return CheckovConfig._from_file(file)

    @staticmethod
    def _from_file(stream: TextIO) -> 'CheckovConfig':
        kwargs = {}
        try:
            content = yaml.safe_load(stream)
        except YAMLError as e:
            raise CheckovConfigError('Failed to parse YAML') from e
        else:
            if content is not None:
                def get_error(message: str, value: Any) -> CheckovConfigError:
                    if isinstance(value, (bool, int, float)):
                        message += f' You may just want to quote the value like this: "{value}"'
                    return CheckovConfigError(message)

                def handle_set(src: str, dest: str):
                    if src not in content:
                        return
                    values = content[src]
                    if isinstance(values, str):
                        values = [values]
                    elif not isinstance(values, list):
                        raise get_error(f'{src} has to be a list or if you use the short hand version for a single '
                                        f'value, just a str.', values)
                    for value in values:
                        if not isinstance(value, str):
                            raise get_error(f'Elements of {src} have to be str.', value)
                    kwargs[dest] = values
                    del content[src]

                def handle_choice(src: str, dest: str, choices: Iterable[str]):
                    if src not in content:
                        return
                    value = content[src]
                    if not isinstance(value, str):
                        message = f'{src} has to be a str.'
                        raise get_error(message, value)
                    if value not in choices:
                        choices_str = ', '.join(map(lambda c: f'"{c}"', choices))
                        message = f'{src} was "{value}" but has to be one of: {choices_str}'
                        value_caseless = value.casefold()
                        # I didn't know how hard string comparison could be. This is enough for case insensitive but
                        # if you are interested in a deep dive:
                        # https://stackoverflow.com/questions/319426/how-do-i-do-a-case-insensitive-string-comparison
                        possible_choices = [f'"{choice}"' for choice in choices if value_caseless == choice.casefold()]
                        if possible_choices:
                            possible_choices = ', '.join(sorted(possible_choices))
                            if len(possible_choices) == 1:
                                message = f'{message} You may want to use this value instead: {possible_choices}'
                            else:
                                message = f'{message} You may want to use one of this values instead: {possible_choices}'
                        raise CheckovConfigError(message)
                    kwargs[dest] = value
                    del content[src]

                def handle_type(src: str, dest: str, t: type):
                    if src not in content:
                        return
                    value = content[src]
                    if not isinstance(value, t):
                        message = f'{src} has to be a {t.__name__}.'
                        if t == str:
                            raise get_error(message, value)
                        raise CheckovConfigError(message)
                    kwargs[dest] = value
                    del content[src]

                def handle_check(src: str, dest: str):
                    if src not in content:
                        return
                    values = content[src]

                    if isinstance(values, list):
                        for value in values:
                            if not isinstance(value, str):
                                raise get_error(f'Elements of {src} have to be str.', values)
                        values = ','.join(values)
                    elif not isinstance(values, str):
                        raise get_error(f'{src} has to be a string or a list of strings', values)
                    kwargs[dest] = values
                    del content[src]

                handle_set('directories', 'directory')
                handle_set('files', 'file')
                handle_set('external_checks_dirs', 'external_checks_dir')
                handle_set('external_checks_gits', 'external_checks_git')
                handle_choice('output', 'output', OUTPUT_CHOICES)
                handle_type('no_guide', 'no_guide', bool)
                handle_type('quiet', 'quiet', bool)
                handle_choice('framework', 'framework', FRAMEWORK_CHOICES)
                handle_check('checks', 'check')
                handle_check('skip_checks', 'skip_check')
                handle_type('soft_fail', 'soft_fail', bool)
                handle_type('repo_id', 'repo_id', str)
                handle_type('branch', 'branch', str)
                if content:
                    keys = map(lambda v: f'"{v}"', sorted(content))
                    raise CheckovConfigError(f'File contained unexpected keys: {", ".join(keys)}')

        return CheckovConfig('file', **kwargs)

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
