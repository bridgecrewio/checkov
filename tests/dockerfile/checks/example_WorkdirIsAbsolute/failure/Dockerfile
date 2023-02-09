FROM alpine:3.5
RUN apk add --update py2-pip
RUN pip install --upgrade pip
WORKDIR /path/to/workdir
WORKDIR workdir
WORKDIR "../workdir"
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt
WORKDIR workdir2
COPY app.py /usr/src/app/
COPY templates/index.html /usr/src/app/templates/
EXPOSE 5000
CMD ["python", "/usr/src/app/app.py"]
