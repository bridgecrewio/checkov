# This dockerfile is built from the parent dir, hence the addition of `admissioncontroller/` everywhere
FROM python:3.8-slim

ENV RUN_IN_DOCKER=True

RUN apt-get update -y && apt-get install -y python3-pip python-dev
WORKDIR /app
COPY admissioncontroller/requirements.txt /app/requirements.txt
COPY admissioncontroller/checkov-requirements.txt /app/checkov-requirements.txt

RUN pip3 install -r /app/requirements.txt
RUN pip3 install -r /app/checkov-requirements.txt

COPY admissioncontroller/whorf.py /app
COPY admissioncontroller/wsgi.py /app

# create the app user
RUN addgroup --gid 11000 app && adduser --disabled-password --gecos "" --uid 11000 --ingroup app app
# chown all the files to the app user
RUN chown -R app:app /app
# change to the app user
USER app

# mention "admissionController" as the source of integration to bridgecrew.cloud
ENV BC_SOURCE=admissionController

CMD gunicorn --certfile=/certs/webhook.crt --keyfile=/certs/webhook.key --bind 0.0.0.0:8443 wsgi:webhook
