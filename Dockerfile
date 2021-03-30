FROM python:3.8-alpine

RUN apk --no-cache add git

RUN pip install --no-cache-dir -U checkov
ENTRYPOINT ["checkov"]