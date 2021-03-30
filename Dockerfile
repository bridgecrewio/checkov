FROM python:3.8-alpine

RUN apk update && apk add git

RUN pip install -U checkov
ENTRYPOINT ["checkov"]