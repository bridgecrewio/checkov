FROM python

RUN pip install checkov

ENTRYPOINT ["checkov"]