FROM python:3.9.7-slim

WORKDIR /workspace

COPY ./tag_unique/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir -p storage
COPY ./tag_unique .
COPY ./common ./common
ENV PYTHONHASHSEED 7
ENTRYPOINT ["/bin/sh"]