FROM python:3.8-slim-buster

RUN pip install -U checkov
RUN apt-get update
RUN apt install -y git

ENTRYPOINT ["checkov"]
