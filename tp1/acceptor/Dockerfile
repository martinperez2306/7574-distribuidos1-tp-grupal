FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./acceptor/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir -p storage
COPY ./acceptor .
COPY ./common ./common

ENV PYTHONHASHSEED 7
ENTRYPOINT ["/bin/sh"]