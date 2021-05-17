import yaml


class CheckovConfig:

    def __init__(self, branch='master', ca_certificate=None, check=None, compact=False, config=None, directory=None,
                 docker_image=None, dockerfile_path=None, download_external_modules=False,
                 evaluate_variables=True, external_checks_dir=None, external_checks_git=None,
                 external_modules_download_path='.external_modules', file=None, framework='all', no_guide=None,
                 output='cli', quiet=None, repo_id=None, skip_check=None, skip_fixes=None,
                 skip_framework=None, skip_suppressions=None, soft_fail=None):
        self.branch = branch
        self.ca_certificate = ca_certificate
        self.check = check
        self.compact = compact
        self.config = config
        self.directory = directory
        self.docker_image = docker_image
        self.dockerfile_path = dockerfile_path
        self.download_external_modules = download_external_modules
        self.evaluate_variables = evaluate_variables
        self.external_checks_dir = external_checks_dir
        self.external_checks_git = external_checks_git
        self.external_modules_download_path = external_modules_download_path
        self.file = file
        self.framework = framework
        self.no_guide = no_guide
        self.output = output
        self.quiet = quiet
        self.repo_id = repo_id
        self.skip_check = skip_check
        self.skip_fixes = skip_fixes
        self.skip_framework = skip_framework
        self.skip_suppressions = skip_suppressions
        self.soft_fail = soft_fail

    @classmethod
    def from_args(cls, args):
        return cls(
            branch=args.branch,
            ca_certificate=args.ca_certificate,
            check=args.check,
            compact=args.compact,
            directory=args.directory,
            docker_image=args.docker_image,
            dockerfile_path=args.dockerfile_path,
            download_external_modules=args.download_external_modules,
            evaluate_variables=args.evaluate_variables,
            external_checks_dir=args.external_checks_dir,
            external_checks_git=args.external_checks_git,
            external_modules_download_path=args.external_modules_download_path,
            file=args.file,
            framework=args.framework,
            no_guide=args.no_guide,
            output=args.output,
            quiet=args.quiet,
            repo_id=args.repo_id,
            skip_check=args.skip_check,
            skip_fixes=args.skip_fixes,
            skip_framework=args.skip_framework,
            skip_suppressions=args.skip_suppressions,
            soft_fail=args.soft_fail
        )

    @classmethod
    def from_yaml(cls, yaml_file_path):
        with open(yaml_file_path, "r") as f:
            yaml_data = yaml.safe_load(f)
        # All the attributes are None by default when reading from config file.
        return cls(**yaml_data)

