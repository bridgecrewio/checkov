FROM python

RUN pip install -U checkov

ENTRYPOINT ["checkov"]
