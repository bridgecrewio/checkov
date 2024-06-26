# Contributing

The developer guide is for anyone wanting to contribute directly to the Checkov project. 

If you've already developed new checks we'd be happy to take a look at them and merge them as part of the [fast-lane](https://github.com/bridgecrewio/checkov/issues?q=is%3Aopen+is%3Aissue+label%3Afast-lane).  



## Open an issue

Checkov is an open source project maintained by 
[Prisma Cloud by Palo Alto Networks](https://www.prismacloud.io/?utm_source=github&utm_medium=organic_oss&utm_campaign=checkov). 
Our team of maintainers continuously works on developing new features and enhancing existing features. If you encounter 
a bug or have a suggestion, please start by opening an Issue. When reporting, provide a detailed description with examples 
to help us understand the context and specifics. Please note that while we review every issue, non-critical or 
non-blocking issues may be prioritized based on their popularity or frequency. We appreciate your contributions and 
engagement in helping us improve Checkov.

## Developing and contributing code

Dedicated Prisma Cloud maintainers are actively developing new content and adding more features. We would be delighted to 
chat and look at your code. Here are a few guidelines we follow. Hopefully, these will ensure your contribution could 
quickly be added to the project. 

### Work locally

Most Checkov users run their own local instances of Checkov and either run it manually or routinely using Jenkins or 
CircleCI. As Checkov is a non-intrusive library we recommend developing against a local repository and ensuring you are 
able to add your contributions successfully on your local fork/repo. 

If you are developing against remote libraries or repositories - that's great! We'd love to hear how you're doing with it.
In the meantime, before you open a PR, deploy and test your contributions locally.

### Keep your fork in sync

Checkov is usually updated on a weekly basis. Syncing your fork weekly ensures you are working on an updated version that will not break your PR.  

### Rationalize your commits

Try to work on structured and well-defined contributions. If you are building a new feature try to build a unified 
feature block that can be easily reviewed and tested.

If you are fixing or patching changing existing code break changes into logical blocks which individually make sense 
and in aggregate solve a broader issue. 

### Test where it matters

1. Unit: Unit tests, including check tests, are stored in checkov/tests/. 
2. E2E: End-to-end tests will help us establish if the feature is in high readiness. They are not required for simple 
or straight forward features but will help us in evaluating the PR.

#### Tests for new checks

When you add a new check, please write a test for it. While there are many different ways that tests have been written in the past, we have standardized on [this](https://github.com/bridgecrewio/checkov/blob/main/tests/terraform/checks/resource/aws/test_IAMAdminPolicyDocument.py) format. The key points are:

* The test defines templates as strings (in this case, in separate files, but hardcoding a string is also acceptable) and parses them using the runner. The configuration should NOT be hard-coded as an object, as in [this](https://github.com/bridgecrewio/checkov/blob/main/tests/terraform/checks/resource/aws/test_ALBListenerHTTPS.py) example. The reason is that parsers sometimes produce unexpected object structures, so it is quite common that hardcoding the object allows the test to pass but causes the check to be incorrect in practice.
* The test explicitly lists which resources should pass and which should fail. Merely checking the count of passes and failures is not enough. While rare, in the past this has resulted in tests that pass but checks that are incorrect in practice.

#### Running tests

Continuous integration will run these tests either as pre-submits on PRs and post-submits against master branch. 
Results will appear under [actions](https://github.com/bridgecrewio/checkov/actions).

To run tests locally use the following commands (install dev dependencies, run tests and compute tests coverage):
If you are using conda, create a new environment with Python 3.10.14 version:
```sh
conda create -n python310 --m python=Python 3.10.14
conda activate python310
```
Then, we need pipenv installation and run the tests and coverage modules 
```sh
pip install pipenv
pipenv install --dev
pipenv run python -m coverage run -m pytest tests
```

### Build package locally
Change the version number on the file with your version : `<checkov>/checkov/version.py`
To build package locally run the following on `<checkov>` root folder:

```sh
pipenv run python setup.py sdist bdist_wheel
```
- This will create a `*.whl` package under a new folder named `dist`

To install package from local directory, update the release version value and run the installation:
```sh
RELEASE_VERSION='xxx'
pip install dist/checkov-${RELEASE_VERSION}-py3-none-any.whl
```

### Test the package
First verify you have the right version installed:
```sh
checkov --version
```
Then, optionally, you can run on a terraform file/directory with your success and failure test scenarios.

### Setting up the pre-commit hooks

After setting up your Python environment simply run 
```shell
pre-commit install
```

To check the code base against the pre-commit hooks just run
```shell
pre-commit run -a
```

### Using regex

Use re.compile for all regex in order to scan them in flake8.

### Documentation is awesome

Contributing to the documentation is not mandatory but it will ensure people are aware of your important contribution. 
The best way to add documentation is by including suggestions to the [docs](https://github.com/bridgecrewio/checkov/tree/main/docs) 
library as part of your PR. If you'd rather send us a short blurb on slack that's also fine.

## Creating a pull-request

If a trivial fix such as a broken link, typo or grammar mistake, review the entire document for other potential mistakes. 
Try not to open multiple PRs for small fixes in the same document.
Reference any issues related to your PR, or issues that PR may solve.
Comment on your own PR where you believe something may need further explanation.
No need to assign explicit reviewers. We have maintainers reviewing contributions on a daily basis
If your PR is considered a "Work in progress" prefix the name with [WIP] or use the /hold command. This will prevent 
the PR from being merged till the [WIP] or hold is lifted.
If your PR isn't getting enough attention, don't hesitate to ping one of the maintainers on Slack to find additional reviewers.

## Fast-lane for new checks

If you would like to contribute a new check, please label your issue or PR with a `fast-lane` label. This ensures your 
inputs are seen and reviewed quickly and get distributed back to the entire community.
