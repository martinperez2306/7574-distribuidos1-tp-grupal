FROM python:3.9.7-slim

WORKDIR /workspace


COPY ./downloader/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir storage
COPY ./downloader .
COPY ./common ./common

ENTRYPOINT ["/bin/sh"]