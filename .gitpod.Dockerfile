FROM gitpod/workspace-python
RUN pyenv install 3.7.12
RUN pipenv sync --dev