FROM python:3.8-slim-buster

RUN pip install -U checkov

ENTRYPOINT ["checkov"]
