FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./likes_filter/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY ./likes_filter .
COPY ./common ./common
RUN mkdir -p storage
ENV PYTHONHASHSEED 7
ENTRYPOINT ["/bin/sh"]