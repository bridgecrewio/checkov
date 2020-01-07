# Contributing

The developer guide is for anyone wanting to contribute directly to the Checkov project. 

If you've already developed new checks we'd be happy to take a look at them and merge them as part of the [fast-lane](Fast-lane for new checks).  



## Open an issue

Checkov is an open source project maintained by [Bridgecrew](https://bridgecrew.io). We have dedicated maintainers developing 
new content and adding more features. If you have a bug or an idea, start by opening an issue. Try to make it as 
descriptive as possible. 

## Developing and contributing code

Dedicated Bridgecrew maintainers are actively developing new content and adding more features. We would be delighted to 
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

1. Unit: Unit tests are stored in checkov/tests/. 
2. E2E: End-to-end tests will help us establish if the feature is in high readiness. They are not required for simple 
or straight forward features but will help us in evaluating the PR.

Continuous integration will run these tests either as pre-submits on PRs and post-submits against master branch. 
Results will appear under [actions](https://github.com/bridgecrewio/checkov/actions).

To run tests locally use the following commands (install dev dependencies, run tests and compute tests coverage):
```sh
pipenv install --dev
pipenv run python -m coverage run -m pytest
```

### Build package locally
To build package locally run the following on Checkov root folder:
```sh
pipenv run python setup.py sdist bdist_wheel
```
- This will create a `*.whl` package under a new folder named `dist`

To install package from local directory run:
```sh
pip install dist/checkov-${RELEASE_VERSION}-py3-none-any.whl
```

### Documentation is awesome

Contributing to the documentation is not mandatory but it will ensure people are aware of your important contribution. 
The best way to add documentation is by including suggestions to the [docs](https://github.com/bridgecrewio/checkov/tree/master/docs) 
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
