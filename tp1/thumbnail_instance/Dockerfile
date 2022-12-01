FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./thumbnail_instance/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir storage
COPY ./thumbnail_instance .
COPY ./common ./common
RUN mkdir storage
ENTRYPOINT ["/bin/sh"]